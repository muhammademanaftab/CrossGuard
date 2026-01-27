"""Tests for HTMLParser.parse_string() method.

Tests: String parsing, various input types, return values
"""

import pytest


class TestParseStringBasic:
    """Tests for basic parse_string functionality."""

    def test_parse_string_returns_set(self, html_parser):
        """Test that parse_string returns a set."""
        result = html_parser.parse_string("<div>Content</div>")
        assert isinstance(result, set)

    def test_parse_string_empty(self, html_parser):
        """Test parse_string with empty string."""
        result = html_parser.parse_string("")
        assert result == set()

    def test_parse_string_basic_html(self, html_parser):
        """Test parse_string with basic HTML."""
        result = html_parser.parse_string("<p>Hello</p>")
        assert isinstance(result, set)

    def test_parse_string_finds_feature(self, html_parser):
        """Test that parse_string finds features."""
        result = html_parser.parse_string("<main>Content</main>")
        assert 'html5semantic' in result


class TestParseStringFeatureDetection:
    """Tests for feature detection via parse_string."""

    def test_detect_single_feature(self, html_parser):
        """Test detection of single feature."""
        features = html_parser.parse_string("<video src='v.mp4'></video>")
        assert 'video' in features

    def test_detect_multiple_features(self, html_parser):
        """Test detection of multiple features."""
        html = """
        <main>
            <video src="video.mp4"></video>
            <audio src="audio.mp3"></audio>
            <canvas></canvas>
        </main>
        """
        features = html_parser.parse_string(html)
        assert 'html5semantic' in features
        assert 'video' in features
        assert 'audio' in features
        assert 'canvas' in features

    def test_detect_nested_features(self, html_parser):
        """Test detection of nested features."""
        html = """
        <main>
            <article>
                <figure>
                    <video src="video.mp4"></video>
                    <figcaption>Caption</figcaption>
                </figure>
            </article>
        </main>
        """
        features = html_parser.parse_string(html)
        assert 'html5semantic' in features
        assert 'video' in features

    def test_detect_attribute_features(self, html_parser):
        """Test detection of attribute-based features."""
        html = '<input type="text" placeholder="Enter name" required autofocus>'
        features = html_parser.parse_string(html)
        assert 'input-placeholder' in features
        assert 'form-validation' in features
        assert 'autofocus' in features


class TestParseStringInputVariations:
    """Tests for parse_string with various input variations."""

    def test_parse_string_multiline(self, html_parser):
        """Test parse_string with multiline HTML."""
        html = """
        <main>
            <section>
                <h1>Title</h1>
                <p>Content</p>
            </section>
        </main>
        """
        features = html_parser.parse_string(html)
        assert 'html5semantic' in features

    def test_parse_string_minified(self, html_parser):
        """Test parse_string with minified HTML."""
        html = "<main><video src='v.mp4'></video><audio src='a.mp3'></audio></main>"
        features = html_parser.parse_string(html)
        assert 'html5semantic' in features
        assert 'video' in features
        assert 'audio' in features

    def test_parse_string_with_doctype(self, html_parser):
        """Test parse_string with DOCTYPE."""
        html = "<!DOCTYPE html><html><body><main>Content</main></body></html>"
        features = html_parser.parse_string(html)
        assert 'html5semantic' in features

    def test_parse_string_fragment(self, html_parser):
        """Test parse_string with HTML fragment."""
        html = "<video src='video.mp4'></video>"
        features = html_parser.parse_string(html)
        assert 'video' in features


class TestParseStringStateManagement:
    """Tests for state management in parse_string."""

    def test_features_found_updated(self, html_parser):
        """Test that features_found attribute is updated."""
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert 'video' in html_parser.features_found

    def test_elements_found_updated(self, html_parser):
        """Test that elements_found attribute is updated."""
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert any(e['element'] == 'video' for e in html_parser.elements_found)

    def test_attributes_found_updated(self, html_parser):
        """Test that attributes_found attribute is updated."""
        html_parser.parse_string('<input placeholder="test">')
        assert any(a['attribute'] == 'placeholder' for a in html_parser.attributes_found)

    def test_state_reset_between_calls(self, html_parser):
        """Test that state is reset between parse_string calls."""
        # First call
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert 'video' in html_parser.features_found

        # Second call with different content
        html_parser.parse_string("<audio src='a.mp3'></audio>")
        assert 'audio' in html_parser.features_found
        assert 'video' not in html_parser.features_found


class TestParseStringReturnValue:
    """Tests for parse_string return value."""

    def test_return_value_is_set(self, html_parser):
        """Test that return value is a set."""
        result = html_parser.parse_string("<main>Content</main>")
        assert isinstance(result, set)

    def test_return_value_contains_strings(self, html_parser):
        """Test that return value contains strings."""
        result = html_parser.parse_string("<main>Content</main>")
        for feature in result:
            assert isinstance(feature, str)

    def test_return_value_matches_features_found(self, html_parser):
        """Test that return value matches features_found attribute."""
        result = html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        assert result == html_parser.features_found

    def test_no_duplicates_in_return(self, html_parser):
        """Test that return value has no duplicates."""
        html = "<main></main><main></main><main></main>"
        result = html_parser.parse_string(html)
        # Set by definition has no duplicates
        assert isinstance(result, set)
        # Check 'html5semantic' appears exactly once
        count = sum(1 for f in result if f == 'html5semantic')
        assert count == 1


class TestParseStringEdgeCases:
    """Tests for parse_string edge cases."""

    def test_parse_string_whitespace_only(self, html_parser):
        """Test parse_string with whitespace only."""
        result = html_parser.parse_string("   \n\t   ")
        assert result == set()

    def test_parse_string_text_only(self, html_parser):
        """Test parse_string with text only (no HTML)."""
        result = html_parser.parse_string("Just some text content")
        assert result == set()

    def test_parse_string_special_characters(self, html_parser):
        """Test parse_string with special characters."""
        result = html_parser.parse_string("<main>&lt;test&gt; &amp; &copy;</main>")
        assert 'html5semantic' in result

    def test_parse_string_unicode(self, html_parser):
        """Test parse_string with Unicode content."""
        result = html_parser.parse_string("<main>日本語 🎉 Ελληνικά</main>")
        assert 'html5semantic' in result


class TestParseStringConvenienceFunction:
    """Tests for parse_html_string convenience function."""

    def test_convenience_function_exists(self):
        """Test that convenience function exists."""
        from src.parsers.html_parser import parse_html_string
        assert callable(parse_html_string)

    def test_convenience_function_works(self):
        """Test that convenience function works."""
        from src.parsers.html_parser import parse_html_string
        result = parse_html_string("<main>Content</main>")
        assert 'html5semantic' in result

    def test_convenience_function_returns_set(self):
        """Test that convenience function returns set."""
        from src.parsers.html_parser import parse_html_string
        result = parse_html_string("<video src='v.mp4'></video>")
        assert isinstance(result, set)
