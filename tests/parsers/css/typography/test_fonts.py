"""Tests for CSS Font features.

Tests features: fontface, variable-fonts, font-feature, font-kerning, font-size-adjust,
                font-smooth, font-variant-alternates, font-variant-numeric,
                font-unicode-range, font-family-system-ui, extended-system-fonts,
                css-font-stretch, css-font-palette, css-font-rendering-controls

Note: Font format detection (woff, woff2, ttf, eot, svg-fonts, colr, colr-v1)
requires URLs to be outside quoted strings. The parser strips string literals
to avoid false positives, which affects font format detection patterns.
"""

import pytest


class TestFontFace:
    """Tests for @font-face detection."""

    def test_font_face_basic(self, parse_and_check):
        """Test @font-face rule detection."""
        css = """
        @font-face {
            font-family: CustomFont;
            src: local(Test);
        }
        """
        assert parse_and_check(css, 'fontface')

    def test_font_face_with_descriptors(self, parse_and_check):
        """Test @font-face with font descriptors."""
        css = """
        @font-face {
            font-family: CustomFont;
            font-weight: 400 700;
            font-style: normal;
        }
        """
        assert parse_and_check(css, 'fontface')


class TestVariableFonts:
    """Tests for variable fonts detection."""

    def test_font_variation_settings(self, parse_and_check):
        """Test font-variation-settings detection."""
        css = ".text { font-variation-settings: 'wght' 700; }"
        assert parse_and_check(css, 'variable-fonts')

    def test_font_optical_sizing(self, parse_and_check):
        """Test font-optical-sizing detection."""
        css = ".text { font-optical-sizing: auto; }"
        assert parse_and_check(css, 'variable-fonts')

    def test_font_variation_multiple(self, parse_and_check):
        """Test font-variation-settings with multiple axes."""
        css = ".text { font-variation-settings: 'wght' 700, 'wdth' 100; }"
        assert parse_and_check(css, 'variable-fonts')


class TestFontFeatureSettings:
    """Tests for font-feature-settings detection."""

    def test_font_feature_settings(self, parse_and_check):
        """Test font-feature-settings detection."""
        css = ".text { font-feature-settings: 'liga' 1, 'kern' 1; }"
        assert parse_and_check(css, 'font-feature')

    def test_font_variant_ligatures(self, parse_and_check):
        """Test font-variant-ligatures detection."""
        css = ".text { font-variant-ligatures: common-ligatures; }"
        assert parse_and_check(css, 'font-feature')

    def test_font_variant_ligatures_none(self, parse_and_check):
        """Test font-variant-ligatures: none detection."""
        css = ".text { font-variant-ligatures: none; }"
        assert parse_and_check(css, 'font-feature')


class TestFontKerning:
    """Tests for font-kerning detection."""

    def test_font_kerning_auto(self, parse_and_check):
        """Test font-kerning: auto detection."""
        css = ".text { font-kerning: auto; }"
        assert parse_and_check(css, 'font-kerning')

    def test_font_kerning_normal(self, parse_and_check):
        """Test font-kerning: normal detection."""
        css = ".text { font-kerning: normal; }"
        assert parse_and_check(css, 'font-kerning')

    def test_font_kerning_none(self, parse_and_check):
        """Test font-kerning: none detection."""
        css = ".text { font-kerning: none; }"
        assert parse_and_check(css, 'font-kerning')


class TestFontSizeAdjust:
    """Tests for font-size-adjust detection."""

    def test_font_size_adjust(self, parse_and_check):
        """Test font-size-adjust detection."""
        css = ".text { font-size-adjust: 0.5; }"
        assert parse_and_check(css, 'font-size-adjust')

    def test_font_size_adjust_none(self, parse_and_check):
        """Test font-size-adjust: none detection."""
        css = ".text { font-size-adjust: none; }"
        assert parse_and_check(css, 'font-size-adjust')


class TestFontSmooth:
    """Tests for font-smooth detection."""

    def test_webkit_font_smoothing(self, parse_and_check):
        """Test -webkit-font-smoothing detection."""
        css = ".text { -webkit-font-smoothing: antialiased; }"
        assert parse_and_check(css, 'font-smooth')

    def test_moz_osx_font_smoothing(self, parse_and_check):
        """Test -moz-osx-font-smoothing detection."""
        css = ".text { -moz-osx-font-smoothing: grayscale; }"
        assert parse_and_check(css, 'font-smooth')

    def test_webkit_font_smoothing_none(self, parse_and_check):
        """Test -webkit-font-smoothing: none detection."""
        css = ".text { -webkit-font-smoothing: none; }"
        assert parse_and_check(css, 'font-smooth')


class TestFontVariantAlternates:
    """Tests for font-variant-alternates detection."""

    def test_font_variant_alternates(self, parse_and_check):
        """Test font-variant-alternates detection."""
        css = ".text { font-variant-alternates: stylistic(alt); }"
        assert parse_and_check(css, 'font-variant-alternates')

    def test_font_variant_alternates_normal(self, parse_and_check):
        """Test font-variant-alternates: normal detection."""
        css = ".text { font-variant-alternates: normal; }"
        assert parse_and_check(css, 'font-variant-alternates')


class TestFontVariantNumeric:
    """Tests for font-variant-numeric detection."""

    def test_font_variant_numeric(self, parse_and_check):
        """Test font-variant-numeric detection."""
        css = ".numbers { font-variant-numeric: tabular-nums; }"
        assert parse_and_check(css, 'font-variant-numeric')

    def test_font_variant_numeric_oldstyle(self, parse_and_check):
        """Test font-variant-numeric: oldstyle-nums detection."""
        css = ".numbers { font-variant-numeric: oldstyle-nums; }"
        assert parse_and_check(css, 'font-variant-numeric')


class TestFontUnicodeRange:
    """Tests for unicode-range detection."""

    def test_unicode_range(self, parse_and_check):
        """Test unicode-range detection."""
        css = "@font-face { unicode-range: U+0000-00FF; }"
        assert parse_and_check(css, 'font-unicode-range')

    def test_unicode_range_multiple(self, parse_and_check):
        """Test unicode-range with multiple ranges."""
        css = "@font-face { unicode-range: U+0000-00FF, U+0100-017F; }"
        assert parse_and_check(css, 'font-unicode-range')


class TestSystemUI:
    """Tests for system-ui font detection."""

    def test_system_ui(self, parse_and_check):
        """Test system-ui font family detection."""
        css = ".text { font-family: system-ui, sans-serif; }"
        assert parse_and_check(css, 'font-family-system-ui')

    def test_system_ui_alone(self, parse_and_check):
        """Test system-ui as only font family."""
        css = ".text { font-family: system-ui; }"
        assert parse_and_check(css, 'font-family-system-ui')


class TestExtendedSystemFonts:
    """Tests for extended system fonts detection."""

    def test_ui_serif(self, parse_and_check):
        """Test ui-serif detection."""
        css = ".text { font-family: ui-serif, serif; }"
        assert parse_and_check(css, 'extended-system-fonts')

    def test_ui_sans_serif(self, parse_and_check):
        """Test ui-sans-serif detection."""
        css = ".text { font-family: ui-sans-serif, sans-serif; }"
        assert parse_and_check(css, 'extended-system-fonts')

    def test_ui_monospace(self, parse_and_check):
        """Test ui-monospace detection."""
        css = ".code { font-family: ui-monospace, monospace; }"
        assert parse_and_check(css, 'extended-system-fonts')

    def test_ui_rounded(self, parse_and_check):
        """Test ui-rounded detection."""
        css = ".text { font-family: ui-rounded, sans-serif; }"
        assert parse_and_check(css, 'extended-system-fonts')


class TestFontStretch:
    """Tests for font-stretch detection."""

    def test_font_stretch_condensed(self, parse_and_check):
        """Test font-stretch: condensed detection."""
        css = ".text { font-stretch: condensed; }"
        assert parse_and_check(css, 'css-font-stretch')

    def test_font_stretch_expanded(self, parse_and_check):
        """Test font-stretch: expanded detection."""
        css = ".text { font-stretch: expanded; }"
        assert parse_and_check(css, 'css-font-stretch')

    def test_font_stretch_percentage(self, parse_and_check):
        """Test font-stretch with percentage."""
        css = ".text { font-stretch: 75%; }"
        assert parse_and_check(css, 'css-font-stretch')


class TestFontPalette:
    """Tests for font-palette detection."""

    def test_font_palette_dark(self, parse_and_check):
        """Test font-palette: dark detection."""
        css = ".emoji { font-palette: dark; }"
        assert parse_and_check(css, 'css-font-palette')

    def test_font_palette_light(self, parse_and_check):
        """Test font-palette: light detection."""
        css = ".emoji { font-palette: light; }"
        assert parse_and_check(css, 'css-font-palette')


class TestFontDisplay:
    """Tests for font-display detection."""

    def test_font_display_swap(self, parse_and_check):
        """Test font-display: swap detection."""
        css = "@font-face { font-display: swap; }"
        assert parse_and_check(css, 'css-font-rendering-controls')

    def test_font_display_optional(self, parse_and_check):
        """Test font-display: optional detection."""
        css = "@font-face { font-display: optional; }"
        assert parse_and_check(css, 'css-font-rendering-controls')

    def test_font_display_fallback(self, parse_and_check):
        """Test font-display: fallback detection."""
        css = "@font-face { font-display: fallback; }"
        assert parse_and_check(css, 'css-font-rendering-controls')

    def test_font_display_block(self, parse_and_check):
        """Test font-display: block detection."""
        css = "@font-face { font-display: block; }"
        assert parse_and_check(css, 'css-font-rendering-controls')
