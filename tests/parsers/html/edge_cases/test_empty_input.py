"""Tests for empty and minimal input handling.

Tests: Empty string, whitespace only, None-like inputs, minimal HTML
"""

import pytest


class TestEmptyString:
    """Tests for empty string input."""

    def test_empty_string(self, parse_html):
        """Test parsing empty string."""
        html = ""
        features = parse_html(html)
        assert features == set()

    def test_empty_string_returns_empty_set(self, html_parser):
        """Test that empty string returns empty set of features."""
        result = html_parser.parse_string("")
        assert isinstance(result, set)
        assert len(result) == 0


class TestWhitespaceOnly:
    """Tests for whitespace-only input."""

    def test_whitespace_only_spaces(self, parse_html):
        """Test parsing whitespace-only (spaces)."""
        html = "     "
        features = parse_html(html)
        assert features == set()

    def test_whitespace_only_newlines(self, parse_html):
        """Test parsing whitespace-only (newlines)."""
        html = "\n\n\n"
        features = parse_html(html)
        assert features == set()

    def test_whitespace_only_tabs(self, parse_html):
        """Test parsing whitespace-only (tabs)."""
        html = "\t\t\t"
        features = parse_html(html)
        assert features == set()

    def test_whitespace_mixed(self, parse_html):
        """Test parsing mixed whitespace."""
        html = "  \n\t  \n  \t  "
        features = parse_html(html)
        assert features == set()


class TestMinimalHTML:
    """Tests for minimal valid HTML."""

    def test_minimal_doctype_only(self, parse_html):
        """Test minimal doctype only."""
        html = "<!DOCTYPE html>"
        features = parse_html(html)
        assert features == set()

    def test_minimal_html_tags(self, parse_html):
        """Test minimal html tags."""
        html = "<html></html>"
        features = parse_html(html)
        assert features == set()

    def test_minimal_head_body(self, parse_html):
        """Test minimal head and body."""
        html = "<html><head></head><body></body></html>"
        features = parse_html(html)
        assert features == set()

    def test_single_element(self, parse_html):
        """Test single element."""
        html = "<div></div>"
        features = parse_html(html)
        assert features == set()

    def test_single_self_closing(self, parse_html):
        """Test single self-closing element."""
        html = "<br>"
        features = parse_html(html)
        assert features == set()

    def test_single_text_node(self, parse_html):
        """Test single text node (no HTML)."""
        html = "Just some text"
        features = parse_html(html)
        assert features == set()


class TestNoneAndInvalid:
    """Tests for None and invalid input handling."""

    def test_none_input(self, html_parser):
        """Test None input handling."""
        # Depending on implementation, this might raise or handle gracefully
        try:
            result = html_parser.parse_string(None)
            # If it doesn't raise, it should return empty set
            assert result == set() or isinstance(result, set)
        except (TypeError, AttributeError):
            # Expected behavior for None input
            pass

    def test_numeric_input(self, html_parser):
        """Test numeric input handling."""
        try:
            result = html_parser.parse_string(123)
            # If it doesn't raise, check result type
            assert isinstance(result, set)
        except (TypeError, AttributeError):
            # Expected behavior
            pass


class TestEmptyElements:
    """Tests for empty HTML5 elements."""

    def test_empty_video(self, parse_html):
        """Test empty video element."""
        html = "<video></video>"
        features = parse_html(html)
        assert 'video' in features

    def test_empty_audio(self, parse_html):
        """Test empty audio element."""
        html = "<audio></audio>"
        features = parse_html(html)
        assert 'audio' in features

    def test_empty_canvas(self, parse_html):
        """Test empty canvas element."""
        html = "<canvas></canvas>"
        features = parse_html(html)
        assert 'canvas' in features

    def test_empty_dialog(self, parse_html):
        """Test empty dialog element."""
        html = "<dialog></dialog>"
        features = parse_html(html)
        assert 'dialog' in features

    def test_empty_details(self, parse_html):
        """Test empty details element."""
        html = "<details></details>"
        features = parse_html(html)
        assert 'details' in features


class TestResetBetweenParses:
    """Tests for state reset between parses."""

    def test_state_reset(self, html_parser):
        """Test that parser state is reset between parses."""
        # First parse with features
        html1 = '<video src="video.mp4"></video>'
        features1 = html_parser.parse_string(html1)
        assert 'video' in features1

        # Second parse without features
        html2 = '<div>No features</div>'
        features2 = html_parser.parse_string(html2)
        assert 'video' not in features2

    def test_elements_found_reset(self, html_parser):
        """Test that elements_found is reset between parses."""
        html_parser.parse_string('<main>Content</main>')
        count1 = len(html_parser.elements_found)

        html_parser.parse_string('<div>Basic</div>')
        count2 = len(html_parser.elements_found)

        # After parsing basic div, elements_found should be empty or different
        assert count2 == 0 or count2 != count1

    def test_attributes_found_reset(self, html_parser):
        """Test that attributes_found is reset between parses."""
        html_parser.parse_string('<input required placeholder="test">')
        count1 = len(html_parser.attributes_found)

        html_parser.parse_string('<input type="text">')
        count2 = len(html_parser.attributes_found)

        # Attributes should be reset
        assert count2 < count1


class TestParserReuse:
    """Tests for parser reuse."""

    def test_parser_reuse_multiple_times(self, html_parser):
        """Test that parser can be reused multiple times."""
        for i in range(10):
            html = f'<main>Content {i}</main>'
            features = html_parser.parse_string(html)
            assert 'html5semantic' in features

    def test_parser_reuse_different_content(self, html_parser):
        """Test parser reuse with different content types."""
        # Video
        features1 = html_parser.parse_string('<video src="v.mp4"></video>')
        assert 'video' in features1

        # Semantic
        features2 = html_parser.parse_string('<main>Content</main>')
        assert 'html5semantic' in features2
        assert 'video' not in features2

        # Form
        features3 = html_parser.parse_string('<input type="date">')
        assert 'input-datetime' in features3
        assert 'video' not in features3
        assert 'html5semantic' not in features3
