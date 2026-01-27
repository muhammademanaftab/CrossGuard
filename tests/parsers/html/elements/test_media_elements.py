"""Tests for HTML5 media element detection.

Tests elements: video, audio, picture, source, track
"""

import pytest


class TestVideoElement:
    """Tests for <video> element detection."""

    def test_video_basic(self, parse_and_check):
        """Test basic video element detection."""
        html = '<video src="video.mp4"></video>'
        assert parse_and_check(html, 'video')

    def test_video_with_source(self, parse_and_check):
        """Test video element with source children."""
        html = """
        <video>
            <source src="video.mp4" type="video/mp4">
            <source src="video.webm" type="video/webm">
        </video>
        """
        assert parse_and_check(html, 'video')

    def test_video_with_controls(self, parse_and_check):
        """Test video element with controls attribute."""
        html = '<video src="video.mp4" controls></video>'
        assert parse_and_check(html, 'video')

    def test_video_with_all_attributes(self, parse_and_check):
        """Test video element with multiple attributes."""
        html = '''
        <video
            src="video.mp4"
            controls
            autoplay
            loop
            muted
            poster="poster.jpg"
            preload="auto"
            width="640"
            height="360">
        </video>
        '''
        assert parse_and_check(html, 'video')

    def test_video_with_fallback(self, parse_and_check):
        """Test video element with fallback content."""
        html = """
        <video src="video.mp4">
            Your browser does not support the video element.
        </video>
        """
        assert parse_and_check(html, 'video')


class TestAudioElement:
    """Tests for <audio> element detection."""

    def test_audio_basic(self, parse_and_check):
        """Test basic audio element detection."""
        html = '<audio src="audio.mp3"></audio>'
        assert parse_and_check(html, 'audio')

    def test_audio_with_source(self, parse_and_check):
        """Test audio element with source children."""
        html = """
        <audio>
            <source src="audio.mp3" type="audio/mpeg">
            <source src="audio.ogg" type="audio/ogg">
        </audio>
        """
        assert parse_and_check(html, 'audio')

    def test_audio_with_controls(self, parse_and_check):
        """Test audio element with controls attribute."""
        html = '<audio src="audio.mp3" controls></audio>'
        assert parse_and_check(html, 'audio')

    def test_audio_with_all_attributes(self, parse_and_check):
        """Test audio element with multiple attributes."""
        html = '''
        <audio
            src="audio.mp3"
            controls
            autoplay
            loop
            muted
            preload="auto">
        </audio>
        '''
        assert parse_and_check(html, 'audio')


class TestPictureElement:
    """Tests for <picture> element detection."""

    def test_picture_basic(self, parse_and_check):
        """Test basic picture element detection."""
        html = """
        <picture>
            <img src="fallback.jpg" alt="test">
        </picture>
        """
        assert parse_and_check(html, 'picture')

    def test_picture_with_sources(self, parse_html):
        """Test picture element with source elements."""
        html = """
        <picture>
            <source srcset="image.webp" type="image/webp">
            <source srcset="image.jpg" type="image/jpeg">
            <img src="fallback.jpg" alt="test">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features

    def test_picture_responsive(self, parse_html):
        """Test picture element for responsive images."""
        html = """
        <picture>
            <source media="(min-width: 800px)" srcset="large.jpg">
            <source media="(min-width: 400px)" srcset="medium.jpg">
            <img src="small.jpg" alt="Responsive image">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features

    def test_picture_art_direction(self, parse_html):
        """Test picture element for art direction."""
        html = """
        <picture>
            <source media="(orientation: portrait)" srcset="portrait.jpg">
            <source media="(orientation: landscape)" srcset="landscape.jpg">
            <img src="default.jpg" alt="Art directed image">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features


class TestSourceElement:
    """Tests for <source> element detection.

    IMPORTANT: <source> element is used in video, audio, AND picture elements.
    It should NOT by itself trigger the 'picture' feature. Only the <picture>
    element triggers the 'picture' feature.
    """

    def test_source_in_video_does_not_trigger_picture(self, parse_html):
        """Test that source element inside video does NOT trigger picture feature.

        This is a critical false positive test - <source> is used in video/audio too,
        so it should not map to the 'picture' feature.
        """
        html = """
        <video>
            <source src="video.mp4" type="video/mp4">
        </video>
        """
        features = parse_html(html)
        assert 'video' in features  # video element detected
        assert 'picture' not in features  # source in video should NOT trigger picture

    def test_source_in_audio_does_not_trigger_picture(self, parse_html):
        """Test that source element inside audio does NOT trigger picture feature.

        Similar to video, <source> in audio should not trigger 'picture' feature.
        """
        html = """
        <audio>
            <source src="audio.mp3" type="audio/mpeg">
        </audio>
        """
        features = parse_html(html)
        assert 'audio' in features  # audio element detected
        assert 'picture' not in features  # source in audio should NOT trigger picture

    def test_source_in_picture(self, parse_html):
        """Test source element inside picture - picture feature is triggered by <picture>, not <source>."""
        html = """
        <picture>
            <source srcset="image.webp" type="image/webp">
            <img src="image.jpg" alt="test">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features  # triggered by <picture> element, not <source>

    def test_video_with_source_no_false_positive(self, parse_html):
        """Test comprehensive video with multiple sources - no picture false positive."""
        html = """
        <video controls width="640">
            <source src="video.webm" type="video/webm">
            <source src="video.mp4" type="video/mp4">
            <source src="video.ogv" type="video/ogg">
            Your browser does not support the video element.
        </video>
        """
        features = parse_html(html)
        assert 'video' in features
        assert 'picture' not in features  # MUST NOT have picture false positive

    def test_audio_with_source_no_false_positive(self, parse_html):
        """Test comprehensive audio with multiple sources - no picture false positive."""
        html = """
        <audio controls>
            <source src="audio.mp3" type="audio/mpeg">
            <source src="audio.ogg" type="audio/ogg">
            <source src="audio.wav" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        """
        features = parse_html(html)
        assert 'audio' in features
        assert 'picture' not in features  # MUST NOT have picture false positive


class TestTrackElement:
    """Tests for <track> element detection."""

    def test_track_basic(self, parse_html):
        """Test basic track element detection."""
        html = """
        <video>
            <track src="captions.vtt" kind="captions" srclang="en" label="English">
        </video>
        """
        features = parse_html(html)
        assert 'webvtt' in features

    def test_track_subtitles(self, parse_html):
        """Test track element with subtitles kind."""
        html = """
        <video>
            <track kind="subtitles" src="subs_en.vtt" srclang="en" label="English">
            <track kind="subtitles" src="subs_es.vtt" srclang="es" label="Spanish">
        </video>
        """
        features = parse_html(html)
        assert 'webvtt' in features

    def test_track_chapters(self, parse_html):
        """Test track element with chapters kind."""
        html = """
        <video>
            <track kind="chapters" src="chapters.vtt" srclang="en">
        </video>
        """
        features = parse_html(html)
        assert 'webvtt' in features

    def test_track_in_audio(self, parse_html):
        """Test track element inside audio (podcast transcripts)."""
        html = """
        <audio>
            <track kind="captions" src="transcript.vtt">
        </audio>
        """
        features = parse_html(html)
        assert 'webvtt' in features

    def test_track_default(self, parse_html):
        """Test track element with default attribute."""
        html = """
        <video>
            <track kind="captions" src="captions.vtt" srclang="en" label="English" default>
        </video>
        """
        features = parse_html(html)
        assert 'webvtt' in features


class TestVideoWithTracks:
    """Tests for video element with track children (videotracks feature)."""

    def test_video_with_track_detects_videotracks(self, parse_html):
        """Test that video with track detects videotracks feature."""
        html = """
        <video src="movie.mp4">
            <track kind="captions" src="captions.vtt">
        </video>
        """
        features = parse_html(html)
        assert 'videotracks' in features

    def test_video_without_track(self, parse_html):
        """Test that video without track does not detect videotracks."""
        html = '<video src="movie.mp4"></video>'
        features = parse_html(html)
        assert 'videotracks' not in features


class TestAudioWithTracks:
    """Tests for audio element with track children (audiotracks feature)."""

    def test_audio_with_track_detects_audiotracks(self, parse_html):
        """Test that audio with track detects audiotracks feature."""
        html = """
        <audio src="podcast.mp3">
            <track kind="captions" src="transcript.vtt">
        </audio>
        """
        features = parse_html(html)
        assert 'audiotracks' in features

    def test_audio_without_track(self, parse_html):
        """Test that audio without track does not detect audiotracks."""
        html = '<audio src="audio.mp3"></audio>'
        features = parse_html(html)
        assert 'audiotracks' not in features


class TestCombinedMediaElements:
    """Tests for combinations of media elements."""

    def test_all_media_elements(self, parse_html):
        """Test page with all media elements."""
        html = """
        <video src="video.mp4" controls></video>
        <audio src="audio.mp3" controls></audio>
        <picture>
            <source srcset="image.webp" type="image/webp">
            <img src="image.jpg" alt="test">
        </picture>
        """
        features = parse_html(html)
        assert 'video' in features
        assert 'audio' in features
        assert 'picture' in features

    def test_video_with_multiple_sources_and_tracks(self, parse_html):
        """Test video with sources and tracks."""
        html = """
        <video poster="poster.jpg" controls>
            <source src="video.webm" type="video/webm">
            <source src="video.mp4" type="video/mp4">
            <track kind="captions" src="en.vtt" srclang="en" label="English" default>
            <track kind="captions" src="es.vtt" srclang="es" label="Spanish">
        </video>
        """
        features = parse_html(html)
        assert 'video' in features
        assert 'webvtt' in features
        assert 'videotracks' in features


class TestNoMediaElements:
    """Tests for HTML without media elements."""

    def test_no_media_elements(self, parse_html):
        """Test HTML without any media elements."""
        html = """
        <div>
            <p>No media here</p>
            <img src="image.jpg" alt="Just an image">
        </div>
        """
        features = parse_html(html)
        assert 'video' not in features
        assert 'audio' not in features
        assert 'picture' not in features
