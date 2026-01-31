"""Tests for CSS Multi-column layout features.

Tests features: multicolumn

Note: Multicolumn patterns include: column-count, column-width, column-rule, columns, column-span, column-fill
      column-gap is NOT included because it's now primarily used with flexbox/grid (flexbox-gap feature).
      When column-gap is used with column-count/column-width, multicolumn is detected via those properties.
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

    def test_column_gap_with_column_count(self, parse_and_check):
        """Test column-gap with column-count detects multicolumn (via column-count)."""
        css = ".content { column-count: 3; column-gap: 40px; }"
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
