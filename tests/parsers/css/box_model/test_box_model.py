"""Tests for CSS Box Model features.

Tests features: css3-boxsizing, minmaxwh, intrinsic-width, object-fit,
                border-image, border-radius, outline, css-boxdecorationbreak,
                css-boxshadow, css-textshadow

Note: outline patterns include: outline:, outline-width, outline-style, outline-color
outline-offset is not in the parser patterns.
"""

import pytest


class TestBoxSizing:
    """Tests for box-sizing detection."""

    def test_box_sizing_border_box(self, parse_and_check):
        """Test box-sizing: border-box detection."""
        css = "* { box-sizing: border-box; }"
        assert parse_and_check(css, 'css3-boxsizing')

    def test_box_sizing_content_box(self, parse_and_check):
        """Test box-sizing: content-box detection."""
        css = ".element { box-sizing: content-box; }"
        assert parse_and_check(css, 'css3-boxsizing')


class TestMinMaxWidthHeight:
    """Tests for min/max width/height detection."""

    def test_min_width(self, parse_and_check):
        """Test min-width detection."""
        css = ".element { min-width: 200px; }"
        assert parse_and_check(css, 'minmaxwh')

    def test_max_width(self, parse_and_check):
        """Test max-width detection."""
        css = ".element { max-width: 1200px; }"
        assert parse_and_check(css, 'minmaxwh')

    def test_min_height(self, parse_and_check):
        """Test min-height detection."""
        css = ".element { min-height: 100vh; }"
        assert parse_and_check(css, 'minmaxwh')

    def test_max_height(self, parse_and_check):
        """Test max-height detection."""
        css = ".element { max-height: 500px; }"
        assert parse_and_check(css, 'minmaxwh')


class TestIntrinsicWidth:
    """Tests for intrinsic sizing keywords detection."""

    def test_min_content(self, parse_and_check):
        """Test width: min-content detection."""
        css = ".element { width: min-content; }"
        assert parse_and_check(css, 'intrinsic-width')

    def test_max_content(self, parse_and_check):
        """Test width: max-content detection."""
        css = ".element { width: max-content; }"
        assert parse_and_check(css, 'intrinsic-width')

    def test_fit_content(self, parse_and_check):
        """Test width: fit-content detection."""
        css = ".element { width: fit-content; }"
        assert parse_and_check(css, 'intrinsic-width')


class TestObjectFit:
    """Tests for object-fit detection."""

    def test_object_fit_cover(self, parse_and_check):
        """Test object-fit: cover detection."""
        css = "img { object-fit: cover; }"
        assert parse_and_check(css, 'object-fit')

    def test_object_fit_contain(self, parse_and_check):
        """Test object-fit: contain detection."""
        css = "img { object-fit: contain; }"
        assert parse_and_check(css, 'object-fit')

    def test_object_position(self, parse_and_check):
        """Test object-position detection."""
        css = "img { object-position: center top; }"
        assert parse_and_check(css, 'object-fit')


class TestBorderImage:
    """Tests for border-image detection."""

    def test_border_image(self, parse_and_check):
        """Test border-image detection."""
        css = ".element { border-image: url(border.png) 30 round; }"
        assert parse_and_check(css, 'border-image')

    def test_border_image_source(self, parse_and_check):
        """Test border-image-source detection."""
        css = ".element { border-image-source: url(border.png); }"
        assert parse_and_check(css, 'border-image')


class TestBorderRadius:
    """Tests for border-radius detection."""

    def test_border_radius(self, parse_and_check):
        """Test border-radius detection."""
        css = ".element { border-radius: 10px; }"
        assert parse_and_check(css, 'border-radius')

    def test_border_radius_percentage(self, parse_and_check):
        """Test border-radius with percentage detection."""
        css = ".circle { border-radius: 50%; }"
        assert parse_and_check(css, 'border-radius')


class TestOutline:
    """Tests for outline detection."""

    def test_outline(self, parse_and_check):
        """Test outline detection."""
        css = ".element { outline: 2px solid blue; }"
        assert parse_and_check(css, 'outline')

    def test_outline_width(self, parse_and_check):
        """Test outline-width detection."""
        css = ".element { outline-width: 3px; }"
        assert parse_and_check(css, 'outline')

    def test_outline_style(self, parse_and_check):
        """Test outline-style detection."""
        css = ".element { outline-style: dashed; }"
        assert parse_and_check(css, 'outline')

    def test_outline_color(self, parse_and_check):
        """Test outline-color detection."""
        css = ".element { outline-color: red; }"
        assert parse_and_check(css, 'outline')


class TestBoxDecorationBreak:
    """Tests for box-decoration-break detection."""

    def test_box_decoration_break(self, parse_and_check):
        """Test box-decoration-break detection."""
        css = ".element { box-decoration-break: clone; }"
        assert parse_and_check(css, 'css-boxdecorationbreak')


class TestBoxShadow:
    """Tests for box-shadow detection."""

    def test_box_shadow(self, parse_and_check):
        """Test box-shadow detection."""
        css = ".element { box-shadow: 0 2px 4px rgba(0,0,0,0.1); }"
        assert parse_and_check(css, 'css-boxshadow')

    def test_box_shadow_inset(self, parse_and_check):
        """Test box-shadow inset detection."""
        css = ".element { box-shadow: inset 0 0 10px black; }"
        assert parse_and_check(css, 'css-boxshadow')

    def test_multiple_box_shadows(self, parse_and_check):
        """Test multiple box-shadows detection."""
        css = ".element { box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); }"
        assert parse_and_check(css, 'css-boxshadow')


class TestTextShadow:
    """Tests for text-shadow detection."""

    def test_text_shadow(self, parse_and_check):
        """Test text-shadow detection."""
        css = ".element { text-shadow: 2px 2px 4px black; }"
        assert parse_and_check(css, 'css-textshadow')

    def test_multiple_text_shadows(self, parse_and_check):
        """Test multiple text-shadows detection."""
        css = ".element { text-shadow: 1px 1px white, -1px -1px black; }"
        assert parse_and_check(css, 'css-textshadow')
