"""Consolidated CSS custom rules tests -- kept as-is from originals.

Merged from: custom_rules/test_css_custom_detection.py,
custom_rules/test_css_custom_report.py
"""

import pytest
from unittest.mock import patch
from src.parsers.css_parser import CSSParser


# --- Fixtures ---

@pytest.fixture
def custom_css_rules():
    """Custom CSS rules for testing."""
    return {
        "test-custom-prop": {
            "patterns": [r"test-custom-prop\s*:"],
            "description": "Test Custom Property"
        },
        "custom-animation-feat": {
            "patterns": [r"custom-animation-name\s*:"],
            "description": "Custom Animation Feature"
        },
        "multi-pattern-feat": {
            "patterns": [r"multi-a\s*:", r"multi-b\s*:"],
            "description": "Multi Pattern Feature"
        },
        "complex-regex-feat": {
            "patterns": [r"(?:fancy|special)-gradient\s*\("],
            "description": "Complex Regex Feature"
        }
    }


@pytest.fixture
def css_parser_with_custom(custom_css_rules):
    """CSSParser with injected custom rules."""
    with patch('src.parsers.css_parser.get_custom_css_rules', return_value=custom_css_rules):
        parser = CSSParser()
        yield parser


@pytest.fixture
def custom_report_rules():
    """Custom CSS rules for report testing."""
    return {
        "report-test-feat": {
            "patterns": [r"report-prop\s*:"],
            "description": "Report Test Feature"
        }
    }


@pytest.fixture
def css_parser_with_report_custom(custom_report_rules):
    """CSSParser with injected custom rules for report testing."""
    with patch('src.parsers.css_parser.get_custom_css_rules', return_value=custom_report_rules):
        parser = CSSParser()
        yield parser


# ═══════════════════════════════════════════════════════════════════════════
# Custom Rule Detection
# ═══════════════════════════════════════════════════════════════════════════

class TestCSSCustomDetection:

    def test_custom_property_detected(self, css_parser_with_custom):
        css = ".box { test-custom-prop: value; }"
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" in features

    def test_custom_animation_detected(self, css_parser_with_custom):
        css = ".anim { custom-animation-name: slidein; }"
        features = css_parser_with_custom.parse_string(css)
        assert "custom-animation-feat" in features

    def test_custom_rule_not_triggered_on_unrelated_css(self, css_parser_with_custom):
        css = ".box { color: red; margin: 10px; }"
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" not in features
        assert "custom-animation-feat" not in features

    def test_multiple_custom_rules_detected(self, css_parser_with_custom):
        css = """
        .box { test-custom-prop: value; }
        .anim { custom-animation-name: slidein; }
        """
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" in features
        assert "custom-animation-feat" in features

    def test_custom_rule_merged_with_builtin(self, css_parser_with_custom):
        css = ".box { display: flex; test-custom-prop: value; }"
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" in features
        assert "flexbox" in features

    def test_builtin_still_works_with_custom_rules(self, css_parser_with_custom):
        css = ".grid { display: grid; }"
        features = css_parser_with_custom.parse_string(css)
        assert "css-grid" in features

    def test_custom_rule_with_complex_regex(self, css_parser_with_custom):
        css = ".bg { background: fancy-gradient(red, blue); }"
        features = css_parser_with_custom.parse_string(css)
        assert "complex-regex-feat" in features

        css2 = ".bg { background: special-gradient(red, blue); }"
        features2 = css_parser_with_custom.parse_string(css2)
        assert "complex-regex-feat" in features2

    def test_empty_custom_rules_no_effect(self):
        with patch('src.parsers.css_parser.get_custom_css_rules', return_value={}):
            parser = CSSParser()
            css = ".box { display: flex; }"
            features = parser.parse_string(css)
            assert "flexbox" in features


# ═══════════════════════════════════════════════════════════════════════════
# Custom Rule Report
# ═══════════════════════════════════════════════════════════════════════════

class TestCSSCustomReport:

    def test_custom_rule_appears_in_report(self, css_parser_with_report_custom):
        css = ".box { report-prop: value; }"
        css_parser_with_report_custom.parse_string(css)
        report = css_parser_with_report_custom.get_detailed_report()
        assert "report-test-feat" in report["features"]

    def test_custom_rule_feature_id_correct(self, css_parser_with_report_custom):
        css = ".box { report-prop: value; }"
        css_parser_with_report_custom.parse_string(css)
        report = css_parser_with_report_custom.get_detailed_report()
        detail_ids = [d["feature"] for d in report["feature_details"]]
        assert "report-test-feat" in detail_ids

    def test_custom_rule_count_accurate(self, css_parser_with_report_custom):
        css = ".a { report-prop: val1; } .b { report-prop: val2; }"
        css_parser_with_report_custom.parse_string(css)
        report = css_parser_with_report_custom.get_detailed_report()
        assert report["features"].count("report-test-feat") == 1

    def test_custom_and_builtin_in_same_report(self, css_parser_with_report_custom):
        css = ".box { display: flex; report-prop: value; }"
        css_parser_with_report_custom.parse_string(css)
        report = css_parser_with_report_custom.get_detailed_report()
        assert "flexbox" in report["features"]
        assert "report-test-feat" in report["features"]
