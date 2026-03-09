"""Edge case and special scenario tests for the JavaScript parser.

Tests comment stripping, string handling, minified code, empty input,
combined features, feature details, and real-world patterns.
"""

import pytest


class TestCommentStripping:
    """Tests that comments don't trigger false positives."""

    def test_single_line_comment(self, parse_features):
        js = """
        // fetch('/api') is commented out
        var x = 1;
        """
        assert 'fetch' not in parse_features(js)

    def test_multi_line_comment(self, parse_features):
        js = """
        /*
        const promise = new Promise((resolve) => resolve());
        promise.then(console.log);
        */
        var x = 1;
        """
        assert 'promises' not in parse_features(js)

    def test_code_after_comment(self, parse_features):
        js = """
        // This is a comment
        fetch('/api');
        """
        assert 'fetch' in parse_features(js)


class TestStringHandling:
    """Tests that string contents don't trigger false positives."""

    def test_api_name_in_string(self, parse_features):
        js = """
        const message = "We should use fetch instead of XMLHttpRequest";
        """
        assert 'fetch' not in parse_features(js)

    def test_use_strict_detected(self, parse_features):
        js = '"use strict"; var x = 1;'
        assert 'use-strict' in parse_features(js)


class TestMinifiedCode:
    """Tests detection in minified code."""

    def test_minified_arrow_function(self, parse_features):
        js = "const a=(b,c)=>b+c;const d=e=>e*2;"
        assert 'arrow-functions' in parse_features(js)

    def test_minified_promise(self, parse_features):
        js = "new Promise(r=>r(1)).then(x=>x*2).catch(e=>e)"
        assert 'promises' in parse_features(js)

    def test_minified_fetch(self, parse_features):
        js = "fetch('/api').then(r=>r.json())"
        assert 'fetch' in parse_features(js)


class TestEmptyAndMinimal:
    """Tests for empty and minimal input."""

    def test_empty_string(self, parse_features):
        features = parse_features("")
        assert len(features) == 0

    def test_whitespace_only(self, parse_features):
        features = parse_features("   \n\t   ")
        assert len(features) == 0

    def test_minimal_js(self, parse_features):
        features = parse_features("var x = 1;")
        assert 'const' not in features
        assert 'let' not in features
        assert 'arrow-functions' not in features


class TestCombinedFeatures:
    """Tests for combined feature detection."""

    def test_multiple_features(self, parse_features):
        js = """
        const fetchData = async () => {
            const response = await fetch('/api');
            return response.json();
        };

        document.querySelector('.btn').addEventListener('click', () => {
            localStorage.setItem('clicked', 'true');
        });
        """
        features = parse_features(js)
        for expected in [
            'const', 'arrow-functions', 'async-functions', 'fetch',
            'queryselector', 'addeventlistener', 'namevalue-storage'
        ]:
            assert expected in features


class TestFeatureDetails:
    """Tests for feature details reporting."""

    def test_feature_details_populated(self, get_feature_details):
        js = "const fn = () => 1; fetch('/api');"
        details = get_feature_details(js)
        assert len(details) > 0

    def test_feature_details_has_matched_apis(self, get_feature_details):
        js = "navigator.geolocation.getCurrentPosition(callback);"
        details = get_feature_details(js)
        geo_detail = next((d for d in details if d['feature'] == 'geolocation'), None)
        assert geo_detail is not None
        assert 'matched_apis' in geo_detail


class TestRealWorldPatterns:
    """Tests for real-world code patterns."""

    def test_react_component(self, parse_features):
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
        features = parse_features(js)
        for expected in ['arrow-functions', 'const', 'fetch']:
            assert expected in features

    def test_async_await_pattern(self, parse_features):
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
        features = parse_features(js)
        for expected in ['async-functions', 'fetch', 'namevalue-storage', 'json']:
            assert expected in features

    def test_class_with_observers(self, parse_features):
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
        features = parse_features(js)
        for expected in ['es6-class', 'intersectionobserver']:
            assert expected in features
