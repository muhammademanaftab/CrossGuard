"""Tests for Miscellaneous CSS features.

Tests features: css-opacity, css-zoom, css-all, css-unset-value, css-initial-value,
                css-revert-value, css-widows-orphans, css-writing-mode, css-color-adjust,
                css-element-function, css-cross-fade, css-crisp-edges, css-unicode-bidi,
                css3-attr, justify-content-space-evenly, css-sticky, css-fixed,
                css-overflow, css-overflow-anchor, css-overflow-overlay,
                css-initial-letter, css-reflections, css-regions, css-exclusions,
                css-descendant-gtgt, css-canvas, css-if, webkit-user-drag, svg-css,
                style-scoped, fullscreen, getcomputedstyle, devicepixelratio,
                pointer, font-loading
"""

import pytest


class TestOpacity:
    """Tests for opacity detection."""

    def test_opacity(self, parse_and_check):
        """Test opacity detection."""
        css = ".transparent { opacity: 0.5; }"
        assert parse_and_check(css, 'css-opacity')


class TestZoom:
    """Tests for zoom detection."""

    def test_zoom(self, parse_and_check):
        """Test zoom detection."""
        css = ".zoomed { zoom: 1.5; }"
        assert parse_and_check(css, 'css-zoom')


class TestAll:
    """Tests for all property detection."""

    def test_all_unset(self, parse_and_check):
        """Test all: unset detection."""
        css = ".reset { all: unset; }"
        assert parse_and_check(css, 'css-all')

    def test_all_initial(self, parse_and_check):
        """Test all: initial detection."""
        css = ".reset { all: initial; }"
        assert parse_and_check(css, 'css-all')


class TestUnsetValue:
    """Tests for unset value detection."""

    def test_unset_value(self, parse_and_check):
        """Test unset value detection."""
        css = ".element { color: unset; }"
        assert parse_and_check(css, 'css-unset-value')


class TestInitialValue:
    """Tests for initial value detection."""

    def test_initial_value(self, parse_and_check):
        """Test initial value detection."""
        css = ".element { font-size: initial; }"
        assert parse_and_check(css, 'css-initial-value')


class TestRevertValue:
    """Tests for revert value detection."""

    def test_revert_value(self, parse_and_check):
        """Test revert value detection."""
        css = ".element { color: revert; }"
        assert parse_and_check(css, 'css-revert-value')


class TestWidowsOrphans:
    """Tests for widows/orphans detection."""

    def test_widows(self, parse_and_check):
        """Test widows detection."""
        css = "p { widows: 3; }"
        assert parse_and_check(css, 'css-widows-orphans')

    def test_orphans(self, parse_and_check):
        """Test orphans detection."""
        css = "p { orphans: 2; }"
        assert parse_and_check(css, 'css-widows-orphans')


class TestWritingMode:
    """Tests for writing-mode detection."""

    def test_writing_mode_vertical(self, parse_and_check):
        """Test writing-mode: vertical-rl detection."""
        css = ".vertical { writing-mode: vertical-rl; }"
        assert parse_and_check(css, 'css-writing-mode')

    def test_writing_mode_horizontal(self, parse_and_check):
        """Test writing-mode: horizontal-tb detection."""
        css = ".element { writing-mode: horizontal-tb; }"
        assert parse_and_check(css, 'css-writing-mode')


class TestColorAdjust:
    """Tests for color-adjust/print-color-adjust detection."""

    def test_print_color_adjust(self, parse_and_check):
        """Test print-color-adjust detection."""
        css = ".print { print-color-adjust: exact; }"
        assert parse_and_check(css, 'css-color-adjust')

    def test_color_adjust(self, parse_and_check):
        """Test color-adjust detection."""
        css = ".print { color-adjust: exact; }"
        assert parse_and_check(css, 'css-color-adjust')


class TestElementFunction:
    """Tests for element() function detection."""

    def test_element_function(self, parse_and_check):
        """Test element() function detection."""
        css = ".bg { background: element(#myElement); }"
        assert parse_and_check(css, 'css-element-function')


class TestCrossFade:
    """Tests for cross-fade() function detection."""

    def test_cross_fade(self, parse_and_check):
        """Test cross-fade() function detection."""
        css = ".element { background-image: cross-fade(url(a.png), url(b.png), 50%); }"
        assert parse_and_check(css, 'css-cross-fade')


class TestCrispEdges:
    """Tests for crisp-edges/pixelated detection."""

    def test_image_rendering_crisp_edges(self, parse_and_check):
        """Test image-rendering: crisp-edges detection."""
        css = "img { image-rendering: crisp-edges; }"
        assert parse_and_check(css, 'css-crisp-edges')

    def test_image_rendering_pixelated(self, parse_and_check):
        """Test image-rendering: pixelated detection."""
        css = "img { image-rendering: pixelated; }"
        assert parse_and_check(css, 'css-crisp-edges')


class TestUnicodeBidi:
    """Tests for unicode-bidi detection."""

    def test_unicode_bidi(self, parse_and_check):
        """Test unicode-bidi detection."""
        css = ".rtl { unicode-bidi: bidi-override; }"
        assert parse_and_check(css, 'css-unicode-bidi')


class TestAttr:
    """Tests for attr() function detection."""

    def test_attr_function(self, parse_and_check):
        """Test attr() function detection."""
        css = ".tooltip::after { content: attr(data-tooltip); }"
        assert parse_and_check(css, 'css3-attr')


class TestJustifyContentSpaceEvenly:
    """Tests for justify-content: space-evenly detection."""

    def test_space_evenly(self, parse_and_check):
        """Test justify-content: space-evenly detection."""
        css = ".container { justify-content: space-evenly; }"
        assert parse_and_check(css, 'justify-content-space-evenly')


class TestPositionSticky:
    """Tests for position: sticky detection."""

    def test_position_sticky(self, parse_and_check):
        """Test position: sticky detection."""
        css = ".header { position: sticky; top: 0; }"
        assert parse_and_check(css, 'css-sticky')


class TestPositionFixed:
    """Tests for position: fixed detection."""

    def test_position_fixed(self, parse_and_check):
        """Test position: fixed detection."""
        css = ".modal { position: fixed; }"
        assert parse_and_check(css, 'css-fixed')


class TestOverflow:
    """Tests for overflow detection."""

    def test_overflow(self, parse_and_check):
        """Test overflow detection."""
        css = ".scrollable { overflow: auto; }"
        assert parse_and_check(css, 'css-overflow')

    def test_overflow_x(self, parse_and_check):
        """Test overflow-x detection."""
        css = ".horizontal { overflow-x: scroll; }"
        assert parse_and_check(css, 'css-overflow')

    def test_overflow_y(self, parse_and_check):
        """Test overflow-y detection."""
        css = ".vertical { overflow-y: hidden; }"
        assert parse_and_check(css, 'css-overflow')


class TestOverflowAnchor:
    """Tests for overflow-anchor detection."""

    def test_overflow_anchor(self, parse_and_check):
        """Test overflow-anchor detection."""
        css = ".element { overflow-anchor: none; }"
        assert parse_and_check(css, 'css-overflow-anchor')


class TestOverflowOverlay:
    """Tests for overflow: overlay detection."""

    def test_overflow_overlay(self, parse_and_check):
        """Test overflow: overlay detection."""
        css = ".scrollable { overflow: overlay; }"
        assert parse_and_check(css, 'css-overflow-overlay')


class TestInitialLetter:
    """Tests for initial-letter detection."""

    def test_initial_letter(self, parse_and_check):
        """Test initial-letter detection."""
        css = "p::first-letter { initial-letter: 3; }"
        assert parse_and_check(css, 'css-initial-letter')


class TestReflections:
    """Tests for CSS reflections detection."""

    def test_webkit_box_reflect(self, parse_and_check):
        """Test -webkit-box-reflect detection."""
        css = ".element { -webkit-box-reflect: below 10px; }"
        assert parse_and_check(css, 'css-reflections')


class TestRegions:
    """Tests for CSS Regions detection."""

    def test_flow_into(self, parse_and_check):
        """Test flow-into detection."""
        css = ".source { flow-into: myFlow; }"
        assert parse_and_check(css, 'css-regions')

    def test_flow_from(self, parse_and_check):
        """Test flow-from detection."""
        css = ".region { flow-from: myFlow; }"
        assert parse_and_check(css, 'css-regions')


class TestExclusions:
    """Tests for CSS Exclusions detection."""

    def test_wrap_flow(self, parse_and_check):
        """Test wrap-flow detection."""
        css = ".exclusion { wrap-flow: both; }"
        assert parse_and_check(css, 'css-exclusions')

    def test_wrap_through(self, parse_and_check):
        """Test wrap-through detection."""
        css = ".element { wrap-through: none; }"
        assert parse_and_check(css, 'css-exclusions')


class TestDescendantCombinator:
    """Tests for >> descendant combinator detection."""

    def test_descendant_gtgt(self, parse_and_check):
        """Test >> descendant combinator detection."""
        css = "div >> p { color: blue; }"
        assert parse_and_check(css, 'css-descendant-gtgt')


class TestCanvas:
    """Tests for CSS Canvas detection."""

    def test_webkit_canvas(self, parse_and_check):
        """Test -webkit-canvas() detection."""
        css = ".element { background: -webkit-canvas(myCanvas); }"
        assert parse_and_check(css, 'css-canvas')


class TestIfFunction:
    """Tests for CSS if() function detection."""

    def test_if_function(self, parse_and_check):
        """Test if() function detection."""
        css = ".element { color: if(style(--dark: true), white, black); }"
        assert parse_and_check(css, 'css-if')


class TestWebkitUserDrag:
    """Tests for -webkit-user-drag detection."""

    def test_webkit_user_drag(self, parse_and_check):
        """Test -webkit-user-drag detection."""
        css = "img { -webkit-user-drag: none; }"
        assert parse_and_check(css, 'webkit-user-drag')


class TestSVGCSS:
    """Tests for SVG in CSS backgrounds detection."""

    def test_svg_background(self, parse_and_check):
        """Test SVG background detection."""
        css = ".icon { background: url(icon.svg); }"
        assert parse_and_check(css, 'svg-css')

    def test_svg_background_image(self, parse_and_check):
        """Test SVG background-image detection."""
        css = ".icon { background-image: url(pattern.svg); }"
        assert parse_and_check(css, 'svg-css')
