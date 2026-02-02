"""Tests for edge cases and special scenarios.

Tests comment stripping, string handling, and false positive prevention.
"""

import pytest


class TestCommentStripping:
    """Tests that comments don't trigger false positives."""

    def test_single_line_comment(self, parse_and_check_not):
        """Test that single-line comments are ignored."""
        js = """
        // fetch('/api') is commented out
        var x = 1;
        """
        assert parse_and_check_not(js, 'fetch')

    def test_multi_line_comment(self, parse_and_check_not):
        """Test that multi-line comments are ignored."""
        js = """
        /*
        const promise = new Promise((resolve) => resolve());
        promise.then(console.log);
        */
        var x = 1;
        """
        assert parse_and_check_not(js, 'promises')

    def test_code_after_comment(self, parse_and_check):
        """Test that code after comments is still detected."""
        js = """
        // This is a comment
        fetch('/api');
        """
        assert parse_and_check(js, 'fetch')


class TestStringHandling:
    """Tests that string contents don't trigger false positives."""

    def test_api_name_in_string(self, parse_and_check_not):
        """Test that API names in strings don't trigger detection."""
        js = """
        const message = "We should use fetch instead of XMLHttpRequest";
        """
        # The word "fetch" in string shouldn't trigger fetch API detection
        # Note: This depends on implementation - adjust if needed
        assert parse_and_check_not(js, 'fetch')

    def test_use_strict_detected(self, parse_and_check):
        """Test that 'use strict' directive IS detected."""
        js = '"use strict"; var x = 1;'
        assert parse_and_check(js, 'use-strict')


class TestMinifiedCode:
    """Tests detection in minified code."""

    def test_minified_arrow_function(self, parse_and_check):
        """Test arrow function in minified code."""
        js = "const a=(b,c)=>b+c;const d=e=>e*2;"
        assert parse_and_check(js, 'arrow-functions')

    def test_minified_promise(self, parse_and_check):
        """Test Promise in minified code."""
        js = "new Promise(r=>r(1)).then(x=>x*2).catch(e=>e)"
        assert parse_and_check(js, 'promises')

    def test_minified_fetch(self, parse_and_check):
        """Test fetch in minified code."""
        js = "fetch('/api').then(r=>r.json())"
        assert parse_and_check(js, 'fetch')


class TestEmptyAndMinimal:
    """Tests for empty and minimal input."""

    def test_empty_string(self, parse_js):
        """Test empty string returns empty set."""
        features = parse_js("")
        assert len(features) == 0

    def test_whitespace_only(self, parse_js):
        """Test whitespace-only string."""
        features = parse_js("   \n\t   ")
        assert len(features) == 0

    def test_minimal_js(self, parse_js):
        """Test minimal JS with no modern features."""
        features = parse_js("var x = 1;")
        # Should not detect any modern features
        assert 'const' not in features
        assert 'let' not in features
        assert 'arrow-functions' not in features


class TestCombinedFeatures:
    """Tests for combined feature detection."""

    def test_multiple_features(self, parse_and_check_multiple):
        """Test detecting multiple features in one file."""
        js = """
        const fetchData = async () => {
            const response = await fetch('/api');
            return response.json();
        };

        document.querySelector('.btn').addEventListener('click', () => {
            localStorage.setItem('clicked', 'true');
        });
        """
        assert parse_and_check_multiple(js, [
            'const',
            'arrow-functions',
            'async-functions',
            'fetch',
            'queryselector',
            'addeventlistener',
            'namevalue-storage'
        ])


class TestFeatureDetails:
    """Tests for feature details reporting."""

    def test_feature_details_populated(self, get_feature_details):
        """Test that feature details are populated."""
        js = "const fn = () => 1; fetch('/api');"
        details = get_feature_details(js)
        assert len(details) > 0

    def test_feature_details_has_matched_apis(self, get_feature_details):
        """Test that feature details include matched APIs."""
        js = "navigator.geolocation.getCurrentPosition(callback);"
        details = get_feature_details(js)
        # Find geolocation feature
        geo_detail = next((d for d in details if d['feature'] == 'geolocation'), None)
        assert geo_detail is not None
        assert 'matched_apis' in geo_detail


class TestRealWorldPatterns:
    """Tests for real-world code patterns."""

    def test_react_component(self, parse_and_check_multiple):
        """Test React-like component patterns."""
        js = """
        const MyComponent = () => {
            const [state, setState] = useState(null);

            useEffect(() => {
                fetch('/api/data')
                    .then(r => r.json())
                    .then(setState);
            }, []);

            return state;
        };
        """
        assert parse_and_check_multiple(js, ['arrow-functions', 'const', 'fetch'])

    def test_async_await_pattern(self, parse_and_check_multiple):
        """Test async/await pattern."""
        js = """
        async function loadData() {
            try {
                const response = await fetch('/api');
                const data = await response.json();
                localStorage.setItem('data', JSON.stringify(data));
                return data;
            } catch (error) {
                console.error(error);
            }
        }
        """
        assert parse_and_check_multiple(js, [
            'async-functions',
            'fetch',
            'namevalue-storage',
            'json'
        ])

    def test_class_with_observers(self, parse_and_check_multiple):
        """Test class with observers."""
        js = """
        class LazyLoader {
            constructor() {
                this.observer = new IntersectionObserver(this.handleIntersect);
            }

            observe(element) {
                this.observer.observe(element);
            }
        }
        """
        assert parse_and_check_multiple(js, ['es6-class', 'intersectionobserver'])
