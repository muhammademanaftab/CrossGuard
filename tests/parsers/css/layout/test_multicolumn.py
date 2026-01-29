"""Tests for CSS Multi-column layout features.

Tests features: multicolumn

Note: Multicolumn patterns only include: column-count, column-width, column-gap, column-rule
Other properties (columns shorthand, column-span, column-fill) are not in the parser patterns.
"""

import pytest


class TestMulticolumn:
    """Tests for CSS Multi-column layout detection."""

    def test_column_count(self, parse_and_check):
        """Test column-count detection."""
        css = ".content { column-count: 3; }"
        assert parse_and_check(css, 'multicolumn')

    def test_column_width(self, parse_and_check):
        """Test column-width detection."""
        css = ".content { column-width: 200px; }"
        assert parse_and_check(css, 'multicolumn')

    def test_column_gap(self, parse_and_check):
        """Test column-gap detection."""
        css = ".content { column-gap: 40px; }"
        assert parse_and_check(css, 'multicolumn')

    def test_column_rule(self, parse_and_check):
        """Test column-rule shorthand detection."""
        css = ".content { column-rule: 1px solid #ccc; }"
        assert parse_and_check(css, 'multicolumn')

    def test_column_rule_width(self, parse_and_check):
        """Test column-rule-width detection."""
        css = ".content { column-rule-width: 2px; }"
        assert parse_and_check(css, 'multicolumn')

    def test_column_rule_style(self, parse_and_check):
        """Test column-rule-style detection."""
        css = ".content { column-rule-style: dotted; }"
        assert parse_and_check(css, 'multicolumn')

    def test_column_rule_color(self, parse_and_check):
        """Test column-rule-color detection."""
        css = ".content { column-rule-color: blue; }"
        assert parse_and_check(css, 'multicolumn')

    def test_complete_multicolumn(self, parse_and_check):
        """Test complete multicolumn layout with supported patterns."""
        css = """
        .article {
            column-count: 3;
            column-gap: 2em;
            column-rule: 1px solid #ddd;
        }
        """
        assert parse_and_check(css, 'multicolumn')
