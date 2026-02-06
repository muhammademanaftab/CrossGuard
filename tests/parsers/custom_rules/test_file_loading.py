"""Tests for JSON file loading and error handling."""

import json
import pytest
from unittest.mock import patch

from src.parsers.custom_rules_loader import CustomRulesLoader


class TestFileLoading:

    def test_loads_from_default_path(self, tmp_rules_file, sample_rules_json):
        """Loads from patched path and returns expected data."""
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "test-css-feature" in css

    def test_missing_file_returns_empty_rules(self, mock_custom_rules_path):
        """No crash when JSON file doesn't exist."""
        # mock_custom_rules_path points to non-existent file
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules() == {}
        assert loader.get_custom_js_rules() == {}
        html = loader.get_custom_html_rules()
        assert html['elements'] == {}

    def test_invalid_json_returns_empty_rules(self, mock_custom_rules_path):
        """Handles malformed JSON gracefully."""
        mock_custom_rules_path.write_text("{invalid json", encoding='utf-8')
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules() == {}
        assert loader.get_custom_js_rules() == {}

    def test_empty_file_returns_empty_rules(self, mock_custom_rules_path):
        """Empty file doesn't crash."""
        mock_custom_rules_path.write_text("", encoding='utf-8')
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules() == {}

    def test_loads_all_three_sections(self, tmp_rules_file):
        """CSS, JS, HTML sections all loaded."""
        loader = CustomRulesLoader()
        assert len(loader.get_custom_css_rules()) > 0
        assert len(loader.get_custom_js_rules()) > 0
        html = loader.get_custom_html_rules()
        assert len(html['elements']) > 0

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
