"""Consolidated custom rules tests for the JavaScript parser.

Tests custom rule detection, false positive prevention, merging with built-in
rules, and custom rule appearance in detailed reports.
"""

import pytest
from unittest.mock import patch
from src.parsers.js_parser import JavaScriptParser


@pytest.fixture
def custom_js_rules():
    """Custom JS rules for testing."""
    return {
        "test-custom-api": {
            "patterns": [r"\bCustomTestAPI\b"],
            "description": "Custom Test API"
        },
        "custom-syntax-feat": {
            "patterns": [r"customSyntax\s*\("],
            "description": "Custom Syntax Feature"
        },
        "multi-pattern-js": {
            "patterns": [r"\bmultiApiA\b", r"\bmultiApiB\b"],
            "description": "Multi Pattern JS Feature"
        },
        "word-boundary-feat": {
            "patterns": [r"\bspecificBoundaryAPI\b"],
            "description": "Word Boundary Feature"
        },
        "report-js-feat": {
            "patterns": [r"\bReportTestJSAPI\b"],
            "description": "Report Test JS Feature"
        }
    }


@pytest.fixture
def js_parser_with_custom(custom_js_rules):
    """JavaScriptParser with injected custom rules."""
    with patch('src.parsers.js_parser.get_custom_js_rules', return_value=custom_js_rules):
        parser = JavaScriptParser()
        yield parser


class TestJSCustomDetection:

    def test_custom_api_pattern_detected(self, js_parser_with_custom):
        js = "const result = CustomTestAPI.doSomething();"
        features = js_parser_with_custom.parse_string(js)
        assert "test-custom-api" in features

    def test_custom_syntax_pattern_detected(self, js_parser_with_custom):
        js = "customSyntax(arg1, arg2);"
        features = js_parser_with_custom.parse_string(js)
        assert "custom-syntax-feat" in features

    def test_custom_rule_not_triggered_on_unrelated_js(self, js_parser_with_custom):
        js = "var x = 1; var y = 2;"
        features = js_parser_with_custom.parse_string(js)
        assert "test-custom-api" not in features
        assert "custom-syntax-feat" not in features

    def test_multiple_custom_rules_detected(self, js_parser_with_custom):
        js = """
        CustomTestAPI.init();
        customSyntax(42);
        """
        features = js_parser_with_custom.parse_string(js)
        assert "test-custom-api" in features
        assert "custom-syntax-feat" in features

    def test_custom_rule_merged_with_builtin(self, js_parser_with_custom):
        js = """
        const p = new Promise((resolve) => resolve(42));
        CustomTestAPI.start();
        """
        features = js_parser_with_custom.parse_string(js)
        assert "test-custom-api" in features
        assert "promises" in features

    def test_builtin_still_works_with_custom_rules(self, js_parser_with_custom):
        js = """
        const data = await fetch('/api/data');
        const items = [...array];
        """
        features = js_parser_with_custom.parse_string(js)
        assert "fetch" in features

    def test_custom_rule_with_word_boundary_regex(self, js_parser_with_custom):
        js = "const val = specificBoundaryAPI;"
        features = js_parser_with_custom.parse_string(js)
        assert "word-boundary-feat" in features

        # Should not match partial word
        js2 = "const val = notspecificBoundaryAPIhere;"
        features2 = js_parser_with_custom.parse_string(js2)
        assert "word-boundary-feat" not in features2

    def test_empty_custom_rules_no_effect(self):
        with patch('src.parsers.js_parser.get_custom_js_rules', return_value={}):
            parser = JavaScriptParser()
            js = "const p = new Promise((r) => r(1));"
            features = parser.parse_string(js)
            assert "promises" in features


class TestJSCustomReport:

    def test_custom_rule_appears_in_report(self, js_parser_with_custom):
        js = "ReportTestJSAPI.init();"
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        assert "report-js-feat" in report['features']

    def test_custom_rule_feature_id_correct(self, js_parser_with_custom):
        js = "ReportTestJSAPI.start();"
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        detail_ids = [d['feature'] for d in report['feature_details']]
        assert "report-js-feat" in detail_ids

    def test_custom_rule_count_accurate(self, js_parser_with_custom):
        js = """
        ReportTestJSAPI.a();
        ReportTestJSAPI.b();
        """
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        assert report['features'].count("report-js-feat") == 1

    def test_custom_and_builtin_in_same_report(self, js_parser_with_custom):
        js = """
        const p = new Promise((r) => r(1));
        ReportTestJSAPI.run();
        """
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        assert "promises" in report['features']
        assert "report-js-feat" in report['features']
