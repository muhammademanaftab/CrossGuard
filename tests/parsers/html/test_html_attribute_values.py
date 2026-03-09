"""Consolidated HTML attribute value detection tests.

Covers: rel values, type values (media/module/icon), crossorigin (cors),
referrer-policy, and content-security-policy.
"""

import pytest


# ---------------------------------------------------------------------------
# rel= values on <link> and <a>
# ---------------------------------------------------------------------------

class TestRelValues:

    @pytest.mark.parametrize("html, feature_id", [
        ('<link rel="preload" href="s.css" as="style">', 'link-rel-preload'),
        ('<link rel="prefetch" href="n.js">', 'link-rel-prefetch'),
        ('<link rel="dns-prefetch" href="//cdn.example.com">', 'link-rel-dns-prefetch'),
        ('<link rel="preconnect" href="https://fonts.googleapis.com">', 'link-rel-preconnect'),
        ('<link rel="modulepreload" href="app.js">', 'link-rel-modulepreload'),
        ('<link rel="prerender" href="/next">', 'link-rel-prerender'),
        ('<link rel="icon" type="image/png" href="icon.png">', 'link-icon-png'),
        ('<a href="https://example.com" rel="noopener">Link</a>', 'rel-noopener'),
        ('<a href="https://example.com" rel="noreferrer">Link</a>', 'rel-noreferrer'),
        ('<link rel="import" href="comp.html">', 'imports'),
    ], ids=[
        "preload", "prefetch", "dns-prefetch", "preconnect",
        "modulepreload", "prerender", "link-icon-png",
        "noopener", "noreferrer", "imports",
    ])
    @pytest.mark.unit
    def test_rel_value(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)

    @pytest.mark.unit
    def test_multiple_rel_values(self, parse_features):
        html = """
        <link rel="preload" href="s.css" as="style">
        <link rel="prefetch" href="next.js">
        <link rel="preconnect" href="https://cdn.example.com">
        <a href="https://external.com" rel="noopener noreferrer">Ext</a>
        """
        features = parse_features(html)
        assert 'link-rel-preload' in features
        assert 'link-rel-prefetch' in features
        assert 'link-rel-preconnect' in features
        assert 'rel-noopener' in features


# ---------------------------------------------------------------------------
# type= values (media types, ES modules, SVG icons)
# ---------------------------------------------------------------------------

class TestTypeValues:

    @pytest.mark.parametrize("html, feature_id", [
        # ES module
        ('<script type="module" src="app.js"></script>', 'es6-module'),
        # SVG icon
        ('<link rel="icon" type="image/svg+xml" href="fav.svg">', 'link-icon-svg'),
        # Video formats
        ('<source type="video/webm" src="v.webm">', 'webm'),
        ('<source type="video/mp4" src="v.mp4">', 'mpeg4'),
        ('<source type="video/ogg" src="v.ogv">', 'ogv'),
        ('<source type="video/av1" src="v.av1">', 'av1'),
        # Audio formats
        ('<source type="audio/mpeg" src="a.mp3">', 'mp3'),
        ('<source type="audio/ogg" src="a.ogg">', 'ogg-vorbis'),
        ('<source type="audio/wav" src="a.wav">', 'wav'),
        ('<source type="audio/flac" src="a.flac">', 'flac'),
        ('<source type="audio/aac" src="a.aac">', 'aac'),
        ('<source type="audio/opus" src="a.opus">', 'opus'),
        # Image formats
        ('<source type="image/webp" srcset="i.webp">', 'webp'),
        ('<source type="image/avif" srcset="i.avif">', 'avif'),
        ('<source type="image/heif" srcset="i.heif">', 'heif'),
        ('<source type="image/jp2" srcset="i.jp2">', 'jpeg2000'),
        ('<source type="image/jxl" srcset="i.jxl">', 'jpegxl'),
        ('<source type="image/jxr" srcset="i.jxr">', 'jpegxr'),
        ('<source type="image/apng" srcset="i.apng">', 'apng'),
        # AC3/EC3 audio
        ('<source type="audio/ac3" src="a.ac3">', 'ac3-ec3'),
    ], ids=[
        "es-module", "svg-icon",
        "webm", "mp4", "ogv", "av1",
        "mp3", "ogg-vorbis", "wav", "flac", "aac", "opus",
        "webp", "avif", "heif", "jpeg2000", "jpegxl", "jpegxr", "apng",
        "ac3-ec3",
    ])
    @pytest.mark.unit
    def test_type_value(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)


# ---------------------------------------------------------------------------
# crossorigin -> cors
# ---------------------------------------------------------------------------

class TestCrossoriginValues:

    @pytest.mark.parametrize("html", [
        '<img src="i.jpg" crossorigin="anonymous" alt="t">',
        '<img src="i.jpg" crossorigin="use-credentials" alt="t">',
        '<script src="a.js" crossorigin="anonymous"></script>',
        '<link rel="stylesheet" href="s.css" crossorigin="anonymous">',
        '<video src="v.mp4" crossorigin="anonymous"></video>',
        '<audio src="a.mp3" crossorigin="anonymous"></audio>',
    ], ids=[
        "img-anonymous", "img-credentials",
        "script", "link", "video", "audio",
    ])
    @pytest.mark.unit
    def test_cors(self, parse_features, html):
        assert 'cors' in parse_features(html)

    @pytest.mark.unit
    def test_no_cors(self, parse_features):
        html = '<img src="local.jpg" alt="t">'
        assert 'cors' not in parse_features(html)


# ---------------------------------------------------------------------------
# referrerpolicy -> referrer-policy
# ---------------------------------------------------------------------------

class TestReferrerPolicyValues:

    @pytest.mark.parametrize("html", [
        '<a href="https://example.com" referrerpolicy="no-referrer">Link</a>',
        '<a href="https://example.com" referrerpolicy="origin">Link</a>',
        '<a href="https://example.com" referrerpolicy="strict-origin-when-cross-origin">Link</a>',
        '<img src="i.jpg" referrerpolicy="no-referrer" alt="t">',
        '<script src="a.js" referrerpolicy="no-referrer"></script>',
        '<link rel="stylesheet" href="s.css" referrerpolicy="origin">',
        '<iframe src="p.html" referrerpolicy="no-referrer"></iframe>',
    ], ids=[
        "a-no-referrer", "a-origin", "a-strict-origin",
        "img", "script", "link", "iframe",
    ])
    @pytest.mark.unit
    def test_referrer_policy(self, parse_features, html):
        assert 'referrer-policy' in parse_features(html)

    @pytest.mark.unit
    def test_no_referrer_policy(self, parse_features):
        html = '<a href="https://example.com">Link</a>'
        assert 'referrer-policy' not in parse_features(html)


# ---------------------------------------------------------------------------
# CSP meta -> contentsecuritypolicy / contentsecuritypolicy2
# ---------------------------------------------------------------------------

class TestContentSecurityPolicy:

    @pytest.mark.parametrize("html", [
        '<meta http-equiv="content-security-policy" content="default-src \'self\'">',
        '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\'">',
    ])
    @pytest.mark.unit
    def test_csp2(self, parse_features, html):
        assert 'contentsecuritypolicy2' in parse_features(html)

    @pytest.mark.unit
    def test_csp1_fallback(self, parse_features):
        html = '<meta http-equiv="X-Content-Security-Policy" content="default-src \'self\'">'
        assert 'contentsecuritypolicy' in parse_features(html)

    @pytest.mark.unit
    def test_no_csp(self, parse_features):
        html = '<meta charset="UTF-8">'
        features = parse_features(html)
        assert 'contentsecuritypolicy' not in features
        assert 'contentsecuritypolicy2' not in features
