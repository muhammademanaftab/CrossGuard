"""Tests for type attribute value detection.

Tests type values: module, image/svg+xml, video/webm, audio/ogg, and various media types
"""

import pytest


class TestTypeModule:
    """Tests for type=module detection."""

    def test_type_module_basic(self, parse_and_check):
        """Test type=module on script."""
        html = '<script type="module" src="app.js"></script>'
        assert parse_and_check(html, 'es6-module')

    def test_type_module_inline(self, parse_and_check):
        """Test type=module on inline script."""
        html = '''
        <script type="module">
            import { foo } from './module.js';
            foo();
        </script>
        '''
        assert parse_and_check(html, 'es6-module')

    def test_type_module_multiple(self, parse_html):
        """Test multiple module scripts."""
        html = """
        <script type="module" src="vendor.js"></script>
        <script type="module" src="app.js"></script>
        """
        features = parse_html(html)
        assert 'es6-module' in features


class TestTypeSvgIcon:
    """Tests for type=image/svg+xml detection (SVG icons)."""

    def test_type_svg_link_icon(self, parse_and_check):
        """Test SVG icon in link element."""
        html = '<link rel="icon" type="image/svg+xml" href="icon.svg">'
        assert parse_and_check(html, 'link-icon-svg')


class TestVideoTypes:
    """Tests for video type attribute values."""

    def test_type_video_webm(self, parse_and_check):
        """Test type=video/webm."""
        html = '<source src="video.webm" type="video/webm">'
        assert parse_and_check(html, 'webm')

    def test_type_video_mp4(self, parse_and_check):
        """Test type=video/mp4."""
        html = '<source src="video.mp4" type="video/mp4">'
        assert parse_and_check(html, 'mpeg4')

    def test_type_video_ogg(self, parse_and_check):
        """Test type=video/ogg."""
        html = '<source src="video.ogv" type="video/ogg">'
        assert parse_and_check(html, 'ogv')

    def test_type_video_av1(self, parse_and_check):
        """Test type=video/av1."""
        html = '<source src="video.av1" type="video/av1">'
        assert parse_and_check(html, 'av1')

    def test_video_with_multiple_sources(self, parse_html):
        """Test video element with multiple source types."""
        html = """
        <video controls>
            <source src="video.webm" type="video/webm">
            <source src="video.mp4" type="video/mp4">
            <source src="video.ogv" type="video/ogg">
        </video>
        """
        features = parse_html(html)
        assert 'webm' in features
        assert 'mpeg4' in features
        assert 'ogv' in features


class TestAudioTypes:
    """Tests for audio type attribute values."""

    def test_type_audio_mpeg(self, parse_and_check):
        """Test type=audio/mpeg (MP3)."""
        html = '<source src="audio.mp3" type="audio/mpeg">'
        assert parse_and_check(html, 'mp3')

    def test_type_audio_mp3(self, parse_and_check):
        """Test type=audio/mp3 (alternative)."""
        html = '<source src="audio.mp3" type="audio/mp3">'
        assert parse_and_check(html, 'mp3')

    def test_type_audio_ogg(self, parse_and_check):
        """Test type=audio/ogg (Vorbis)."""
        html = '<source src="audio.ogg" type="audio/ogg">'
        assert parse_and_check(html, 'ogg-vorbis')

    def test_type_audio_wav(self, parse_and_check):
        """Test type=audio/wav."""
        html = '<source src="audio.wav" type="audio/wav">'
        assert parse_and_check(html, 'wav')

    def test_type_audio_flac(self, parse_and_check):
        """Test type=audio/flac."""
        html = '<source src="audio.flac" type="audio/flac">'
        assert parse_and_check(html, 'flac')

    def test_type_audio_aac(self, parse_and_check):
        """Test type=audio/aac."""
        html = '<source src="audio.aac" type="audio/aac">'
        assert parse_and_check(html, 'aac')

    def test_type_audio_opus(self, parse_and_check):
        """Test type=audio/opus."""
        html = '<source src="audio.opus" type="audio/opus">'
        assert parse_and_check(html, 'opus')

    def test_type_audio_webm(self, parse_and_check):
        """Test type=audio/webm."""
        html = '<source src="audio.webm" type="audio/webm">'
        assert parse_and_check(html, 'webm')

    def test_audio_with_multiple_sources(self, parse_html):
        """Test audio element with multiple source types."""
        html = """
        <audio controls>
            <source src="audio.opus" type="audio/opus">
            <source src="audio.ogg" type="audio/ogg">
            <source src="audio.mp3" type="audio/mpeg">
        </audio>
        """
        features = parse_html(html)
        assert 'opus' in features
        assert 'ogg-vorbis' in features
        assert 'mp3' in features


class TestImageTypes:
    """Tests for image type attribute values."""

    def test_type_image_webp(self, parse_and_check):
        """Test type=image/webp."""
        html = '<source srcset="image.webp" type="image/webp">'
        assert parse_and_check(html, 'webp')

    def test_type_image_avif(self, parse_and_check):
        """Test type=image/avif."""
        html = '<source srcset="image.avif" type="image/avif">'
        assert parse_and_check(html, 'avif')

    def test_type_image_heif(self, parse_and_check):
        """Test type=image/heif."""
        html = '<source srcset="image.heif" type="image/heif">'
        assert parse_and_check(html, 'heif')

    def test_type_image_heic(self, parse_and_check):
        """Test type=image/heic (maps to heif)."""
        html = '<source srcset="image.heic" type="image/heic">'
        assert parse_and_check(html, 'heif')

    def test_type_image_jp2(self, parse_and_check):
        """Test type=image/jp2 (JPEG 2000)."""
        html = '<source srcset="image.jp2" type="image/jp2">'
        assert parse_and_check(html, 'jpeg2000')

    def test_type_image_jxl(self, parse_and_check):
        """Test type=image/jxl (JPEG XL)."""
        html = '<source srcset="image.jxl" type="image/jxl">'
        assert parse_and_check(html, 'jpegxl')

    def test_type_image_jxr(self, parse_and_check):
        """Test type=image/jxr (JPEG XR)."""
        html = '<source srcset="image.jxr" type="image/jxr">'
        assert parse_and_check(html, 'jpegxr')

    def test_type_image_apng(self, parse_and_check):
        """Test type=image/apng (Animated PNG)."""
        html = '<source srcset="image.apng" type="image/apng">'
        assert parse_and_check(html, 'apng')

    def test_picture_with_modern_formats(self, parse_html):
        """Test picture element with modern image formats."""
        html = """
        <picture>
            <source srcset="image.avif" type="image/avif">
            <source srcset="image.webp" type="image/webp">
            <img src="image.jpg" alt="test">
        </picture>
        """
        features = parse_html(html)
        assert 'avif' in features
        assert 'webp' in features


class TestDolbyAudioTypes:
    """Tests for Dolby audio type detection."""

    def test_type_audio_ac3(self, parse_and_check):
        """Test type=audio/ac3 (Dolby Digital)."""
        html = '<source src="audio.ac3" type="audio/ac3">'
        assert parse_and_check(html, 'ac3-ec3')

    def test_type_audio_eac3(self, parse_and_check):
        """Test type=audio/eac3 (Dolby Digital Plus)."""
        html = '<source src="audio.eac3" type="audio/eac3">'
        assert parse_and_check(html, 'ac3-ec3')

    def test_type_audio_ec3(self, parse_and_check):
        """Test type=audio/ec3 (alternative)."""
        html = '<source src="audio.ec3" type="audio/ec3">'
        assert parse_and_check(html, 'ac3-ec3')


class TestCombinedTypeValues:
    """Tests for combined type value scenarios."""

    def test_multimedia_page(self, parse_html):
        """Test page with various multimedia types."""
        html = """
        <video controls>
            <source src="video.webm" type="video/webm">
            <source src="video.mp4" type="video/mp4">
        </video>

        <audio controls>
            <source src="audio.opus" type="audio/opus">
            <source src="audio.mp3" type="audio/mpeg">
        </audio>

        <picture>
            <source srcset="hero.avif" type="image/avif">
            <source srcset="hero.webp" type="image/webp">
            <img src="hero.jpg" alt="Hero image">
        </picture>
        """
        features = parse_html(html)
        assert 'webm' in features
        assert 'mpeg4' in features
        assert 'opus' in features
        assert 'mp3' in features
        assert 'avif' in features
        assert 'webp' in features

    def test_modern_web_page(self, parse_html):
        """Test modern web page with modules and media."""
        html = """
        <head>
            <link rel="icon" type="image/svg+xml" href="icon.svg">
            <script type="module" src="app.js"></script>
        </head>
        <body>
            <picture>
                <source srcset="photo.avif" type="image/avif">
                <img src="photo.jpg" alt="Photo">
            </picture>
        </body>
        """
        features = parse_html(html)
        assert 'link-icon-svg' in features
        assert 'es6-module' in features
        assert 'avif' in features


class TestCaseInsensitivity:
    """Tests for case insensitivity of type values."""

    def test_type_module_uppercase(self, parse_and_check):
        """Test type=MODULE in uppercase."""
        html = '<script type="MODULE" src="app.js"></script>'
        assert parse_and_check(html, 'es6-module')

    def test_type_video_webm_mixed_case(self, parse_and_check):
        """Test type=video/WebM in mixed case."""
        html = '<source src="video.webm" type="video/WebM">'
        assert parse_and_check(html, 'webm')


class TestNoTypeValues:
    """Tests for elements without tracked type values."""

    def test_script_no_type(self, parse_html):
        """Test script without type (defaults to JavaScript)."""
        html = '<script src="app.js"></script>'
        features = parse_html(html)
        assert 'es6-module' not in features

    def test_script_text_javascript(self, parse_html):
        """Test script with type=text/javascript (common, not tracked)."""
        html = '<script type="text/javascript" src="app.js"></script>'
        features = parse_html(html)
        assert 'es6-module' not in features
