"""Tests for CSS Text features.

Tests features: text-overflow, text-decoration, text-emphasis, text-stroke,
                text-size-adjust, word-break, wordwrap, css3-tabsize,
                css-letter-spacing, css-text-align-last, css-text-indent,
                css-text-justify, css-text-orientation, css-text-spacing,
                css-text-wrap-balance, css-hyphens, css-hanging-punctuation,
                css-line-clamp, kerning-pairs-ligatures, css-text-box-trim

Note: text-overflow pattern is: text-overflow\s*:\s*ellipsis
Only ellipsis is matched, not clip.

Note: text-decoration patterns include: text-decoration-line, text-decoration-style, text-decoration-color
text-decoration-thickness is not in the parser patterns.
"""

import pytest


class TestTextOverflow:
    """Tests for text-overflow detection."""

    def test_text_overflow_ellipsis(self, parse_and_check):
        """Test text-overflow: ellipsis detection."""
        css = ".truncate { text-overflow: ellipsis; }"
        assert parse_and_check(css, 'text-overflow')


class TestTextDecoration:
    """Tests for text-decoration detection."""

    def test_text_decoration_line(self, parse_and_check):
        """Test text-decoration-line detection."""
        css = ".link { text-decoration-line: underline; }"
        assert parse_and_check(css, 'text-decoration')

    def test_text_decoration_style(self, parse_and_check):
        """Test text-decoration-style detection."""
        css = ".link { text-decoration-style: wavy; }"
        assert parse_and_check(css, 'text-decoration')

    def test_text_decoration_color(self, parse_and_check):
        """Test text-decoration-color detection."""
        css = ".link { text-decoration-color: red; }"
        assert parse_and_check(css, 'text-decoration')


class TestTextEmphasis:
    """Tests for text-emphasis detection."""

    def test_text_emphasis(self, parse_and_check):
        """Test text-emphasis detection."""
        css = ".emphasized { text-emphasis: filled dot; }"
        assert parse_and_check(css, 'text-emphasis')

    def test_text_emphasis_style(self, parse_and_check):
        """Test text-emphasis-style detection."""
        css = ".emphasized { text-emphasis-style: circle; }"
        assert parse_and_check(css, 'text-emphasis')


class TestTextStroke:
    """Tests for text-stroke detection."""

    def test_webkit_text_stroke(self, parse_and_check):
        """Test -webkit-text-stroke detection."""
        css = ".outline { -webkit-text-stroke: 1px black; }"
        assert parse_and_check(css, 'text-stroke')

    def test_text_stroke(self, parse_and_check):
        """Test text-stroke detection."""
        css = ".outline { text-stroke: 1px black; }"
        assert parse_and_check(css, 'text-stroke')


class TestTextSizeAdjust:
    """Tests for text-size-adjust detection."""

    def test_text_size_adjust(self, parse_and_check):
        """Test text-size-adjust detection."""
        css = "body { text-size-adjust: 100%; }"
        assert parse_and_check(css, 'text-size-adjust')

    def test_webkit_text_size_adjust(self, parse_and_check):
        """Test -webkit-text-size-adjust detection."""
        css = "body { -webkit-text-size-adjust: 100%; }"
        assert parse_and_check(css, 'text-size-adjust')


class TestWordBreak:
    """Tests for word-break detection."""

    def test_word_break(self, parse_and_check):
        """Test word-break detection."""
        css = ".text { word-break: break-all; }"
        assert parse_and_check(css, 'word-break')

    def test_word_break_keep_all(self, parse_and_check):
        """Test word-break: keep-all detection."""
        css = ".text { word-break: keep-all; }"
        assert parse_and_check(css, 'word-break')


class TestWordWrap:
    """Tests for word-wrap/overflow-wrap detection."""

    def test_word_wrap(self, parse_and_check):
        """Test word-wrap detection."""
        css = ".text { word-wrap: break-word; }"
        assert parse_and_check(css, 'wordwrap')

    def test_overflow_wrap(self, parse_and_check):
        """Test overflow-wrap detection."""
        css = ".text { overflow-wrap: break-word; }"
        assert parse_and_check(css, 'wordwrap')


class TestTabSize:
    """Tests for tab-size detection."""

    def test_tab_size(self, parse_and_check):
        """Test tab-size detection."""
        css = "pre { tab-size: 4; }"
        assert parse_and_check(css, 'css3-tabsize')


class TestLetterSpacing:
    """Tests for letter-spacing detection."""

    def test_letter_spacing(self, parse_and_check):
        """Test letter-spacing detection."""
        css = ".text { letter-spacing: 0.05em; }"
        assert parse_and_check(css, 'css-letter-spacing')


class TestTextAlignLast:
    """Tests for text-align-last detection."""

    def test_text_align_last(self, parse_and_check):
        """Test text-align-last detection."""
        css = ".text { text-align-last: justify; }"
        assert parse_and_check(css, 'css-text-align-last')


class TestTextIndent:
    """Tests for text-indent detection."""

    def test_text_indent(self, parse_and_check):
        """Test text-indent detection."""
        css = "p { text-indent: 2em; }"
        assert parse_and_check(css, 'css-text-indent')


class TestTextJustify:
    """Tests for text-justify detection."""

    def test_text_justify(self, parse_and_check):
        """Test text-justify detection."""
        css = ".text { text-justify: inter-word; }"
        assert parse_and_check(css, 'css-text-justify')


class TestTextOrientation:
    """Tests for text-orientation detection."""

    def test_text_orientation(self, parse_and_check):
        """Test text-orientation detection."""
        css = ".vertical { text-orientation: upright; }"
        assert parse_and_check(css, 'css-text-orientation')


class TestTextSpacing:
    """Tests for text-spacing detection."""

    def test_text_spacing(self, parse_and_check):
        """Test text-spacing detection."""
        css = ".text { text-spacing: trim-start; }"
        assert parse_and_check(css, 'css-text-spacing')


class TestTextWrapBalance:
    """Tests for text-wrap: balance detection."""

    def test_text_wrap_balance(self, parse_and_check):
        """Test text-wrap: balance detection."""
        css = "h1 { text-wrap: balance; }"
        assert parse_and_check(css, 'css-text-wrap-balance')


class TestHyphens:
    """Tests for hyphens detection."""

    def test_hyphens(self, parse_and_check):
        """Test hyphens detection."""
        css = ".text { hyphens: auto; }"
        assert parse_and_check(css, 'css-hyphens')


class TestHangingPunctuation:
    """Tests for hanging-punctuation detection."""

    def test_hanging_punctuation(self, parse_and_check):
        """Test hanging-punctuation detection."""
        css = ".text { hanging-punctuation: first; }"
        assert parse_and_check(css, 'css-hanging-punctuation')


class TestLineClamp:
    """Tests for line-clamp detection."""

    def test_line_clamp(self, parse_and_check):
        """Test line-clamp detection."""
        css = ".truncate { line-clamp: 3; }"
        assert parse_and_check(css, 'css-line-clamp')

    def test_webkit_line_clamp(self, parse_and_check):
        """Test -webkit-line-clamp detection."""
        css = ".truncate { -webkit-line-clamp: 3; }"
        assert parse_and_check(css, 'css-line-clamp')


class TestKerningPairsLigatures:
    """Tests for kerning pairs and ligatures detection."""

    def test_text_rendering_optimize_legibility(self, parse_and_check):
        """Test text-rendering: optimizeLegibility detection."""
        css = ".text { text-rendering: optimizeLegibility; }"
        assert parse_and_check(css, 'kerning-pairs-ligatures')


class TestTextBoxTrim:
    """Tests for text-box-trim detection."""

    def test_text_box_trim(self, parse_and_check):
        """Test text-box-trim detection."""
        css = ".heading { text-box-trim: both; }"
        assert parse_and_check(css, 'css-text-box-trim')

    def test_leading_trim(self, parse_and_check):
        """Test leading-trim detection (older name)."""
        css = ".heading { leading-trim: both; }"
        assert parse_and_check(css, 'css-text-box-trim')
