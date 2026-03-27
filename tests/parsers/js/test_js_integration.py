"""Integration tests for the JavaScript parser.

End-to-end tests with validation files, feature category coverage, and parser
statistics -- exercises the full pipeline from file I/O through detection.
"""

import pytest
from pathlib import Path


class TestValidationFiles:
    """Tests using the validation test files."""

    @pytest.fixture
    def validation_path(self):
        """Path to JS validation test files."""
        return Path(__file__).parent.parent.parent / 'validation' / 'js'

    @pytest.mark.integration
    def test_es6_syntax_file(self, js_parser, validation_path):
        file_path = validation_path / '01_es6_syntax.js'
        if file_path.exists():
            features = js_parser.parse_file(str(file_path))
            for feat in ['arrow-functions', 'async-functions', 'const', 'let',
                         'template-literals', 'es6-class', 'es6-generators', 'use-strict']:
                assert feat in features, f"Missing feature: {feat}"

    @pytest.mark.integration
    def test_promises_file(self, js_parser, validation_path):
        file_path = validation_path / '02_promises_async.js'
        if file_path.exists():
            features = js_parser.parse_file(str(file_path))
            for feat in ['promises', 'fetch', 'abortcontroller', 'requestanimationframe']:
                assert feat in features, f"Missing feature: {feat}"


class TestFeatureCategories:
    """Tests that each feature category is properly detected end-to-end."""

    @pytest.mark.integration
    def test_syntax_features(self, parse_features):
        js = """
        const fn = async () => {
            let x = 1;
            class Foo {}
            function* gen() { yield 1; }
        };
        """
        features = parse_features(js)
        for expected in ['const', 'let', 'arrow-functions', 'async-functions',
                         'es6-class', 'es6-generators']:
            assert expected in features

    @pytest.mark.integration
    def test_promise_features(self, parse_features):
        js = """
        new Promise((r) => r(1))
            .then(x => x)
            .catch(e => e)
            .finally(() => {});
        fetch('/api');
        const ctrl = new AbortController();
        """
        features = parse_features(js)
        for expected in ['promises', 'promise-finally', 'fetch', 'abortcontroller']:
            assert expected in features

    @pytest.mark.integration
    def test_observer_features(self, parse_features):
        js = """
        new IntersectionObserver(cb);
        new MutationObserver(cb);
        new ResizeObserver(cb);
        """
        features = parse_features(js)
        for expected in ['intersectionobserver', 'mutationobserver', 'resizeobserver']:
            assert expected in features

    @pytest.mark.integration
    def test_storage_features(self, parse_features):
        js = """
        localStorage.setItem('k', 'v');
        indexedDB.open('db');
        new FileReader();
        new TextEncoder();
        """
        features = parse_features(js)
        for expected in ['namevalue-storage', 'indexeddb', 'filereader', 'textencoder']:
            assert expected in features


class TestParserStatistics:
    """Tests for parser statistics functionality."""

    @pytest.mark.integration
    def test_statistics_populated(self, js_parser):
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

    @pytest.mark.integration
    def test_detailed_report(self, js_parser):
        js = "new IntersectionObserver(cb);"
        js_parser.parse_string(js)
        report = js_parser.get_detailed_report()

        assert 'total_features' in report
        assert 'features' in report
        assert 'feature_details' in report
        assert 'intersectionobserver' in report['features']
