"""Tests for HTML5 loading-related attribute detection.

Tests attributes: loading, async, defer, integrity, capture
"""

import pytest


class TestLoadingAttribute:
    """Tests for loading attribute detection."""

    def test_loading_lazy_on_img(self, parse_and_check):
        """Test loading=lazy on img."""
        html = '<img src="image.jpg" loading="lazy" alt="test">'
        assert parse_and_check(html, 'loading-lazy-attr')

    def test_loading_eager_on_img(self, parse_and_check):
        """Test loading=eager on img."""
        html = '<img src="hero.jpg" loading="eager" alt="hero">'
        assert parse_and_check(html, 'loading-lazy-attr')

    def test_loading_lazy_on_iframe(self, parse_and_check):
        """Test loading=lazy on iframe."""
        html = '<iframe src="embed.html" loading="lazy"></iframe>'
        assert parse_and_check(html, 'loading-lazy-attr')

    def test_loading_lazy_gallery(self, parse_and_check):
        """Test loading=lazy in image gallery."""
        html = """
        <div class="gallery">
            <img src="img1.jpg" loading="lazy" alt="Image 1">
            <img src="img2.jpg" loading="lazy" alt="Image 2">
            <img src="img3.jpg" loading="lazy" alt="Image 3">
        </div>
        """
        assert parse_and_check(html, 'loading-lazy-attr')

    def test_loading_mixed(self, parse_html):
        """Test mixed loading values."""
        html = """
        <img src="hero.jpg" loading="eager" alt="Hero">
        <img src="below-fold.jpg" loading="lazy" alt="Below fold">
        """
        features = parse_html(html)
        assert 'loading-lazy-attr' in features


class TestAsyncAttribute:
    """Tests for async attribute detection."""

    def test_async_on_script(self, parse_and_check):
        """Test async attribute on script."""
        html = '<script src="analytics.js" async></script>'
        assert parse_and_check(html, 'script-async')

    def test_async_with_value(self, parse_and_check):
        """Test async with explicit value."""
        html = '<script src="script.js" async="async"></script>'
        assert parse_and_check(html, 'script-async')

    def test_async_multiple_scripts(self, parse_html):
        """Test multiple async scripts."""
        html = """
        <script src="analytics.js" async></script>
        <script src="tracking.js" async></script>
        """
        features = parse_html(html)
        assert 'script-async' in features


class TestDeferAttribute:
    """Tests for defer attribute detection."""

    def test_defer_on_script(self, parse_and_check):
        """Test defer attribute on script."""
        html = '<script src="app.js" defer></script>'
        assert parse_and_check(html, 'script-defer')

    def test_defer_with_value(self, parse_and_check):
        """Test defer with explicit value."""
        html = '<script src="script.js" defer="defer"></script>'
        assert parse_and_check(html, 'script-defer')

    def test_defer_multiple_scripts(self, parse_html):
        """Test multiple deferred scripts."""
        html = """
        <script src="vendor.js" defer></script>
        <script src="app.js" defer></script>
        """
        features = parse_html(html)
        assert 'script-defer' in features


class TestAsyncAndDefer:
    """Tests for async and defer together."""

    def test_async_and_defer_separate(self, parse_html):
        """Test async and defer on separate scripts."""
        html = """
        <script src="analytics.js" async></script>
        <script src="app.js" defer></script>
        """
        features = parse_html(html)
        assert 'script-async' in features
        assert 'script-defer' in features

    def test_realistic_head(self, parse_html):
        """Test realistic head with various script loading."""
        html = """
        <head>
            <script src="critical.js"></script>
            <script src="analytics.js" async></script>
            <script src="vendor.js" defer></script>
            <script src="app.js" defer></script>
        </head>
        """
        features = parse_html(html)
        assert 'script-async' in features
        assert 'script-defer' in features


class TestIntegrityAttribute:
    """Tests for integrity attribute detection (SRI)."""

    def test_integrity_on_script(self, parse_and_check):
        """Test integrity attribute on script."""
        html = '''
        <script src="https://cdn.example.com/lib.js"
                integrity="sha384-abc123..."
                crossorigin="anonymous"></script>
        '''
        assert parse_and_check(html, 'subresource-integrity')

    def test_integrity_on_link(self, parse_and_check):
        """Test integrity attribute on link (CSS)."""
        html = '''
        <link rel="stylesheet"
              href="https://cdn.example.com/style.css"
              integrity="sha384-xyz789..."
              crossorigin="anonymous">
        '''
        assert parse_and_check(html, 'subresource-integrity')

    def test_integrity_sha256(self, parse_and_check):
        """Test integrity with sha256."""
        html = '''
        <script src="lib.js" integrity="sha256-abc123..."></script>
        '''
        assert parse_and_check(html, 'subresource-integrity')

    def test_integrity_sha512(self, parse_and_check):
        """Test integrity with sha512."""
        html = '''
        <script src="lib.js" integrity="sha512-def456..."></script>
        '''
        assert parse_and_check(html, 'subresource-integrity')

    def test_integrity_multiple_hashes(self, parse_and_check):
        """Test integrity with multiple hash algorithms."""
        html = '''
        <script src="lib.js"
                integrity="sha256-abc... sha384-def..."></script>
        '''
        assert parse_and_check(html, 'subresource-integrity')

    def test_integrity_cdn_resources(self, parse_html):
        """Test integrity on multiple CDN resources."""
        html = """
        <link rel="stylesheet"
              href="https://cdn.example.com/bootstrap.css"
              integrity="sha384-..."
              crossorigin="anonymous">
        <script src="https://cdn.example.com/jquery.js"
                integrity="sha384-..."
                crossorigin="anonymous"></script>
        <script src="https://cdn.example.com/bootstrap.js"
                integrity="sha384-..."
                crossorigin="anonymous"></script>
        """
        features = parse_html(html)
        assert 'subresource-integrity' in features


class TestCaptureAttribute:
    """Tests for capture attribute detection (media capture)."""

    def test_capture_user(self, parse_and_check):
        """Test capture=user for front camera."""
        html = '<input type="file" accept="image/*" capture="user">'
        assert parse_and_check(html, 'html-media-capture')

    def test_capture_environment(self, parse_and_check):
        """Test capture=environment for back camera."""
        html = '<input type="file" accept="image/*" capture="environment">'
        assert parse_and_check(html, 'html-media-capture')

    def test_capture_boolean(self, parse_and_check):
        """Test capture as boolean attribute."""
        html = '<input type="file" accept="image/*" capture>'
        assert parse_and_check(html, 'html-media-capture')

    def test_capture_video(self, parse_and_check):
        """Test capture for video recording."""
        html = '<input type="file" accept="video/*" capture="environment">'
        assert parse_and_check(html, 'html-media-capture')

    def test_capture_audio(self, parse_and_check):
        """Test capture for audio recording."""
        html = '<input type="file" accept="audio/*" capture>'
        assert parse_and_check(html, 'html-media-capture')

    def test_capture_selfie(self, parse_and_check):
        """Test capture for selfie photo."""
        html = """
        <label>Take a selfie:
            <input type="file" accept="image/*" capture="user">
        </label>
        """
        assert parse_and_check(html, 'html-media-capture')


class TestCombinedLoadingAttributes:
    """Tests for combined loading attributes."""

    def test_optimized_page_head(self, parse_html):
        """Test optimized page head with various loading strategies."""
        html = """
        <head>
            <link rel="stylesheet"
                  href="https://cdn.example.com/style.css"
                  integrity="sha384-..."
                  crossorigin="anonymous">

            <script src="https://cdn.example.com/critical.js"
                    integrity="sha384-..."></script>

            <script src="analytics.js" async></script>
            <script src="app.js" defer></script>
        </head>
        """
        features = parse_html(html)
        assert 'subresource-integrity' in features
        assert 'script-async' in features
        assert 'script-defer' in features

    def test_lazy_loading_page(self, parse_html):
        """Test page with lazy loading images."""
        html = """
        <main>
            <img src="hero.jpg" loading="eager" alt="Hero">
            <article>
                <img src="content1.jpg" loading="lazy" alt="Content 1">
                <img src="content2.jpg" loading="lazy" alt="Content 2">
            </article>
            <iframe src="comments.html" loading="lazy"></iframe>
        </main>
        """
        features = parse_html(html)
        assert 'loading-lazy-attr' in features

    def test_camera_form(self, parse_html):
        """Test form with camera capture and file upload."""
        html = """
        <form>
            <label>Photo ID (front):
                <input type="file" accept="image/*" capture="environment">
            </label>
            <label>Selfie:
                <input type="file" accept="image/*" capture="user">
            </label>
        </form>
        """
        features = parse_html(html)
        assert 'html-media-capture' in features


class TestNoLoadingAttributes:
    """Tests for HTML without loading attributes."""

    def test_basic_script(self, parse_html):
        """Test script without async/defer."""
        html = '<script src="script.js"></script>'
        features = parse_html(html)
        assert 'script-async' not in features
        assert 'script-defer' not in features

    def test_basic_image(self, parse_html):
        """Test image without loading attribute."""
        html = '<img src="image.jpg" alt="test">'
        features = parse_html(html)
        assert 'loading-lazy-attr' not in features

    def test_basic_file_input(self, parse_html):
        """Test file input without capture."""
        html = '<input type="file">'
        features = parse_html(html)
        assert 'html-media-capture' not in features
