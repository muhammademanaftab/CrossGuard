"""Tests for CSS parser custom rule feature detection."""

import pytest
from unittest.mock import patch
from src.parsers.css_parser import CSSParser


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


class TestCSSCustomDetection:

    def test_custom_property_detected(self, css_parser_with_custom):
        """Custom CSS property rule triggers on matching CSS."""
        css = ".box { test-custom-prop: value; }"
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" in features

    def test_custom_animation_detected(self, css_parser_with_custom):
        """Custom animation rule triggers correctly."""
        css = ".anim { custom-animation-name: slidein; }"
        features = css_parser_with_custom.parse_string(css)
        assert "custom-animation-feat" in features

    def test_custom_rule_not_triggered_on_unrelated_css(self, css_parser_with_custom):
        """No false positives for unrelated CSS."""
        css = ".box { color: red; margin: 10px; }"
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" not in features
        assert "custom-animation-feat" not in features

    def test_multiple_custom_rules_detected(self, css_parser_with_custom):
        """Two custom rules both found in one file."""
        css = """
        .box { test-custom-prop: value; }
        .anim { custom-animation-name: slidein; }
        """
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" in features
        assert "custom-animation-feat" in features

    def test_custom_rule_merged_with_builtin(self, css_parser_with_custom):
        """Custom rule doesn't break built-in detection."""
        css = """
        .box {
            display: flex;
            test-custom-prop: value;
        }
        """
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" in features
        assert "flexbox" in features

    def test_builtin_still_works_with_custom_rules(self, css_parser_with_custom):
        """Built-in rules still function when custom rules are present."""
        css = """
        .grid { display: grid; }
        @keyframes spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }
        """
        features = css_parser_with_custom.parse_string(css)
        assert "css-grid" in features

    def test_custom_rule_with_complex_regex(self, css_parser_with_custom):
        """Regex with groups, alternation works."""
        css = ".bg { background: fancy-gradient(red, blue); }"
        features = css_parser_with_custom.parse_string(css)
        assert "complex-regex-feat" in features

        css2 = ".bg { background: special-gradient(red, blue); }"
        features2 = css_parser_with_custom.parse_string(css2)
        assert "complex-regex-feat" in features2

    def test_empty_custom_rules_no_effect(self):
        """Parser works normally with no custom rules."""
        with patch('src.parsers.css_parser.get_custom_css_rules', return_value={}):
            parser = CSSParser()
            css = ".box { display: flex; }"
            features = parser.parse_string(css)
            assert "flexbox" in features
