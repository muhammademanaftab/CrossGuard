"""Tests for get_custom_css_rules() and get_custom_js_rules() output.

CSS and JS rule loading share the same structure, so tests are parametrized.
"""

import json
import re
import pytest
from src.parsers.custom_rules_loader import CustomRulesLoader


@pytest.mark.parametrize("section,getter,feature_key,expected_pattern", [
    ("css", "get_custom_css_rules", "test-css-feature", r"test-property\s*:"),
    ("javascript", "get_custom_js_rules", "test-js-feature", r"\bTestAPI\b"),
])
class TestCSSAndJSRulesLoading:

    def test_known_rule_extracted_with_valid_regex(self, tmp_rules_file, section, getter, feature_key, expected_pattern):
        """Known rule is present with compilable regex patterns."""
        loader = CustomRulesLoader()
        rules = getattr(loader, getter)()
        assert isinstance(rules, dict)
        assert feature_key in rules
        assert expected_pattern in rules[feature_key]["patterns"]
        # All patterns compile
        for info in rules.values():
            for pattern in info['patterns']:
                re.compile(pattern)

    def test_missing_patterns_key_skipped(self, mock_custom_rules_path, section, getter, feature_key, expected_pattern):
        """Entries without patterns are ignored."""
        data = {"css": {}, "javascript": {}, "html": {}}
        data[section] = {
            "no-patterns": {"description": "Missing patterns key"},
            "has-patterns": {"patterns": ["test"], "description": "OK"}
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        rules = getattr(loader, getter)()
        assert "no-patterns" not in rules
        assert "has-patterns" in rules

    def test_empty_section(self, mock_custom_rules_path, section, getter, feature_key, expected_pattern):
        """Returns empty dict when section has no rules."""
        data = {"css": {}, "javascript": {}, "html": {}}
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        assert getattr(loader, getter)() == {}


class TestCSSMultiplePatterns:

    def test_multiple_patterns_per_rule(self, tmp_rules_file):
        """Rules with multiple patterns return all."""
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "another-css-feature" in css
        assert len(css["another-css-feature"]["patterns"]) == 2
