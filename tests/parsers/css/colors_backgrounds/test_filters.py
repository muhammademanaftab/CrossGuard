"""Tests for CSS Filter features.

Tests features: css-filter-function, css-backdrop-filter, css-filters, css-mixblendmode
"""

import pytest


class TestCSSFilterFunction:
    """Tests for CSS Filter function detection."""

    def test_filter_property(self, parse_and_check):
        """Test filter property detection."""
        css = ".element { filter: blur(5px); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_blur_filter(self, parse_and_check):
        """Test blur() filter detection."""
        css = ".element { filter: blur(10px); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_brightness_filter(self, parse_and_check):
        """Test brightness() filter detection."""
        css = ".element { filter: brightness(150%); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_contrast_filter(self, parse_and_check):
        """Test contrast() filter detection."""
        css = ".element { filter: contrast(200%); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_grayscale_filter(self, parse_and_check):
        """Test grayscale() filter detection."""
        css = ".element { filter: grayscale(100%); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_hue_rotate_filter(self, parse_and_check):
        """Test hue-rotate() filter detection."""
        css = ".element { filter: hue-rotate(90deg); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_invert_filter(self, parse_and_check):
        """Test invert() filter detection."""
        css = ".element { filter: invert(100%); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_saturate_filter(self, parse_and_check):
        """Test saturate() filter detection."""
        css = ".element { filter: saturate(200%); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_sepia_filter(self, parse_and_check):
        """Test sepia() filter detection."""
        css = ".element { filter: sepia(100%); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_drop_shadow_filter(self, parse_and_check):
        """Test drop-shadow() filter detection."""
        css = ".element { filter: drop-shadow(2px 2px 4px black); }"
        assert parse_and_check(css, 'css-filter-function')

    def test_multiple_filters(self, parse_and_check):
        """Test multiple filters detection."""
        css = ".element { filter: blur(5px) brightness(150%) contrast(120%); }"
        assert parse_and_check(css, 'css-filter-function')


class TestBackdropFilter:
    """Tests for backdrop-filter detection."""

    def test_backdrop_filter(self, parse_and_check):
        """Test backdrop-filter property detection."""
        css = ".overlay { backdrop-filter: blur(10px); }"
        assert parse_and_check(css, 'css-backdrop-filter')

    def test_backdrop_filter_blur(self, parse_and_check):
        """Test backdrop-filter: blur detection."""
        css = ".glass { backdrop-filter: blur(20px); }"
        assert parse_and_check(css, 'css-backdrop-filter')

    def test_backdrop_filter_brightness(self, parse_and_check):
        """Test backdrop-filter with brightness."""
        css = ".overlay { backdrop-filter: brightness(150%); }"
        assert parse_and_check(css, 'css-backdrop-filter')

    def test_backdrop_filter_multiple(self, parse_and_check):
        """Test backdrop-filter with multiple effects."""
        css = ".glass { backdrop-filter: blur(10px) saturate(180%); }"
        assert parse_and_check(css, 'css-backdrop-filter')

    def test_webkit_backdrop_filter(self, parse_and_check):
        """Test -webkit-backdrop-filter detection."""
        css = ".glass { -webkit-backdrop-filter: blur(10px); }"
        assert parse_and_check(css, 'css-backdrop-filter')


class TestCSSFilters:
    """Tests for general CSS filters detection."""

    def test_filter_none(self, parse_and_check):
        """Test filter: none detection."""
        css = ".element { filter: none; }"
        assert parse_and_check(css, 'css-filters')

    def test_filter_url(self, parse_and_check):
        """Test filter: url() detection."""
        css = ".element { filter: url(#blur); }"
        assert parse_and_check(css, 'css-filters')


class TestMixBlendMode:
    """Tests for mix-blend-mode detection."""

    def test_mix_blend_mode(self, parse_and_check):
        """Test mix-blend-mode detection."""
        css = ".overlay { mix-blend-mode: multiply; }"
        assert parse_and_check(css, 'css-mixblendmode')

    def test_mix_blend_mode_screen(self, parse_and_check):
        """Test mix-blend-mode: screen detection."""
        css = ".overlay { mix-blend-mode: screen; }"
        assert parse_and_check(css, 'css-mixblendmode')

    def test_mix_blend_mode_overlay(self, parse_and_check):
        """Test mix-blend-mode: overlay detection."""
        css = ".overlay { mix-blend-mode: overlay; }"
        assert parse_and_check(css, 'css-mixblendmode')

    def test_mix_blend_mode_darken(self, parse_and_check):
        """Test mix-blend-mode: darken detection."""
        css = ".overlay { mix-blend-mode: darken; }"
        assert parse_and_check(css, 'css-mixblendmode')

    def test_mix_blend_mode_lighten(self, parse_and_check):
        """Test mix-blend-mode: lighten detection."""
        css = ".overlay { mix-blend-mode: lighten; }"
        assert parse_and_check(css, 'css-mixblendmode')

    def test_mix_blend_mode_color_dodge(self, parse_and_check):
        """Test mix-blend-mode: color-dodge detection."""
        css = ".overlay { mix-blend-mode: color-dodge; }"
        assert parse_and_check(css, 'css-mixblendmode')

    def test_mix_blend_mode_difference(self, parse_and_check):
        """Test mix-blend-mode: difference detection."""
        css = ".overlay { mix-blend-mode: difference; }"
        assert parse_and_check(css, 'css-mixblendmode')
