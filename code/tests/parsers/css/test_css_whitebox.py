"""CSS parser white box tests.

Tests internals: tinycss2 AST pipeline, and custom rules with mocked dependencies.
"""

import pytest
from unittest.mock import patch
from src.parsers.css_parser import CSSParser


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
