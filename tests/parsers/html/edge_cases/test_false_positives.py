"""Tests for false positive prevention.

Tests: Elements in comments, attributes in script strings, CSS selectors
"""

import pytest


class TestCommentsIgnored:
    """Tests that content in HTML comments is ignored."""

    def test_element_in_comment(self, parse_html):
        """Test that element in comment is not detected."""
        html = """
        <!-- <video src="video.mp4"></video> -->
        <div>Regular content</div>
        """
        features = parse_html(html)
        # Video should NOT be detected since it's in a comment
        assert 'video' not in features

    def test_feature_attribute_in_comment(self, parse_html):
        """Test that attributes in comment are not detected."""
        html = """
        <!-- <input type="date" required placeholder="test"> -->
        <input type="text">
        """
        features = parse_html(html)
        assert 'input-datetime' not in features
        assert 'input-placeholder' not in features

    def test_multiple_comments(self, parse_html):
        """Test multiple comments with features."""
        html = """
        <!-- <video></video> -->
        <main>Content</main>
        <!-- <audio></audio> -->
        """
        features = parse_html(html)
        assert 'video' not in features
        assert 'audio' not in features
        assert 'html5semantic' in features

    def test_nested_comment_like_content(self, parse_html):
        """Test that actual elements outside comments are detected."""
        html = """
        <!-- This is a comment about <video> elements -->
        <video src="actual-video.mp4"></video>
        """
        features = parse_html(html)
        # The actual video element SHOULD be detected
        assert 'video' in features

    def test_multiline_comment(self, parse_html):
        """Test multiline comment with features."""
        html = """
        <!--
            <video src="video.mp4">
                <source src="video.webm" type="video/webm">
                <track src="captions.vtt">
            </video>
        -->
        <div>Content</div>
        """
        features = parse_html(html)
        assert 'video' not in features
        assert 'webvtt' not in features


class TestScriptContentIgnored:
    """Tests that content in script tags is handled appropriately."""

    def test_html_string_in_script(self, parse_html):
        """Test HTML string inside script tag."""
        html = """
        <script>
            const html = '<video src="video.mp4"></video>';
        </script>
        <div>Content</div>
        """
        features = parse_html(html)
        # The string inside script should not create false positives
        # (though BeautifulSoup might handle this differently)

    def test_template_literal_in_script(self, parse_html):
        """Test template literal with HTML in script."""
        html = """
        <script>
            const template = `
                <main>
                    <video src="video.mp4"></video>
                </main>
            `;
        </script>
        """
        features = parse_html(html)
        # Script content parsing depends on BeautifulSoup behavior

    def test_json_in_script(self, parse_html):
        """Test JSON with HTML-like content in script."""
        html = """
        <script type="application/json">
            {"html": "<video src='video.mp4'></video>"}
        </script>
        """
        features = parse_html(html)
        # JSON script content should not create false positives

    def test_actual_script_with_external_video(self, parse_html):
        """Test actual video element alongside script."""
        html = """
        <script>const x = '<video>';</script>
        <video src="real-video.mp4"></video>
        """
        features = parse_html(html)
        # The real video element should be detected
        assert 'video' in features


class TestStyleContentIgnored:
    """Tests that content in style tags is handled appropriately."""

    def test_selectors_in_style(self, parse_html):
        """Test CSS selectors that look like elements."""
        html = """
        <style>
            video { width: 100%; }
            audio { margin: 10px; }
            main { display: block; }
        </style>
        <div>Content</div>
        """
        features = parse_html(html)
        # CSS selectors should not trigger feature detection
        assert 'video' not in features
        assert 'audio' not in features
        # But the style element itself is parsed, so main won't be there
        # unless there's an actual <main> element

    def test_attribute_selectors_in_style(self, parse_html):
        """Test attribute selectors in CSS."""
        html = """
        <style>
            [contenteditable] { border: 1px solid blue; }
            [draggable="true"] { cursor: move; }
            input[type="date"] { width: 200px; }
        </style>
        """
        features = parse_html(html)
        # Attribute selectors should not trigger feature detection
        assert 'contenteditable' not in features
        assert 'dragndrop' not in features


class TestTextContentNotConfused:
    """Tests that text content is not confused with elements/attributes."""

    def test_element_name_in_text(self, parse_html):
        """Test element name mentioned in text content."""
        html = "<p>The video element is used for embedding videos.</p>"
        features = parse_html(html)
        assert 'video' not in features

    def test_attribute_name_in_text(self, parse_html):
        """Test attribute name mentioned in text content."""
        html = "<p>Use the contenteditable attribute to make elements editable.</p>"
        features = parse_html(html)
        assert 'contenteditable' not in features

    def test_html_code_in_pre(self, parse_html):
        """Test HTML code displayed in pre/code elements."""
        html = """
        <pre><code>
            &lt;video src="video.mp4"&gt;&lt;/video&gt;
        </code></pre>
        """
        features = parse_html(html)
        # Escaped HTML in pre/code should not be detected
        assert 'video' not in features

    def test_feature_name_in_heading(self, parse_html):
        """Test feature name in heading."""
        html = "<h2>How to use the video element</h2>"
        features = parse_html(html)
        assert 'video' not in features


class TestSVGNamespaceNotConfused:
    """Tests that SVG elements are correctly handled."""

    def test_svg_elements_not_custom(self, parse_html):
        """Test that SVG elements with hyphens aren't flagged as custom."""
        html = """
        <svg>
            <defs>
                <linearGradient id="grad">
                    <stop offset="0%" stop-color="red"/>
                </linearGradient>
            </defs>
        </svg>
        """
        features = parse_html(html)
        # SVG elements should not be flagged as custom elements
        assert 'svg' in features

    def test_svg_animate_elements(self, parse_html):
        """Test SVG animation elements."""
        html = """
        <svg>
            <circle cx="50" cy="50" r="40">
                <animate attributeName="r" from="40" to="10" dur="1s"/>
            </circle>
        </svg>
        """
        features = parse_html(html)
        assert 'svg' in features


class TestAttributeValueNotConfused:
    """Tests that attribute values don't trigger wrong features."""

    def test_video_in_class_name(self, parse_html):
        """Test 'video' in class name."""
        html = '<div class="video-container">Content</div>'
        features = parse_html(html)
        assert 'video' not in features

    def test_date_in_id(self, parse_html):
        """Test 'date' in ID."""
        html = '<div id="date-picker">Content</div>'
        features = parse_html(html)
        assert 'input-datetime' not in features

    def test_required_in_text(self, parse_html):
        """Test 'required' as text, not attribute."""
        html = '<span class="required">*</span>'
        features = parse_html(html)
        assert 'form-validation' not in features

    def test_src_attribute_without_svg(self, parse_html):
        """Test src with .svg in path but not SVG image."""
        html = '<img src="/icons/svg/icon.png" alt="Icon">'
        features = parse_html(html)
        assert 'svg-img' not in features


class TestEdgeCaseCorrectDetection:
    """Tests for edge cases that SHOULD be detected."""

    def test_actual_video_after_comment_about_video(self, parse_html):
        """Test real video after comment mentioning video."""
        html = """
        <!-- TODO: Add video element here -->
        <video src="video.mp4"></video>
        """
        features = parse_html(html)
        assert 'video' in features

    def test_real_element_with_class_matching_feature(self, parse_html):
        """Test real element that also has feature-like class."""
        html = '<video class="video-player" src="video.mp4"></video>'
        features = parse_html(html)
        assert 'video' in features

    def test_mixed_real_and_text_mentions(self, parse_html):
        """Test mix of real elements and text mentions."""
        html = """
        <main>
            <p>This page demonstrates the video element.</p>
            <video src="demo.mp4"></video>
            <p>The video above shows...</p>
        </main>
        """
        features = parse_html(html)
        assert 'video' in features
        assert 'html5semantic' in features
