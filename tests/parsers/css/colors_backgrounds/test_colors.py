"""Tests for CSS Color features.

Tests features: css3-colors, currentcolor, css-rrggbbaa, css-lch-lab, css-color-function,
                css-rebeccapurple, css-relative-colors
"""

import pytest


class TestCSS3Colors:
    """Tests for CSS3 Colors detection."""

    def test_rgb_function(self, parse_and_check):
        """Test rgb() function detection."""
        css = ".element { color: rgb(255, 0, 0); }"
        assert parse_and_check(css, 'css3-colors')

    def test_rgba_function(self, parse_and_check):
        """Test rgba() function detection."""
        css = ".element { color: rgba(255, 0, 0, 0.5); }"
        assert parse_and_check(css, 'css3-colors')

    def test_hsl_function(self, parse_and_check):
        """Test hsl() function detection."""
        css = ".element { color: hsl(120, 100%, 50%); }"
        assert parse_and_check(css, 'css3-colors')

    def test_hsla_function(self, parse_and_check):
        """Test hsla() function detection."""
        css = ".element { color: hsla(120, 100%, 50%, 0.5); }"
        assert parse_and_check(css, 'css3-colors')

    def test_hex_color(self, parse_and_check):
        """Test 6-digit hex color detection."""
        css = ".element { color: #ff0000; }"
        assert parse_and_check(css, 'css3-colors')


class TestCurrentColor:
    """Tests for currentColor value detection."""

    def test_currentcolor_border(self, parse_and_check):
        """Test currentColor in border."""
        css = ".element { border-color: currentColor; }"
        assert parse_and_check(css, 'currentcolor')

    def test_currentcolor_box_shadow(self, parse_and_check):
        """Test currentColor in box-shadow."""
        css = ".element { box-shadow: 0 0 5px currentColor; }"
        assert parse_and_check(css, 'currentcolor')

    def test_currentcolor_fill(self, parse_and_check):
        """Test currentColor in fill."""
        css = ".icon { fill: currentColor; }"
        assert parse_and_check(css, 'currentcolor')


class TestRRGGBBAA:
    """Tests for 8-digit hex color (#rrggbbaa) detection."""

    def test_8_digit_hex(self, parse_and_check):
        """Test 8-digit hex color detection."""
        css = ".element { background-color: #ff000080; }"
        assert parse_and_check(css, 'css-rrggbbaa')

    def test_8_digit_hex_full_opacity(self, parse_and_check):
        """Test 8-digit hex with full opacity."""
        css = ".element { color: #336699ff; }"
        assert parse_and_check(css, 'css-rrggbbaa')


class TestLCHLab:
    """Tests for LCH and Lab color detection."""

    def test_lch_function(self, parse_and_check):
        """Test lch() function detection."""
        css = ".element { color: lch(50% 100 180); }"
        assert parse_and_check(css, 'css-lch-lab')

    def test_lab_function(self, parse_and_check):
        """Test lab() function detection."""
        css = ".element { color: lab(50% 50 50); }"
        assert parse_and_check(css, 'css-lch-lab')

    def test_oklch_function(self, parse_and_check):
        """Test oklch() function detection."""
        css = ".element { color: oklch(70% 0.15 180); }"
        assert parse_and_check(css, 'css-lch-lab')

    def test_oklab_function(self, parse_and_check):
        """Test oklab() function detection."""
        css = ".element { color: oklab(70% 0.1 -0.1); }"
        assert parse_and_check(css, 'css-lch-lab')


class TestColorFunction:
    """Tests for color() function detection."""

    def test_color_function_display_p3(self, parse_and_check):
        """Test color() with display-p3 color space."""
        css = ".element { color: color(display-p3 1 0 0); }"
        assert parse_and_check(css, 'css-color-function')

    def test_color_function_srgb(self, parse_and_check):
        """Test color() with sRGB color space."""
        css = ".element { color: color(srgb 1 0 0); }"
        assert parse_and_check(css, 'css-color-function')


class TestRebeccaPurple:
    """Tests for rebeccapurple color detection."""

    def test_rebeccapurple(self, parse_and_check):
        """Test rebeccapurple color name."""
        css = ".element { color: rebeccapurple; }"
        assert parse_and_check(css, 'css-rebeccapurple')

    def test_rebeccapurple_background(self, parse_and_check):
        """Test rebeccapurple in background."""
        css = ".element { background-color: rebeccapurple; }"
        assert parse_and_check(css, 'css-rebeccapurple')


class TestRelativeColors:
    """Tests for CSS relative colors detection."""

    def test_relative_color_from(self, parse_and_check):
        """Test relative color with 'from' keyword."""
        css = ".element { color: rgb(from red r g b / 50%); }"
        assert parse_and_check(css, 'css-relative-colors')
