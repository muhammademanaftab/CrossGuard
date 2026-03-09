"""Bug hunt tests -- documents real bugs and known behavior.

Kept as-is from original. Each test documents a specific issue found
via pattern analysis.
"""

import pytest
from src.parsers.css_parser import CSSParser


@pytest.fixture
def parse_css(css_parser):
    """Alias for parse_features -- bug hunt tests use parse_css name."""
    def _parse(css: str) -> set:
        return css_parser.parse_string(css)
    return _parse


# --- BUG 1: Duplicate key 'css-cascade-scope' ---

class TestCascadeScopeOverwrite:
    """css-cascade-scope is defined in BOTH CSS_SELECTORS (with :scope pattern)
    and CSS_ADDITIONAL_1 (with @scope pattern). The later dict overwrites the
    earlier, so the :scope pseudo-class pattern is lost."""

    def test_at_scope_rule_detected(self, parse_css):
        assert "css-cascade-scope" in parse_css(
            "@scope (.card) { .title { color: red; } }"
        )

    def test_scope_pseudo_class_detected(self, parse_css):
        features = parse_css(":scope > .child { color: red; }")
        assert "css-cascade-scope" in features


# --- BUG 2: Duplicate key 'css-color-adjust' (harmless) ---

class TestColorAdjustDuplicate:
    def test_print_color_adjust_works(self, parse_css):
        assert "css-color-adjust" in parse_css("div { print-color-adjust: exact; }")

    def test_color_adjust_works(self, parse_css):
        assert "css-color-adjust" in parse_css("div { color-adjust: exact; }")

    def test_duplicate_key_removed(self):
        from src.parsers.css_feature_maps import CSS_MISC, CSS_ADDITIONAL_1
        assert "css-color-adjust" in CSS_MISC
        assert "css-color-adjust" not in CSS_ADDITIONAL_1


# --- BUG 3: 'woff' pattern overlap with 'woff2' ---

class TestWoffPatternOverlap:
    def test_woff2_only_does_not_trigger_woff(self, parse_css):
        features = parse_css(
            "@font-face { font-family: T; src: url('f.woff2'); }"
        )
        assert "woff2" in features
        assert "woff" not in features

    def test_woff1_only_works(self, parse_css):
        features = parse_css(
            "@font-face { font-family: T; src: url('f.woff'); }"
        )
        assert "woff" in features

    def test_woff2_format_function_does_not_trigger_woff(self, parse_css):
        features = parse_css(
            "@font-face { font-family: T; src: url('f.woff2') format('woff2'); }"
        )
        assert "woff2" in features
        assert "woff" not in features


# --- BUG 4: circle() triggers css-shapes from clip-path context ---

class TestCircleFalsePositive:
    def test_clip_path_circle_no_shapes(self, parse_css):
        features = parse_css("div { clip-path: circle(50%); }")
        assert "css-clip-path" in features
        assert "css-shapes" not in features

    def test_shape_outside_circle_correct(self, parse_css):
        features = parse_css("div { shape-outside: circle(50%); }")
        assert "css-shapes" in features


# --- BUG 5: css-gencontent not in selector_features set ---

class TestGenContentCategorization:
    def test_gencontent_in_selectors_category(self):
        p = CSSParser()
        p.parse_string("div::before { content: 'x'; }")
        stats = p.get_statistics()
        assert "css-gencontent" in stats["categories"]["selectors"]


# --- Pattern precision tests ---

class TestPatternPrecision:
    def test_transform_property_triggers_2d_for_3d_value(self, parse_css):
        features = parse_css("div { transform: rotateY(45deg); }")
        assert "transforms2d" in features
        assert "transforms3d" in features

    def test_justify_items_triggers_grid_without_display_grid(self, parse_css):
        features = parse_css("div { justify-items: center; }")
        assert "css-grid" in features

    def test_filter_triggers_both_features(self, parse_css):
        features = parse_css("div { filter: blur(5px); }")
        assert "css-filters" in features
        assert "css-filter-function" in features

    def test_revert_layer_matches_revert_value(self, parse_css):
        features = parse_css("div { display: revert-layer; }")
        assert "css-revert-value" in features

    def test_transition_all_does_not_trigger_css_all(self, parse_css):
        features = parse_css("div { transition: all 0.3s ease; }")
        assert "css-all" not in features

    def test_initial_letter_does_not_trigger_initial_value(self, parse_css):
        features = parse_css("p::first-letter { initial-letter: 3; }")
        assert "css-initial-value" not in features
