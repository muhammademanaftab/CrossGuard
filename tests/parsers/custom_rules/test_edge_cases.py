"""Tests for edge cases: malformed JSON, empty sections, etc."""

import json
import pytest
from src.parsers.custom_rules_loader import CustomRulesLoader


class TestEdgeCases:

    @pytest.mark.parametrize("feature_id,patterns", [
        ("unicode-feature", [r"caf\u00e9\s*:"]),
        ("long-feature", ["a" * 1000]),
        ("empty-patterns", []),
    ])
    def test_unusual_patterns_handled(self, mock_custom_rules_path, feature_id, patterns):
        """Unicode, very long, and empty pattern lists all load without error."""
        data = {
            "css": {feature_id: {"patterns": patterns, "description": "Test"}},
            "javascript": {},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert feature_id in css

    def test_nested_invalid_types_skipped(self, mock_custom_rules_path):
        """Non-dict feature info entries are skipped."""
        data = {
            "css": {
                "string-entry": "not a dict",
                "list-entry": [1, 2, 3],
                "valid-entry": {"patterns": ["valid"], "description": "Valid"}
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
            "css": {"shared-id": {"patterns": ["css-pattern"], "description": "CSS version"}},
            "javascript": {"shared-id": {"patterns": ["js-pattern"], "description": "JS version"}},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules()["shared-id"]["patterns"] == ["css-pattern"]
        assert loader.get_custom_js_rules()["shared-id"]["patterns"] == ["js-pattern"]

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
        assert loader.get_custom_css_rules() == {}
