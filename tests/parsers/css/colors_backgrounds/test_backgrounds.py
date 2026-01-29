"""Tests for CSS Background features.

Tests features: css-gradients, css-conic-gradients, css-repeating-gradients, multibackgrounds,
                background-img-opts, background-clip-text, css-backgroundblendmode,
                background-position-x-y, background-repeat-round-space, background-attachment,
                css-background-offsets, css-image-set
"""

import pytest


class TestCSSGradients:
    """Tests for CSS Gradient detection."""

    def test_linear_gradient(self, parse_and_check):
        """Test linear-gradient detection."""
        css = ".element { background: linear-gradient(to right, red, blue); }"
        assert parse_and_check(css, 'css-gradients')

    def test_linear_gradient_angle(self, parse_and_check):
        """Test linear-gradient with angle."""
        css = ".element { background: linear-gradient(45deg, red, blue); }"
        assert parse_and_check(css, 'css-gradients')

    def test_radial_gradient(self, parse_and_check):
        """Test radial-gradient detection."""
        css = ".element { background: radial-gradient(circle, red, blue); }"
        assert parse_and_check(css, 'css-gradients')

    def test_radial_gradient_ellipse(self, parse_and_check):
        """Test radial-gradient with ellipse."""
        css = ".element { background: radial-gradient(ellipse at center, red, blue); }"
        assert parse_and_check(css, 'css-gradients')

    def test_multiple_color_stops(self, parse_and_check):
        """Test gradient with multiple color stops."""
        css = ".element { background: linear-gradient(red, yellow 50%, blue); }"
        assert parse_and_check(css, 'css-gradients')


class TestConicGradients:
    """Tests for CSS Conic Gradient detection."""

    def test_conic_gradient(self, parse_and_check):
        """Test conic-gradient detection."""
        css = ".element { background: conic-gradient(red, yellow, green); }"
        assert parse_and_check(css, 'css-conic-gradients')

    def test_conic_gradient_from(self, parse_and_check):
        """Test conic-gradient with from angle."""
        css = ".element { background: conic-gradient(from 45deg, red, blue); }"
        assert parse_and_check(css, 'css-conic-gradients')

    def test_repeating_conic_gradient(self, parse_and_check):
        """Test repeating-conic-gradient detection."""
        css = ".element { background: repeating-conic-gradient(red 10%, blue 20%); }"
        assert parse_and_check(css, 'css-conic-gradients')


class TestRepeatingGradients:
    """Tests for CSS Repeating Gradient detection."""

    def test_repeating_linear_gradient(self, parse_and_check):
        """Test repeating-linear-gradient detection."""
        css = ".element { background: repeating-linear-gradient(45deg, red, blue 10px); }"
        assert parse_and_check(css, 'css-repeating-gradients')

    def test_repeating_radial_gradient(self, parse_and_check):
        """Test repeating-radial-gradient detection."""
        css = ".element { background: repeating-radial-gradient(circle, red, blue 10px); }"
        assert parse_and_check(css, 'css-repeating-gradients')


class TestMultipleBackgrounds:
    """Tests for multiple backgrounds detection."""

    def test_multiple_background_images(self, parse_and_check):
        """Test multiple background images with url."""
        css = ".element { background: url(img1.png), url(img2.png); }"
        assert parse_and_check(css, 'multibackgrounds')

    def test_multiple_background_image_property(self, parse_and_check):
        """Test multiple values in background-image."""
        css = ".element { background-image: url(top.png), url(bottom.png); }"
        assert parse_and_check(css, 'multibackgrounds')


class TestBackgroundImageOptions:
    """Tests for background-image options detection."""

    def test_background_size(self, parse_and_check):
        """Test background-size detection."""
        css = ".element { background-size: cover; }"
        assert parse_and_check(css, 'background-img-opts')

    def test_background_size_contain(self, parse_and_check):
        """Test background-size: contain detection."""
        css = ".element { background-size: contain; }"
        assert parse_and_check(css, 'background-img-opts')

    def test_background_size_pixels(self, parse_and_check):
        """Test background-size with pixels."""
        css = ".element { background-size: 100px 200px; }"
        assert parse_and_check(css, 'background-img-opts')

    def test_background_origin(self, parse_and_check):
        """Test background-origin detection."""
        css = ".element { background-origin: content-box; }"
        assert parse_and_check(css, 'background-img-opts')

    def test_background_clip(self, parse_and_check):
        """Test background-clip detection."""
        css = ".element { background-clip: padding-box; }"
        assert parse_and_check(css, 'background-img-opts')


class TestBackgroundClipText:
    """Tests for background-clip: text detection."""

    def test_background_clip_text(self, parse_and_check):
        """Test background-clip: text detection."""
        css = ".element { background-clip: text; }"
        assert parse_and_check(css, 'background-clip-text')

    def test_webkit_background_clip_text(self, parse_and_check):
        """Test -webkit-background-clip: text detection."""
        css = ".element { -webkit-background-clip: text; }"
        assert parse_and_check(css, 'background-clip-text')

    def test_gradient_text_effect(self, parse_and_check):
        """Test gradient text effect."""
        css = """
        .gradient-text {
            background: linear-gradient(to right, red, blue);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        """
        assert parse_and_check(css, 'background-clip-text')


class TestBackgroundBlendMode:
    """Tests for background-blend-mode detection."""

    def test_background_blend_mode(self, parse_and_check):
        """Test background-blend-mode detection."""
        css = ".element { background-blend-mode: multiply; }"
        assert parse_and_check(css, 'css-backgroundblendmode')

    def test_background_blend_mode_overlay(self, parse_and_check):
        """Test background-blend-mode: overlay detection."""
        css = ".element { background-blend-mode: overlay; }"
        assert parse_and_check(css, 'css-backgroundblendmode')


class TestBackgroundPositionXY:
    """Tests for background-position-x/y detection."""

    def test_background_position_x(self, parse_and_check):
        """Test background-position-x detection."""
        css = ".element { background-position-x: center; }"
        assert parse_and_check(css, 'background-position-x-y')

    def test_background_position_y(self, parse_and_check):
        """Test background-position-y detection."""
        css = ".element { background-position-y: 50%; }"
        assert parse_and_check(css, 'background-position-x-y')


class TestBackgroundRepeatRoundSpace:
    """Tests for background-repeat round/space detection."""

    def test_background_repeat_round(self, parse_and_check):
        """Test background-repeat: round detection."""
        css = ".element { background-repeat: round; }"
        assert parse_and_check(css, 'background-repeat-round-space')

    def test_background_repeat_space(self, parse_and_check):
        """Test background-repeat: space detection."""
        css = ".element { background-repeat: space; }"
        assert parse_and_check(css, 'background-repeat-round-space')


class TestBackgroundAttachment:
    """Tests for background-attachment detection."""

    def test_background_attachment_fixed(self, parse_and_check):
        """Test background-attachment: fixed detection."""
        css = ".element { background-attachment: fixed; }"
        assert parse_and_check(css, 'background-attachment')

    def test_background_attachment_local(self, parse_and_check):
        """Test background-attachment: local detection."""
        css = ".element { background-attachment: local; }"
        assert parse_and_check(css, 'background-attachment')


class TestImageSet:
    """Tests for image-set() function detection."""

    def test_image_set(self, parse_and_check):
        """Test image-set() detection."""
        css = '.element { background-image: image-set("img.png" 1x, "img@2x.png" 2x); }'
        assert parse_and_check(css, 'css-image-set')

    def test_webkit_image_set(self, parse_and_check):
        """Test -webkit-image-set() detection."""
        css = '.element { background-image: -webkit-image-set("img.png" 1x); }'
        assert parse_and_check(css, 'css-image-set')
