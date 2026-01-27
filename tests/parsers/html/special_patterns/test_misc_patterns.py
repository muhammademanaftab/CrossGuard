"""Tests for miscellaneous pattern detection.

Tests patterns: datauri, xhtml detection, meta theme-color, fieldset-disabled
"""

import pytest


class TestDataURIs:
    """Tests for data URI detection."""

    def test_data_uri_in_img_src(self, parse_and_check):
        """Test data URI in img src."""
        html = '<img src="data:image/png;base64,iVBORw0KGgo..." alt="test">'
        assert parse_and_check(html, 'datauri')

    def test_data_uri_svg(self, parse_and_check):
        """Test data URI with SVG."""
        html = '<img src="data:image/svg+xml,<svg>...</svg>" alt="icon">'
        assert parse_and_check(html, 'datauri')

    def test_data_uri_in_href(self, parse_and_check):
        """Test data URI in anchor href."""
        html = '<a href="data:text/html,<h1>Hello</h1>" target="_blank">Open</a>'
        assert parse_and_check(html, 'datauri')

    def test_data_uri_in_object_data(self, parse_and_check):
        """Test data URI in object data attribute."""
        html = '<object data="data:application/pdf;base64,..." type="application/pdf"></object>'
        assert parse_and_check(html, 'datauri')

    def test_data_uri_in_video_poster(self, parse_and_check):
        """Test data URI in video poster."""
        html = '<video poster="data:image/jpeg;base64,..." src="video.mp4"></video>'
        assert parse_and_check(html, 'datauri')

    def test_data_uri_in_srcset(self, parse_and_check):
        """Test data URI in srcset."""
        html = '<img src="placeholder.jpg" srcset="data:image/png;base64,... 1x" alt="test">'
        assert parse_and_check(html, 'datauri')

    def test_data_uri_case_insensitive(self, parse_and_check):
        """Test data URI detection is case insensitive."""
        html = '<img src="DATA:image/png;base64,..." alt="test">'
        assert parse_and_check(html, 'datauri')


class TestXHTMLDetection:
    """Tests for XHTML namespace detection."""

    def test_xhtml_namespace(self, parse_and_check):
        """Test XHTML namespace in html element."""
        html = '<html xmlns="http://www.w3.org/1999/xhtml"><body></body></html>'
        assert parse_and_check(html, 'xhtml')

    def test_xhtml_full_namespace(self, parse_and_check):
        """Test full XHTML namespace declaration."""
        html = '''
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head><title>Test</title></head>
            <body></body>
        </html>
        '''
        assert parse_and_check(html, 'xhtml')

    def test_no_xhtml_namespace(self, parse_html):
        """Test HTML without XHTML namespace."""
        html = '<html><head></head><body></body></html>'
        features = parse_html(html)
        assert 'xhtml' not in features


class TestMetaThemeColor:
    """Tests for meta theme-color detection."""

    def test_meta_theme_color(self, parse_and_check):
        """Test meta theme-color."""
        html = '<meta name="theme-color" content="#4285f4">'
        assert parse_and_check(html, 'meta-theme-color')

    def test_meta_theme_color_with_media(self, parse_and_check):
        """Test meta theme-color with media query."""
        html = '<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">'
        assert parse_and_check(html, 'meta-theme-color')

    def test_meta_theme_color_dark_mode(self, parse_html):
        """Test multiple theme-color for light/dark modes."""
        html = """
        <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
        <meta name="theme-color" content="#1a1a1a" media="(prefers-color-scheme: dark)">
        """
        features = parse_html(html)
        assert 'meta-theme-color' in features

    def test_meta_theme_color_rgb(self, parse_and_check):
        """Test meta theme-color with RGB value."""
        html = '<meta name="theme-color" content="rgb(66, 133, 244)">'
        assert parse_and_check(html, 'meta-theme-color')


class TestFieldsetDisabled:
    """Tests for fieldset disabled attribute detection."""

    def test_fieldset_disabled(self, parse_and_check):
        """Test fieldset with disabled attribute."""
        html = """
        <fieldset disabled>
            <legend>Disabled Section</legend>
            <input type="text" name="field">
            <button>Submit</button>
        </fieldset>
        """
        assert parse_and_check(html, 'fieldset-disabled')

    def test_fieldset_disabled_with_value(self, parse_and_check):
        """Test fieldset with disabled="disabled"."""
        html = """
        <fieldset disabled="disabled">
            <input type="text">
        </fieldset>
        """
        assert parse_and_check(html, 'fieldset-disabled')

    def test_fieldset_not_disabled(self, parse_html):
        """Test fieldset without disabled attribute."""
        html = """
        <fieldset>
            <legend>Active Section</legend>
            <input type="text">
        </fieldset>
        """
        features = parse_html(html)
        assert 'fieldset-disabled' not in features

    def test_nested_fieldset_disabled(self, parse_html):
        """Test nested fieldsets with disabled."""
        html = """
        <fieldset>
            <legend>Outer</legend>
            <fieldset disabled>
                <legend>Inner Disabled</legend>
                <input type="text">
            </fieldset>
        </fieldset>
        """
        features = parse_html(html)
        assert 'fieldset-disabled' in features


class TestMetaViewport:
    """Tests for meta viewport detection."""

    def test_meta_viewport(self, parse_and_check):
        """Test meta viewport."""
        html = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        assert parse_and_check(html, 'viewport-units')

    def test_meta_viewport_simple(self, parse_and_check):
        """Test simple meta viewport."""
        html = '<meta name="viewport" content="width=device-width">'
        assert parse_and_check(html, 'viewport-units')

    def test_meta_viewport_complex(self, parse_and_check):
        """Test complex meta viewport."""
        html = '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">'
        assert parse_and_check(html, 'viewport-units')


class TestCombinedMiscPatterns:
    """Tests for combined miscellaneous patterns."""

    def test_pwa_head(self, parse_html):
        """Test PWA-style head with meta tags."""
        html = """
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="theme-color" content="#4285f4">
            <link rel="icon" type="image/svg+xml" href="icon.svg">
            <link rel="manifest" href="manifest.json">
        </head>
        """
        features = parse_html(html)
        assert 'viewport-units' in features
        assert 'meta-theme-color' in features
        assert 'link-icon-svg' in features

    def test_inline_images_page(self, parse_html):
        """Test page with data URI images."""
        html = """
        <body>
            <img src="data:image/png;base64,iVBORw0KGgo..." alt="Logo">
            <img src="data:image/svg+xml,<svg>...</svg>" alt="Icon">
        </body>
        """
        features = parse_html(html)
        assert 'datauri' in features

    def test_xhtml_with_features(self, parse_html):
        """Test XHTML document with various features."""
        html = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta name="theme-color" content="#000" />
        </head>
        <body>
            <main>Content</main>
        </body>
        </html>
        """
        features = parse_html(html)
        assert 'xhtml' in features
        assert 'meta-theme-color' in features
        assert 'html5semantic' in features


class TestNoMiscPatterns:
    """Tests for HTML without miscellaneous patterns."""

    def test_basic_page(self, parse_html):
        """Test basic page without special patterns."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Basic</title></head>
        <body><p>Hello</p></body>
        </html>
        """
        features = parse_html(html)
        assert 'datauri' not in features
        assert 'xhtml' not in features
        assert 'meta-theme-color' not in features
        assert 'fieldset-disabled' not in features
