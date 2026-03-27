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
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        js = loader.get_custom_js_rules()
        html = loader.get_custom_html_rules()

        assert "test-css-feature" in css
        assert "test-js-feature" in js
        assert html["elements"]["test-element"] == "test-feature-id"

    def test_bad_file_returns_empty_rules(self, mock_custom_rules_path):
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules() == {}
        assert loader.get_custom_js_rules() == {}


@pytest.mark.blackbox
class TestIsUserRule:

    def test_identifies_custom_vs_builtin(self, tmp_rules_file):
        CustomRulesLoader()
        assert is_user_rule("css", "test-css-feature") is True
        assert is_user_rule("html", "test-element", subtype="elements") is True
        assert is_user_rule("css", "flexbox") is False


@pytest.mark.blackbox
class TestLoadRaw:

    def test_returns_full_json_structure(self, tmp_rules_file):
        raw = load_raw_custom_rules()
        assert "css" in raw and "javascript" in raw and "html" in raw
        assert "test-css-feature" in raw["css"]
