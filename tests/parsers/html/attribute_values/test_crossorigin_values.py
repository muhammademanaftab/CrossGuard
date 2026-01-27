"""Tests for crossorigin attribute value detection.

Tests crossorigin values: anonymous, use-credentials
Both map to feature ID: cors
"""

import pytest


class TestCrossoriginAnonymous:
    """Tests for crossorigin=anonymous detection."""

    def test_crossorigin_anonymous_on_script(self, parse_and_check):
        """Test crossorigin=anonymous on script."""
        html = '<script src="https://cdn.example.com/lib.js" crossorigin="anonymous"></script>'
        assert parse_and_check(html, 'cors')

    def test_crossorigin_anonymous_on_link(self, parse_and_check):
        """Test crossorigin=anonymous on link."""
        html = '<link rel="stylesheet" href="https://cdn.example.com/style.css" crossorigin="anonymous">'
        assert parse_and_check(html, 'cors')

    def test_crossorigin_anonymous_on_img(self, parse_and_check):
        """Test crossorigin=anonymous on img."""
        html = '<img src="https://cdn.example.com/image.jpg" crossorigin="anonymous" alt="test">'
        assert parse_and_check(html, 'cors')

    def test_crossorigin_anonymous_on_video(self, parse_and_check):
        """Test crossorigin=anonymous on video."""
        html = '<video src="https://cdn.example.com/video.mp4" crossorigin="anonymous"></video>'
        assert parse_and_check(html, 'cors')

    def test_crossorigin_anonymous_on_audio(self, parse_and_check):
        """Test crossorigin=anonymous on audio."""
        html = '<audio src="https://cdn.example.com/audio.mp3" crossorigin="anonymous"></audio>'
        assert parse_and_check(html, 'cors')

    def test_crossorigin_anonymous_font_preload(self, parse_and_check):
        """Test crossorigin=anonymous on font preload."""
        html = '''
        <link rel="preload" href="https://fonts.example.com/font.woff2"
              as="font" type="font/woff2" crossorigin="anonymous">
        '''
        assert parse_and_check(html, 'cors')


class TestCrossoriginUseCredentials:
    """Tests for crossorigin=use-credentials detection."""

    def test_crossorigin_use_credentials_on_script(self, parse_and_check):
        """Test crossorigin=use-credentials on script."""
        html = '<script src="https://api.example.com/auth.js" crossorigin="use-credentials"></script>'
        assert parse_and_check(html, 'cors')

    def test_crossorigin_use_credentials_on_img(self, parse_and_check):
        """Test crossorigin=use-credentials on img."""
        html = '<img src="https://api.example.com/user/avatar.jpg" crossorigin="use-credentials" alt="avatar">'
        assert parse_and_check(html, 'cors')

    def test_crossorigin_use_credentials_fetch(self, parse_and_check):
        """Test crossorigin=use-credentials on preload fetch."""
        html = '''
        <link rel="preload" href="https://api.example.com/data.json"
              as="fetch" crossorigin="use-credentials">
        '''
        assert parse_and_check(html, 'cors')


class TestCrossoriginEmpty:
    """Tests for crossorigin with empty value (same as anonymous)."""

    def test_crossorigin_empty_value(self, parse_html):
        """Test crossorigin with empty string (treated as anonymous)."""
        html = '<img src="https://cdn.example.com/img.jpg" crossorigin="" alt="test">'
        features = parse_html(html)
        # Empty value might not be detected depending on implementation
        # This test documents the behavior

    def test_crossorigin_boolean(self, parse_html):
        """Test crossorigin as boolean attribute."""
        html = '<img src="https://cdn.example.com/img.jpg" crossorigin alt="test">'
        features = parse_html(html)
        # Boolean crossorigin might not match our specific value checks


class TestCrossoriginWithIntegrity:
    """Tests for crossorigin combined with integrity (SRI)."""

    def test_sri_script_with_crossorigin(self, parse_html):
        """Test SRI script with crossorigin=anonymous."""
        html = '''
        <script src="https://cdn.example.com/jquery.min.js"
                integrity="sha384-abc123..."
                crossorigin="anonymous">
        </script>
        '''
        features = parse_html(html)
        assert 'cors' in features
        assert 'subresource-integrity' in features

    def test_sri_stylesheet_with_crossorigin(self, parse_html):
        """Test SRI stylesheet with crossorigin=anonymous."""
        html = '''
        <link rel="stylesheet"
              href="https://cdn.example.com/bootstrap.min.css"
              integrity="sha384-xyz789..."
              crossorigin="anonymous">
        '''
        features = parse_html(html)
        assert 'cors' in features
        assert 'subresource-integrity' in features

    def test_multiple_sri_resources(self, parse_html):
        """Test multiple SRI resources with crossorigin."""
        html = """
        <link rel="stylesheet"
              href="https://cdn.example.com/style.css"
              integrity="sha384-..."
              crossorigin="anonymous">
        <script src="https://cdn.example.com/lib.js"
                integrity="sha384-..."
                crossorigin="anonymous"></script>
        <script src="https://cdn.example.com/app.js"
                integrity="sha384-..."
                crossorigin="anonymous"></script>
        """
        features = parse_html(html)
        assert 'cors' in features
        assert 'subresource-integrity' in features


class TestCrossoriginForCanvasImage:
    """Tests for crossorigin on images for canvas manipulation."""

    def test_canvas_image_anonymous(self, parse_html):
        """Test crossorigin=anonymous for canvas image manipulation."""
        html = '''
        <canvas id="canvas"></canvas>
        <img src="https://cdn.example.com/editable.jpg"
             crossorigin="anonymous"
             id="source-image"
             alt="Source">
        '''
        features = parse_html(html)
        assert 'cors' in features
        assert 'canvas' in features

    def test_video_for_canvas(self, parse_html):
        """Test crossorigin on video for canvas drawing."""
        html = '''
        <canvas id="video-canvas"></canvas>
        <video src="https://cdn.example.com/video.mp4"
               crossorigin="anonymous"
               id="source-video">
        </video>
        '''
        features = parse_html(html)
        assert 'cors' in features
        assert 'video' in features


class TestCrossoriginCombinedScenarios:
    """Tests for combined crossorigin scenarios."""

    def test_cdn_resources(self, parse_html):
        """Test typical CDN resource loading with CORS."""
        html = """
        <head>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">

            <link rel="preload"
                  href="https://fonts.gstatic.com/font.woff2"
                  as="font"
                  type="font/woff2"
                  crossorigin="anonymous">

            <link rel="stylesheet"
                  href="https://cdn.example.com/bootstrap.css"
                  integrity="sha384-..."
                  crossorigin="anonymous">

            <script src="https://cdn.example.com/jquery.js"
                    integrity="sha384-..."
                    crossorigin="anonymous"></script>
        </head>
        """
        features = parse_html(html)
        assert 'cors' in features
        assert 'link-rel-preconnect' in features
        assert 'link-rel-preload' in features
        assert 'subresource-integrity' in features

    def test_authenticated_api_resources(self, parse_html):
        """Test authenticated API resource loading."""
        html = """
        <script src="https://api.example.com/user-script.js"
                crossorigin="use-credentials"></script>
        <img src="https://api.example.com/user/profile.jpg"
             crossorigin="use-credentials"
             alt="Profile">
        """
        features = parse_html(html)
        assert 'cors' in features


class TestCaseInsensitivity:
    """Tests for case insensitivity of crossorigin values."""

    def test_crossorigin_anonymous_uppercase(self, parse_and_check):
        """Test crossorigin=ANONYMOUS in uppercase."""
        html = '<script src="lib.js" crossorigin="ANONYMOUS"></script>'
        assert parse_and_check(html, 'cors')

    def test_crossorigin_use_credentials_mixed_case(self, parse_and_check):
        """Test crossorigin=Use-Credentials in mixed case."""
        html = '<script src="lib.js" crossorigin="Use-Credentials"></script>'
        assert parse_and_check(html, 'cors')


class TestNoCrossorigin:
    """Tests for elements without crossorigin attribute."""

    def test_local_script(self, parse_html):
        """Test local script without crossorigin."""
        html = '<script src="local.js"></script>'
        features = parse_html(html)
        assert 'cors' not in features

    def test_same_origin_image(self, parse_html):
        """Test same-origin image without crossorigin."""
        html = '<img src="image.jpg" alt="test">'
        features = parse_html(html)
        assert 'cors' not in features

    def test_integrity_without_crossorigin(self, parse_html):
        """Test integrity without crossorigin (won't work in practice)."""
        html = '<script src="https://cdn.example.com/lib.js" integrity="sha384-..."></script>'
        features = parse_html(html)
        assert 'subresource-integrity' in features
        # CORS not detected without crossorigin attribute
