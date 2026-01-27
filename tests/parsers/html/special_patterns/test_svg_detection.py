"""Tests for SVG-related pattern detection.

Tests patterns: svg-img (.svg in src), svg-fragment (#id references)
"""

import pytest


class TestSvgInImg:
    """Tests for SVG image detection (svg-img)."""

    def test_svg_in_img_src(self, parse_and_check):
        """Test SVG file in img src."""
        html = '<img src="icon.svg" alt="Icon">'
        assert parse_and_check(html, 'svg-img')

    def test_svg_in_img_src_with_path(self, parse_and_check):
        """Test SVG with path in img src."""
        html = '<img src="/images/logo.svg" alt="Logo">'
        assert parse_and_check(html, 'svg-img')

    def test_svg_in_img_src_absolute_url(self, parse_and_check):
        """Test SVG with absolute URL in img src."""
        html = '<img src="https://example.com/images/icon.svg" alt="Icon">'
        assert parse_and_check(html, 'svg-img')

    def test_svg_in_img_src_with_query(self, parse_and_check):
        """Test SVG with query string in img src."""
        html = '<img src="icon.svg?v=1.2.3" alt="Icon">'
        assert parse_and_check(html, 'svg-img')

    def test_svg_in_picture_source(self, parse_and_check):
        """Test SVG in picture source srcset."""
        html = """
        <picture>
            <source srcset="icon.svg" type="image/svg+xml">
            <img src="icon.png" alt="Icon">
        </picture>
        """
        assert parse_and_check(html, 'svg-img')

    def test_svg_case_insensitive(self, parse_and_check):
        """Test SVG extension case insensitivity."""
        html = '<img src="icon.SVG" alt="Icon">'
        assert parse_and_check(html, 'svg-img')

    def test_svg_mixed_case(self, parse_and_check):
        """Test SVG extension mixed case."""
        html = '<img src="icon.Svg" alt="Icon">'
        assert parse_and_check(html, 'svg-img')

    def test_multiple_svg_images(self, parse_html):
        """Test multiple SVG images."""
        html = """
        <img src="logo.svg" alt="Logo">
        <img src="icon-home.svg" alt="Home">
        <img src="icon-settings.svg" alt="Settings">
        """
        features = parse_html(html)
        assert 'svg-img' in features


class TestSvgFragments:
    """Tests for SVG fragment identifier detection."""

    def test_svg_fragment_in_use_href(self, parse_and_check):
        """Test SVG fragment in use element href."""
        html = """
        <svg>
            <use href="#icon-home"></use>
        </svg>
        """
        assert parse_and_check(html, 'svg-fragment')

    def test_svg_fragment_in_use_xlink_href(self, parse_and_check):
        """Test SVG fragment in use element xlink:href."""
        html = """
        <svg>
            <use xlink:href="#icon-menu"></use>
        </svg>
        """
        assert parse_and_check(html, 'svg-fragment')

    def test_svg_fragment_external_file(self, parse_and_check):
        """Test SVG fragment with external file reference."""
        html = """
        <svg>
            <use href="icons.svg#home"></use>
        </svg>
        """
        assert parse_and_check(html, 'svg-fragment')

    def test_svg_fragment_in_img(self, parse_and_check):
        """Test SVG fragment in img src."""
        html = '<img src="sprites.svg#icon-user" alt="User">'
        assert parse_and_check(html, 'svg-fragment')

    def test_svg_fragment_absolute_url(self, parse_and_check):
        """Test SVG fragment with absolute URL."""
        html = """
        <svg>
            <use href="https://cdn.example.com/icons.svg#logo"></use>
        </svg>
        """
        assert parse_and_check(html, 'svg-fragment')


class TestSvgSpritePatterns:
    """Tests for common SVG sprite patterns."""

    def test_icon_system(self, parse_html):
        """Test SVG icon system with use elements."""
        html = """
        <nav>
            <a href="/">
                <svg class="icon"><use href="#icon-home"></use></svg>
                Home
            </a>
            <a href="/settings">
                <svg class="icon"><use href="#icon-settings"></use></svg>
                Settings
            </a>
            <a href="/profile">
                <svg class="icon"><use href="#icon-user"></use></svg>
                Profile
            </a>
        </nav>
        """
        features = parse_html(html)
        assert 'svg-fragment' in features
        assert 'svg' in features

    def test_external_sprite(self, parse_html):
        """Test external SVG sprite."""
        html = """
        <div class="icons">
            <svg><use href="sprites.svg#check"></use></svg>
            <svg><use href="sprites.svg#close"></use></svg>
            <svg><use href="sprites.svg#menu"></use></svg>
        </div>
        """
        features = parse_html(html)
        assert 'svg-fragment' in features
        assert 'svg' in features

    def test_symbol_definitions(self, parse_html):
        """Test SVG with symbol definitions and use."""
        html = """
        <svg style="display: none;">
            <symbol id="icon-star" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87..."/>
            </symbol>
            <symbol id="icon-heart" viewBox="0 0 24 24">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36..."/>
            </symbol>
        </svg>

        <svg class="icon"><use href="#icon-star"></use></svg>
        <svg class="icon"><use href="#icon-heart"></use></svg>
        """
        features = parse_html(html)
        assert 'svg-fragment' in features
        assert 'svg' in features


class TestCombinedSvgPatterns:
    """Tests for combined SVG patterns."""

    def test_svg_img_and_inline(self, parse_html):
        """Test page with both SVG img and inline SVG."""
        html = """
        <header>
            <img src="logo.svg" alt="Logo">
        </header>
        <main>
            <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10"/>
            </svg>
        </main>
        """
        features = parse_html(html)
        assert 'svg-img' in features
        assert 'svg' in features

    def test_svg_all_patterns(self, parse_html):
        """Test page with all SVG patterns."""
        html = """
        <!-- SVG as img -->
        <img src="hero.svg" alt="Hero">

        <!-- Inline SVG -->
        <svg viewBox="0 0 100 100">
            <rect width="100" height="100"/>
        </svg>

        <!-- SVG sprite with fragments -->
        <svg class="icon">
            <use href="icons.svg#menu"></use>
        </svg>
        """
        features = parse_html(html)
        assert 'svg-img' in features
        assert 'svg' in features
        assert 'svg-fragment' in features

    def test_svg_favicon(self, parse_html):
        """Test SVG favicon."""
        html = """
        <head>
            <link rel="icon" type="image/svg+xml" href="favicon.svg">
        </head>
        """
        features = parse_html(html)
        assert 'link-icon-svg' in features


class TestNoSvgPatterns:
    """Tests for HTML without SVG patterns."""

    def test_png_img(self, parse_html):
        """Test PNG image (not SVG)."""
        html = '<img src="image.png" alt="test">'
        features = parse_html(html)
        assert 'svg-img' not in features

    def test_jpg_img(self, parse_html):
        """Test JPG image (not SVG)."""
        html = '<img src="photo.jpg" alt="test">'
        features = parse_html(html)
        assert 'svg-img' not in features

    def test_inline_svg_without_use(self, parse_html):
        """Test inline SVG without use/fragments."""
        html = """
        <svg viewBox="0 0 24 24">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
        </svg>
        """
        features = parse_html(html)
        assert 'svg' in features
        assert 'svg-fragment' not in features

    def test_svg_in_text_not_detected(self, parse_html):
        """Test that .svg in text doesn't trigger detection."""
        html = '<p>Download the file icon.svg from the server.</p>'
        features = parse_html(html)
        # Text content shouldn't be detected as svg-img
        assert 'svg-img' not in features
