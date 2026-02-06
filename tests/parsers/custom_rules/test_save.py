"""Tests for save_custom_rules() function."""

import json
import pytest
from unittest.mock import patch
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    save_custom_rules,
    get_custom_rules_loader,
)


class TestSave:

    def test_save_writes_json_file(self, mock_custom_rules_path):
        """File is created/updated on disk."""
        rules = {
            "css": {
                "saved-feature": {
                    "patterns": ["saved-pattern"],
                    "description": "Saved Feature"
                }
            },
            "javascript": {},
            "html": {}
        }
        result = save_custom_rules(rules)
        assert result is True
        assert mock_custom_rules_path.exists()

        saved = json.loads(mock_custom_rules_path.read_text(encoding='utf-8'))
        assert "saved-feature" in saved["css"]

    def test_save_preserves_existing_rules(self, mock_custom_rules_path):
        """Other sections not lost on save."""
        rules = {
            "css": {"css-rule": {"patterns": ["p1"], "description": "CSS"}},
            "javascript": {"js-rule": {"patterns": ["p2"], "description": "JS"}},
            "html": {
                "elements": {"my-el": "feat-id"},
                "attributes": {},
                "input_types": {},
                "attribute_values": {}
            }
        }
        save_custom_rules(rules)

        saved = json.loads(mock_custom_rules_path.read_text(encoding='utf-8'))
        assert "css-rule" in saved["css"]
        assert "js-rule" in saved["javascript"]
        assert "my-el" in saved["html"]["elements"]

    def test_save_roundtrip(self, mock_custom_rules_path):
        """Save then load returns same data."""
        rules = {
            "css": {
                "roundtrip-feature": {
                    "patterns": [r"roundtrip\s*:"],
                    "description": "Roundtrip"
                }
            },
            "javascript": {},
            "html": {}
        }
        save_custom_rules(rules)

        # After save, reload happens automatically
        loader = get_custom_rules_loader()
        css = loader.get_custom_css_rules()
        assert "roundtrip-feature" in css
        assert css["roundtrip-feature"]["patterns"] == [r"roundtrip\s*:"]

    def test_save_creates_valid_json(self, mock_custom_rules_path):
        """Output is parseable JSON."""
        rules = {"css": {}, "javascript": {}, "html": {}}
        save_custom_rules(rules)

        # Should not raise
        content = mock_custom_rules_path.read_text(encoding='utf-8')
        parsed = json.loads(content)
        assert isinstance(parsed, dict)

    def test_save_with_special_characters(self, mock_custom_rules_path):
        """Regex patterns with special chars preserved."""
        rules = {
            "css": {
                "special-feature": {
                    "patterns": [r"color\s*:\s*rgba?\(", r"background\s*:\s*#[0-9a-f]+"],
                    "description": "Special Chars"
                }
            },
            "javascript": {},
            "html": {}
        }
        save_custom_rules(rules)

        saved = json.loads(mock_custom_rules_path.read_text(encoding='utf-8'))
        patterns = saved["css"]["special-feature"]["patterns"]
        assert r"color\s*:\s*rgba?\(" in patterns
        assert r"background\s*:\s*#[0-9a-f]+" in patterns
