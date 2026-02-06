"""Tests for load_raw_custom_rules() function."""

import json
import pytest
from src.parsers.custom_rules_loader import load_raw_custom_rules


class TestLoadRaw:

    def test_returns_full_json_dict(self, tmp_rules_file, sample_rules_json):
        """Returns complete JSON structure."""
        raw = load_raw_custom_rules()
        assert isinstance(raw, dict)
        assert "css" in raw
        assert "javascript" in raw
        assert "html" in raw
        assert "test-css-feature" in raw["css"]

    def test_includes_comments(self, mock_custom_rules_path):
        """Comment keys (_comment) included in raw output."""
        data = {
            "css": {
                "_comment": "This is a CSS comment",
                "real-feature": {"patterns": ["test"], "description": "Test"}
            },
            "javascript": {},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        raw = load_raw_custom_rules()
        assert "_comment" in raw["css"]

    def test_missing_file_returns_empty(self, mock_custom_rules_path):
        """No crash on missing file."""
        # mock_custom_rules_path doesn't exist yet
        raw = load_raw_custom_rules()
        assert raw == {
            "css": {},
            "javascript": {},
            "html": {
                "elements": {},
                "attributes": {},
                "input_types": {},
                "attribute_values": {}
            }
        }

    def test_returns_fresh_copy(self, tmp_rules_file):
        """Modifying result doesn't affect source."""
        raw1 = load_raw_custom_rules()
        raw1["css"]["injected"] = "bad"
        raw2 = load_raw_custom_rules()
        assert "injected" not in raw2["css"]
