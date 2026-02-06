"""Tests for edge cases: malformed JSON, empty sections, etc."""

import json
import pytest
from src.parsers.custom_rules_loader import CustomRulesLoader


class TestEdgeCases:

    def test_unicode_in_patterns(self, mock_custom_rules_path):
        """Unicode regex patterns handled."""
        data = {
            "css": {
                "unicode-feature": {
                    "patterns": [r"caf\u00e9\s*:"],
                    "description": "Unicode Test"
                }
            },
            "javascript": {},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "unicode-feature" in css

    def test_very_long_pattern(self, mock_custom_rules_path):
        """Long regex strings don't crash."""
        long_pattern = "a" * 1000
        data = {
            "css": {
                "long-feature": {
                    "patterns": [long_pattern],
                    "description": "Long Pattern"
                }
            },
            "javascript": {},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "long-feature" in css

    def test_empty_pattern_list(self, mock_custom_rules_path):
        """'patterns': [] handled gracefully."""
        data = {
            "css": {
                "empty-patterns": {
                    "patterns": [],
                    "description": "Empty Patterns"
                }
            },
            "javascript": {},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        # The loader stores it since it has the 'patterns' key
        assert "empty-patterns" in css
        assert css["empty-patterns"]["patterns"] == []

    def test_nested_invalid_types(self, mock_custom_rules_path):
        """Non-dict feature info entries are skipped."""
        data = {
            "css": {
                "string-entry": "not a dict",
                "list-entry": [1, 2, 3],
                "valid-entry": {
                    "patterns": ["valid"],
                    "description": "Valid"
                }
            },
            "javascript": {},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "string-entry" not in css
        assert "list-entry" not in css
        assert "valid-entry" in css

    def test_duplicate_feature_ids_across_sections(self, mock_custom_rules_path):
        """Same ID in CSS and JS sections works independently."""
        data = {
            "css": {
                "shared-id": {
                    "patterns": ["css-pattern"],
                    "description": "CSS version"
                }
            },
            "javascript": {
                "shared-id": {
                    "patterns": ["js-pattern"],
                    "description": "JS version"
                }
            },
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        js = loader.get_custom_js_rules()
        assert css["shared-id"]["patterns"] == ["css-pattern"]
        assert js["shared-id"]["patterns"] == ["js-pattern"]

    def test_extra_unknown_keys_ignored(self, mock_custom_rules_path):
        """Unknown JSON keys don't crash."""
        data = {
            "css": {},
            "javascript": {},
            "html": {},
            "unknown_section": {"foo": "bar"},
            "metadata": {"version": 1}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        # Should not crash
        assert loader.get_custom_css_rules() == {}
