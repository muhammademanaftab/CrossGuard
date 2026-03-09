"""Consolidated HTML edge case tests.

Covers: empty/minimal input, malformed HTML, encoding/special chars,
large files/performance, false positive prevention, state reset, parser reuse.
"""

import pytest


# ---------------------------------------------------------------------------
# Empty / minimal input
# ---------------------------------------------------------------------------

class TestEmptyInput:

    @pytest.mark.parametrize("html", [
        "",
        "     ",
        "\n\n\n",
        "\t\t\t",
        "  \n\t  \n  ",
    ], ids=["empty", "spaces", "newlines", "tabs", "mixed-ws"])
    @pytest.mark.unit
    def test_empty_returns_empty_set(self, parse_features, html):
        assert parse_features(html) == set()

    @pytest.mark.parametrize("html", [
        "<!DOCTYPE html>",
        "<html></html>",
        "<html><head></head><body></body></html>",
        "<div></div>",
        "<br>",
        "Just some text",
    ], ids=["doctype", "html-only", "full-minimal", "empty-div", "self-close", "text-only"])
    @pytest.mark.unit
    def test_minimal_html_no_features(self, parse_features, html):
        assert parse_features(html) == set()


class TestNoneAndInvalidInput:

    @pytest.mark.unit
    def test_none_input(self, html_parser):
        try:
            result = html_parser.parse_string(None)
            assert result == set() or isinstance(result, set)
        except (TypeError, AttributeError):
            pass

    @pytest.mark.unit
    def test_numeric_input(self, html_parser):
        try:
            result = html_parser.parse_string(123)
            assert isinstance(result, set)
        except (TypeError, AttributeError):
            pass


class TestEmptyElements:
    """Empty HTML5 elements should still be detected."""

    @pytest.mark.parametrize("html, feature_id", [
        ("<video></video>", "video"),
        ("<audio></audio>", "audio"),
        ("<canvas></canvas>", "canvas"),
        ("<dialog></dialog>", "dialog"),
        ("<details></details>", "details"),
    ])
    @pytest.mark.unit
    def test_empty_element(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)


# ---------------------------------------------------------------------------
# Malformed HTML
# ---------------------------------------------------------------------------

class TestMalformedHTML:

    @pytest.mark.parametrize("html, expected_features", [
        # Unclosed tags — should still detect features
        ("<main><section><article>Content", {'html5semantic'}),
        ('<video src="v.mp4">', {'video'}),
        ("<main><video src='v.mp4'><audio src='a.mp3'>", {'html5semantic', 'video', 'audio'}),
        # Mismatched close
        ("<main><div>Content</main></div>", {'html5semantic'}),
        # Body only / partial
        ("<main>Content</main><aside>Sidebar</aside>", {'html5semantic'}),
        ('<meta name="viewport" content="width=device-width">', {'viewport-units'}),
        ("<video></video><main></main><input type='date'>", {'video', 'html5semantic', 'input-datetime'}),
    ], ids=[
        "unclosed-nested", "unclosed-video", "unclosed-multi",
        "mismatched-close", "body-only", "head-only", "random-tags",
    ])
    @pytest.mark.unit
    def test_malformed_still_detects(self, parse_features, html, expected_features):
        features = parse_features(html)
        for f in expected_features:
            assert f in features

    @pytest.mark.parametrize("html", [
        "<div>Content",
        '<input type=text placeholder=test>',
        '<input @#$%="bad" type="date">',
        "<span><div>Content</div></span>",
        "<unknownelement>Content</unknownelement>",
        "<html><html><body></body></html></html>",
    ], ids=[
        "unclosed-div", "missing-quotes", "bad-attr",
        "block-in-inline", "unknown-element", "double-html",
    ])
    @pytest.mark.unit
    def test_graceful_handling(self, parse_features, html):
        """Parser handles malformed HTML without crashing."""
        assert isinstance(parse_features(html), set)

    @pytest.mark.unit
    def test_recovery_valid_after_errors(self, parse_features):
        html = """
        <broken<tag>
        <main>Valid content</main>
        <video src="video.mp4"></video>
        """
        features = parse_features(html)
        assert 'html5semantic' in features or 'video' in features

    @pytest.mark.unit
    def test_mixed_quote_styles(self, parse_features):
        html = """<input type="text" placeholder='Enter name'>"""
        assert 'input-placeholder' in parse_features(html)

    @pytest.mark.unit
    def test_duplicate_attributes(self, parse_features):
        html = '<input type="text" type="email" placeholder="test" placeholder="other">'
        assert isinstance(parse_features(html), set)

    @pytest.mark.unit
    def test_content_before_and_after_html(self, parse_features):
        html = "Some text<html><body><main>Content</main></body></html>Extra"
        assert 'html5semantic' in parse_features(html)


# ---------------------------------------------------------------------------
# Encoding / special characters
# ---------------------------------------------------------------------------

class TestEncoding:

    @pytest.mark.parametrize("html", [
        "<main>Hello, 世界! Привет мир!</main>",
        '<input placeholder="输入您的名字" type="text">',
        "<main>مرحبا بالعالم</main>",
        "<main>Hello 👋 World 🌍</main>",
        "<main>Family: 👨‍👩‍👧‍👦 Waving: 👋🏽</main>",
        "\ufeff<main>Content</main>",
    ], ids=["unicode", "unicode-attr", "arabic", "emoji", "complex-emoji", "bom"])
    @pytest.mark.unit
    def test_unicode_handling(self, parse_features, html):
        """Unicode/emoji content should not break detection."""
        features = parse_features(html)
        assert isinstance(features, set)
        # All these contain <main> or <input> which should detect features
        assert len(features) > 0

    @pytest.mark.parametrize("html", [
        "<main>&copy; 2024 &mdash; All rights &amp; reserved</main>",
        "<main>&#169; &#8212; &#38;</main>",
        "<main>&#x00A9; &#x2014;</main>",
        "<main>&lt;tag&gt; content &lt;/tag&gt;</main>",
        "<main>Hello&nbsp;World</main>",
    ], ids=["named-entities", "numeric-entities", "hex-entities", "lt-gt", "nbsp"])
    @pytest.mark.unit
    def test_html_entities(self, parse_features, html):
        assert 'html5semantic' in parse_features(html)

    @pytest.mark.unit
    def test_null_character(self, parse_features):
        html = "<main>Before\x00After</main>"
        assert isinstance(parse_features(html), set)

    @pytest.mark.unit
    def test_unicode_doesnt_interfere(self, parse_features):
        html = '<video src="视频.mp4"></video><audio src="音频.mp3"></audio>'
        features = parse_features(html)
        assert 'video' in features
        assert 'audio' in features

    @pytest.mark.unit
    def test_meta_charset(self, parse_features):
        html = '<meta charset="UTF-8"><main>Content</main>'
        assert 'html5semantic' in parse_features(html)


# ---------------------------------------------------------------------------
# Large files / performance
# ---------------------------------------------------------------------------

class TestLargeFiles:

    @pytest.mark.unit
    def test_large_text(self, parse_features):
        html = f"<main>{'Lorem ipsum ' * 10000}</main>"
        assert 'html5semantic' in parse_features(html)

    @pytest.mark.unit
    def test_many_paragraphs(self, parse_features):
        html = f"<main>{'<p>Paragraph content.</p>' * 1000}</main>"
        assert 'html5semantic' in parse_features(html)

    @pytest.mark.unit
    def test_large_attribute_value(self, parse_features):
        html = f'<div data-content="{"x" * 10000}">Content</div>'
        assert 'dataset' in parse_features(html)

    @pytest.mark.unit
    def test_1000_divs(self, parse_features):
        html = f"<body>{'<div>Content</div>' * 1000}</body>"
        assert isinstance(parse_features(html), set)

    @pytest.mark.unit
    def test_many_semantic(self, parse_features):
        block = '<article><header><h2>T</h2></header><section><p>C</p></section></article>'
        html = f"<main>{block * 100}</main>"
        assert 'html5semantic' in parse_features(html)

    @pytest.mark.unit
    def test_many_inputs(self, parse_features):
        inputs = """
        <input type="text" placeholder="Name">
        <input type="email" required>
        <input type="date">
        <input type="number" min="0" max="100">
        """ * 100
        features = parse_features(f"<form>{inputs}</form>")
        assert 'input-placeholder' in features
        assert 'form-validation' in features
        assert 'input-datetime' in features

    @pytest.mark.unit
    def test_deeply_nested(self, parse_features):
        depth = 100
        html = "<div>" * depth + "Content" + "</div>" * depth
        assert isinstance(parse_features(html), set)

    @pytest.mark.unit
    def test_many_different_features(self, parse_features):
        html = """
        <main>
            <video src="v.mp4"></video>
            <audio src="a.mp3"></audio>
            <canvas></canvas>
            <dialog></dialog>
            <details><summary>S</summary></details>
            <meter value="0.5"></meter>
            <progress value="50" max="100"></progress>
        </main>
        """ * 50
        features = parse_features(html)
        for f in ('video', 'audio', 'canvas', 'dialog', 'details', 'meter', 'progress'):
            assert f in features

    @pytest.mark.unit
    def test_repeated_same_feature(self, parse_features):
        html = "<main></main>" * 1000
        assert 'html5semantic' in parse_features(html)


# ---------------------------------------------------------------------------
# False positive prevention
# ---------------------------------------------------------------------------

class TestFalsePositives:

    @pytest.mark.unit
    def test_element_in_comment_not_detected(self, parse_features):
        html = '<!-- <video src="v.mp4"></video> --><div>Content</div>'
        assert 'video' not in parse_features(html)

    @pytest.mark.unit
    def test_attributes_in_comment_not_detected(self, parse_features):
        html = '<!-- <input type="date" required placeholder="test"> --><input type="text">'
        features = parse_features(html)
        assert 'input-datetime' not in features
        assert 'input-placeholder' not in features

    @pytest.mark.unit
    def test_multiline_comment(self, parse_features):
        html = """
        <!--
            <video src="v.mp4">
                <source src="v.webm" type="video/webm">
                <track src="c.vtt">
            </video>
        -->
        <div>Content</div>
        """
        features = parse_features(html)
        assert 'video' not in features
        assert 'webvtt' not in features

    @pytest.mark.unit
    def test_actual_element_outside_comment(self, parse_features):
        html = """
        <!-- comment about <video> -->
        <video src="real-video.mp4"></video>
        """
        assert 'video' in parse_features(html)

    @pytest.mark.unit
    def test_style_selectors_not_detected(self, parse_features):
        html = """
        <style>
            video { width: 100%; }
            audio { margin: 10px; }
            [contenteditable] { border: 1px solid blue; }
        </style>
        <div>Content</div>
        """
        features = parse_features(html)
        assert 'video' not in features
        assert 'audio' not in features
        assert 'contenteditable' not in features

    @pytest.mark.unit
    def test_element_name_in_text(self, parse_features):
        html = "<p>The video element is used for embedding videos.</p>"
        assert 'video' not in parse_features(html)

    @pytest.mark.unit
    def test_attribute_name_in_text(self, parse_features):
        html = "<p>Use the contenteditable attribute to make elements editable.</p>"
        assert 'contenteditable' not in parse_features(html)

    @pytest.mark.unit
    def test_escaped_html_in_code(self, parse_features):
        html = '<pre><code>&lt;video src="v.mp4"&gt;&lt;/video&gt;</code></pre>'
        assert 'video' not in parse_features(html)

    @pytest.mark.unit
    def test_video_in_class_name(self, parse_features):
        html = '<div class="video-container">Content</div>'
        assert 'video' not in parse_features(html)

    @pytest.mark.unit
    def test_date_in_id(self, parse_features):
        html = '<div id="date-picker">Content</div>'
        assert 'input-datetime' not in parse_features(html)

    @pytest.mark.unit
    def test_required_in_class(self, parse_features):
        html = '<span class="required">*</span>'
        assert 'form-validation' not in parse_features(html)

    @pytest.mark.unit
    def test_svg_elements_not_custom(self, parse_features):
        html = """
        <svg>
            <defs>
                <linearGradient id="grad">
                    <stop offset="0%" stop-color="red"/>
                </linearGradient>
            </defs>
        </svg>
        """
        assert 'svg' in parse_features(html)

    @pytest.mark.unit
    def test_real_element_with_feature_class(self, parse_features):
        html = '<video class="video-player" src="v.mp4"></video>'
        assert 'video' in parse_features(html)

    @pytest.mark.unit
    def test_mixed_real_and_text_mentions(self, parse_features):
        html = """
        <main>
            <p>This page demonstrates the video element.</p>
            <video src="demo.mp4"></video>
        </main>
        """
        features = parse_features(html)
        assert 'video' in features
        assert 'html5semantic' in features


# ---------------------------------------------------------------------------
# State reset / parser reuse
# ---------------------------------------------------------------------------

class TestStateReset:

    @pytest.mark.unit
    def test_state_reset_between_parses(self, html_parser):
        features1 = html_parser.parse_string('<video src="v.mp4"></video>')
        assert 'video' in features1

        features2 = html_parser.parse_string('<div>No features</div>')
        assert 'video' not in features2

    @pytest.mark.unit
    def test_elements_found_reset(self, html_parser):
        html_parser.parse_string('<main>Content</main>')
        count1 = len(html_parser.elements_found)

        html_parser.parse_string('<div>Basic</div>')
        count2 = len(html_parser.elements_found)
        assert count2 == 0 or count2 != count1

    @pytest.mark.unit
    def test_attributes_found_reset(self, html_parser):
        html_parser.parse_string('<input required placeholder="test">')
        count1 = len(html_parser.attributes_found)

        html_parser.parse_string('<input type="text">')
        count2 = len(html_parser.attributes_found)
        assert count2 < count1

    @pytest.mark.unit
    def test_features_found_reset(self, html_parser):
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert 'video' in html_parser.features_found

        html_parser.parse_string("<audio src='a.mp3'></audio>")
        assert 'audio' in html_parser.features_found
        assert 'video' not in html_parser.features_found


class TestParserReuse:

    @pytest.mark.unit
    def test_reuse_multiple_times(self, html_parser):
        for i in range(10):
            features = html_parser.parse_string(f'<main>Content {i}</main>')
            assert 'html5semantic' in features

    @pytest.mark.unit
    def test_reuse_different_content(self, html_parser):
        features1 = html_parser.parse_string('<video src="v.mp4"></video>')
        assert 'video' in features1

        features2 = html_parser.parse_string('<main>Content</main>')
        assert 'html5semantic' in features2
        assert 'video' not in features2

        features3 = html_parser.parse_string('<input type="date">')
        assert 'input-datetime' in features3
        assert 'video' not in features3
        assert 'html5semantic' not in features3
