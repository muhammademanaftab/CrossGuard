"""Tests for CSS Unit features.

Tests features: rem, viewport-units, viewport-unit-variants, calc, ch-unit,
                css-container-query-units
"""

import pytest


class TestRemUnit:
    """Tests for rem unit detection."""

    def test_rem_font_size(self, parse_and_check):
        """Test rem in font-size detection."""
        css = "body { font-size: 1rem; }"
        assert parse_and_check(css, 'rem')

    def test_rem_margin(self, parse_and_check):
        """Test rem in margin detection."""
        css = ".element { margin: 2rem; }"
        assert parse_and_check(css, 'rem')

    def test_rem_decimal(self, parse_and_check):
        """Test rem with decimal value detection."""
        css = ".element { padding: 1.5rem; }"
        assert parse_and_check(css, 'rem')


class TestViewportUnits:
    """Tests for viewport units (vw, vh, vmin, vmax) detection."""

    def test_vw(self, parse_and_check):
        """Test vw unit detection."""
        css = ".full-width { width: 100vw; }"
        assert parse_and_check(css, 'viewport-units')

    def test_vh(self, parse_and_check):
        """Test vh unit detection."""
        css = ".full-height { height: 100vh; }"
        assert parse_and_check(css, 'viewport-units')

    def test_vmin(self, parse_and_check):
        """Test vmin unit detection."""
        css = ".element { font-size: 5vmin; }"
        assert parse_and_check(css, 'viewport-units')

    def test_vmax(self, parse_and_check):
        """Test vmax unit detection."""
        css = ".element { width: 50vmax; }"
        assert parse_and_check(css, 'viewport-units')

    def test_viewport_decimal(self, parse_and_check):
        """Test viewport unit with decimal value."""
        css = ".element { height: 50.5vh; }"
        assert parse_and_check(css, 'viewport-units')


class TestViewportUnitVariants:
    """Tests for small/large/dynamic viewport units detection."""

    def test_svw(self, parse_and_check):
        """Test svw (small viewport width) detection."""
        css = ".element { width: 100svw; }"
        assert parse_and_check(css, 'viewport-unit-variants')

    def test_svh(self, parse_and_check):
        """Test svh (small viewport height) detection."""
        css = ".element { height: 100svh; }"
        assert parse_and_check(css, 'viewport-unit-variants')

    def test_lvw(self, parse_and_check):
        """Test lvw (large viewport width) detection."""
        css = ".element { width: 100lvw; }"
        assert parse_and_check(css, 'viewport-unit-variants')

    def test_lvh(self, parse_and_check):
        """Test lvh (large viewport height) detection."""
        css = ".element { height: 100lvh; }"
        assert parse_and_check(css, 'viewport-unit-variants')

    def test_dvw(self, parse_and_check):
        """Test dvw (dynamic viewport width) detection."""
        css = ".element { width: 100dvw; }"
        assert parse_and_check(css, 'viewport-unit-variants')

    def test_dvh(self, parse_and_check):
        """Test dvh (dynamic viewport height) detection."""
        css = ".element { height: 100dvh; }"
        assert parse_and_check(css, 'viewport-unit-variants')


class TestCalc:
    """Tests for calc() function detection."""

    def test_calc_basic(self, parse_and_check):
        """Test calc() function detection."""
        css = ".element { width: calc(100% - 20px); }"
        assert parse_and_check(css, 'calc')

    def test_calc_addition(self, parse_and_check):
        """Test calc() with addition."""
        css = ".element { margin: calc(1rem + 10px); }"
        assert parse_and_check(css, 'calc')

    def test_calc_multiplication(self, parse_and_check):
        """Test calc() with multiplication."""
        css = ".element { width: calc(100% * 0.5); }"
        assert parse_and_check(css, 'calc')

    def test_calc_division(self, parse_and_check):
        """Test calc() with division."""
        css = ".element { width: calc(100vw / 3); }"
        assert parse_and_check(css, 'calc')

    def test_calc_nested(self, parse_and_check):
        """Test nested calc() function."""
        css = ".element { width: calc(100% - calc(20px + 1rem)); }"
        assert parse_and_check(css, 'calc')


class TestChUnit:
    """Tests for ch unit detection."""

    def test_ch_width(self, parse_and_check):
        """Test ch unit in width detection."""
        css = ".input { width: 20ch; }"
        assert parse_and_check(css, 'ch-unit')

    def test_ch_max_width(self, parse_and_check):
        """Test ch unit in max-width detection."""
        css = ".text { max-width: 65ch; }"
        assert parse_and_check(css, 'ch-unit')


class TestContainerQueryUnits:
    """Tests for container query units detection."""

    def test_cqw(self, parse_and_check):
        """Test cqw (container query width) detection."""
        css = ".element { width: 50cqw; }"
        assert parse_and_check(css, 'css-container-query-units')

    def test_cqh(self, parse_and_check):
        """Test cqh (container query height) detection."""
        css = ".element { height: 50cqh; }"
        assert parse_and_check(css, 'css-container-query-units')

    def test_cqi(self, parse_and_check):
        """Test cqi (container query inline) detection."""
        css = ".element { width: 50cqi; }"
        assert parse_and_check(css, 'css-container-query-units')

    def test_cqb(self, parse_and_check):
        """Test cqb (container query block) detection."""
        css = ".element { height: 50cqb; }"
        assert parse_and_check(css, 'css-container-query-units')
