"""Tests for is_user_rule() function."""

import json
import pytest
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    is_user_rule,
    save_custom_rules,
)


class TestIsUserRule:

    def test_known_custom_rule_returns_true(self, tmp_rules_file):
        """Rule defined in custom_rules.json returns True."""
        # Initialize loader
        CustomRulesLoader()
        assert is_user_rule('css', 'test-css-feature') is True

    def test_builtin_rule_returns_false(self, tmp_rules_file):
        """Built-in feature ID returns False."""
        CustomRulesLoader()
        assert is_user_rule('css', 'flexbox') is False

    def test_unknown_rule_returns_false(self, tmp_rules_file):
        """Random string returns False."""
        CustomRulesLoader()
        assert is_user_rule('css', 'nonexistent-random-feature') is False

    def test_checks_all_sections(self, tmp_rules_file):
        """Works for CSS, JS, and HTML rules."""
        CustomRulesLoader()
        assert is_user_rule('css', 'test-css-feature') is True
        assert is_user_rule('javascript', 'test-js-feature') is True
        assert is_user_rule('html', 'test-element', subtype='elements') is True
        assert is_user_rule('html', 'test-attr', subtype='attributes') is True
        assert is_user_rule('html', 'test-type', subtype='input_types') is True

    def test_after_adding_new_rule(self, mock_custom_rules_path):
        """Newly saved rule is recognized."""
        # Start with empty rules
        rules = {
            "css": {
                "dynamic-feature": {
                    "patterns": ["dynamic"],
                    "description": "Dynamic"
                }
            },
            "javascript": {},
            "html": {}
        }
        save_custom_rules(rules)
        assert is_user_rule('css', 'dynamic-feature') is True
