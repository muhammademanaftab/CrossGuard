"""Tests for CSS Grid layout features.

Tests features: css-grid, css-subgrid

Note: Grid patterns only include: display: grid, grid-template, grid-column, grid-row
Other grid properties (inline-grid, grid-area, grid-auto-columns, grid-auto-rows, grid-auto-flow)
are not in the parser patterns.
"""

import pytest


class TestCSSGrid:
    """Tests for CSS Grid detection."""

    def test_display_grid(self, parse_and_check):
        """Test display: grid detection."""
        css = ".container { display: grid; }"
        assert parse_and_check(css, 'css-grid')

    def test_grid_template_columns(self, parse_and_check):
        """Test grid-template-columns detection."""
        css = ".container { grid-template-columns: 1fr 1fr 1fr; }"
        assert parse_and_check(css, 'css-grid')

    def test_grid_template_rows(self, parse_and_check):
        """Test grid-template-rows detection."""
        css = ".container { grid-template-rows: auto 1fr auto; }"
        assert parse_and_check(css, 'css-grid')

    def test_grid_template_areas(self, parse_and_check):
        """Test grid-template-areas detection."""
        css = '.container { grid-template-areas: "header header" "sidebar main"; }'
        assert parse_and_check(css, 'css-grid')

    def test_grid_column(self, parse_and_check):
        """Test grid-column detection."""
        css = ".item { grid-column: 1 / 3; }"
        assert parse_and_check(css, 'css-grid')

    def test_grid_column_start(self, parse_and_check):
        """Test grid-column-start detection."""
        css = ".item { grid-column-start: 2; }"
        assert parse_and_check(css, 'css-grid')

    def test_grid_column_end(self, parse_and_check):
        """Test grid-column-end detection."""
        css = ".item { grid-column-end: span 2; }"
        assert parse_and_check(css, 'css-grid')

    def test_grid_row(self, parse_and_check):
        """Test grid-row detection."""
        css = ".item { grid-row: 1 / 3; }"
        assert parse_and_check(css, 'css-grid')

    def test_grid_row_start(self, parse_and_check):
        """Test grid-row-start detection."""
        css = ".item { grid-row-start: 1; }"
        assert parse_and_check(css, 'css-grid')

    def test_grid_row_end(self, parse_and_check):
        """Test grid-row-end detection."""
        css = ".item { grid-row-end: -1; }"
        assert parse_and_check(css, 'css-grid')

    def test_complete_grid_layout(self, parse_and_check):
        """Test complete grid layout with supported patterns."""
        css = """
        .container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-template-rows: auto;
        }
        .item { grid-column: span 2; }
        """
        assert parse_and_check(css, 'css-grid')


class TestCSSSubgrid:
    """Tests for CSS Subgrid detection."""

    def test_subgrid_columns(self, parse_and_check):
        """Test grid-template-columns: subgrid detection."""
        css = ".item { grid-template-columns: subgrid; }"
        assert parse_and_check(css, 'css-subgrid')

    def test_subgrid_rows(self, parse_and_check):
        """Test grid-template-rows: subgrid detection."""
        css = ".item { grid-template-rows: subgrid; }"
        assert parse_and_check(css, 'css-subgrid')

    def test_subgrid_both(self, parse_and_check_multiple):
        """Test subgrid on both axes."""
        css = """
        .nested {
            display: grid;
            grid-template-columns: subgrid;
            grid-template-rows: subgrid;
        }
        """
        assert parse_and_check_multiple(css, ['css-grid', 'css-subgrid'])
