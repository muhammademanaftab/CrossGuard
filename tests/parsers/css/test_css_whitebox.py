"""CSS parser white box tests.

Tests internals: state management, tinycss2 AST pipeline, private methods,
bug documentation, and custom rules with mocked dependencies.
"""

import re
import pytest
import tinycss2
from unittest.mock import patch
from src.parsers.css_parser import CSSParser


# =====================================================================
# State Reset
# =====================================================================

@pytest.mark.whitebox
class TestStateReset:
    def test_features_reset(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        assert "flexbox" in css_parser.features_found
        css_parser.parse_string("div { color: red; }")
        assert "flexbox" not in css_parser.features_found

    def test_feature_details_reset(self, css_parser):
        css_parser.parse_string("div { display: grid; }")
        assert len(css_parser.feature_details) > 0
        css_parser.parse_string("")
        assert len(css_parser.feature_details) == 0

    def test_unrecognized_reset(self, css_parser):
        css_parser.parse_string("div { weird-prop: val; }")
        assert len(css_parser.unrecognized_patterns) > 0
        css_parser.parse_string("div { color: red; }")
        assert len(css_parser.unrecognized_patterns) == 0

    def test_block_counter_reset(self, css_parser):
        css_parser.parse_string("div { color: red; } span { color: blue; }")
        assert css_parser._block_counter > 0
        css_parser.parse_string("")
        assert css_parser._block_counter == 0


# =====================================================================
# Block Boundary Preservation (flexbox-gap context detection)
# =====================================================================

@pytest.mark.whitebox
class TestBlockBoundaryPreservation:
    def test_flex_and_gap_same_block(self, parse_features):
        assert "flexbox-gap" in parse_features(".c { display: flex; gap: 10px; }")

    def test_flex_and_gap_different_blocks(self, parse_features):
        css = ".flex { display: flex; } .grid { display: grid; gap: 10px; }"
        assert "flexbox-gap" not in parse_features(css)

    def test_gap_before_flex_same_block(self, parse_features):
        assert "flexbox-gap" in parse_features(".c { gap: 10px; display: flex; }")

    def test_inline_flex_with_gap(self, parse_features):
        assert "flexbox-gap" in parse_features(".c { display: inline-flex; gap: 10px; }")

    def test_duplicate_selectors_separate_blocks(self, parse_features):
        css = ".item { display: flex; } .item { gap: 10px; }"
        assert "flexbox-gap" not in parse_features(css)

    def test_grid_gap_not_detected_as_flexbox_gap(self, parse_features):
        assert "flexbox-gap" not in parse_features(".grid { display: grid; gap: 10px; }")


# =====================================================================
# tinycss2 Internals: _build_matchable_text
# =====================================================================

@pytest.mark.whitebox
class TestBuildMatchableText:
    def test_matchable_text_contains_selectors(self, css_parser):
        rules = tinycss2.parse_stylesheet(
            ".container { display: flex; }", skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        assert ".container" in text

    def test_matchable_text_has_braces(self, css_parser):
        rules = tinycss2.parse_stylesheet(
            "div { color: red; }", skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        assert "{" in text and "}" in text

    def test_matchable_text_block_separation(self, css_parser):
        css = ".a { display: flex; } .a { gap: 10px; }"
        rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        blocks = re.findall(r'\.a\s*\{', text)
        assert len(blocks) == 2


# =====================================================================
# tinycss2 Internals: _extract_components
# =====================================================================

@pytest.mark.whitebox
class TestExtractComponents:
    def test_simple_declaration(self, css_parser):
        rules = tinycss2.parse_stylesheet(
            "div { color: red; }", skip_comments=True, skip_whitespace=True
        )
        declarations, _, _ = css_parser._extract_components(rules)
        assert "color" in [d[0] for d in declarations]

    def test_selectors_extracted(self, css_parser):
        rules = tinycss2.parse_stylesheet(
            ".foo { color: red; } #bar { color: blue; }",
            skip_comments=True, skip_whitespace=True
        )
        _, _, selectors = css_parser._extract_components(rules)
        assert ".foo" in selectors
        assert "#bar" in selectors

    def test_at_rules_extracted(self, css_parser):
        rules = tinycss2.parse_stylesheet(
            "@media screen { div { color: red; } }",
            skip_comments=True, skip_whitespace=True
        )
        _, at_rules, _ = css_parser._extract_components(rules)
        assert "media" in [a[0] for a in at_rules]

    def test_font_face_declarations(self, css_parser):
        rules = tinycss2.parse_stylesheet(
            "@font-face { font-family: 'Test'; font-weight: bold; }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, _, _ = css_parser._extract_components(rules)
        prop_names = [d[0] for d in declarations]
        assert "font-family" in prop_names
        assert "font-weight" in prop_names

    def test_parse_error_handled(self, css_parser):
        rules = tinycss2.parse_stylesheet(
            "@@invalid { }", skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        assert isinstance(declarations, list)

    def test_nested_media_extracts_inner(self, css_parser):
        rules = tinycss2.parse_stylesheet(
            "@media screen { .inner { display: grid; } }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, _, selectors = css_parser._extract_components(rules)
        assert ".inner" in selectors
        assert "display" in [d[0] for d in declarations]


# =====================================================================
# Unrecognized Patterns (internal state inspection)
# =====================================================================

@pytest.mark.whitebox
class TestUnrecognizedPatterns:
    def test_basic_property_not_flagged(self, css_parser):
        css_parser.parse_string("div { color: red; margin: 10px; }")
        assert len(css_parser.unrecognized_patterns) == 0

    def test_unknown_property_flagged(self, css_parser):
        css_parser.parse_string("div { some-unknown-property: value; }")
        assert any("some-unknown-property" in p for p in css_parser.unrecognized_patterns)

    def test_custom_property_not_flagged(self, css_parser):
        css_parser.parse_string(":root { --my-color: red; }")
        assert not any("--my-color" in p for p in css_parser.unrecognized_patterns)

    def test_known_feature_property_not_flagged(self, css_parser):
        css_parser.parse_string("div { clip-path: circle(); }")
        assert not any("clip-path" in p for p in css_parser.unrecognized_patterns)

    def test_unknown_at_rule_flagged(self, css_parser):
        css_parser.parse_string("@some-unknown-rule { div { color: red; } }")
        assert any("some-unknown-rule" in p for p in css_parser.unrecognized_patterns)

    def test_font_face_at_rule_not_flagged(self, css_parser):
        css_parser.parse_string("@font-face { font-family: 'Test'; }")
        assert not any("@font-face" in p for p in css_parser.unrecognized_patterns)

    def test_import_not_flagged(self, css_parser):
        css_parser.parse_string("@import url('style.css');")
        assert not any("@import" in p for p in css_parser.unrecognized_patterns)


# =====================================================================
# Bug Documentation
# =====================================================================

@pytest.mark.whitebox
class TestCascadeScopeOverwrite:
    """BUG 1: Duplicate key 'css-cascade-scope' -- both @scope and :scope patterns."""

    def test_at_scope_rule_detected(self, parse_features):
        assert "css-cascade-scope" in parse_features(
            "@scope (.card) { .title { color: red; } }"
        )

    def test_scope_pseudo_class_detected(self, parse_features):
        assert "css-cascade-scope" in parse_features(":scope > .child { color: red; }")


@pytest.mark.whitebox
class TestColorAdjustDuplicate:
    """BUG 2: Duplicate key 'css-color-adjust' (harmless)."""

    def test_print_color_adjust_works(self, parse_features):
        assert "css-color-adjust" in parse_features("div { print-color-adjust: exact; }")

    def test_color_adjust_works(self, parse_features):
        assert "css-color-adjust" in parse_features("div { color-adjust: exact; }")

    def test_duplicate_key_removed(self):
        from src.parsers.css_feature_maps import CSS_MISC, CSS_ADDITIONAL_1
        assert "css-color-adjust" in CSS_MISC
        assert "css-color-adjust" not in CSS_ADDITIONAL_1


@pytest.mark.whitebox
class TestWoffPatternOverlap:
    """BUG 3: 'woff' pattern must not match 'woff2'."""

    def test_woff2_only_does_not_trigger_woff(self, parse_features):
        features = parse_features(
            "@font-face { font-family: T; src: url('f.woff2'); }"
        )
        assert "woff2" in features
        assert "woff" not in features

    def test_woff1_only_works(self, parse_features):
        assert "woff" in parse_features(
            "@font-face { font-family: T; src: url('f.woff'); }"
        )

    def test_woff2_format_function_does_not_trigger_woff(self, parse_features):
        features = parse_features(
            "@font-face { font-family: T; src: url('f.woff2') format('woff2'); }"
        )
        assert "woff2" in features
        assert "woff" not in features


@pytest.mark.whitebox
class TestCircleFalsePositive:
    """BUG 4: circle() in clip-path must not trigger css-shapes."""

    def test_clip_path_circle_no_shapes(self, parse_features):
        features = parse_features("div { clip-path: circle(50%); }")
        assert "css-clip-path" in features
        assert "css-shapes" not in features

    def test_shape_outside_circle_correct(self, parse_features):
        assert "css-shapes" in parse_features("div { shape-outside: circle(50%); }")


@pytest.mark.whitebox
class TestGenContentCategorization:
    """BUG 5: css-gencontent must appear in selectors category."""

    def test_gencontent_in_selectors_category(self):
        p = CSSParser()
        p.parse_string("div::before { content: 'x'; }")
        stats = p.get_statistics()
        assert "css-gencontent" in stats["categories"]["selectors"]


@pytest.mark.whitebox
class TestPatternPrecision:
    def test_transform_property_triggers_2d_for_3d_value(self, parse_features):
        features = parse_features("div { transform: rotateY(45deg); }")
        assert "transforms2d" in features
        assert "transforms3d" in features

    def test_justify_items_triggers_grid_without_display_grid(self, parse_features):
        assert "css-grid" in parse_features("div { justify-items: center; }")

    def test_filter_triggers_both_features(self, parse_features):
        features = parse_features("div { filter: blur(5px); }")
        assert "css-filters" in features
        assert "css-filter-function" in features

    def test_revert_layer_matches_revert_value(self, parse_features):
        assert "css-revert-value" in parse_features("div { display: revert-layer; }")

    def test_transition_all_does_not_trigger_css_all(self, parse_features):
        assert "css-all" not in parse_features("div { transition: all 0.3s ease; }")

    def test_initial_letter_does_not_trigger_initial_value(self, parse_features):
        assert "css-initial-value" not in parse_features(
            "p::first-letter { initial-letter: 3; }"
        )


# =====================================================================
# Custom Rules
# =====================================================================

@pytest.fixture
def custom_css_rules():
    return {
        "test-custom-prop": {
            "patterns": [r"test-custom-prop\s*:"],
            "description": "Test Custom Property"
        },
        "custom-animation-feat": {
            "patterns": [r"custom-animation-name\s*:"],
            "description": "Custom Animation Feature"
        },
        "multi-pattern-feat": {
            "patterns": [r"multi-a\s*:", r"multi-b\s*:"],
            "description": "Multi Pattern Feature"
        },
        "complex-regex-feat": {
            "patterns": [r"(?:fancy|special)-gradient\s*\("],
            "description": "Complex Regex Feature"
        }
    }


@pytest.fixture
def css_parser_with_custom(custom_css_rules):
    with patch('src.parsers.css_parser.get_custom_css_rules', return_value=custom_css_rules):
        yield CSSParser()


@pytest.fixture
def custom_report_rules():
    return {
        "report-test-feat": {
            "patterns": [r"report-prop\s*:"],
            "description": "Report Test Feature"
        }
    }


@pytest.fixture
def css_parser_with_report_custom(custom_report_rules):
    with patch('src.parsers.css_parser.get_custom_css_rules', return_value=custom_report_rules):
        yield CSSParser()


@pytest.mark.whitebox
class TestCSSCustomDetection:
    def test_custom_property_detected(self, css_parser_with_custom):
        assert "test-custom-prop" in css_parser_with_custom.parse_string(
            ".box { test-custom-prop: value; }"
        )

    def test_custom_animation_detected(self, css_parser_with_custom):
        assert "custom-animation-feat" in css_parser_with_custom.parse_string(
            ".anim { custom-animation-name: slidein; }"
        )

    def test_custom_rule_not_triggered_on_unrelated_css(self, css_parser_with_custom):
        features = css_parser_with_custom.parse_string(".box { color: red; margin: 10px; }")
        assert "test-custom-prop" not in features
        assert "custom-animation-feat" not in features

    def test_multiple_custom_rules_detected(self, css_parser_with_custom):
        css = ".box { test-custom-prop: value; } .anim { custom-animation-name: slidein; }"
        features = css_parser_with_custom.parse_string(css)
        assert "test-custom-prop" in features
        assert "custom-animation-feat" in features

    def test_custom_rule_merged_with_builtin(self, css_parser_with_custom):
        features = css_parser_with_custom.parse_string(
            ".box { display: flex; test-custom-prop: value; }"
        )
        assert "test-custom-prop" in features
        assert "flexbox" in features

    def test_builtin_still_works_with_custom_rules(self, css_parser_with_custom):
        assert "css-grid" in css_parser_with_custom.parse_string(".grid { display: grid; }")

    def test_custom_rule_with_complex_regex(self, css_parser_with_custom):
        assert "complex-regex-feat" in css_parser_with_custom.parse_string(
            ".bg { background: fancy-gradient(red, blue); }"
        )
        assert "complex-regex-feat" in css_parser_with_custom.parse_string(
            ".bg { background: special-gradient(red, blue); }"
        )

    def test_empty_custom_rules_no_effect(self):
        with patch('src.parsers.css_parser.get_custom_css_rules', return_value={}):
            assert "flexbox" in CSSParser().parse_string(".box { display: flex; }")


@pytest.mark.whitebox
class TestCSSCustomReport:
    def test_custom_rule_appears_in_report(self, css_parser_with_report_custom):
        css_parser_with_report_custom.parse_string(".box { report-prop: value; }")
        report = css_parser_with_report_custom.get_detailed_report()
        assert "report-test-feat" in report["features"]

    def test_custom_rule_feature_id_correct(self, css_parser_with_report_custom):
        css_parser_with_report_custom.parse_string(".box { report-prop: value; }")
        report = css_parser_with_report_custom.get_detailed_report()
        assert "report-test-feat" in [d["feature"] for d in report["feature_details"]]

    def test_custom_rule_count_accurate(self, css_parser_with_report_custom):
        css_parser_with_report_custom.parse_string(
            ".a { report-prop: val1; } .b { report-prop: val2; }"
        )
        report = css_parser_with_report_custom.get_detailed_report()
        assert report["features"].count("report-test-feat") == 1

    def test_custom_and_builtin_in_same_report(self, css_parser_with_report_custom):
        css_parser_with_report_custom.parse_string(
            ".box { display: flex; report-prop: value; }"
        )
        report = css_parser_with_report_custom.get_detailed_report()
        assert "flexbox" in report["features"]
        assert "report-test-feat" in report["features"]
