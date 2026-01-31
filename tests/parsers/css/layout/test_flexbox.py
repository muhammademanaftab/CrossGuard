"""Tests for CSS Flexbox layout features.

Tests features: flexbox, flexbox-gap

Note: Flexbox patterns only match display: flex (not inline-flex).
The pattern is: display\s*:\s*flex
"""

import pytest


class TestFlexbox:
    """Tests for CSS Flexbox detection."""

    def test_display_flex(self, parse_and_check):
        """Test display: flex detection."""
        css = ".container { display: flex; }"
        assert parse_and_check(css, 'flexbox')

    def test_flex_direction_row(self, parse_and_check):
        """Test flex-direction: row detection."""
        css = ".container { flex-direction: row; }"
        assert parse_and_check(css, 'flexbox')

    def test_flex_direction_column(self, parse_and_check):
        """Test flex-direction: column detection."""
        css = ".container { flex-direction: column; }"
        assert parse_and_check(css, 'flexbox')

    def test_flex_wrap(self, parse_and_check):
        """Test flex-wrap detection."""
        css = ".container { flex-wrap: wrap; }"
        assert parse_and_check(css, 'flexbox')

    def test_justify_content(self, parse_and_check):
        """Test justify-content with display: flex detection."""
        css = ".container { display: flex; justify-content: center; }"
        assert parse_and_check(css, 'flexbox')

    def test_justify_content_space_between(self, parse_and_check):
        """Test justify-content: space-between with display: flex detection."""
        css = ".container { display: flex; justify-content: space-between; }"
        assert parse_and_check(css, 'flexbox')

    def test_align_items(self, parse_and_check):
        """Test align-items with display: flex detection."""
        css = ".container { display: flex; align-items: center; }"
        assert parse_and_check(css, 'flexbox')

    def test_align_items_stretch(self, parse_and_check):
        """Test align-items: stretch with display: flex detection."""
        css = ".container { display: flex; align-items: stretch; }"
        assert parse_and_check(css, 'flexbox')

    def test_complete_flexbox(self, parse_and_check):
        """Test complete flexbox layout."""
        css = """
        .container {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
        }
        """
        assert parse_and_check(css, 'flexbox')


class TestFlexboxGap:
    """Tests for Flexbox gap property detection.

    Note: flexbox-gap is context-aware and only detects gap when used with display: flex.
    Using gap without display: flex would be detected as grid gap, not flexbox-gap.
    """

    def test_gap_property(self, parse_and_check):
        """Test gap property with display: flex detection."""
        css = ".container { display: flex; gap: 20px; }"
        assert parse_and_check(css, 'flexbox-gap')

    def test_gap_two_values(self, parse_and_check):
        """Test gap with row and column values in flex context."""
        css = ".container { display: flex; gap: 20px 10px; }"
        assert parse_and_check(css, 'flexbox-gap')

    def test_row_gap(self, parse_and_check):
        """Test row-gap property with display: flex detection."""
        css = ".container { display: flex; row-gap: 20px; }"
        assert parse_and_check(css, 'flexbox-gap')

    def test_column_gap(self, parse_and_check):
        """Test column-gap property with display: flex detection."""
        css = ".container { display: flex; column-gap: 10px; }"
        assert parse_and_check(css, 'flexbox-gap')

    def test_flexbox_with_gap(self, parse_and_check_multiple):
        """Test flexbox combined with gap."""
        css = """
        .container {
            display: flex;
            gap: 1rem;
        }
        """
        assert parse_and_check_multiple(css, ['flexbox', 'flexbox-gap'])
