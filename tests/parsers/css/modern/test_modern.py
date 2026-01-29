"""Tests for Modern CSS features.

Tests features: css-container-queries, css-container-queries-style, css-nesting,
                css-anchor-positioning, css-containment, css-content-visibility,
                css-motion-paths, css-shapes, css-masks, css-clip-path,
                css-logical-props, view-transitions, cross-document-view-transitions,
                css-paint-api, css-env-function
"""

import pytest


class TestContainerQueries:
    """Tests for container queries detection."""

    def test_container_at_rule(self, parse_and_check):
        """Test @container rule detection."""
        css = "@container (min-width: 400px) { .card { display: flex; } }"
        assert parse_and_check(css, 'css-container-queries')

    def test_container_type(self, parse_and_check):
        """Test container-type detection."""
        css = ".wrapper { container-type: inline-size; }"
        assert parse_and_check(css, 'css-container-queries')

    def test_container_name(self, parse_and_check):
        """Test container-name detection."""
        css = ".sidebar { container-name: sidebar; }"
        assert parse_and_check(css, 'css-container-queries')


class TestContainerStyleQueries:
    """Tests for container style queries detection."""

    def test_container_style(self, parse_and_check):
        """Test @container style() detection."""
        css = "@container style(--theme: dark) { .card { background: #333; } }"
        assert parse_and_check(css, 'css-container-queries-style')


class TestCSSNesting:
    """Tests for CSS Nesting detection."""

    def test_nesting_ampersand(self, parse_and_check):
        """Test & nesting selector detection."""
        css = ".card { & { padding: 10px; } }"
        assert parse_and_check(css, 'css-nesting')

    def test_nesting_hover(self, parse_and_check):
        """Test &:hover nesting detection."""
        css = ".button { &:hover { background: blue; } }"
        assert parse_and_check(css, 'css-nesting')

    def test_nesting_descendant(self, parse_and_check):
        """Test & descendant nesting detection."""
        css = ".nav { & .item { color: blue; } }"
        assert parse_and_check(css, 'css-nesting')


class TestAnchorPositioning:
    """Tests for anchor positioning detection."""

    def test_anchor_name(self, parse_and_check):
        """Test anchor-name detection."""
        css = ".target { anchor-name: --my-anchor; }"
        assert parse_and_check(css, 'css-anchor-positioning')

    def test_position_anchor(self, parse_and_check):
        """Test position-anchor detection."""
        css = ".tooltip { position-anchor: --my-anchor; }"
        assert parse_and_check(css, 'css-anchor-positioning')

    def test_anchor_function(self, parse_and_check):
        """Test anchor() function detection."""
        css = ".tooltip { top: anchor(bottom); }"
        assert parse_and_check(css, 'css-anchor-positioning')


class TestContainment:
    """Tests for CSS containment detection."""

    def test_contain_layout(self, parse_and_check):
        """Test contain: layout detection."""
        css = ".element { contain: layout; }"
        assert parse_and_check(css, 'css-containment')

    def test_contain_paint(self, parse_and_check):
        """Test contain: paint detection."""
        css = ".element { contain: paint; }"
        assert parse_and_check(css, 'css-containment')

    def test_contain_strict(self, parse_and_check):
        """Test contain: strict detection."""
        css = ".element { contain: strict; }"
        assert parse_and_check(css, 'css-containment')


class TestContentVisibility:
    """Tests for content-visibility detection."""

    def test_content_visibility_auto(self, parse_and_check):
        """Test content-visibility: auto detection."""
        css = ".lazy { content-visibility: auto; }"
        assert parse_and_check(css, 'css-content-visibility')

    def test_content_visibility_hidden(self, parse_and_check):
        """Test content-visibility: hidden detection."""
        css = ".hidden { content-visibility: hidden; }"
        assert parse_and_check(css, 'css-content-visibility')


class TestMotionPaths:
    """Tests for CSS Motion Path detection."""

    def test_offset_path(self, parse_and_check):
        """Test offset-path detection."""
        css = ".animated { offset-path: path('M 0 0 L 100 100'); }"
        assert parse_and_check(css, 'css-motion-paths')

    def test_offset_distance(self, parse_and_check):
        """Test offset-distance detection."""
        css = ".animated { offset-distance: 50%; }"
        assert parse_and_check(css, 'css-motion-paths')

    def test_offset_rotate(self, parse_and_check):
        """Test offset-rotate detection."""
        css = ".animated { offset-rotate: auto 45deg; }"
        assert parse_and_check(css, 'css-motion-paths')


class TestCSSShapes:
    """Tests for CSS Shapes detection."""

    def test_shape_outside(self, parse_and_check):
        """Test shape-outside detection."""
        css = ".float { shape-outside: circle(50%); }"
        assert parse_and_check(css, 'css-shapes')

    def test_shape_margin(self, parse_and_check):
        """Test shape-margin detection."""
        css = ".float { shape-margin: 10px; }"
        assert parse_and_check(css, 'css-shapes')

    def test_circle_function(self, parse_and_check):
        """Test circle() function detection."""
        css = ".element { shape-outside: circle(50% at center); }"
        assert parse_and_check(css, 'css-shapes')

    def test_polygon_function(self, parse_and_check):
        """Test polygon() function detection."""
        css = ".element { shape-outside: polygon(0 0, 100% 0, 100% 100%); }"
        assert parse_and_check(css, 'css-shapes')


class TestCSSMasks:
    """Tests for CSS Masks detection."""

    def test_mask(self, parse_and_check):
        """Test mask property detection."""
        css = ".element { mask: url(mask.svg); }"
        assert parse_and_check(css, 'css-masks')

    def test_mask_image(self, parse_and_check):
        """Test mask-image detection."""
        css = ".element { mask-image: linear-gradient(black, transparent); }"
        assert parse_and_check(css, 'css-masks')

    def test_mask_border(self, parse_and_check):
        """Test mask-border detection."""
        css = ".element { mask-border: url(border-mask.png) 30 round; }"
        assert parse_and_check(css, 'css-masks')


class TestClipPath:
    """Tests for clip-path detection."""

    def test_clip_path(self, parse_and_check):
        """Test clip-path detection."""
        css = ".element { clip-path: circle(50%); }"
        assert parse_and_check(css, 'css-clip-path')

    def test_clip_path_polygon(self, parse_and_check):
        """Test clip-path with polygon detection."""
        css = ".element { clip-path: polygon(50% 0%, 0% 100%, 100% 100%); }"
        assert parse_and_check(css, 'css-clip-path')

    def test_clip_path_url(self, parse_and_check):
        """Test clip-path with url detection."""
        css = ".element { clip-path: url(#myClip); }"
        assert parse_and_check(css, 'css-clip-path')


class TestLogicalProperties:
    """Tests for CSS Logical Properties detection."""

    def test_margin_inline(self, parse_and_check):
        """Test margin-inline detection."""
        css = ".element { margin-inline: auto; }"
        assert parse_and_check(css, 'css-logical-props')

    def test_padding_block(self, parse_and_check):
        """Test padding-block detection."""
        css = ".element { padding-block: 20px; }"
        assert parse_and_check(css, 'css-logical-props')

    def test_inset_inline(self, parse_and_check):
        """Test inset-inline detection."""
        css = ".element { inset-inline: 0; }"
        assert parse_and_check(css, 'css-logical-props')


class TestViewTransitions:
    """Tests for View Transitions detection."""

    def test_view_transition_pseudo(self, parse_and_check):
        """Test ::view-transition-old pseudo-element detection."""
        css = "::view-transition-old(root) { animation: fade-out 0.5s; }"
        assert parse_and_check(css, 'view-transitions')

    def test_view_transition_new(self, parse_and_check):
        """Test ::view-transition-new pseudo-element detection."""
        css = "::view-transition-new(root) { animation: fade-in 0.5s; }"
        assert parse_and_check(css, 'view-transitions')


class TestCrossDocumentViewTransitions:
    """Tests for cross-document view transitions detection."""

    def test_view_transition_at_rule(self, parse_and_check):
        """Test @view-transition rule detection."""
        css = "@view-transition { navigation: auto; }"
        assert parse_and_check(css, 'cross-document-view-transitions')

    def test_view_transition_name(self, parse_and_check):
        """Test view-transition-name detection."""
        css = ".header { view-transition-name: header; }"
        assert parse_and_check(css, 'cross-document-view-transitions')


class TestPaintAPI:
    """Tests for CSS Paint API detection."""

    def test_paint_function(self, parse_and_check):
        """Test paint() function detection."""
        css = ".element { background-image: paint(myPainter); }"
        assert parse_and_check(css, 'css-paint-api')


class TestEnvFunction:
    """Tests for env() function detection."""

    def test_env_safe_area_inset(self, parse_and_check):
        """Test env(safe-area-inset-*) detection."""
        css = ".element { padding-top: env(safe-area-inset-top); }"
        assert parse_and_check(css, 'css-env-function')

    def test_env_with_fallback(self, parse_and_check):
        """Test env() with fallback detection."""
        css = ".element { padding: env(safe-area-inset-top, 20px); }"
        assert parse_and_check(css, 'css-env-function')
