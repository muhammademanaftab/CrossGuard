"""Tests for CSS Display layout features.

Tests features: inline-block, flow-root, run-in, css-display-contents, css-table
"""

import pytest


class TestInlineBlock:
    """Tests for display: inline-block detection."""

    def test_inline_block(self, parse_and_check):
        """Test display: inline-block detection."""
        css = ".box { display: inline-block; }"
        assert parse_and_check(css, 'inline-block')

    def test_inline_block_with_dimensions(self, parse_and_check):
        """Test inline-block with width/height."""
        css = """
        .box {
            display: inline-block;
            width: 100px;
            height: 100px;
        }
        """
        assert parse_and_check(css, 'inline-block')


class TestFlowRoot:
    """Tests for display: flow-root detection."""

    def test_flow_root(self, parse_and_check):
        """Test display: flow-root detection."""
        css = ".clearfix { display: flow-root; }"
        assert parse_and_check(css, 'flow-root')

    def test_flow_root_bfc(self, parse_and_check):
        """Test flow-root for BFC creation."""
        css = """
        .container {
            display: flow-root;
            overflow: visible;
        }
        """
        assert parse_and_check(css, 'flow-root')


class TestRunIn:
    """Tests for display: run-in detection."""

    def test_run_in(self, parse_and_check):
        """Test display: run-in detection."""
        css = ".heading { display: run-in; }"
        assert parse_and_check(css, 'run-in')


class TestDisplayContents:
    """Tests for display: contents detection."""

    def test_display_contents(self, parse_and_check):
        """Test display: contents detection."""
        css = ".wrapper { display: contents; }"
        assert parse_and_check(css, 'css-display-contents')

    def test_display_contents_for_accessibility(self, parse_and_check):
        """Test display: contents for semantic wrapper."""
        css = """
        .grid-wrapper {
            display: contents;
        }
        """
        assert parse_and_check(css, 'css-display-contents')


class TestCSSTable:
    """Tests for CSS Table display detection."""

    def test_display_table(self, parse_and_check):
        """Test display: table detection."""
        css = ".table-layout { display: table; }"
        assert parse_and_check(css, 'css-table')

    def test_display_table_cell(self, parse_and_check):
        """Test display: table-cell detection."""
        css = ".cell { display: table-cell; }"
        assert parse_and_check(css, 'css-table')

    def test_display_table_row(self, parse_and_check):
        """Test display: table-row detection."""
        css = ".row { display: table-row; }"
        assert parse_and_check(css, 'css-table')

    def test_complete_table_layout(self, parse_and_check):
        """Test complete table-based layout."""
        css = """
        .table { display: table; width: 100%; }
        .row { display: table-row; }
        .cell { display: table-cell; padding: 10px; }
        """
        assert parse_and_check(css, 'css-table')
