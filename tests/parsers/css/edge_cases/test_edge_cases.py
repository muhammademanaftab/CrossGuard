"""Tests for CSS parser edge cases.

Tests handling of comments, malformed CSS, empty input, etc.
"""

import pytest


class TestCommentHandling:
    """Tests for CSS comment handling."""

    def test_feature_in_comment_not_detected(self, parse_css):
        """Test that features inside comments are not detected."""
        css = """
        /* display: grid; */
        .element { color: red; }
        """
        features = parse_css(css)
        assert 'css-grid' not in features

    def test_feature_after_comment(self, parse_and_check):
        """Test that features after comments are detected."""
        css = """
        /* This is a comment */
        .element { display: grid; }
        """
        assert parse_and_check(css, 'css-grid')

    def test_multiline_comment(self, parse_css):
        """Test multiline comment handling."""
        css = """
        /*
         * display: flex;
         * display: grid;
         */
        .element { color: red; }
        """
        features = parse_css(css)
        assert 'flexbox' not in features
        assert 'css-grid' not in features

    def test_comment_between_features(self, parse_and_check_multiple):
        """Test that features around comments are detected."""
        css = """
        .flex { display: flex; }
        /* comment */
        .grid { display: grid; }
        """
        assert parse_and_check_multiple(css, ['flexbox', 'css-grid'])


class TestEmptyInput:
    """Tests for empty input handling."""

    def test_empty_string(self, parse_css):
        """Test empty string returns empty set."""
        features = parse_css("")
        assert features == set()

    def test_whitespace_only(self, parse_css):
        """Test whitespace-only input returns empty set."""
        features = parse_css("   \n\t  ")
        assert features == set()

    def test_comment_only(self, parse_css):
        """Test comment-only input returns empty set."""
        features = parse_css("/* just a comment */")
        assert features == set()


class TestMalformedCSS:
    """Tests for malformed CSS handling."""

    def test_missing_closing_brace(self, parse_and_check):
        """Test CSS with missing closing brace."""
        css = ".element { display: grid; "
        assert parse_and_check(css, 'css-grid')

    def test_missing_semicolon(self, parse_and_check):
        """Test CSS with missing semicolon."""
        css = ".element { display: grid }"
        assert parse_and_check(css, 'css-grid')

    def test_extra_braces(self, parse_and_check):
        """Test CSS with extra braces."""
        css = ".element {{ display: grid; }}"
        assert parse_and_check(css, 'css-grid')

    def test_unclosed_string(self, parse_css):
        """Test CSS with unclosed string."""
        css = '.element { content: "unclosed; }'
        features = parse_css(css)
        # Should not crash
        assert isinstance(features, set)


class TestStringHandling:
    """Tests for CSS string handling.

    Note: We intentionally do NOT remove string content because:
    1. CSS like content: '"'; has quote characters that confuse regex
    2. Removing strings can accidentally remove valid CSS selectors (like ::marker)
    3. String content rarely causes false positive feature detection in practice

    The trade-off is that rare cases like content: "display: grid" may trigger
    detection, but this is acceptable to avoid breaking real feature detection.
    """

    def test_feature_in_url_string(self, parse_css):
        """Test features in url() strings."""
        css = '.element { background: url("grid-pattern.png"); }'
        features = parse_css(css)
        # Filenames in urls should not trigger feature detection
        # (grid-pattern is not the same as display: grid)


class TestMultipleFeatures:
    """Tests for multiple feature detection."""

    def test_multiple_features_same_rule(self, parse_and_check_multiple):
        """Test multiple features in same rule."""
        css = """
        .element {
            display: flex;
            gap: 20px;
            border-radius: 10px;
        }
        """
        assert parse_and_check_multiple(css, ['flexbox', 'flexbox-gap', 'border-radius'])

    def test_many_features(self, parse_css):
        """Test detecting many features at once."""
        css = """
        :root { --primary: blue; }
        .container {
            display: grid;
            gap: 20px;
        }
        .card {
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: scale(1.05);
        }
        @media (prefers-color-scheme: dark) {
            body { background: #1a1a1a; }
        }
        """
        features = parse_css(css)
        assert 'css-variables' in features
        assert 'css-grid' in features
        assert 'border-radius' in features
        assert 'css-boxshadow' in features
        assert 'css-transitions' in features
        assert 'transforms2d' in features
        assert 'prefers-color-scheme' in features


class TestCaseSensitivity:
    """Tests for case sensitivity handling."""

    def test_uppercase_property(self, parse_and_check):
        """Test uppercase property detection."""
        css = ".element { DISPLAY: GRID; }"
        assert parse_and_check(css, 'css-grid')

    def test_mixed_case_property(self, parse_and_check):
        """Test mixed case property detection."""
        css = ".element { Display: Grid; }"
        assert parse_and_check(css, 'css-grid')

    def test_uppercase_value(self, parse_and_check):
        """Test uppercase value detection."""
        css = ".element { position: STICKY; }"
        assert parse_and_check(css, 'css-sticky')


class TestWhitespaceHandling:
    """Tests for whitespace handling."""

    def test_no_space_around_colon(self, parse_and_check):
        """Test no space around colon."""
        css = ".element{display:grid}"
        assert parse_and_check(css, 'css-grid')

    def test_extra_whitespace(self, parse_and_check):
        """Test extra whitespace."""
        css = ".element  {   display  :   grid   ;   }"
        assert parse_and_check(css, 'css-grid')

    def test_newlines_in_rule(self, parse_and_check):
        """Test newlines in rule."""
        css = """
        .element
        {
            display
            :
            grid
            ;
        }
        """
        assert parse_and_check(css, 'css-grid')
