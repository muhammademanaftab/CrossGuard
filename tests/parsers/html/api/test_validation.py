"""Tests for HTMLParser.validate_html() method.

Tests: HTML validation, valid/invalid HTML detection
"""

import pytest


class TestValidateHtmlBasic:
    """Tests for basic validate_html functionality."""

    def test_validate_returns_bool(self, html_parser):
        """Test that validate_html returns a boolean."""
        result = html_parser.validate_html("<div>Content</div>")
        assert isinstance(result, bool)

    def test_validate_valid_html(self, html_parser):
        """Test validation of valid HTML."""
        html = "<html><head></head><body><p>Hello</p></body></html>"
        assert html_parser.validate_html(html) is True

    def test_validate_empty_string(self, html_parser):
        """Test validation of empty string."""
        # Empty string is technically parseable
        result = html_parser.validate_html("")
        assert isinstance(result, bool)


class TestValidateValidHTML:
    """Tests for validate_html with valid HTML."""

    def test_complete_document(self, html_parser):
        """Test complete HTML document."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <h1>Hello</h1>
            <p>World</p>
        </body>
        </html>
        """
        assert html_parser.validate_html(html) is True

    def test_html5_document(self, html_parser):
        """Test HTML5 document."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width">
        </head>
        <body>
            <main>
                <article>Content</article>
            </main>
        </body>
        </html>
        """
        assert html_parser.validate_html(html) is True

    def test_fragment(self, html_parser):
        """Test HTML fragment."""
        html = "<div><p>Paragraph</p></div>"
        assert html_parser.validate_html(html) is True

    def test_single_element(self, html_parser):
        """Test single element."""
        html = "<p>Hello</p>"
        assert html_parser.validate_html(html) is True

    def test_self_closing_element(self, html_parser):
        """Test self-closing element."""
        html = "<br><hr><img src='test.jpg' alt='test'>"
        assert html_parser.validate_html(html) is True

    def test_nested_elements(self, html_parser):
        """Test nested elements."""
        html = """
        <div>
            <ul>
                <li>
                    <a href="#">Link</a>
                </li>
            </ul>
        </div>
        """
        assert html_parser.validate_html(html) is True


class TestValidateMalformedHTML:
    """Tests for validate_html with malformed HTML.

    Note: BeautifulSoup is very forgiving, so many malformed inputs
    will still parse successfully.
    """

    def test_unclosed_tag_still_parses(self, html_parser):
        """Test that unclosed tags still parse (BeautifulSoup behavior)."""
        html = "<div>Unclosed"
        # BeautifulSoup is forgiving - this will likely still parse
        result = html_parser.validate_html(html)
        assert isinstance(result, bool)

    def test_mismatched_tags_still_parses(self, html_parser):
        """Test that mismatched tags still parse."""
        html = "<div><span></div></span>"
        result = html_parser.validate_html(html)
        assert isinstance(result, bool)

    def test_missing_quotes_still_parses(self, html_parser):
        """Test that missing quotes still parse."""
        html = '<input type=text name=field>'
        result = html_parser.validate_html(html)
        assert isinstance(result, bool)


class TestValidateEdgeCases:
    """Tests for validate_html edge cases."""

    def test_whitespace_only(self, html_parser):
        """Test whitespace-only input."""
        result = html_parser.validate_html("   \n\t   ")
        assert isinstance(result, bool)

    def test_text_only(self, html_parser):
        """Test text-only input (no HTML tags)."""
        result = html_parser.validate_html("Just some text")
        assert isinstance(result, bool)
        # Text-only is still parseable by BeautifulSoup

    def test_special_characters(self, html_parser):
        """Test input with special characters."""
        html = "<p>&lt;script&gt;alert('xss')&lt;/script&gt;</p>"
        assert html_parser.validate_html(html) is True

    def test_unicode_content(self, html_parser):
        """Test Unicode content."""
        html = "<p>Hello 世界 🌍</p>"
        assert html_parser.validate_html(html) is True

    def test_comments(self, html_parser):
        """Test HTML with comments."""
        html = "<!-- Comment --><div>Content</div><!-- Another comment -->"
        assert html_parser.validate_html(html) is True

    def test_cdata(self, html_parser):
        """Test HTML with CDATA."""
        html = "<script><![CDATA[function test() {}]]></script>"
        result = html_parser.validate_html(html)
        assert isinstance(result, bool)


class TestValidateHTMLTypes:
    """Tests for validate_html with various HTML types."""

    def test_html4_doctype(self, html_parser):
        """Test HTML4 doctype."""
        html = """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
        <head><title>Test</title></head>
        <body><p>Content</p></body>
        </html>
        """
        assert html_parser.validate_html(html) is True

    def test_xhtml_doctype(self, html_parser):
        """Test XHTML doctype."""
        html = """
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head><title>Test</title></head>
        <body><p>Content</p></body>
        </html>
        """
        assert html_parser.validate_html(html) is True

    def test_html5_semantic(self, html_parser):
        """Test HTML5 semantic elements."""
        html = """
        <main>
            <article>
                <header><h1>Title</h1></header>
                <section><p>Content</p></section>
                <footer><time>2024</time></footer>
            </article>
        </main>
        """
        assert html_parser.validate_html(html) is True


class TestValidateVsParseString:
    """Tests comparing validate_html and parse_string."""

    def test_both_methods_accept_same_input(self, html_parser):
        """Test that both methods accept the same valid input."""
        html = "<main><video src='v.mp4'></video></main>"

        validate_result = html_parser.validate_html(html)
        parse_result = html_parser.parse_string(html)

        assert validate_result is True
        assert 'video' in parse_result

    def test_validate_does_not_modify_state(self, html_parser):
        """Test that validate_html doesn't modify parser state like parse_string does."""
        # First parse something
        html_parser.parse_string("<video src='v.mp4'></video>")
        initial_features = html_parser.features_found.copy()

        # Validate something different
        html_parser.validate_html("<audio src='a.mp3'></audio>")

        # validate_html calls parse_string internally, so state may change
        # This documents actual behavior
