"""Tests for CSS Transform features.

Tests features: transforms2d, transforms3d

Note: transforms3d patterns only include: translate3d, rotateX, rotateY, rotateZ, perspective
Other 3D functions (translateZ, scale3d, scaleZ, rotate3d, matrix3d, backface-visibility,
transform-style) are not in the parser patterns.
"""

import pytest


class TestTransforms2D:
    """Tests for CSS 2D Transform detection."""

    def test_transform_property(self, parse_and_check):
        """Test transform property detection."""
        css = ".element { transform: rotate(45deg); }"
        assert parse_and_check(css, 'transforms2d')

    def test_translate(self, parse_and_check):
        """Test translate() function detection."""
        css = ".element { transform: translate(50px, 100px); }"
        assert parse_and_check(css, 'transforms2d')

    def test_translateX(self, parse_and_check):
        """Test translateX() function detection."""
        css = ".element { transform: translateX(50px); }"
        assert parse_and_check(css, 'transforms2d')

    def test_translateY(self, parse_and_check):
        """Test translateY() function detection."""
        css = ".element { transform: translateY(100px); }"
        assert parse_and_check(css, 'transforms2d')

    def test_rotate(self, parse_and_check):
        """Test rotate() function detection."""
        css = ".element { transform: rotate(45deg); }"
        assert parse_and_check(css, 'transforms2d')

    def test_scale(self, parse_and_check):
        """Test scale() function detection."""
        css = ".element { transform: scale(1.5); }"
        assert parse_and_check(css, 'transforms2d')

    def test_scaleX(self, parse_and_check):
        """Test scaleX() function detection."""
        css = ".element { transform: scaleX(2); }"
        assert parse_and_check(css, 'transforms2d')

    def test_scaleY(self, parse_and_check):
        """Test scaleY() function detection."""
        css = ".element { transform: scaleY(0.5); }"
        assert parse_and_check(css, 'transforms2d')

    def test_skew(self, parse_and_check):
        """Test skew() function detection."""
        css = ".element { transform: skew(30deg, 20deg); }"
        assert parse_and_check(css, 'transforms2d')

    def test_skewX(self, parse_and_check):
        """Test skewX() function detection."""
        css = ".element { transform: skewX(30deg); }"
        assert parse_and_check(css, 'transforms2d')

    def test_skewY(self, parse_and_check):
        """Test skewY() function detection."""
        css = ".element { transform: skewY(20deg); }"
        assert parse_and_check(css, 'transforms2d')

    def test_matrix(self, parse_and_check):
        """Test matrix() function detection."""
        css = ".element { transform: matrix(1, 0, 0, 1, 50, 50); }"
        assert parse_and_check(css, 'transforms2d')

    def test_multiple_transforms(self, parse_and_check):
        """Test multiple transforms detection."""
        css = ".element { transform: translate(50px, 50px) rotate(45deg) scale(1.5); }"
        assert parse_and_check(css, 'transforms2d')


class TestTransforms3D:
    """Tests for CSS 3D Transform detection.

    Note: Parser patterns only detect translate3d, rotateX, rotateY, rotateZ, perspective.
    """

    def test_translate3d(self, parse_and_check):
        """Test translate3d() function detection."""
        css = ".element { transform: translate3d(50px, 100px, 20px); }"
        assert parse_and_check(css, 'transforms3d')

    def test_rotateX(self, parse_and_check):
        """Test rotateX() function detection."""
        css = ".element { transform: rotateX(45deg); }"
        assert parse_and_check(css, 'transforms3d')

    def test_rotateY(self, parse_and_check):
        """Test rotateY() function detection."""
        css = ".element { transform: rotateY(45deg); }"
        assert parse_and_check(css, 'transforms3d')

    def test_rotateZ(self, parse_and_check):
        """Test rotateZ() function detection."""
        css = ".element { transform: rotateZ(45deg); }"
        assert parse_and_check(css, 'transforms3d')

    def test_perspective_function(self, parse_and_check):
        """Test perspective() function detection."""
        css = ".element { transform: perspective(500px) rotateY(45deg); }"
        assert parse_and_check(css, 'transforms3d')

    def test_perspective_property(self, parse_and_check):
        """Test perspective property detection."""
        css = ".container { perspective: 1000px; }"
        assert parse_and_check(css, 'transforms3d')

    def test_complete_3d_card_flip(self, parse_and_check):
        """Test complete 3D card flip setup with supported patterns."""
        css = """
        .scene { perspective: 600px; }
        .card { transform: rotateY(180deg); }
        """
        assert parse_and_check(css, 'transforms3d')
