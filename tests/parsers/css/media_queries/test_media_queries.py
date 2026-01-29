"""Tests for CSS Media Query features.

Tests features: css-mediaqueries, prefers-color-scheme, prefers-reduced-motion,
                css-media-resolution, css-media-range-syntax, css-media-interaction,
                css-media-scripting
"""

import pytest


class TestCSSMediaQueries:
    """Tests for CSS3 Media Queries detection."""

    def test_media_at_rule(self, parse_and_check):
        """Test @media rule detection."""
        css = "@media screen { body { color: black; } }"
        assert parse_and_check(css, 'css-mediaqueries')

    def test_min_width(self, parse_and_check):
        """Test min-width media query detection."""
        css = "@media (min-width: 768px) { .container { width: 750px; } }"
        assert parse_and_check(css, 'css-mediaqueries')

    def test_max_width(self, parse_and_check):
        """Test max-width media query detection."""
        css = "@media (max-width: 480px) { .mobile { display: block; } }"
        assert parse_and_check(css, 'css-mediaqueries')

    def test_combined_media_query(self, parse_and_check):
        """Test combined media query detection."""
        css = "@media screen and (min-width: 768px) and (max-width: 1024px) { .tablet { display: block; } }"
        assert parse_and_check(css, 'css-mediaqueries')


class TestPrefersColorScheme:
    """Tests for prefers-color-scheme detection."""

    def test_prefers_color_scheme_dark(self, parse_and_check):
        """Test prefers-color-scheme: dark detection."""
        css = "@media (prefers-color-scheme: dark) { body { background: #1a1a1a; } }"
        assert parse_and_check(css, 'prefers-color-scheme')

    def test_prefers_color_scheme_light(self, parse_and_check):
        """Test prefers-color-scheme: light detection."""
        css = "@media (prefers-color-scheme: light) { body { background: white; } }"
        assert parse_and_check(css, 'prefers-color-scheme')


class TestPrefersReducedMotion:
    """Tests for prefers-reduced-motion detection."""

    def test_prefers_reduced_motion_reduce(self, parse_and_check):
        """Test prefers-reduced-motion: reduce detection."""
        css = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"
        assert parse_and_check(css, 'prefers-reduced-motion')

    def test_prefers_reduced_motion_no_preference(self, parse_and_check):
        """Test prefers-reduced-motion: no-preference detection."""
        css = "@media (prefers-reduced-motion: no-preference) { .animate { animation: fadeIn 1s; } }"
        assert parse_and_check(css, 'prefers-reduced-motion')


class TestMediaResolution:
    """Tests for resolution media feature detection."""

    def test_min_resolution(self, parse_and_check):
        """Test min-resolution detection."""
        css = "@media (min-resolution: 2dppx) { .retina { background-image: url(img@2x.png); } }"
        assert parse_and_check(css, 'css-media-resolution')

    def test_max_resolution(self, parse_and_check):
        """Test max-resolution detection."""
        css = "@media (max-resolution: 150dpi) { .low-res { background-image: url(img.png); } }"
        assert parse_and_check(css, 'css-media-resolution')


class TestMediaRangeSyntax:
    """Tests for media query range syntax detection."""

    def test_range_less_than(self, parse_and_check):
        """Test range syntax with < operator."""
        css = "@media (width < 600px) { .mobile { display: block; } }"
        assert parse_and_check(css, 'css-media-range-syntax')

    def test_range_greater_than(self, parse_and_check):
        """Test range syntax with > operator."""
        css = "@media (width > 900px) { .desktop { display: block; } }"
        assert parse_and_check(css, 'css-media-range-syntax')

    def test_range_less_equal(self, parse_and_check):
        """Test range syntax with <= operator."""
        css = "@media (width <= 768px) { .tablet { display: block; } }"
        assert parse_and_check(css, 'css-media-range-syntax')

    def test_range_between(self, parse_and_check):
        """Test range syntax with between values."""
        css = "@media (600px <= width <= 900px) { .tablet { display: block; } }"
        assert parse_and_check(css, 'css-media-range-syntax')


class TestMediaInteraction:
    """Tests for interaction media features detection."""

    def test_hover_media(self, parse_and_check):
        """Test hover media feature detection."""
        css = "@media (hover: hover) { .hoverable:hover { background: blue; } }"
        assert parse_and_check(css, 'css-media-interaction')

    def test_pointer_media(self, parse_and_check):
        """Test pointer media feature detection."""
        css = "@media (pointer: coarse) { .button { min-height: 44px; } }"
        assert parse_and_check(css, 'css-media-interaction')

    def test_any_hover(self, parse_and_check):
        """Test any-hover media feature detection."""
        css = "@media (any-hover: hover) { .link:hover { text-decoration: underline; } }"
        assert parse_and_check(css, 'css-media-interaction')

    def test_any_pointer(self, parse_and_check):
        """Test any-pointer media feature detection."""
        css = "@media (any-pointer: fine) { .small-target { padding: 5px; } }"
        assert parse_and_check(css, 'css-media-interaction')


class TestMediaScripting:
    """Tests for scripting media feature detection."""

    def test_scripting_enabled(self, parse_and_check):
        """Test scripting: enabled detection."""
        css = "@media (scripting: enabled) { .js-only { display: block; } }"
        assert parse_and_check(css, 'css-media-scripting')

    def test_scripting_none(self, parse_and_check):
        """Test scripting: none detection."""
        css = "@media (scripting: none) { .noscript { display: block; } }"
        assert parse_and_check(css, 'css-media-scripting')
