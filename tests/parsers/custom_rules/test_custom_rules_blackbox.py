"""Black-box tests for the custom rules loader public API.

Tests loading rules, querying rules across CSS/JS/HTML, and raw access.
"""

import json
import re
import pytest
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    is_user_rule,
    load_raw_custom_rules,
)


@pytest.mark.blackbox
class TestLoadRules:

    def test_loads_all_sections(self, tmp_rules_file):
        """CSS, JS, and HTML rules all load from a valid JSON file."""
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        js = loader.get_custom_js_rules()
        html = loader.get_custom_html_rules()

        assert "test-css-feature" in css
        assert css["test-css-feature"]["patterns"] == [r"test-property\s*:"]
        assert "test-js-feature" in js
        assert js["test-js-feature"]["patterns"] == [r"\bTestAPI\b"]
        assert html["elements"]["test-element"] == "test-feature-id"
        assert html["attributes"]["test-attr"] == "test-attr-feature"
        assert html["input_types"]["test-type"] == "test-input-feature"
        assert html["attribute_values"]["data-test:value1"] == "test-value-feature"

    def test_css_js_patterns_are_valid_regex(self, tmp_rules_file):
        """All loaded CSS and JS patterns compile as valid regex."""
        loader = CustomRulesLoader()
        for rules in (loader.get_custom_css_rules(), loader.get_custom_js_rules()):
            for info in rules.values():
                for pattern in info["patterns"]:
                    re.compile(pattern)

    def test_multiple_patterns_per_rule(self, tmp_rules_file):
        """Rules with multiple patterns return all of them."""
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert len(css["another-css-feature"]["patterns"]) == 2

    @pytest.mark.parametrize("content,desc", [
        (None, "missing file"),
        ("{invalid json", "invalid JSON"),
        ("", "empty file"),
    ])
    def test_bad_file_returns_empty_rules(self, mock_custom_rules_path, content, desc):
        """Missing, invalid, or empty files produce empty rule sets."""
        if content is not None:
            mock_custom_rules_path.write_text(content, encoding="utf-8")
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules() == {}
        assert loader.get_custom_js_rules() == {}

    def test_entries_without_patterns_skipped(self, mock_custom_rules_path):
        """CSS/JS entries missing the 'patterns' key are silently ignored."""
        data = {
            "css": {
                "no-patterns": {"description": "Missing patterns key"},
                "has-patterns": {"patterns": ["test"], "description": "OK"},
            },
            "javascript": {},
            "html": {},
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding="utf-8")
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "no-patterns" not in css
        assert "has-patterns" in css

    def test_comment_keys_skipped(self, mock_custom_rules_path):
        """Keys starting with _ are filtered out of loaded rules."""
        data = {
            "css": {
                "_comment": "This is a comment",
                "real-feature": {"patterns": ["real"], "description": "Real"},
            },
            "javascript": {},
            "html": {},
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding="utf-8")
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "_comment" not in css
        assert "real-feature" in css

    def test_partial_html_section(self, mock_custom_rules_path):
        """Only some HTML sub-sections present; missing ones default to empty."""
        data = {
            "css": {},
            "javascript": {},
            "html": {"elements": {"my-elem": "elem-feature"}},
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding="utf-8")
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert "my-elem" in html["elements"]
        assert html["attributes"] == {}
        assert html["input_types"] == {}
        assert html["attribute_values"] == {}


@pytest.mark.blackbox
class TestIsUserRule:

    def test_identifies_custom_vs_builtin(self, tmp_rules_file):
        """Custom rules return True; built-in and unknown return False."""
        CustomRulesLoader()
        assert is_user_rule("css", "test-css-feature") is True
        assert is_user_rule("javascript", "test-js-feature") is True
        assert is_user_rule("html", "test-element", subtype="elements") is True
        assert is_user_rule("html", "test-attr", subtype="attributes") is True
        assert is_user_rule("css", "flexbox") is False
        assert is_user_rule("css", "nonexistent") is False


@pytest.mark.blackbox
class TestLoadRaw:

    def test_returns_full_json_structure(self, tmp_rules_file):
        """Returns complete JSON with css, javascript, html keys."""
        raw = load_raw_custom_rules()
        assert "css" in raw and "javascript" in raw and "html" in raw
        assert "test-css-feature" in raw["css"]

    def test_missing_file_returns_empty_skeleton(self, mock_custom_rules_path):
        """Missing file returns empty structure (not crash)."""
        raw = load_raw_custom_rules()
        assert raw["css"] == {}
        assert raw["javascript"] == {}
        assert raw["html"]["elements"] == {}
