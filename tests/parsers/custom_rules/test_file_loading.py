"""Tests for JSON file loading and error handling."""

import json
import pytest
from unittest.mock import patch

from src.parsers.custom_rules_loader import CustomRulesLoader


class TestFileLoading:

    def test_loads_all_sections_from_default_path(self, tmp_rules_file):
        """Loads CSS, JS, HTML sections from patched path."""
        loader = CustomRulesLoader()
        assert "test-css-feature" in loader.get_custom_css_rules()
        assert len(loader.get_custom_js_rules()) > 0
        html = loader.get_custom_html_rules()
        assert len(html['elements']) > 0

    @pytest.mark.parametrize("content,desc", [
        (None, "missing file"),
        ("{invalid json", "invalid JSON"),
        ("", "empty file"),
    ])
    def test_bad_file_returns_empty_rules(self, mock_custom_rules_path, content, desc):
        """Missing, invalid, or empty files return empty rule sets."""
        if content is not None:
            mock_custom_rules_path.write_text(content, encoding='utf-8')
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules() == {}
        assert loader.get_custom_js_rules() == {}

    def test_comment_keys_skipped(self, mock_custom_rules_path):
        """Keys starting with _ are ignored."""
        data = {
            "css": {
                "_comment": "This is a comment",
                "real-feature": {
                    "patterns": ["real-pattern"],
                    "description": "Real Feature"
                }
            },
            "javascript": {},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "_comment" not in css
        assert "real-feature" in css
