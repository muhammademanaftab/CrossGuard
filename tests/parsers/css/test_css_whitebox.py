"""CSS parser white box tests.

Tests internals: state management, tinycss2 AST pipeline, private methods,
bug documentation, and custom rules with mocked dependencies.
"""

import pytest
from unittest.mock import patch
from src.parsers.css_parser import CSSParser


# =====================================================================
# State Reset
# =====================================================================

@pytest.mark.whitebox
class TestStateReset:
    def test_features_reset(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        assert "flexbox" in css_parser.features_found
        css_parser.parse_string("div { color: red; }")
        assert "flexbox" not in css_parser.features_found

    def test_block_counter_reset(self, css_parser):
        css_parser.parse_string("div { color: red; } span { color: blue; }")
        assert css_parser._block_counter > 0
        css_parser.parse_string("")
        assert css_parser._block_counter == 0


# =====================================================================
# Block Boundary Preservation (flexbox-gap context detection)
# =====================================================================

@pytest.mark.whitebox
class TestBlockBoundaryPreservation:
    def test_flex_and_gap_same_block(self, parse_features):
        assert "flexbox-gap" in parse_features(".c { display: flex; gap: 10px; }")

    def test_flex_and_gap_different_blocks(self, parse_features):
        css = ".flex { display: flex; } .grid { display: grid; gap: 10px; }"
        assert "flexbox-gap" not in parse_features(css)

    def test_grid_gap_not_detected_as_flexbox_gap(self, parse_features):
        assert "flexbox-gap" not in parse_features(".grid { display: grid; gap: 10px; }")


# =====================================================================
# Unrecognized Patterns (internal state inspection)
# =====================================================================

@pytest.mark.whitebox
class TestUnrecognizedPatterns:
    def test_unknown_property_flagged(self, css_parser):
        css_parser.parse_string("div { some-unknown-property: value; }")
        assert any("some-unknown-property" in p for p in css_parser.unrecognized_patterns)


# =====================================================================
# Bug Documentation
# =====================================================================

@pytest.mark.whitebox
class TestWoffPatternOverlap:
    """BUG 3: 'woff' pattern must not match 'woff2'."""

    def test_woff2_only_does_not_trigger_woff(self, parse_features):
        features = parse_features(
            "@font-face { font-family: T; src: url('f.woff2'); }"
        )
        assert "woff2" in features
        assert "woff" not in features


@pytest.mark.whitebox
class TestPatternPrecision:
    def test_transform_property_triggers_2d_for_3d_value(self, parse_features):
        features = parse_features("div { transform: rotateY(45deg); }")
        assert "transforms2d" in features
        assert "transforms3d" in features

    def test_filter_triggers_both_features(self, parse_features):
        features = parse_features("div { filter: blur(5px); }")
        assert "css-filters" in features
        assert "css-filter-function" in features

    def test_transition_all_does_not_trigger_css_all(self, parse_features):
        assert "css-all" not in parse_features("div { transition: all 0.3s ease; }")


# =====================================================================
# Custom Rules
# =====================================================================

@pytest.fixture
def custom_css_rules():
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
    with patch('src.parsers.css_parser.get_custom_css_rules', return_value=custom_css_rules):
        yield CSSParser()


@pytest.fixture
def custom_report_rules():
    return {
        "report-test-feat": {
            "patterns": [r"report-prop\s*:"],
            "description": "Report Test Feature"
        }
    }


@pytest.fixture
def css_parser_with_report_custom(custom_report_rules):
    with patch('src.parsers.css_parser.get_custom_css_rules', return_value=custom_report_rules):
        yield CSSParser()


@pytest.mark.whitebox
class TestCSSCustomDetection:
    def test_custom_property_detected(self, css_parser_with_custom):
        assert "test-custom-prop" in css_parser_with_custom.parse_string(
            ".box { test-custom-prop: value; }"
        )

    def test_custom_rule_not_triggered_on_unrelated_css(self, css_parser_with_custom):
        features = css_parser_with_custom.parse_string(".box { color: red; margin: 10px; }")
        assert "test-custom-prop" not in features
        assert "custom-animation-feat" not in features

    def test_custom_rule_merged_with_builtin(self, css_parser_with_custom):
        features = css_parser_with_custom.parse_string(
            ".box { display: flex; test-custom-prop: value; }"
        )
        assert "test-custom-prop" in features
        assert "flexbox" in features

    def test_empty_custom_rules_no_effect(self):
        with patch('src.parsers.css_parser.get_custom_css_rules', return_value={}):
            assert "flexbox" in CSSParser().parse_string(".box { display: flex; }")


@pytest.mark.whitebox
class TestCSSCustomReport:
    def test_custom_rule_appears_in_report(self, css_parser_with_report_custom):
        css_parser_with_report_custom.parse_string(".box { report-prop: value; }")
        report = css_parser_with_report_custom.get_detailed_report()
        assert "report-test-feat" in report["features"]

    def test_custom_and_builtin_in_same_report(self, css_parser_with_report_custom):
        css_parser_with_report_custom.parse_string(
            ".box { display: flex; report-prop: value; }"
        )
        report = css_parser_with_report_custom.get_detailed_report()
        assert "flexbox" in report["features"]
        assert "report-test-feat" in report["features"]
