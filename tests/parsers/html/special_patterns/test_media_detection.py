"""Tests for media-related pattern detection.

Tests patterns: media-fragments (#t=), audiotracks, videotracks, webvtt
"""

import pytest


class TestMediaFragments:
    """Tests for media fragment URI detection (#t=, #track=, etc.)."""

    def test_time_fragment_video(self, parse_and_check):
        """Test time fragment on video."""
        html = '<video src="video.mp4#t=10,20"></video>'
        assert parse_and_check(html, 'media-fragments')

    def test_time_fragment_audio(self, parse_and_check):
        """Test time fragment on audio."""
        html = '<audio src="podcast.mp3#t=60"></audio>'
        assert parse_and_check(html, 'media-fragments')

    def test_time_fragment_start_only(self, parse_and_check):
        """Test time fragment with start time only."""
        html = '<video src="video.mp4#t=30"></video>'
        assert parse_and_check(html, 'media-fragments')

    def test_time_fragment_with_end(self, parse_and_check):
        """Test time fragment with start and end time."""
        html = '<video src="video.mp4#t=10,60"></video>'
        assert parse_and_check(html, 'media-fragments')

    def test_time_fragment_seconds_decimal(self, parse_and_check):
        """Test time fragment with decimal seconds."""
        html = '<audio src="audio.mp3#t=10.5,30.25"></audio>'
        assert parse_and_check(html, 'media-fragments')

    def test_time_fragment_npt_format(self, parse_and_check):
        """Test time fragment with NPT (Normal Play Time) format."""
        html = '<video src="video.mp4#t=npt:10,20"></video>'
        assert parse_and_check(html, 'media-fragments')

    def test_time_fragment_in_source(self, parse_and_check):
        """Test time fragment in source element."""
        html = """
        <video>
            <source src="video.mp4#t=5,30" type="video/mp4">
        </video>
        """
        assert parse_and_check(html, 'media-fragments')

    def test_track_fragment(self, parse_and_check):
        """Test track fragment identifier."""
        html = '<video src="video.mp4#track=audio&t=10"></video>'
        assert parse_and_check(html, 'media-fragments')

    def test_spatial_fragment(self, parse_and_check):
        """Test spatial (xywh) fragment identifier."""
        html = '<video src="video.mp4#xywh=0,0,640,360"></video>'
        assert parse_and_check(html, 'media-fragments')

    def test_id_fragment(self, parse_and_check):
        """Test id fragment identifier."""
        html = '<video src="video.mp4#id=chapter1"></video>'
        assert parse_and_check(html, 'media-fragments')


class TestWebVTT:
    """Tests for WebVTT detection (.vtt files)."""

    def test_vtt_in_track(self, parse_and_check):
        """Test .vtt file in track element."""
        html = """
        <video src="video.mp4">
            <track src="captions.vtt" kind="captions" srclang="en" label="English">
        </video>
        """
        assert parse_and_check(html, 'webvtt')

    def test_vtt_subtitles(self, parse_and_check):
        """Test WebVTT for subtitles."""
        html = """
        <video src="video.mp4">
            <track src="subtitles.vtt" kind="subtitles" srclang="en" label="English">
        </video>
        """
        assert parse_and_check(html, 'webvtt')

    def test_vtt_chapters(self, parse_and_check):
        """Test WebVTT for chapters."""
        html = """
        <video src="video.mp4">
            <track src="chapters.vtt" kind="chapters" srclang="en">
        </video>
        """
        assert parse_and_check(html, 'webvtt')

    def test_vtt_descriptions(self, parse_and_check):
        """Test WebVTT for descriptions."""
        html = """
        <video src="video.mp4">
            <track src="descriptions.vtt" kind="descriptions" srclang="en">
        </video>
        """
        assert parse_and_check(html, 'webvtt')

    def test_vtt_metadata(self, parse_and_check):
        """Test WebVTT for metadata."""
        html = """
        <video src="video.mp4">
            <track src="metadata.vtt" kind="metadata">
        </video>
        """
        assert parse_and_check(html, 'webvtt')

    def test_vtt_with_query_string(self, parse_and_check):
        """Test WebVTT with query string."""
        html = """
        <video src="video.mp4">
            <track src="captions.vtt?v=1.0" kind="captions">
        </video>
        """
        assert parse_and_check(html, 'webvtt')

    def test_vtt_multiple_languages(self, parse_html):
        """Test multiple WebVTT tracks for different languages."""
        html = """
        <video src="video.mp4">
            <track src="captions-en.vtt" kind="captions" srclang="en" label="English" default>
            <track src="captions-es.vtt" kind="captions" srclang="es" label="Spanish">
            <track src="captions-fr.vtt" kind="captions" srclang="fr" label="French">
        </video>
        """
        features = parse_html(html)
        assert 'webvtt' in features


class TestVideoTracks:
    """Tests for videotracks feature detection."""

    def test_video_with_track(self, parse_and_check):
        """Test video element with track child."""
        html = """
        <video src="video.mp4">
            <track kind="captions" src="captions.vtt">
        </video>
        """
        assert parse_and_check(html, 'videotracks')

    def test_video_multiple_tracks(self, parse_html):
        """Test video with multiple tracks."""
        html = """
        <video src="video.mp4">
            <track kind="captions" src="captions-en.vtt" srclang="en">
            <track kind="subtitles" src="subtitles-es.vtt" srclang="es">
            <track kind="chapters" src="chapters.vtt">
        </video>
        """
        features = parse_html(html)
        assert 'videotracks' in features

    def test_video_without_track(self, parse_html):
        """Test video without track doesn't trigger videotracks."""
        html = '<video src="video.mp4"></video>'
        features = parse_html(html)
        assert 'videotracks' not in features


class TestAudioTracks:
    """Tests for audiotracks feature detection."""

    def test_audio_with_track(self, parse_and_check):
        """Test audio element with track child."""
        html = """
        <audio src="podcast.mp3">
            <track kind="captions" src="transcript.vtt">
        </audio>
        """
        assert parse_and_check(html, 'audiotracks')

    def test_audio_multiple_tracks(self, parse_html):
        """Test audio with multiple tracks."""
        html = """
        <audio src="podcast.mp3">
            <track kind="captions" src="transcript-en.vtt" srclang="en">
            <track kind="captions" src="transcript-es.vtt" srclang="es">
        </audio>
        """
        features = parse_html(html)
        assert 'audiotracks' in features

    def test_audio_without_track(self, parse_html):
        """Test audio without track doesn't trigger audiotracks."""
        html = '<audio src="audio.mp3"></audio>'
        features = parse_html(html)
        assert 'audiotracks' not in features


class TestCombinedMediaPatterns:
    """Tests for combined media patterns."""

    def test_accessible_video(self, parse_html):
        """Test fully accessible video with all track types."""
        html = """
        <video src="video.mp4" controls>
            <track kind="captions" src="captions.vtt" srclang="en" label="English" default>
            <track kind="subtitles" src="subtitles-es.vtt" srclang="es" label="Spanish">
            <track kind="descriptions" src="descriptions.vtt" srclang="en" label="Audio Description">
            <track kind="chapters" src="chapters.vtt" srclang="en">
        </video>
        """
        features = parse_html(html)
        assert 'video' in features
        assert 'webvtt' in features
        assert 'videotracks' in features

    def test_video_with_fragment_and_tracks(self, parse_html):
        """Test video with time fragment and tracks."""
        html = """
        <video src="video.mp4#t=10,60" controls>
            <track kind="captions" src="captions.vtt">
        </video>
        """
        features = parse_html(html)
        assert 'media-fragments' in features
        assert 'webvtt' in features
        assert 'videotracks' in features

    def test_podcast_with_transcript(self, parse_html):
        """Test podcast audio with transcript track."""
        html = """
        <audio src="episode-42.mp3" controls>
            <track kind="captions" src="episode-42-transcript.vtt" srclang="en">
        </audio>
        """
        features = parse_html(html)
        assert 'audio' in features
        assert 'webvtt' in features
        assert 'audiotracks' in features


class TestNoMediaPatterns:
    """Tests for media without special patterns."""

    def test_video_without_fragments_or_tracks(self, parse_html):
        """Test basic video without special patterns."""
        html = '<video src="video.mp4" controls></video>'
        features = parse_html(html)
        assert 'video' in features
        assert 'media-fragments' not in features
        assert 'webvtt' not in features
        assert 'videotracks' not in features

    def test_audio_without_fragments_or_tracks(self, parse_html):
        """Test basic audio without special patterns."""
        html = '<audio src="audio.mp3" controls></audio>'
        features = parse_html(html)
        assert 'audio' in features
        assert 'media-fragments' not in features
        assert 'audiotracks' not in features
