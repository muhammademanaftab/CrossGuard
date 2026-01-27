"""Tests for referrerpolicy attribute value detection.

Tests referrerpolicy values: no-referrer, origin, no-referrer-when-downgrade,
                             origin-when-cross-origin, same-origin, strict-origin,
                             strict-origin-when-cross-origin, unsafe-url
All map to feature ID: referrer-policy
"""

import pytest


class TestReferrerpolicyNoReferrer:
    """Tests for referrerpolicy=no-referrer detection."""

    def test_no_referrer_on_link(self, parse_and_check):
        """Test referrerpolicy=no-referrer on anchor."""
        html = '<a href="https://example.com" referrerpolicy="no-referrer">Link</a>'
        assert parse_and_check(html, 'referrer-policy')

    def test_no_referrer_on_img(self, parse_and_check):
        """Test referrerpolicy=no-referrer on img."""
        html = '<img src="https://example.com/img.jpg" referrerpolicy="no-referrer" alt="test">'
        assert parse_and_check(html, 'referrer-policy')

    def test_no_referrer_on_script(self, parse_and_check):
        """Test referrerpolicy=no-referrer on script."""
        html = '<script src="https://example.com/script.js" referrerpolicy="no-referrer"></script>'
        assert parse_and_check(html, 'referrer-policy')

    def test_no_referrer_on_iframe(self, parse_and_check):
        """Test referrerpolicy=no-referrer on iframe."""
        html = '<iframe src="https://example.com" referrerpolicy="no-referrer"></iframe>'
        assert parse_and_check(html, 'referrer-policy')


class TestReferrerpolicyOrigin:
    """Tests for referrerpolicy=origin detection."""

    def test_origin_on_link(self, parse_and_check):
        """Test referrerpolicy=origin on anchor."""
        html = '<a href="https://example.com" referrerpolicy="origin">Link</a>'
        assert parse_and_check(html, 'referrer-policy')

    def test_origin_on_img(self, parse_and_check):
        """Test referrerpolicy=origin on img."""
        html = '<img src="https://example.com/img.jpg" referrerpolicy="origin" alt="test">'
        assert parse_and_check(html, 'referrer-policy')


class TestReferrerpolicyNoReferrerWhenDowngrade:
    """Tests for referrerpolicy=no-referrer-when-downgrade detection."""

    def test_no_referrer_when_downgrade(self, parse_and_check):
        """Test referrerpolicy=no-referrer-when-downgrade."""
        html = '<a href="https://example.com" referrerpolicy="no-referrer-when-downgrade">Link</a>'
        assert parse_and_check(html, 'referrer-policy')


class TestReferrerpolicyOriginWhenCrossOrigin:
    """Tests for referrerpolicy=origin-when-cross-origin detection."""

    def test_origin_when_cross_origin(self, parse_and_check):
        """Test referrerpolicy=origin-when-cross-origin."""
        html = '<a href="https://example.com" referrerpolicy="origin-when-cross-origin">Link</a>'
        assert parse_and_check(html, 'referrer-policy')

    def test_origin_when_cross_origin_on_img(self, parse_and_check):
        """Test referrerpolicy=origin-when-cross-origin on img."""
        html = '<img src="https://cdn.example.com/img.jpg" referrerpolicy="origin-when-cross-origin" alt="test">'
        assert parse_and_check(html, 'referrer-policy')


class TestReferrerpolicySameOrigin:
    """Tests for referrerpolicy=same-origin detection."""

    def test_same_origin(self, parse_and_check):
        """Test referrerpolicy=same-origin."""
        html = '<a href="/page" referrerpolicy="same-origin">Link</a>'
        assert parse_and_check(html, 'referrer-policy')


class TestReferrerpolicyStrictOrigin:
    """Tests for referrerpolicy=strict-origin detection."""

    def test_strict_origin(self, parse_and_check):
        """Test referrerpolicy=strict-origin."""
        html = '<a href="https://example.com" referrerpolicy="strict-origin">Link</a>'
        assert parse_and_check(html, 'referrer-policy')

    def test_strict_origin_on_script(self, parse_and_check):
        """Test referrerpolicy=strict-origin on script."""
        html = '<script src="https://cdn.example.com/lib.js" referrerpolicy="strict-origin"></script>'
        assert parse_and_check(html, 'referrer-policy')


class TestReferrerpolicyStrictOriginWhenCrossOrigin:
    """Tests for referrerpolicy=strict-origin-when-cross-origin detection."""

    def test_strict_origin_when_cross_origin(self, parse_and_check):
        """Test referrerpolicy=strict-origin-when-cross-origin."""
        html = '<a href="https://example.com" referrerpolicy="strict-origin-when-cross-origin">Link</a>'
        assert parse_and_check(html, 'referrer-policy')

    def test_strict_origin_when_cross_origin_default(self, parse_and_check):
        """Test strict-origin-when-cross-origin (modern default)."""
        html = '<img src="https://cdn.example.com/img.jpg" referrerpolicy="strict-origin-when-cross-origin" alt="test">'
        assert parse_and_check(html, 'referrer-policy')


class TestReferrerpolicyUnsafeUrl:
    """Tests for referrerpolicy=unsafe-url detection."""

    def test_unsafe_url(self, parse_and_check):
        """Test referrerpolicy=unsafe-url."""
        html = '<a href="https://example.com" referrerpolicy="unsafe-url">Link</a>'
        assert parse_and_check(html, 'referrer-policy')


class TestReferrerpolicyOnVariousElements:
    """Tests for referrerpolicy on various elements."""

    def test_on_link_element(self, parse_and_check):
        """Test referrerpolicy on link element."""
        html = '<link rel="stylesheet" href="https://cdn.example.com/style.css" referrerpolicy="no-referrer">'
        assert parse_and_check(html, 'referrer-policy')

    def test_on_area(self, parse_and_check):
        """Test referrerpolicy on area element."""
        html = '<area href="https://example.com" referrerpolicy="origin" alt="Area">'
        assert parse_and_check(html, 'referrer-policy')

    def test_on_audio(self, parse_and_check):
        """Test referrerpolicy on audio element."""
        html = '<audio src="https://cdn.example.com/audio.mp3" referrerpolicy="no-referrer"></audio>'
        assert parse_and_check(html, 'referrer-policy')

    def test_on_video(self, parse_and_check):
        """Test referrerpolicy on video element."""
        html = '<video src="https://cdn.example.com/video.mp4" referrerpolicy="no-referrer"></video>'
        assert parse_and_check(html, 'referrer-policy')


class TestCombinedReferrerpolicyScenarios:
    """Tests for combined referrerpolicy scenarios."""

    def test_privacy_focused_page(self, parse_html):
        """Test page with privacy-focused referrer policies."""
        html = """
        <head>
            <link rel="stylesheet" href="https://cdn.example.com/style.css"
                  referrerpolicy="no-referrer">
            <script src="https://cdn.example.com/lib.js"
                    referrerpolicy="no-referrer"></script>
        </head>
        <body>
            <img src="https://cdn.example.com/img.jpg"
                 referrerpolicy="no-referrer" alt="Image">
            <a href="https://external.com"
               referrerpolicy="no-referrer"
               rel="noopener noreferrer">
                External Link
            </a>
        </body>
        """
        features = parse_html(html)
        assert 'referrer-policy' in features
        assert 'rel-noopener' in features
        assert 'rel-noreferrer' in features

    def test_various_policies(self, parse_html):
        """Test page with various referrer policies."""
        html = """
        <a href="/internal" referrerpolicy="same-origin">Internal</a>
        <a href="https://trusted.com" referrerpolicy="strict-origin">Trusted</a>
        <a href="https://analytics.com" referrerpolicy="no-referrer">Analytics</a>
        <img src="https://cdn.example.com/img.jpg"
             referrerpolicy="strict-origin-when-cross-origin" alt="CDN Image">
        """
        features = parse_html(html)
        assert 'referrer-policy' in features


class TestCaseInsensitivity:
    """Tests for case insensitivity of referrerpolicy values."""

    def test_no_referrer_uppercase(self, parse_and_check):
        """Test referrerpolicy=NO-REFERRER in uppercase."""
        html = '<a href="https://example.com" referrerpolicy="NO-REFERRER">Link</a>'
        assert parse_and_check(html, 'referrer-policy')

    def test_origin_mixed_case(self, parse_and_check):
        """Test referrerpolicy=Origin in mixed case."""
        html = '<a href="https://example.com" referrerpolicy="Origin">Link</a>'
        assert parse_and_check(html, 'referrer-policy')


class TestNoReferrerpolicy:
    """Tests for elements without referrerpolicy."""

    def test_link_without_referrerpolicy(self, parse_html):
        """Test link without referrerpolicy attribute."""
        html = '<a href="https://example.com">Link</a>'
        features = parse_html(html)
        assert 'referrer-policy' not in features

    def test_img_without_referrerpolicy(self, parse_html):
        """Test img without referrerpolicy attribute."""
        html = '<img src="image.jpg" alt="test">'
        features = parse_html(html)
        assert 'referrer-policy' not in features
