"""Tests for JS parser detailed report output with custom rules."""

import pytest
from unittest.mock import patch
from src.parsers.js_parser import JavaScriptParser


@pytest.fixture
def custom_js_rules():
    """Custom JS rules for report testing."""
    return {
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


class TestJSCustomReport:

    def test_custom_rule_appears_in_report(self, js_parser_with_custom):
        """Custom rule in detailed report."""
        js = "ReportTestJSAPI.init();"
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        assert "report-js-feat" in report['features']

    def test_custom_rule_feature_id_correct(self, js_parser_with_custom):
        """Feature ID matches definition."""
        js = "ReportTestJSAPI.start();"
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        detail_ids = [d['feature'] for d in report['feature_details']]
        assert "report-js-feat" in detail_ids

    def test_custom_rule_count_accurate(self, js_parser_with_custom):
        """Multiple occurrences counted as single feature (set behavior)."""
        js = """
        ReportTestJSAPI.a();
        ReportTestJSAPI.b();
        """
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        assert report['features'].count("report-js-feat") == 1

    def test_custom_and_builtin_in_same_report(self, js_parser_with_custom):
        """Both appear in results."""
        js = """
        const p = new Promise((r) => r(1));
        ReportTestJSAPI.run();
        """
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        assert "promises" in report['features']
        assert "report-js-feat" in report['features']
