"""Whitebox tests for the JavaScript parser.

Tests internals: tree-sitter AST node handling, false positive prevention via AST
(comments/strings), and custom rules injection.
"""

import pytest
from unittest.mock import patch
from src.parsers.js_parser import JavaScriptParser, _TREE_SITTER_AVAILABLE


# --- AST Syntax Detection ---

@pytest.mark.whitebox
def test_ast_private_class_field(parse_features):
    """Private class fields detected via private_property_identifier node."""
    js = """
    class Foo {
        #value = 42;
        get() { return this.#value; }
    }
    """
    assert "mdn-javascript_classes_private_class_fields" in parse_features(js)


# --- False Positive Prevention ---

@pytest.mark.whitebox
@pytest.mark.skipif(not _TREE_SITTER_AVAILABLE, reason="tree-sitter not available")
class TestFalsePositives:
    """Features inside comments/strings should not be detected."""

    def test_feature_in_comment_not_detected(self, parse_features):
        js = "// fetch('/api/data')\nvar x = 1;"
        assert 'fetch' not in parse_features(js)


# --- Custom Rules ---

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


class TestJSCustomRules:

    @pytest.mark.whitebox
    def test_custom_rule_merged_with_builtin(self, js_parser_with_custom):
        js = """
        const p = new Promise((resolve) => resolve(42));
        CustomTestAPI.start();
        """
        features = js_parser_with_custom.parse_string(js)
        assert "test-custom-api" in features
        assert "promises" in features
