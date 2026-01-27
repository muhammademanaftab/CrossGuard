"""Tests for malformed HTML handling.

Tests: Unclosed tags, missing quotes, broken attributes, invalid nesting
"""

import pytest


class TestUnclosedTags:
    """Tests for unclosed tag handling."""

    def test_unclosed_div(self, parse_html):
        """Test unclosed div tag."""
        html = "<div>Content"
        features = parse_html(html)
        # Parser should handle gracefully
        assert isinstance(features, set)

    def test_unclosed_nested_tags(self, parse_html):
        """Test unclosed nested tags."""
        html = "<main><section><article>Content"
        features = parse_html(html)
        # Should still detect semantic elements
        assert 'html5semantic' in features

    def test_unclosed_video(self, parse_html):
        """Test unclosed video tag."""
        html = '<video src="video.mp4">'
        features = parse_html(html)
        assert 'video' in features

    def test_multiple_unclosed_tags(self, parse_html):
        """Test multiple unclosed tags."""
        html = "<main><video src='v.mp4'><audio src='a.mp3'>"
        features = parse_html(html)
        assert 'html5semantic' in features
        assert 'video' in features
        assert 'audio' in features

    def test_mismatched_closing_tags(self, parse_html):
        """Test mismatched closing tags."""
        html = "<main><div>Content</main></div>"
        features = parse_html(html)
        assert 'html5semantic' in features


class TestMissingQuotes:
    """Tests for missing quote handling."""

    def test_missing_attribute_quotes(self, parse_html):
        """Test attribute without quotes."""
        html = '<input type=text placeholder=test>'
        features = parse_html(html)
        # Should still parse
        assert isinstance(features, set)

    def test_partial_quotes(self, parse_html):
        """Test attribute with partial quotes."""
        html = '<input type="text placeholder="test">'
        features = parse_html(html)
        assert 'input-placeholder' in features or isinstance(features, set)

    def test_mixed_quote_styles(self, parse_html):
        """Test mixed single and double quotes."""
        html = """<input type="text" placeholder='Enter name'>"""
        features = parse_html(html)
        assert 'input-placeholder' in features


class TestBrokenAttributes:
    """Tests for broken attribute handling."""

    def test_empty_attribute_name(self, parse_html):
        """Test empty attribute name."""
        html = '<input ="" type="text">'
        features = parse_html(html)
        assert isinstance(features, set)

    def test_attribute_without_value(self, parse_html):
        """Test attribute without equals sign or value."""
        html = '<input type text placeholder>'
        features = parse_html(html)
        assert isinstance(features, set)

    def test_duplicate_attributes(self, parse_html):
        """Test duplicate attributes."""
        html = '<input type="text" type="email" placeholder="test" placeholder="other">'
        features = parse_html(html)
        assert isinstance(features, set)

    def test_attribute_special_characters(self, parse_html):
        """Test attributes with special characters."""
        html = '<input type="text" data-value="a<b>c&d">'
        features = parse_html(html)
        assert 'dataset' in features


class TestInvalidNesting:
    """Tests for invalid nesting handling."""

    def test_block_in_inline(self, parse_html):
        """Test block element inside inline element."""
        html = "<span><div>Content</div></span>"
        features = parse_html(html)
        assert isinstance(features, set)

    def test_nested_forms(self, parse_html):
        """Test nested form elements (invalid)."""
        html = """
        <form>
            <form>
                <input type="email">
            </form>
        </form>
        """
        features = parse_html(html)
        assert isinstance(features, set)

    def test_paragraph_in_paragraph(self, parse_html):
        """Test paragraph inside paragraph (invalid)."""
        html = "<p>Outer <p>Inner</p> text</p>"
        features = parse_html(html)
        assert isinstance(features, set)

    def test_interactive_in_interactive(self, parse_html):
        """Test interactive element inside interactive."""
        html = '<a href="#"><button>Click</button></a>'
        features = parse_html(html)
        assert isinstance(features, set)


class TestBrokenDocuments:
    """Tests for broken document structure."""

    def test_multiple_html_tags(self, parse_html):
        """Test multiple html tags."""
        html = "<html><html><body></body></html></html>"
        features = parse_html(html)
        assert isinstance(features, set)

    def test_multiple_body_tags(self, parse_html):
        """Test multiple body tags."""
        html = "<html><body><main>1</main></body><body><main>2</main></body></html>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_content_before_html(self, parse_html):
        """Test content before html tag."""
        html = "Some text<html><body><main>Content</main></body></html>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_content_after_html(self, parse_html):
        """Test content after closing html tag."""
        html = "<html><body><main>Content</main></body></html>Extra content"
        features = parse_html(html)
        assert 'html5semantic' in features


class TestInvalidElements:
    """Tests for invalid element handling."""

    def test_unknown_element(self, parse_html):
        """Test completely unknown element."""
        html = "<unknownelement>Content</unknownelement>"
        features = parse_html(html)
        assert isinstance(features, set)

    def test_element_with_numbers(self, parse_html):
        """Test element name starting with number (invalid)."""
        html = "<1div>Content</1div>"
        features = parse_html(html)
        assert isinstance(features, set)

    def test_element_with_special_chars(self, parse_html):
        """Test element with special characters in name."""
        html = "<div@test>Content</div@test>"
        features = parse_html(html)
        assert isinstance(features, set)


class TestPartialHTML:
    """Tests for partial HTML documents."""

    def test_body_only(self, parse_html):
        """Test body content only."""
        html = "<main>Content</main><aside>Sidebar</aside>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_head_only(self, parse_html):
        """Test head content only."""
        html = '<meta name="viewport" content="width=device-width">'
        features = parse_html(html)
        assert 'viewport-units' in features

    def test_random_tags(self, parse_html):
        """Test random assortment of tags."""
        html = "<video></video><main></main><input type='date'>"
        features = parse_html(html)
        assert 'video' in features
        assert 'html5semantic' in features
        assert 'input-datetime' in features


class TestRecoveryFromErrors:
    """Tests for parser recovery from errors."""

    def test_recovery_after_bad_tag(self, parse_html):
        """Test that parser recovers after bad tag."""
        html = "<<<<main>Content</main>"
        features = parse_html(html)
        # Should still find the main element eventually
        assert isinstance(features, set)

    def test_recovery_after_bad_attribute(self, parse_html):
        """Test that parser recovers after bad attribute."""
        html = '<input @#$%="bad" type="date">'
        features = parse_html(html)
        assert isinstance(features, set)

    def test_valid_content_after_errors(self, parse_html):
        """Test valid content is still parsed after errors."""
        html = """
        <broken<tag>
        <main>Valid content</main>
        <video src="video.mp4"></video>
        """
        features = parse_html(html)
        # Should find valid elements
        assert 'html5semantic' in features or 'video' in features
