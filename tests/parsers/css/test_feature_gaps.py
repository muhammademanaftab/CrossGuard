"""Tests for feature IDs that had NO test coverage.

Covers: font formats (woff, woff2, ttf, eot, colr, colr-v1, svg-fonts),
css-background-offsets, css-grid-animation, css-image-orientation,
css-canvas, css-exclusions, css-regions, css-if, css-descendant-gtgt,
and JS-oriented features that appear in css_feature_maps.py.
"""

import pytest
from src.parsers.css_parser import CSSParser


@pytest.fixture
def css_parser():
    return CSSParser()


@pytest.fixture
def parse_css(css_parser):
    def _parse(css: str) -> set:
        return css_parser.parse_string(css)
    return _parse


# ═══════════════════════════════════════════════════════════════════════════
# Font Format Detection
# ═══════════════════════════════════════════════════════════════════════════

class TestWOFF:
    """WOFF font format detection."""

    def test_woff_format_function(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.woff') format('woff');
        }"""
        assert 'woff' in parse_css(css)

    def test_woff_file_extension(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.woff');
        }"""
        assert 'woff' in parse_css(css)


class TestWOFF2:
    """WOFF2 font format detection."""

    def test_woff2_format_function(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.woff2') format('woff2');
        }"""
        assert 'woff2' in parse_css(css)

    def test_woff2_file_extension(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.woff2');
        }"""
        assert 'woff2' in parse_css(css)


class TestTTF:
    """TTF/OTF font format detection."""

    def test_ttf_file_extension(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.ttf');
        }"""
        assert 'ttf' in parse_css(css)

    def test_otf_file_extension(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.otf');
        }"""
        assert 'ttf' in parse_css(css)

    def test_truetype_format(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.ttf') format('truetype');
        }"""
        assert 'ttf' in parse_css(css)


class TestEOT:
    """EOT font format detection."""

    def test_eot_file_extension(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.eot');
        }"""
        assert 'eot' in parse_css(css)

    def test_eot_format_function(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.eot') format('embedded-opentype');
        }"""
        assert 'eot' in parse_css(css)


class TestCOLR:
    """COLR/CPAL font format detection."""

    def test_colr_format(self, parse_css):
        css = """@font-face {
            font-family: 'ColorFont';
            src: url('font.woff2') format('colr');
        }"""
        assert 'colr' in parse_css(css)

    def test_colr_font_technology(self, parse_css):
        css = """@font-face {
            font-family: 'ColorFont';
            src: url('font.woff2') tech(font-technology(colr));
        }"""
        # Pattern: font-technology\s*\(\s*colr\s*\)
        assert 'colr' in parse_css(css)


class TestCOLRV1:
    """COLR v1 font format detection."""

    def test_colr_v1_format(self, parse_css):
        css = """@font-face {
            font-family: 'ColorFont';
            src: url('font.woff2') format('colr-v1');
        }"""
        assert 'colr-v1' in parse_css(css)


class TestSVGFonts:
    """SVG font format detection."""

    def test_svg_format_function(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.svg#glyphs') format('svg');
        }"""
        assert 'svg-fonts' in parse_css(css)

    def test_svg_hash_reference(self, parse_css):
        css = """@font-face {
            font-family: 'Test';
            src: url('font.svg#TestFont');
        }"""
        assert 'svg-fonts' in parse_css(css)


# ═══════════════════════════════════════════════════════════════════════════
# Additional CSS Features Without Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCSSGridAnimation:
    """CSS Grid animation feature."""

    def test_grid_template_transition(self, parse_css):
        css = "div { grid-template-columns: 1fr; transition: grid-template-columns 0.3s; }"
        features = parse_css(css)
        # Pattern: grid-template.*transition or grid.*animation
        # This pattern expects both in same line — may not work with tinycss2 reconstruction
        # The pattern is: r'grid-template.*transition'
        # In matchable text, this becomes: div { grid-template-columns: 1fr; transition: grid-template-columns 0.3s; }
        # So grid-template...transition should match within the reconstructed block
        assert 'css-grid-animation' in features

    def test_grid_animation(self, parse_css):
        css = "div { display: grid; animation: gridExpand 1s; }"
        features = parse_css(css)
        # Pattern: r'grid.*animation' — grid then animation somewhere after
        assert 'css-grid-animation' in features


class TestCSSImageOrientation:
    """CSS image-orientation property."""

    def test_image_orientation(self, parse_css):
        css = "img { image-orientation: from-image; }"
        assert 'css-image-orientation' in parse_css(css)

    def test_image_orientation_none(self, parse_css):
        css = "img { image-orientation: none; }"
        assert 'css-image-orientation' in parse_css(css)


class TestCSSCanvas:
    """CSS -webkit-canvas() function."""

    def test_webkit_canvas(self, parse_css):
        css = "div { background: -webkit-canvas(mycanvas); }"
        assert 'css-canvas' in parse_css(css)


class TestCSSExclusions:
    """CSS Exclusions Level 1."""

    def test_wrap_flow(self, parse_css):
        css = "div { wrap-flow: both; }"
        assert 'css-exclusions' in parse_css(css)

    def test_wrap_through(self, parse_css):
        css = "div { wrap-through: none; }"
        assert 'css-exclusions' in parse_css(css)


class TestCSSRegions:
    """CSS Regions."""

    def test_flow_into(self, parse_css):
        css = "div { flow-into: myflow; }"
        assert 'css-regions' in parse_css(css)

    def test_flow_from(self, parse_css):
        css = "div { flow-from: myflow; }"
        assert 'css-regions' in parse_css(css)


class TestCSSIf:
    """CSS if() function."""

    def test_css_if_function(self, parse_css):
        css = "div { color: if(style(--theme: dark), white, black); }"
        assert 'css-if' in parse_css(css)


class TestCSSBackgroundOffsets:
    """CSS background-position edge offsets."""

    def test_background_position_from_offset(self, parse_css):
        css = "div { background-position: right 10px from bottom 20px; }"
        # Pattern: r'background-position.*\s+from\s+'
        features = parse_css(css)
        # This tests whether the 'from' keyword in background-position is detected
        assert 'css-background-offsets' in features


class TestCSSReflections:
    """CSS -webkit-box-reflect."""

    def test_box_reflect(self, parse_css):
        css = "div { -webkit-box-reflect: below 10px; }"
        assert 'css-reflections' in parse_css(css)


class TestCSSOverflowOverlay:
    """CSS overflow: overlay value."""

    def test_overflow_overlay(self, parse_css):
        css = "div { overflow: overlay; }"
        assert 'css-overflow-overlay' in parse_css(css)


class TestCSSInitialLetter:
    """CSS initial-letter property."""

    def test_initial_letter(self, parse_css):
        css = "p::first-letter { initial-letter: 3; }"
        assert 'css-initial-letter' in parse_css(css)


class TestCSSNotSelList:
    """CSS :not() with selector list argument."""

    def test_not_selector_list(self, parse_css):
        css = "div:not(.a, .b) { color: red; }"
        assert 'css-not-sel-list' in parse_css(css)


class TestCSSNthChildOf:
    """CSS :nth-child() with 'of' selector."""

    def test_nth_child_of(self, parse_css):
        css = "li:nth-child(2 of .important) { font-weight: bold; }"
        assert 'css-nth-child-of' in parse_css(css)


class TestCSSInOutOfRange:
    """CSS :in-range and :out-of-range pseudo-classes."""

    def test_in_range(self, parse_css):
        css = "input:in-range { border-color: green; }"
        assert 'css-in-out-of-range' in parse_css(css)

    def test_out_of_range(self, parse_css):
        css = "input:out-of-range { border-color: red; }"
        assert 'css-in-out-of-range' in parse_css(css)


class TestCSSViewTransitions:
    """View transition pseudo-elements — CSS-specific patterns."""

    def test_view_transition_old(self, parse_css):
        css = "::view-transition-old(root) { animation: fade-out 0.3s; }"
        assert 'view-transitions' in parse_css(css)

    def test_view_transition_new(self, parse_css):
        css = "::view-transition-new(root) { animation: fade-in 0.3s; }"
        assert 'view-transitions' in parse_css(css)

    def test_view_transition_group(self, parse_css):
        css = "::view-transition-group(root) { animation-duration: 0.3s; }"
        assert 'view-transitions' in parse_css(css)


class TestCrossDocumentViewTransitions:
    """Cross-document view transitions."""

    def test_view_transition_at_rule(self, parse_css):
        css = "@view-transition { navigation: auto; }"
        assert 'cross-document-view-transitions' in parse_css(css)

    def test_view_transition_name(self, parse_css):
        css = "div { view-transition-name: hero; }"
        assert 'cross-document-view-transitions' in parse_css(css)


class TestFullscreen:
    """CSS :fullscreen pseudo-class."""

    def test_fullscreen_pseudo(self, parse_css):
        css = ":fullscreen { background: black; }"
        assert 'fullscreen' in parse_css(css)


class TestSVGInCSS:
    """SVG in CSS backgrounds."""

    def test_svg_background(self, parse_css):
        css = "div { background: url('image.svg'); }"
        features = parse_css(css)
        # Pattern: r'background.*\.svg'
        assert 'svg-css' in features

    def test_svg_background_image(self, parse_css):
        css = "div { background-image: url('icon.svg'); }"
        features = parse_css(css)
        assert 'svg-css' in features


class TestWebkitUserDrag:
    """CSS -webkit-user-drag property."""

    def test_webkit_user_drag(self, parse_css):
        css = "img { -webkit-user-drag: none; }"
        assert 'webkit-user-drag' in parse_css(css)


class TestCSSPaintAPI:
    """CSS paint() function."""

    def test_paint_function(self, parse_css):
        css = "div { background-image: paint(myPainter); }"
        assert 'css-paint-api' in parse_css(css)


class TestCSSColorAdjust:
    """CSS print-color-adjust / color-adjust."""

    def test_print_color_adjust(self, parse_css):
        css = "div { print-color-adjust: exact; }"
        assert 'css-color-adjust' in parse_css(css)

    def test_color_adjust(self, parse_css):
        css = "div { color-adjust: exact; }"
        assert 'css-color-adjust' in parse_css(css)
