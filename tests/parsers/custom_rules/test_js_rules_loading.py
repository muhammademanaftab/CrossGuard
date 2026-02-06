"""Tests for get_custom_js_rules() output."""

import json
import re
import pytest
from src.parsers.custom_rules_loader import CustomRulesLoader


class TestJSRulesLoading:

    def test_returns_dict_of_feature_info(self, tmp_rules_file):
        """Output is {feature_id: {patterns: [...], description: ...}}."""
        loader = CustomRulesLoader()
        js = loader.get_custom_js_rules()
        assert isinstance(js, dict)
        for feature_id, info in js.items():
            assert isinstance(info, dict)
            assert 'patterns' in info

    def test_custom_js_rule_extracted(self, tmp_rules_file):
        """Known rule from JSON is present."""
        loader = CustomRulesLoader()
        js = loader.get_custom_js_rules()
        assert "test-js-feature" in js
        assert r"\bTestAPI\b" in js["test-js-feature"]["patterns"]

    def test_patterns_are_valid_regex(self, tmp_rules_file):
        """Patterns compile without error."""
        loader = CustomRulesLoader()
        js = loader.get_custom_js_rules()
        for feature_id, info in js.items():
            for pattern in info['patterns']:
                re.compile(pattern)  # Should not raise

    def test_missing_patterns_key_skipped(self, mock_custom_rules_path):
        """Entries without patterns are ignored."""
        data = {
            "css": {},
            "javascript": {
                "no-patterns": {"description": "Missing patterns"},
                "has-patterns": {"patterns": ["test"], "description": "OK"}
            },
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        js = loader.get_custom_js_rules()
        assert "no-patterns" not in js
        assert "has-patterns" in js

    def test_empty_js_section(self, mock_custom_rules_path):
        """Returns empty dict when no JS rules."""
        data = {"css": {}, "javascript": {}, "html": {}}
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        assert loader.get_custom_js_rules() == {}

    def test_description_field_ignored_in_output(self, tmp_rules_file):
        """Description is part of the info dict but doesn't appear as a pattern."""
        loader = CustomRulesLoader()
        js = loader.get_custom_js_rules()
        for feature_id, info in js.items():
            assert "description" not in info.get('patterns', [])
