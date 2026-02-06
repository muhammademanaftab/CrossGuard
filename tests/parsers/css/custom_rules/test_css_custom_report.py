"""Tests for CSS parser detailed report output with custom rules."""

import pytest
from unittest.mock import patch
from src.parsers.css_parser import CSSParser


@pytest.fixture
def custom_css_rules():
    """Custom CSS rules for report testing."""
    return {
        "report-test-feat": {
            "patterns": [r"report-prop\s*:"],
            "description": "Report Test Feature"
        }
    }


@pytest.fixture
def css_parser_with_custom(custom_css_rules):
    """CSSParser with injected custom rules."""
    with patch('src.parsers.css_parser.get_custom_css_rules', return_value=custom_css_rules):
        parser = CSSParser()
        yield parser


class TestCSSCustomReport:

    def test_custom_rule_appears_in_report(self, css_parser_with_custom):
        """Detected custom rule shows in detailed report."""
        css = ".box { report-prop: value; }"
        css_parser_with_custom.parse_string(css)
        report = css_parser_with_custom.get_detailed_report()
        assert "report-test-feat" in report['features']

    def test_custom_rule_feature_id_correct(self, css_parser_with_custom):
        """Feature ID matches what was defined."""
        css = ".box { report-prop: value; }"
        css_parser_with_custom.parse_string(css)
        report = css_parser_with_custom.get_detailed_report()
        detail_ids = [d['feature'] for d in report['feature_details']]
        assert "report-test-feat" in detail_ids

    def test_custom_rule_count_accurate(self, css_parser_with_custom):
        """Custom rule detected once even with multiple occurrences (feature set)."""
        css = """
        .a { report-prop: val1; }
        .b { report-prop: val2; }
        """
        css_parser_with_custom.parse_string(css)
        report = css_parser_with_custom.get_detailed_report()
        # Feature appears once in features list (it's a set)
        assert report['features'].count("report-test-feat") == 1

    def test_custom_and_builtin_in_same_report(self, css_parser_with_custom):
        """Both custom and built-in appear together in results."""
        css = """
        .box { display: flex; report-prop: value; }
        """
        css_parser_with_custom.parse_string(css)
        report = css_parser_with_custom.get_detailed_report()
        assert "flexbox" in report['features']
        assert "report-test-feat" in report['features']
