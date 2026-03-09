"""Tests for is_user_rule() function."""

import json
import pytest
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    is_user_rule,
    save_custom_rules,
)


class TestIsUserRule:

    def test_identifies_custom_rules_across_sections(self, tmp_rules_file):
        """Custom rules return True, built-in/unknown return False."""
        CustomRulesLoader()
        # CSS and JS custom rules
        assert is_user_rule('css', 'test-css-feature') is True
        assert is_user_rule('javascript', 'test-js-feature') is True
        # HTML subsections
        assert is_user_rule('html', 'test-element', subtype='elements') is True
        assert is_user_rule('html', 'test-attr', subtype='attributes') is True
        assert is_user_rule('html', 'test-type', subtype='input_types') is True
        # Built-in and unknown return False
        assert is_user_rule('css', 'flexbox') is False
        assert is_user_rule('css', 'nonexistent-random-feature') is False

    def test_after_adding_new_rule(self, mock_custom_rules_path):
        """Newly saved rule is recognized."""
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
