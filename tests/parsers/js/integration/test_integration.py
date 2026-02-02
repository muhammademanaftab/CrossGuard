"""Integration tests for JavaScript parser.

Tests the parser with comprehensive test files and verifies
all major feature categories are detected correctly.
"""

import pytest
from pathlib import Path


class TestValidationFiles:
    """Tests using the validation test files."""

    @pytest.fixture
    def validation_path(self):
        """Path to JS validation test files."""
        return Path(__file__).parent.parent.parent.parent / 'validation' / 'js'

    def test_es6_syntax_file(self, js_parser, validation_path):
        """Test ES6 syntax validation file."""
        file_path = validation_path / '01_es6_syntax.js'
        if file_path.exists():
            features = js_parser.parse_file(str(file_path))
            expected = ['arrow-functions', 'async-functions', 'const', 'let',
                        'template-literals', 'es6-class', 'es6-generators', 'use-strict']
            for feat in expected:
                assert feat in features, f"Missing feature: {feat}"

    def test_promises_file(self, js_parser, validation_path):
        """Test promises validation file."""
        file_path = validation_path / '02_promises_async.js'
        if file_path.exists():
            features = js_parser.parse_file(str(file_path))
            expected = ['promises', 'fetch', 'abortcontroller', 'requestanimationframe']
            for feat in expected:
                assert feat in features, f"Missing feature: {feat}"

    def test_dom_apis_file(self, js_parser, validation_path):
        """Test DOM APIs validation file."""
        file_path = validation_path / '03_dom_apis.js'
        if file_path.exists():
            features = js_parser.parse_file(str(file_path))
            expected = ['queryselector', 'classlist', 'dataset', 'addeventlistener']
            for feat in expected:
                assert feat in features, f"Missing feature: {feat}"

    def test_storage_file(self, js_parser, validation_path):
        """Test storage validation file."""
        file_path = validation_path / '04_web_storage.js'
        if file_path.exists():
            features = js_parser.parse_file(str(file_path))
            expected = ['namevalue-storage', 'indexeddb', 'filereader', 'textencoder']
            for feat in expected:
                assert feat in features, f"Missing feature: {feat}"

    def test_comprehensive_file(self, js_parser, validation_path):
        """Test comprehensive validation file detects many features."""
        file_path = validation_path / 'comprehensive_test.js'
        if file_path.exists():
            features = js_parser.parse_file(str(file_path))
            # Should detect at least 100 features
            assert len(features) >= 100, f"Expected 100+ features, got {len(features)}"


class TestFeatureCategories:
    """Tests that each feature category is properly detected."""

    def test_syntax_features(self, parse_and_check_multiple):
        """Test syntax feature category."""
        js = """
        const fn = async () => {
            let x = 1;
            class Foo {}
            function* gen() { yield 1; }
        };
        """
        assert parse_and_check_multiple(js, [
            'const', 'let', 'arrow-functions', 'async-functions',
            'es6-class', 'es6-generators'
        ])

    def test_promise_features(self, parse_and_check_multiple):
        """Test promise feature category."""
        js = """
        new Promise((r) => r(1))
            .then(x => x)
            .catch(e => e)
            .finally(() => {});
        fetch('/api');
        const ctrl = new AbortController();
        """
        assert parse_and_check_multiple(js, [
            'promises', 'promise-finally', 'fetch', 'abortcontroller'
        ])

    def test_dom_features(self, parse_and_check_multiple):
        """Test DOM feature category."""
        js = """
        document.querySelector('.el').classList.add('active');
        element.dataset.id = '1';
        element.addEventListener('click', () => {});
        element.insertAdjacentHTML('beforeend', '<span/>');
        element.scrollIntoView();
        """
        assert parse_and_check_multiple(js, [
            'queryselector', 'classlist', 'dataset',
            'addeventlistener', 'insertadjacenthtml', 'scrollintoview'
        ])

    def test_observer_features(self, parse_and_check_multiple):
        """Test observer feature category."""
        js = """
        new IntersectionObserver(cb);
        new MutationObserver(cb);
        new ResizeObserver(cb);
        """
        assert parse_and_check_multiple(js, [
            'intersectionobserver', 'mutationobserver', 'resizeobserver'
        ])

    def test_storage_features(self, parse_and_check_multiple):
        """Test storage feature category."""
        js = """
        localStorage.setItem('k', 'v');
        indexedDB.open('db');
        new FileReader();
        new TextEncoder();
        """
        assert parse_and_check_multiple(js, [
            'namevalue-storage', 'indexeddb', 'filereader', 'textencoder'
        ])

    def test_array_methods(self, parse_and_check_multiple):
        """Test array method feature category."""
        js = """
        arr.flat();
        arr.includes(x);
        arr.find(x => x);
        arr.forEach(x => x);
        """
        assert parse_and_check_multiple(js, [
            'array-flat', 'array-includes', 'array-find', 'es5'
        ])

    def test_modern_apis(self, parse_and_check_multiple):
        """Test modern API feature category."""
        js = """
        new WebGLRenderingContext();
        new RTCPeerConnection(config);
        element.animate(keyframes, 1000);
        navigator.share({ title: 'Test' });
        history.pushState({}, '', '/');
        """
        assert parse_and_check_multiple(js, [
            'webgl', 'rtcpeerconnection', 'web-animation', 'web-share', 'history'
        ])


class TestParserStatistics:
    """Tests for parser statistics functionality."""

    def test_statistics_populated(self, js_parser):
        """Test that statistics are populated after parsing."""
        js = """
        const fn = () => 1;
        fetch('/api');
        localStorage.setItem('k', 'v');
        """
        js_parser.parse_string(js)
        stats = js_parser.get_statistics()

        assert stats['total_features'] > 0
        assert 'features_list' in stats
        assert len(stats['features_list']) > 0

    def test_detailed_report(self, js_parser):
        """Test detailed report generation."""
        js = "new IntersectionObserver(cb);"
        js_parser.parse_string(js)
        report = js_parser.get_detailed_report()

        assert 'total_features' in report
        assert 'features' in report
        assert 'feature_details' in report
        assert 'intersectionobserver' in report['features']
