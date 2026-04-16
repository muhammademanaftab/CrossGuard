"""CSS parser white box tests.

Tests internals: state management, tinycss2 AST pipeline, private methods,
bug documentation, and custom rules with mocked dependencies.
"""

import pytest
from unittest.mock import patch
from src.parsers.css_parser import CSSParser


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


# =====================================================================
# Bug Documentation
# =====================================================================

@pytest.mark.whitebox
class TestPatternPrecision:
    def test_transform_property_triggers_2d_for_3d_value(self, parse_features):
        features = parse_features("div { transform: rotateY(45deg); }")
        assert "transforms2d" in features
        assert "transforms3d" in features


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


@pytest.mark.whitebox
class TestCSSCustomDetection:
    def test_custom_property_detected(self, css_parser_with_custom):
        assert "test-custom-prop" in css_parser_with_custom.parse_string(
            ".box { test-custom-prop: value; }"
        )

    def test_custom_rule_merged_with_builtin(self, css_parser_with_custom):
        features = css_parser_with_custom.parse_string(
            ".box { display: flex; test-custom-prop: value; }"
        )
        assert "test-custom-prop" in features
        assert "flexbox" in features
