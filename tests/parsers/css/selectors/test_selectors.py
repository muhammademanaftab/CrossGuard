"""Tests for CSS Selector features.

Tests features: css-sel2, css-sel3, css-gencontent, css-first-letter, css-first-line,
                css-selection, css-placeholder, css-marker-pseudo, css-case-insensitive,
                css-optional-pseudo, css-placeholder-shown, css-default-pseudo,
                css-indeterminate-pseudo, css-dir-pseudo, css-any-link, css-read-only-write,
                css-cascade-scope, css-matches-pseudo, css-has, css-focus-within,
                css-focus-visible, css-in-out-of-range, css-not-sel-list, css-nth-child-of

Note: css-sel3 patterns include: :nth-child, :nth-of-type, :first-of-type, :last-of-type, :not
:nth-last-child is not in the parser patterns.

Note: css-cascade-scope pattern is @scope (not :scope) in the merged feature maps.
"""

import pytest


class TestCSS2Selectors:
    """Tests for CSS 2.1 Selectors detection."""

    def test_attribute_selector(self, parse_and_check):
        """Test attribute selector detection."""
        css = "[type] { color: red; }"
        assert parse_and_check(css, 'css-sel2')

    def test_hover_pseudo(self, parse_and_check):
        """Test :hover pseudo-class detection."""
        css = "a:hover { color: blue; }"
        assert parse_and_check(css, 'css-sel2')

    def test_active_pseudo(self, parse_and_check):
        """Test :active pseudo-class detection."""
        css = "button:active { background: gray; }"
        assert parse_and_check(css, 'css-sel2')

    def test_focus_pseudo(self, parse_and_check):
        """Test :focus pseudo-class detection."""
        css = "input:focus { outline: 2px solid blue; }"
        assert parse_and_check(css, 'css-sel2')


class TestCSS3Selectors:
    """Tests for CSS3 Selectors detection."""

    def test_nth_child(self, parse_and_check):
        """Test :nth-child() detection."""
        css = "li:nth-child(odd) { background: #eee; }"
        assert parse_and_check(css, 'css-sel3')

    def test_nth_of_type(self, parse_and_check):
        """Test :nth-of-type() detection."""
        css = "p:nth-of-type(2n) { color: gray; }"
        assert parse_and_check(css, 'css-sel3')

    def test_first_of_type(self, parse_and_check):
        """Test :first-of-type detection."""
        css = "p:first-of-type { font-weight: bold; }"
        assert parse_and_check(css, 'css-sel3')

    def test_last_of_type(self, parse_and_check):
        """Test :last-of-type detection."""
        css = "li:last-of-type { border: none; }"
        assert parse_and_check(css, 'css-sel3')

    def test_not_selector(self, parse_and_check):
        """Test :not() detection."""
        css = "input:not([type='submit']) { border: 1px solid; }"
        assert parse_and_check(css, 'css-sel3')


class TestGeneratedContent:
    """Tests for CSS Generated Content detection."""

    def test_before_pseudo(self, parse_and_check):
        """Test ::before detection."""
        css = ".item::before { content: '•'; }"
        assert parse_and_check(css, 'css-gencontent')

    def test_after_pseudo(self, parse_and_check):
        """Test ::after detection."""
        css = ".item::after { content: ' →'; }"
        assert parse_and_check(css, 'css-gencontent')

    def test_before_single_colon(self, parse_and_check):
        """Test :before (single colon) detection."""
        css = ".item:before { content: '•'; }"
        assert parse_and_check(css, 'css-gencontent')

    def test_after_single_colon(self, parse_and_check):
        """Test :after (single colon) detection."""
        css = ".item:after { content: ' →'; }"
        assert parse_and_check(css, 'css-gencontent')

    def test_content_property(self, parse_and_check):
        """Test content property detection."""
        css = ".quote::before { content: open-quote; }"
        assert parse_and_check(css, 'css-gencontent')


class TestFirstLetter:
    """Tests for ::first-letter detection."""

    def test_first_letter(self, parse_and_check):
        """Test ::first-letter detection."""
        css = "p::first-letter { font-size: 2em; }"
        assert parse_and_check(css, 'css-first-letter')

    def test_first_letter_single_colon(self, parse_and_check):
        """Test :first-letter (single colon) detection."""
        css = "p:first-letter { font-size: 2em; }"
        assert parse_and_check(css, 'css-first-letter')


class TestFirstLine:
    """Tests for ::first-line detection."""

    def test_first_line(self, parse_and_check):
        """Test ::first-line detection."""
        css = "p::first-line { font-weight: bold; }"
        assert parse_and_check(css, 'css-first-line')

    def test_first_line_single_colon(self, parse_and_check):
        """Test :first-line (single colon) detection."""
        css = "p:first-line { font-weight: bold; }"
        assert parse_and_check(css, 'css-first-line')


class TestSelection:
    """Tests for ::selection detection."""

    def test_selection(self, parse_and_check):
        """Test ::selection detection."""
        css = "::selection { background: yellow; color: black; }"
        assert parse_and_check(css, 'css-selection')


class TestPlaceholder:
    """Tests for ::placeholder detection."""

    def test_placeholder(self, parse_and_check):
        """Test ::placeholder detection."""
        css = "input::placeholder { color: gray; }"
        assert parse_and_check(css, 'css-placeholder')

    def test_webkit_input_placeholder(self, parse_and_check):
        """Test ::-webkit-input-placeholder detection."""
        css = "input::-webkit-input-placeholder { color: gray; }"
        assert parse_and_check(css, 'css-placeholder')


class TestMarkerPseudo:
    """Tests for ::marker detection."""

    def test_marker(self, parse_and_check):
        """Test ::marker detection."""
        css = "li::marker { color: red; }"
        assert parse_and_check(css, 'css-marker-pseudo')


class TestCaseInsensitive:
    """Tests for case-insensitive attribute selector detection."""

    def test_case_insensitive_attribute(self, parse_and_check):
        """Test case-insensitive attribute selector detection."""
        css = "[type='text' i] { border: 1px solid; }"
        assert parse_and_check(css, 'css-case-insensitive')


class TestOptionalPseudo:
    """Tests for :optional and :required detection."""

    def test_optional(self, parse_and_check):
        """Test :optional detection."""
        css = "input:optional { border-color: gray; }"
        assert parse_and_check(css, 'css-optional-pseudo')

    def test_required(self, parse_and_check):
        """Test :required detection."""
        css = "input:required { border-color: red; }"
        assert parse_and_check(css, 'css-optional-pseudo')


class TestPlaceholderShown:
    """Tests for :placeholder-shown detection."""

    def test_placeholder_shown(self, parse_and_check):
        """Test :placeholder-shown detection."""
        css = "input:placeholder-shown { border-style: dashed; }"
        assert parse_and_check(css, 'css-placeholder-shown')


class TestDefaultPseudo:
    """Tests for :default detection."""

    def test_default(self, parse_and_check):
        """Test :default detection."""
        css = "button:default { font-weight: bold; }"
        assert parse_and_check(css, 'css-default-pseudo')


class TestIndeterminatePseudo:
    """Tests for :indeterminate detection."""

    def test_indeterminate(self, parse_and_check):
        """Test :indeterminate detection."""
        css = "input:indeterminate { opacity: 0.5; }"
        assert parse_and_check(css, 'css-indeterminate-pseudo')


class TestDirPseudo:
    """Tests for :dir() detection."""

    def test_dir_ltr(self, parse_and_check):
        """Test :dir(ltr) detection."""
        css = ":dir(ltr) { text-align: left; }"
        assert parse_and_check(css, 'css-dir-pseudo')

    def test_dir_rtl(self, parse_and_check):
        """Test :dir(rtl) detection."""
        css = ":dir(rtl) { text-align: right; }"
        assert parse_and_check(css, 'css-dir-pseudo')


class TestAnyLink:
    """Tests for :any-link detection."""

    def test_any_link(self, parse_and_check):
        """Test :any-link detection."""
        css = ":any-link { color: blue; }"
        assert parse_and_check(css, 'css-any-link')


class TestReadOnlyWrite:
    """Tests for :read-only and :read-write detection."""

    def test_read_only(self, parse_and_check):
        """Test :read-only detection."""
        css = "input:read-only { background: #eee; }"
        assert parse_and_check(css, 'css-read-only-write')

    def test_read_write(self, parse_and_check):
        """Test :read-write detection."""
        css = "input:read-write { background: white; }"
        assert parse_and_check(css, 'css-read-only-write')


class TestScopeRule:
    """Tests for @scope rule detection (css-cascade-scope)."""

    def test_scope_rule(self, parse_and_check):
        """Test @scope rule detection."""
        css = "@scope (.card) { h2 { color: blue; } }"
        assert parse_and_check(css, 'css-cascade-scope')

    def test_scope_with_limit(self, parse_and_check):
        """Test @scope with limit detection."""
        css = "@scope (.card) to (.card-footer) { p { margin: 0; } }"
        assert parse_and_check(css, 'css-cascade-scope')


class TestMatchesPseudo:
    """Tests for :is(), :where(), :matches() detection."""

    def test_is_pseudo(self, parse_and_check):
        """Test :is() detection."""
        css = ":is(h1, h2, h3) { margin-top: 1em; }"
        assert parse_and_check(css, 'css-matches-pseudo')

    def test_where_pseudo(self, parse_and_check):
        """Test :where() detection."""
        css = ":where(article, section) p { line-height: 1.5; }"
        assert parse_and_check(css, 'css-matches-pseudo')

    def test_matches_pseudo(self, parse_and_check):
        """Test :matches() detection."""
        css = ":matches(h1, h2) { color: navy; }"
        assert parse_and_check(css, 'css-matches-pseudo')


class TestHasPseudo:
    """Tests for :has() detection."""

    def test_has(self, parse_and_check):
        """Test :has() detection."""
        css = "article:has(img) { padding: 20px; }"
        assert parse_and_check(css, 'css-has')

    def test_has_direct_child(self, parse_and_check):
        """Test :has(> ...) detection."""
        css = "div:has(> p) { border: 1px solid; }"
        assert parse_and_check(css, 'css-has')


class TestFocusWithin:
    """Tests for :focus-within detection."""

    def test_focus_within(self, parse_and_check):
        """Test :focus-within detection."""
        css = "form:focus-within { box-shadow: 0 0 5px blue; }"
        assert parse_and_check(css, 'css-focus-within')


class TestFocusVisible:
    """Tests for :focus-visible detection."""

    def test_focus_visible(self, parse_and_check):
        """Test :focus-visible detection."""
        css = "button:focus-visible { outline: 2px solid blue; }"
        assert parse_and_check(css, 'css-focus-visible')


class TestInOutOfRange:
    """Tests for :in-range and :out-of-range detection."""

    def test_in_range(self, parse_and_check):
        """Test :in-range detection."""
        css = "input:in-range { border-color: green; }"
        assert parse_and_check(css, 'css-in-out-of-range')

    def test_out_of_range(self, parse_and_check):
        """Test :out-of-range detection."""
        css = "input:out-of-range { border-color: red; }"
        assert parse_and_check(css, 'css-in-out-of-range')


class TestNotSelectorList:
    """Tests for :not() with selector list detection."""

    def test_not_selector_list(self, parse_and_check):
        """Test :not() with selector list detection."""
        css = "input:not([type='submit'], [type='reset']) { width: 100%; }"
        assert parse_and_check(css, 'css-not-sel-list')


class TestNthChildOf:
    """Tests for :nth-child() with 'of' selector detection."""

    def test_nth_child_of(self, parse_and_check):
        """Test :nth-child(... of ...) detection."""
        css = "li:nth-child(2 of .important) { font-weight: bold; }"
        assert parse_and_check(css, 'css-nth-child-of')
