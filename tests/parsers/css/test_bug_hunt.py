"""Bug hunt tests — systematic checks for false positives, false negatives,
pattern cross-contamination, duplicate keys, and statistics categorization.

Each test documents a specific issue found via pattern analysis.
Tests marked 'BUG' document current broken behavior; flip the assertion
once the underlying code is fixed.
"""

import pytest
from src.parsers.css_parser import CSSParser


@pytest.fixture
def css_parser():
    return CSSParser()


@pytest.fixture
def parse_css(css_parser):
    def _parse(css: str) -> set:
        return css_parser.parse_string(css)
    return _parse


# ═══════════════════════════════════════════════════════════════════════════
# BUG 1: Duplicate key 'css-cascade-scope' — :scope pattern LOST
# ═══════════════════════════════════════════════════════════════════════════

class TestCascadeScopeOverwrite:
    """css-cascade-scope is defined in BOTH CSS_SELECTORS (with :scope pattern)
    and CSS_ADDITIONAL_1 (with @scope pattern). The later dict overwrites the
    earlier, so the :scope pseudo-class pattern is lost."""

    def test_at_scope_rule_detected(self, parse_css):
        """@scope at-rule IS detected (from CSS_ADDITIONAL_1)."""
        assert 'css-cascade-scope' in parse_css(
            "@scope (.card) { .title { color: red; } }"
        )

    def test_scope_pseudo_class_detected(self, parse_css):
        """:scope pseudo-class is correctly detected. Both :scope and @scope
        patterns are merged into a single css-cascade-scope entry."""
        features = parse_css(":scope > .child { color: red; }")
        assert 'css-cascade-scope' in features


# ═══════════════════════════════════════════════════════════════════════════
# BUG 2: Duplicate key 'css-color-adjust' (harmless)
# ═══════════════════════════════════════════════════════════════════════════

class TestColorAdjustDuplicate:
    """css-color-adjust appears in both CSS_MISC and CSS_ADDITIONAL_1.
    The patterns are the same (just reordered), so this is harmless but
    should be cleaned up to avoid confusion."""

    def test_print_color_adjust_works(self, parse_css):
        assert 'css-color-adjust' in parse_css(
            "div { print-color-adjust: exact; }"
        )

    def test_color_adjust_works(self, parse_css):
        assert 'css-color-adjust' in parse_css(
            "div { color-adjust: exact; }"
        )

    def test_duplicate_key_removed(self):
        """Verify the duplicate css-color-adjust has been cleaned up.
        It now only exists in CSS_MISC."""
        from src.parsers.css_feature_maps import CSS_MISC, CSS_ADDITIONAL_1
        assert 'css-color-adjust' in CSS_MISC
        assert 'css-color-adjust' not in CSS_ADDITIONAL_1


# ═══════════════════════════════════════════════════════════════════════════
# BUG 3: 'woff' pattern r'\.woff' matches '.woff2'
# ═══════════════════════════════════════════════════════════════════════════

class TestWoffPatternOverlap:
    """The pattern r'\\.woff' for woff1 also matches '.woff2' since the
    regex doesn't anchor the end. This causes woff2-only fonts to also
    report woff1 support as needed."""

    def test_woff2_only_does_not_trigger_woff(self, parse_css):
        """A .woff2 file extension triggers only woff2, not woff.
        The woff pattern uses a negative lookahead (?!2) to avoid overlap."""
        features = parse_css(
            "@font-face { font-family: T; src: url('f.woff2'); }"
        )
        assert 'woff2' in features
        assert 'woff' not in features

    def test_woff1_only_works(self, parse_css):
        features = parse_css(
            "@font-face { font-family: T; src: url('f.woff'); }"
        )
        assert 'woff' in features

    def test_woff2_format_function_does_not_trigger_woff(self, parse_css):
        """format('woff2') no longer falsely triggers woff detection."""
        features = parse_css(
            "@font-face { font-family: T; src: url('f.woff2') format('woff2'); }"
        )
        assert 'woff2' in features
        assert 'woff' not in features


# ═══════════════════════════════════════════════════════════════════════════
# BUG 4: circle() triggers css-shapes from clip-path context
# ═══════════════════════════════════════════════════════════════════════════

class TestCircleFalsePositive:
    """The css-shapes patterns include r'circle\\(' which matches circle()
    used in ANY context, not just shape-outside. This causes clip-path:
    circle() to also trigger css-shapes."""

    def test_clip_path_circle_no_shapes(self, parse_css):
        """clip-path: circle(50%) triggers only css-clip-path, not css-shapes.
        The css-shapes patterns now only match shape-outside/shape-margin
        properties, not bare circle()/polygon() functions."""
        features = parse_css("div { clip-path: circle(50%); }")
        assert 'css-clip-path' in features
        assert 'css-shapes' not in features

    def test_shape_outside_circle_correct(self, parse_css):
        features = parse_css("div { shape-outside: circle(50%); }")
        assert 'css-shapes' in features


# ═══════════════════════════════════════════════════════════════════════════
# BUG 5: css-gencontent not in selector_features set
# ═══════════════════════════════════════════════════════════════════════════

class TestGenContentCategorization:
    """css-gencontent (::before/::after) is a pseudo-element feature but
    is not in the selector_features set in get_statistics(), so it ends up
    in 'other' instead of 'selectors'."""

    def test_gencontent_in_selectors_category(self):
        """::before/::after (css-gencontent) is correctly categorized as
        a selector feature in statistics."""
        p = CSSParser()
        p.parse_string("div::before { content: 'x'; }")
        stats = p.get_statistics()
        assert 'css-gencontent' in stats['categories']['selectors']


# ═══════════════════════════════════════════════════════════════════════════
# Pattern precision tests (not bugs, but documenting known behavior)
# ═══════════════════════════════════════════════════════════════════════════

class TestPatternPrecision:
    """Tests documenting known imprecise pattern matches that aren't
    necessarily bugs but should be understood."""

    def test_transform_property_triggers_2d_for_3d_value(self, parse_css):
        """transform: (any value) always triggers transforms2d because the
        pattern r'transform\\s*:' matches the property name regardless of value."""
        features = parse_css("div { transform: rotateY(45deg); }")
        assert 'transforms2d' in features  # property match
        assert 'transforms3d' in features  # value match

    def test_justify_items_triggers_grid_without_display_grid(self, parse_css):
        """justify-items always triggers css-grid even without display: grid,
        because the pattern just checks for the property name."""
        features = parse_css("div { justify-items: center; }")
        assert 'css-grid' in features

    def test_filter_triggers_both_features(self, parse_css):
        """filter: triggers BOTH css-filters and css-filter-function since
        both have matching patterns. These are the same Can I Use feature
        but listed separately."""
        features = parse_css("div { filter: blur(5px); }")
        assert 'css-filters' in features
        assert 'css-filter-function' in features

    def test_revert_layer_matches_revert_value(self, parse_css):
        """revert-layer matches the css-revert-value pattern r':\\s*revert'
        because 'revert-layer' starts with 'revert'."""
        features = parse_css("div { display: revert-layer; }")
        assert 'css-revert-value' in features

    def test_transition_all_does_not_trigger_css_all(self, parse_css):
        """'transition: all 0.3s' does NOT trigger css-all because the
        pattern r'all\\s*:' requires 'all' followed by ':'. In the
        matchable text it's 'transition: all 0.3s ease;'."""
        features = parse_css("div { transition: all 0.3s ease; }")
        assert 'css-all' not in features

    def test_initial_letter_does_not_trigger_initial_value(self, parse_css):
        """initial-letter: 3 does NOT trigger css-initial-value because
        the pattern r':\\s*initial' needs ':' then 'initial', but
        'initial-letter: 3' has ': 3' not ': initial'."""
        features = parse_css("p::first-letter { initial-letter: 3; }")
        assert 'css-initial-value' not in features
