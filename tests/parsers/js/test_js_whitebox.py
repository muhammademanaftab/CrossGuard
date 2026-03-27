"""Whitebox tests for the JavaScript parser.

Tests internals: tree-sitter AST node handling, false positive prevention via AST
(comments/strings), regex fallback behavior with mocked dependencies, and custom
rules injection.
"""

import pytest
from unittest.mock import patch
from src.parsers.js_parser import JavaScriptParser, _TREE_SITTER_AVAILABLE


# --- Tier 1: AST Syntax Node Detection ---

AST_SYNTAX_FEATURES = [
    pytest.param("const fn = () => 1;", "arrow-functions", id="arrow"),
    pytest.param(
        "const x = obj?.prop;",
        "mdn-javascript_operators_optional_chaining", id="optional-chain"
    ),
]


@pytest.mark.whitebox
@pytest.mark.parametrize("js_input,expected_id", AST_SYNTAX_FEATURES)
def test_ast_syntax_node_detection(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


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


# --- Tier 2: AST new/call/member Detection ---

AST_NEW_EXPRESSIONS = [
    pytest.param("new Promise((resolve) => resolve());", "promises", id="promise"),
]


@pytest.mark.whitebox
@pytest.mark.parametrize("js_input,expected_id", AST_NEW_EXPRESSIONS)
def test_ast_new_expressions(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


AST_MEMBER_EXPRESSIONS = [
    pytest.param(
        "navigator.serviceWorker.register('/sw.js');",
        "serviceworkers", id="serviceworker"
    ),
]


@pytest.mark.whitebox
@pytest.mark.parametrize("js_input,expected_id", AST_MEMBER_EXPRESSIONS)
def test_ast_member_expressions(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- False Positive Prevention ---

@pytest.mark.whitebox
@pytest.mark.skipif(not _TREE_SITTER_AVAILABLE, reason="tree-sitter not available")
class TestFalsePositives:
    """Features inside comments/strings should not be detected."""

    def test_feature_in_comment_not_detected(self, parse_features):
        js = "// fetch('/api/data')\nvar x = 1;"
        assert 'fetch' not in parse_features(js)

    def test_feature_in_string_not_detected(self, parse_features):
        js = 'const msg = "navigator.bluetooth is not supported";'
        assert 'web-bluetooth' not in parse_features(js)

    def test_real_code_detected_despite_comment(self, parse_features):
        js = '''
        // This uses Proxy
        const p = new Proxy(target, handler);
        '''
        assert 'proxy' in parse_features(js)


# --- Regex Fallback (mocked tree-sitter) ---

FALLBACK_FEATURES = [
    pytest.param("const fn = () => 1;", "arrow-functions", id="arrow"),
    pytest.param("fetch('/api');", "fetch", id="fetch"),
    pytest.param("new Promise((resolve) => resolve());", "promises", id="promises"),
]


@pytest.mark.whitebox
@pytest.mark.parametrize("js_input,expected_id", FALLBACK_FEATURES)
def test_regex_fallback(js_input, expected_id):
    """Verify features detected when tree-sitter is disabled."""
    with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
        parser = JavaScriptParser()
        features = parser.parse_string(js_input)
        assert expected_id in features


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
    def test_custom_api_pattern_detected(self, js_parser_with_custom):
        js = "const result = CustomTestAPI.doSomething();"
        features = js_parser_with_custom.parse_string(js)
        assert "test-custom-api" in features

    @pytest.mark.whitebox
    def test_custom_rule_not_triggered_on_unrelated_js(self, js_parser_with_custom):
        js = "var x = 1; var y = 2;"
        features = js_parser_with_custom.parse_string(js)
        assert "test-custom-api" not in features
        assert "custom-syntax-feat" not in features

    @pytest.mark.whitebox
    def test_custom_rule_merged_with_builtin(self, js_parser_with_custom):
        js = """
        const p = new Promise((resolve) => resolve(42));
        CustomTestAPI.start();
        """
        features = js_parser_with_custom.parse_string(js)
        assert "test-custom-api" in features
        assert "promises" in features

    @pytest.mark.whitebox
    def test_custom_rule_appears_in_report(self, js_parser_with_custom):
        js = "ReportTestJSAPI.init();"
        js_parser_with_custom.parse_string(js)
        report = js_parser_with_custom.get_detailed_report()
        assert "report-js-feat" in report['features']

