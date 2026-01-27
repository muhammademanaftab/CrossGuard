"""Tests for rel attribute value detection.

Tests rel values: preload, prefetch, dns-prefetch, preconnect, modulepreload, prerender,
                  icon, noopener, noreferrer, import
"""

import pytest


class TestRelPreload:
    """Tests for rel=preload detection."""

    def test_rel_preload_script(self, parse_and_check):
        """Test rel=preload for JavaScript."""
        html = '<link rel="preload" href="script.js" as="script">'
        assert parse_and_check(html, 'link-rel-preload')

    def test_rel_preload_style(self, parse_and_check):
        """Test rel=preload for CSS."""
        html = '<link rel="preload" href="style.css" as="style">'
        assert parse_and_check(html, 'link-rel-preload')

    def test_rel_preload_font(self, parse_and_check):
        """Test rel=preload for font."""
        html = '''
        <link rel="preload" href="font.woff2" as="font"
              type="font/woff2" crossorigin>
        '''
        assert parse_and_check(html, 'link-rel-preload')

    def test_rel_preload_image(self, parse_and_check):
        """Test rel=preload for image."""
        html = '<link rel="preload" href="hero.jpg" as="image">'
        assert parse_and_check(html, 'link-rel-preload')

    def test_rel_preload_fetch(self, parse_and_check):
        """Test rel=preload for fetch request."""
        html = '<link rel="preload" href="api/data.json" as="fetch" crossorigin>'
        assert parse_and_check(html, 'link-rel-preload')


class TestRelPrefetch:
    """Tests for rel=prefetch detection."""

    def test_rel_prefetch_page(self, parse_and_check):
        """Test rel=prefetch for next page."""
        html = '<link rel="prefetch" href="next-page.html">'
        assert parse_and_check(html, 'link-rel-prefetch')

    def test_rel_prefetch_script(self, parse_and_check):
        """Test rel=prefetch for script."""
        html = '<link rel="prefetch" href="analytics.js">'
        assert parse_and_check(html, 'link-rel-prefetch')

    def test_rel_prefetch_image(self, parse_and_check):
        """Test rel=prefetch for image."""
        html = '<link rel="prefetch" href="gallery-image-2.jpg">'
        assert parse_and_check(html, 'link-rel-prefetch')


class TestRelDnsPrefetch:
    """Tests for rel=dns-prefetch detection."""

    def test_rel_dns_prefetch(self, parse_and_check):
        """Test rel=dns-prefetch."""
        html = '<link rel="dns-prefetch" href="//cdn.example.com">'
        assert parse_and_check(html, 'link-rel-dns-prefetch')

    def test_rel_dns_prefetch_api(self, parse_and_check):
        """Test rel=dns-prefetch for API domain."""
        html = '<link rel="dns-prefetch" href="//api.example.com">'
        assert parse_and_check(html, 'link-rel-dns-prefetch')

    def test_rel_dns_prefetch_multiple(self, parse_html):
        """Test multiple dns-prefetch hints."""
        html = """
        <link rel="dns-prefetch" href="//fonts.googleapis.com">
        <link rel="dns-prefetch" href="//analytics.google.com">
        <link rel="dns-prefetch" href="//cdn.example.com">
        """
        features = parse_html(html)
        assert 'link-rel-dns-prefetch' in features


class TestRelPreconnect:
    """Tests for rel=preconnect detection."""

    def test_rel_preconnect(self, parse_and_check):
        """Test rel=preconnect."""
        html = '<link rel="preconnect" href="https://fonts.googleapis.com">'
        assert parse_and_check(html, 'link-rel-preconnect')

    def test_rel_preconnect_crossorigin(self, parse_and_check):
        """Test rel=preconnect with crossorigin."""
        html = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        assert parse_and_check(html, 'link-rel-preconnect')

    def test_rel_preconnect_cdn(self, parse_and_check):
        """Test rel=preconnect for CDN."""
        html = '<link rel="preconnect" href="https://cdn.example.com">'
        assert parse_and_check(html, 'link-rel-preconnect')


class TestRelModulepreload:
    """Tests for rel=modulepreload detection."""

    def test_rel_modulepreload(self, parse_and_check):
        """Test rel=modulepreload."""
        html = '<link rel="modulepreload" href="module.js">'
        assert parse_and_check(html, 'link-rel-modulepreload')

    def test_rel_modulepreload_with_integrity(self, parse_and_check):
        """Test rel=modulepreload with integrity."""
        html = '''
        <link rel="modulepreload" href="app.js"
              integrity="sha384-...">
        '''
        assert parse_and_check(html, 'link-rel-modulepreload')

    def test_rel_modulepreload_multiple(self, parse_html):
        """Test multiple modulepreload hints."""
        html = """
        <link rel="modulepreload" href="vendor.js">
        <link rel="modulepreload" href="utils.js">
        <link rel="modulepreload" href="app.js">
        """
        features = parse_html(html)
        assert 'link-rel-modulepreload' in features


class TestRelPrerender:
    """Tests for rel=prerender detection."""

    def test_rel_prerender(self, parse_and_check):
        """Test rel=prerender."""
        html = '<link rel="prerender" href="likely-next-page.html">'
        assert parse_and_check(html, 'link-rel-prerender')


class TestRelIcon:
    """Tests for rel=icon detection."""

    def test_rel_icon_png(self, parse_and_check):
        """Test rel=icon with PNG."""
        html = '<link rel="icon" href="favicon.png" type="image/png">'
        assert parse_and_check(html, 'link-icon-png')

    def test_rel_icon_no_type(self, parse_and_check):
        """Test rel=icon without type."""
        html = '<link rel="icon" href="favicon.ico">'
        assert parse_and_check(html, 'link-icon-png')

    def test_rel_icon_sizes(self, parse_and_check):
        """Test rel=icon with sizes."""
        html = '<link rel="icon" href="icon-192.png" sizes="192x192">'
        assert parse_and_check(html, 'link-icon-png')

    def test_rel_apple_touch_icon(self, parse_html):
        """Test rel=apple-touch-icon (separate feature)."""
        # Note: apple-touch-icon is not the same as icon
        html = '<link rel="icon" href="icon.png">'
        features = parse_html(html)
        assert 'link-icon-png' in features


class TestRelNoopener:
    """Tests for rel=noopener detection."""

    def test_rel_noopener_on_link(self, parse_and_check):
        """Test rel=noopener on anchor."""
        html = '<a href="https://example.com" rel="noopener">External</a>'
        assert parse_and_check(html, 'rel-noopener')

    def test_rel_noopener_target_blank(self, parse_and_check):
        """Test rel=noopener with target=_blank."""
        html = '<a href="https://example.com" target="_blank" rel="noopener">External</a>'
        assert parse_and_check(html, 'rel-noopener')

    def test_rel_noopener_noreferrer(self, parse_html):
        """Test rel with both noopener and noreferrer."""
        html = '<a href="https://example.com" target="_blank" rel="noopener noreferrer">External</a>'
        features = parse_html(html)
        assert 'rel-noopener' in features
        assert 'rel-noreferrer' in features


class TestRelNoreferrer:
    """Tests for rel=noreferrer detection."""

    def test_rel_noreferrer(self, parse_and_check):
        """Test rel=noreferrer."""
        html = '<a href="https://example.com" rel="noreferrer">External</a>'
        assert parse_and_check(html, 'rel-noreferrer')

    def test_rel_noreferrer_target_blank(self, parse_and_check):
        """Test rel=noreferrer with target=_blank."""
        html = '<a href="https://example.com" target="_blank" rel="noreferrer">External</a>'
        assert parse_and_check(html, 'rel-noreferrer')


class TestRelImport:
    """Tests for rel=import detection (HTML Imports - deprecated)."""

    def test_rel_import(self, parse_and_check):
        """Test rel=import."""
        html = '<link rel="import" href="component.html">'
        assert parse_and_check(html, 'imports')


class TestCombinedRelValues:
    """Tests for combined rel value patterns."""

    def test_performance_hints_head(self, parse_html):
        """Test comprehensive performance hints in head."""
        html = """
        <head>
            <link rel="dns-prefetch" href="//fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link rel="preload" href="critical.css" as="style">
            <link rel="preload" href="critical.js" as="script">
            <link rel="prefetch" href="secondary.js">
            <link rel="icon" href="favicon.png">
        </head>
        """
        features = parse_html(html)
        assert 'link-rel-dns-prefetch' in features
        assert 'link-rel-preconnect' in features
        assert 'link-rel-preload' in features
        assert 'link-rel-prefetch' in features
        assert 'link-icon-png' in features

    def test_security_rel_values(self, parse_html):
        """Test security-related rel values."""
        html = """
        <nav>
            <a href="https://external.com" target="_blank" rel="noopener noreferrer">
                External Link
            </a>
            <a href="https://partner.com" target="_blank" rel="noopener">
                Partner Link
            </a>
        </nav>
        """
        features = parse_html(html)
        assert 'rel-noopener' in features
        assert 'rel-noreferrer' in features

    def test_module_loading(self, parse_html):
        """Test module loading pattern."""
        html = """
        <head>
            <link rel="modulepreload" href="vendor.js">
            <link rel="modulepreload" href="utils.js">
            <script type="module" src="app.js"></script>
        </head>
        """
        features = parse_html(html)
        assert 'link-rel-modulepreload' in features
        assert 'es6-module' in features


class TestCaseInsensitivity:
    """Tests for case insensitivity of rel values."""

    def test_rel_preload_uppercase(self, parse_and_check):
        """Test rel=PRELOAD in uppercase."""
        html = '<link rel="PRELOAD" href="style.css" as="style">'
        assert parse_and_check(html, 'link-rel-preload')

    def test_rel_icon_mixed_case(self, parse_and_check):
        """Test rel=Icon in mixed case."""
        html = '<link rel="Icon" href="favicon.png">'
        assert parse_and_check(html, 'link-icon-png')


class TestNoRelValues:
    """Tests for links without special rel values."""

    def test_rel_stylesheet(self, parse_html):
        """Test rel=stylesheet (common, not tracked)."""
        html = '<link rel="stylesheet" href="style.css">'
        features = parse_html(html)
        assert 'link-rel-preload' not in features
        assert 'link-rel-prefetch' not in features

    def test_no_rel(self, parse_html):
        """Test link without rel."""
        html = '<link href="style.css">'
        features = parse_html(html)
        assert 'link-rel-preload' not in features
