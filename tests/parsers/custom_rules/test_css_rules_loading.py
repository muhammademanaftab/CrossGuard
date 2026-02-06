"""Tests for get_custom_css_rules() output."""

import json
import re
import pytest
from src.parsers.custom_rules_loader import CustomRulesLoader


class TestCSSRulesLoading:

    def test_returns_dict_of_feature_info(self, tmp_rules_file):
        """Output is {feature_id: {patterns: [...], description: ...}}."""
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert isinstance(css, dict)
        for feature_id, info in css.items():
            assert isinstance(info, dict)
            assert 'patterns' in info

    def test_custom_css_rule_extracted(self, tmp_rules_file):
        """Known rule from JSON is present."""
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "test-css-feature" in css
        assert r"test-property\s*:" in css["test-css-feature"]["patterns"]

    def test_patterns_are_valid_regex(self, tmp_rules_file):
        """Patterns compile without error."""
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        for feature_id, info in css.items():
            for pattern in info['patterns']:
                re.compile(pattern)  # Should not raise

    def test_missing_patterns_key_skipped(self, mock_custom_rules_path):
        """Entries without patterns are ignored."""
        data = {
            "css": {
                "no-patterns": {"description": "Missing patterns key"},
                "has-patterns": {"patterns": ["test"], "description": "OK"}
            },
            "javascript": {},
            "html": {}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "no-patterns" not in css
        assert "has-patterns" in css

    def test_empty_css_section(self, mock_custom_rules_path):
        """Returns empty dict when no CSS rules."""
        data = {"css": {}, "javascript": {}, "html": {}}
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules() == {}

    def test_multiple_patterns_per_rule(self, tmp_rules_file):
        """Rules with multiple patterns return all."""
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "another-css-feature" in css
        patterns = css["another-css-feature"]["patterns"]
        assert len(patterns) == 2
