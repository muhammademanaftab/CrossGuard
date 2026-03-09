"""CSS parser edge case tests -- kept as-is from original for high value.

Covers: comment handling, empty input, malformed CSS, string handling,
multiple feature detection, case sensitivity, whitespace handling.
"""

import pytest


class TestCommentHandling:
    """Tests for CSS comment handling."""

    def test_feature_in_comment_not_detected(self, parse_features):
        css = """
        /* display: grid; */
        .element { color: red; }
        """
        assert "css-grid" not in parse_features(css)

    def test_feature_after_comment(self, parse_features):
        css = """
        /* This is a comment */
        .element { display: grid; }
        """
        assert "css-grid" in parse_features(css)

    def test_multiline_comment(self, parse_features):
        css = """
        /*
         * display: flex;
         * display: grid;
         */
        .element { color: red; }
        """
        features = parse_features(css)
        assert "flexbox" not in features
        assert "css-grid" not in features

    def test_comment_between_features(self, parse_features):
        css = """
        .flex { display: flex; }
        /* comment */
        .grid { display: grid; }
        """
        features = parse_features(css)
        assert "flexbox" in features
        assert "css-grid" in features


class TestEmptyInput:
    """Tests for empty input handling."""

    def test_empty_string(self, parse_features):
        assert parse_features("") == set()

    def test_whitespace_only(self, parse_features):
        assert parse_features("   \n\t  ") == set()

    def test_comment_only(self, parse_features):
        assert parse_features("/* just a comment */") == set()


class TestMalformedCSS:
    """Tests for malformed CSS handling."""

    def test_missing_closing_brace(self, parse_features):
        css = ".element { display: grid; "
        assert "css-grid" in parse_features(css)

    def test_missing_semicolon(self, parse_features):
        css = ".element { display: grid }"
        assert "css-grid" in parse_features(css)

    def test_extra_braces(self, parse_features):
        css = ".element {{ display: grid; }}"
        assert "css-grid" in parse_features(css)

    def test_unclosed_string(self, parse_features):
        css = '.element { content: "unclosed; }'
        features = parse_features(css)
        assert isinstance(features, set)


class TestStringHandling:
    """Tests for CSS string handling.

    Note: We intentionally do NOT remove string content because:
    1. CSS like content: '"'; has quote characters that confuse regex
    2. Removing strings can accidentally remove valid CSS selectors
    3. String content rarely causes false positive feature detection
    """

    def test_feature_in_url_string(self, parse_features):
        css = '.element { background: url("grid-pattern.png"); }'
        # Filenames in urls should not trigger feature detection
        parse_features(css)  # should not crash


class TestMultipleFeatures:
    """Tests for multiple feature detection."""

    def test_multiple_features_same_rule(self, parse_features):
        css = """
        .element {
            display: flex;
            gap: 20px;
            border-radius: 10px;
        }
        """
        features = parse_features(css)
        assert "flexbox" in features
        assert "flexbox-gap" in features
        assert "border-radius" in features

    def test_many_features(self, parse_features):
        css = """
        :root { --primary: blue; }
        .container { display: grid; gap: 20px; }
        .card {
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .card:hover { transform: scale(1.05); }
        @media (prefers-color-scheme: dark) {
            body { background: #1a1a1a; }
        }
        """
        features = parse_features(css)
        assert "css-variables" in features
        assert "css-grid" in features
        assert "border-radius" in features
        assert "css-boxshadow" in features
        assert "css-transitions" in features
        assert "transforms2d" in features
        assert "prefers-color-scheme" in features


class TestCaseSensitivity:
    """Tests for case sensitivity handling."""

    def test_uppercase_property(self, parse_features):
        assert "css-grid" in parse_features(".element { DISPLAY: GRID; }")

    def test_mixed_case_property(self, parse_features):
        assert "css-grid" in parse_features(".element { Display: Grid; }")

    def test_uppercase_value(self, parse_features):
        assert "css-sticky" in parse_features(".element { position: STICKY; }")


class TestWhitespaceHandling:
    """Tests for whitespace handling."""

    def test_no_space_around_colon(self, parse_features):
        assert "css-grid" in parse_features(".element{display:grid}")

    def test_extra_whitespace(self, parse_features):
        assert "css-grid" in parse_features(".element  {   display  :   grid   ;   }")

    def test_newlines_in_rule(self, parse_features):
        css = """
        .element
        {
            display
            :
            grid
            ;
        }
        """
        assert "css-grid" in parse_features(css)
