"""Consolidated CSS parser pipeline and API tests.

Merged from: test_parser_methods.py, test_tinycss2_pipeline.py,
test_feature_gaps.py, integration/test_integration.py

Covers: parse_file, parse_multiple_files, get_statistics, validate_css,
convenience functions, unrecognized patterns, detailed reports,
tinycss2 pipeline internals, font format detection, integration scenarios.
"""

import pytest
from src.parsers.css_parser import CSSParser, parse_css_file, parse_css_string


# --- Fixtures ---

@pytest.fixture
def tmp_css_file(tmp_path):
    def _create(content, filename="test.css"):
        filepath = tmp_path / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
    return _create


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: parse_file()
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestParseFile:
    def test_parse_valid_file(self, css_parser, tmp_css_file):
        path = tmp_css_file("div { display: flex; }")
        assert "flexbox" in css_parser.parse_file(path)

    def test_parse_file_returns_set(self, css_parser, tmp_css_file):
        path = tmp_css_file("body { margin: 0; }")
        assert isinstance(css_parser.parse_file(path), set)

    def test_file_not_found_raises(self, css_parser):
        with pytest.raises(FileNotFoundError):
            css_parser.parse_file("/nonexistent/path/file.css")

    def test_non_utf8_file_raises(self, css_parser, tmp_path):
        filepath = tmp_path / "bad.css"
        filepath.write_bytes(b'\xff\xfe\x00\x00' + b'\x80\x81\x82')
        with pytest.raises(ValueError, match="not valid UTF-8"):
            css_parser.parse_file(str(filepath))

    def test_empty_file(self, css_parser, tmp_css_file):
        path = tmp_css_file("")
        assert len(css_parser.parse_file(path)) == 0

    def test_file_with_multiple_features(self, css_parser, tmp_css_file):
        css = """
        .container { display: grid; }
        .item { opacity: 0.5; }
        @keyframes slide { from { transform: translateX(0); } }
        """
        path = tmp_css_file(css)
        features = css_parser.parse_file(path)
        assert "css-grid" in features
        assert "css-animation" in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: parse_multiple_files()
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestParseMultipleFiles:
    def test_multiple_files_combined(self, css_parser, tmp_css_file):
        f1 = tmp_css_file("div { display: flex; }", "a.css")
        f2 = tmp_css_file("div { display: grid; }", "b.css")
        features = css_parser.parse_multiple_files([f1, f2])
        assert "flexbox" in features
        assert "css-grid" in features

    def test_empty_file_list(self, css_parser):
        assert len(css_parser.parse_multiple_files([])) == 0

    def test_one_bad_file_doesnt_break_others(self, css_parser, tmp_css_file):
        good = tmp_css_file("div { display: flex; }", "good.css")
        features = css_parser.parse_multiple_files([good, "/nonexistent.css"])
        assert "flexbox" in features

    def test_single_file_in_list(self, css_parser, tmp_css_file):
        f = tmp_css_file("div { display: grid; }", "single.css")
        assert "css-grid" in css_parser.parse_multiple_files([f])


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: get_statistics()
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestGetStatistics:
    def test_stats_structure(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        stats = css_parser.get_statistics()
        for key in ["total_features", "layout_features", "transform_animation",
                     "color_background", "typography", "selectors",
                     "media_queries", "other_features", "features_list", "categories"]:
            assert key in stats

    def test_stats_layout_category(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        stats = css_parser.get_statistics()
        assert stats["layout_features"] >= 1
        assert "flexbox" in stats["categories"]["layout"]

    def test_stats_empty_input(self, css_parser):
        css_parser.parse_string("")
        stats = css_parser.get_statistics()
        assert stats["total_features"] == 0
        assert stats["features_list"] == []

    def test_stats_features_list_sorted(self, css_parser):
        css_parser.parse_string("div { display: flex; opacity: 0.5; }")
        stats = css_parser.get_statistics()
        assert stats["features_list"] == sorted(stats["features_list"])

    def test_stats_total_matches_sum(self, css_parser):
        css_parser.parse_string("""
            div { display: flex; opacity: 0.5; transform: rotate(0); }
            @media (prefers-color-scheme: dark) { body { color: white; } }
        """)
        stats = css_parser.get_statistics()
        category_sum = (
            stats["layout_features"] + stats["transform_animation"] +
            stats["color_background"] + stats["typography"] +
            stats["selectors"] + stats["media_queries"] + stats["other_features"]
        )
        assert stats["total_features"] == category_sum

    def test_stats_selectors_category(self, css_parser):
        css_parser.parse_string("div:nth-child(2) { color: red; }")
        stats = css_parser.get_statistics()
        assert stats["selectors"] >= 1
        assert "css-sel3" in stats["categories"]["selectors"]

    def test_stats_has_selector_correctly_categorized(self, css_parser):
        css_parser.parse_string("div:has(.child) { color: red; }")
        stats = css_parser.get_statistics()
        assert "css-has" in stats["categories"]["selectors"]


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: validate_css()
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestValidateCSS:
    def test_valid_basic_css(self, css_parser):
        assert css_parser.validate_css("body { margin: 0; }") is True

    def test_valid_media_query(self, css_parser):
        assert css_parser.validate_css("@media screen { }") is True

    def test_valid_keyframes(self, css_parser):
        assert css_parser.validate_css("@keyframes fade { }") is True

    def test_invalid_plain_text(self, css_parser):
        assert css_parser.validate_css("hello world") is False

    def test_invalid_empty_string(self, css_parser):
        assert css_parser.validate_css("") is False

    def test_valid_just_braces(self, css_parser):
        assert css_parser.validate_css("{ }") is True

    def test_valid_just_semicolon(self, css_parser):
        assert css_parser.validate_css("margin: 0;") is True


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: Convenience Functions
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestConvenienceFunctions:
    def test_parse_css_string_basic(self):
        assert "css-grid" in parse_css_string("div { display: grid; }")

    def test_parse_css_string_empty(self):
        assert len(parse_css_string("")) == 0

    def test_parse_css_file_basic(self, tmp_css_file):
        path = tmp_css_file("div { display: grid; }")
        assert "css-grid" in parse_css_file(path)

    def test_parse_css_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_css_file("/nonexistent.css")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: Detailed Report
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestDetailedReport:
    def test_report_structure(self, css_parser):
        css_parser.parse_string("div { display: flex; }")
        report = css_parser.get_detailed_report()
        for key in ["total_features", "features", "feature_details", "unrecognized"]:
            assert key in report

    def test_report_total_matches_features_list(self, css_parser):
        css_parser.parse_string("div { display: flex; opacity: 0.5; }")
        report = css_parser.get_detailed_report()
        assert report["total_features"] == len(report["features"])

    def test_report_features_sorted(self, css_parser):
        css_parser.parse_string("div { display: flex; opacity: 0.5; }")
        report = css_parser.get_detailed_report()
        assert report["features"] == sorted(report["features"])

    def test_report_feature_details_has_description(self, css_parser):
        css_parser.parse_string("div { display: grid; }")
        report = css_parser.get_detailed_report()
        for detail in report["feature_details"]:
            assert "description" in detail
            assert "feature" in detail
            assert "matched_properties" in detail

    def test_report_empty_input(self, css_parser):
        css_parser.parse_string("")
        report = css_parser.get_detailed_report()
        assert report["total_features"] == 0
        assert report["features"] == []
        assert report["feature_details"] == []


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: Unrecognized Patterns
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
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


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: State Reset
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
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


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: tinycss2 Block Boundary Preservation
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
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


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: @font-face Handling
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestFontFaceHandling:
    def test_font_face_basic(self, parse_features):
        css = "@font-face { font-family: 'F'; src: url('f.woff2') format('woff2'); }"
        features = parse_features(css)
        assert "fontface" in features
        assert "woff2" in features

    def test_font_face_multiple_sources(self, parse_features):
        css = """@font-face {
            font-family: 'F';
            src: url('f.woff2') format('woff2'), url('f.woff') format('woff');
        }"""
        features = parse_features(css)
        assert "woff2" in features
        assert "woff" in features

    def test_font_face_font_display(self, parse_features):
        css = "@font-face { font-family: 'F'; src: url('f.woff2'); font-display: swap; }"
        assert "css-font-rendering-controls" in parse_features(css)

    def test_font_face_unicode_range(self, parse_features):
        css = "@font-face { font-family: 'F'; src: url('f.woff2'); unicode-range: U+0000-00FF; }"
        assert "font-unicode-range" in parse_features(css)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 11: @keyframes Handling
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestKeyframesHandling:
    def test_keyframes_basic(self, parse_features):
        css = "@keyframes s { from { transform: translateX(0); } to { transform: translateX(100px); } }"
        features = parse_features(css)
        assert "css-animation" in features
        assert "transforms2d" in features

    def test_keyframes_with_modern_features(self, parse_features):
        css = "@keyframes e { from { clip-path: circle(0%); } to { clip-path: circle(100%); } }"
        features = parse_features(css)
        assert "css-animation" in features
        assert "css-clip-path" in features

    def test_keyframes_3d_transform(self, parse_features):
        css = "@keyframes r { from { transform: rotateY(0deg); } to { transform: rotateY(360deg); } }"
        assert "transforms3d" in parse_features(css)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 12: Nested @-rules
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestNestedAtRules:
    def test_media_wrapping_rules(self, parse_features):
        css = "@media (max-width: 768px) { .c { display: flex; } }"
        features = parse_features(css)
        assert "css-mediaqueries" in features
        assert "flexbox" in features

    def test_supports_wrapping_rules(self, parse_features):
        css = "@supports (display: grid) { .c { display: grid; } }"
        features = parse_features(css)
        assert "css-featurequeries" in features
        assert "css-grid" in features

    def test_media_inside_supports(self, parse_features):
        css = "@supports (display: grid) { @media (min-width: 768px) { .c { display: grid; } } }"
        features = parse_features(css)
        assert "css-featurequeries" in features
        assert "css-mediaqueries" in features
        assert "css-grid" in features

    def test_three_levels_deep(self, parse_features):
        css = "@media (min-width: 768px) { @supports (display: grid) { @layer layout { .g { display: grid; } } } }"
        features = parse_features(css)
        assert "css-mediaqueries" in features
        assert "css-featurequeries" in features
        assert "css-cascade-layers" in features
        assert "css-grid" in features

    def test_four_levels_deep(self, parse_features):
        css = """@layer base { @media screen { @supports (display: flex) {
            @container (min-width: 400px) { .item { display: flex; } } } } }"""
        features = parse_features(css)
        assert "css-cascade-layers" in features
        assert "css-mediaqueries" in features
        assert "css-featurequeries" in features
        assert "css-container-queries" in features
        assert "flexbox" in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 13: CSS Nesting in Pipeline
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCSSNestingPipeline:
    def test_nesting_hover(self, parse_features):
        css = ".parent { color: blue; &:hover { color: red; } }"
        assert "css-nesting" in parse_features(css)

    def test_nesting_child_selector(self, parse_features):
        css = ".parent { color: blue; & .child { color: green; } }"
        assert "css-nesting" in parse_features(css)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 14: Minified CSS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestMinifiedCSS:
    def test_minified_basic(self, parse_features):
        features = parse_features(".a{display:flex}.b{display:grid}.c{opacity:.5}")
        assert "flexbox" in features
        assert "css-grid" in features

    def test_minified_media_query(self, parse_features):
        features = parse_features("@media(max-width:768px){.a{display:flex}}")
        assert "css-mediaqueries" in features
        assert "flexbox" in features

    def test_minified_keyframes(self, parse_features):
        assert "css-animation" in parse_features("@keyframes x{from{opacity:0}to{opacity:1}}")

    def test_minified_with_variables(self, parse_features):
        assert "css-variables" in parse_features(":root{--c:red}div{color:var(--c)}")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 15: Comments in Pipeline
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCommentsInPipeline:
    def test_feature_in_comment_not_detected(self, parse_features):
        css = "/* display: grid; */ body { margin: 0; }"
        assert "css-grid" not in parse_features(css)

    def test_comment_between_declarations(self, parse_features):
        css = "div { display: flex; /* gap: 10px; */ color: red; }"
        features = parse_features(css)
        assert "flexbox" in features
        assert "flexbox-gap" not in features

    def test_multiline_comment_with_features(self, parse_features):
        css = """/*
        @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
        */ body { color: black; }"""
        assert "css-animation" not in parse_features(css)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 16: Malformed CSS Recovery
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestMalformedCSSRecovery:
    def test_missing_closing_brace(self, parse_features):
        assert isinstance(parse_features("div { display: flex; "), set)

    def test_extra_closing_brace(self, parse_features):
        assert isinstance(parse_features("div { display: grid; } }"), set)

    def test_empty_rule(self, parse_features):
        assert isinstance(parse_features("div { }"), set)

    def test_invalid_property_name(self, parse_features):
        assert isinstance(parse_features("div { 123invalid: value; }"), set)

    def test_unclosed_string(self, parse_features):
        assert isinstance(parse_features("div { content: 'unclosed; }"), set)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 17: Vendor Prefix Handling
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestVendorPrefixes:
    def test_webkit_font_smoothing(self, parse_features):
        assert "font-smooth" in parse_features("body { -webkit-font-smoothing: antialiased; }")

    def test_moz_font_smoothing(self, parse_features):
        assert "font-smooth" in parse_features("body { -moz-osx-font-smoothing: grayscale; }")

    def test_webkit_text_stroke(self, parse_features):
        assert "text-stroke" in parse_features("h1 { -webkit-text-stroke: 1px black; }")

    def test_webkit_appearance(self, parse_features):
        assert "css-appearance" in parse_features("button { -webkit-appearance: none; }")

    def test_webkit_user_select(self, parse_features):
        assert "user-select-none" in parse_features("div { -webkit-user-select: none; }")

    def test_webkit_background_clip_text(self, parse_features):
        assert "background-clip-text" in parse_features("h1 { -webkit-background-clip: text; }")

    def test_webkit_box_reflect(self, parse_features):
        assert "css-reflections" in parse_features("img { -webkit-box-reflect: below; }")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 18: Empty and Edge Cases
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestPipelineEdgeCases:
    def test_empty_string(self, parse_features):
        assert len(parse_features("")) == 0

    def test_whitespace_only(self, parse_features):
        assert len(parse_features("   \n\t  ")) == 0

    def test_comment_only(self, parse_features):
        assert len(parse_features("/* comment */")) == 0

    def test_very_long_selector(self, parse_features):
        sel = " > ".join([f".level{i}" for i in range(50)])
        assert "flexbox" in parse_features(f"{sel} {{ display: flex; }}")

    def test_many_declarations_in_one_block(self, parse_features):
        props = "; ".join([f"--prop-{i}: value{i}" for i in range(100)])
        assert "css-variables" in parse_features(f":root {{ {props}; }}")

    def test_unicode_in_content(self, parse_features):
        assert "css-gencontent" in parse_features("div::before { content: '\\2764'; }")

    def test_case_insensitive_properties(self, parse_features):
        assert "flexbox" in parse_features("div { Display: FLEX; }")

    def test_case_insensitive_at_rules(self, parse_features):
        assert "css-mediaqueries" in parse_features("@MEDIA screen { div { color: red; } }")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 19: _build_matchable_text Internals
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestBuildMatchableText:
    def test_matchable_text_contains_selectors(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            ".container { display: flex; }", skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        assert ".container" in text

    def test_matchable_text_has_braces(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "div { color: red; }", skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        assert "{" in text and "}" in text

    def test_matchable_text_block_separation(self, css_parser):
        import tinycss2, re
        css = ".a { display: flex; } .a { gap: 10px; }"
        rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        blocks = re.findall(r'\.a\s*\{', text)
        assert len(blocks) == 2


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 20: _extract_components
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestExtractComponents:
    def test_simple_declaration(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "div { color: red; }", skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        assert "color" in [d[0] for d in declarations]

    def test_selectors_extracted(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            ".foo { color: red; } #bar { color: blue; }",
            skip_comments=True, skip_whitespace=True
        )
        _, _, selectors = css_parser._extract_components(rules)
        assert ".foo" in selectors
        assert "#bar" in selectors

    def test_at_rules_extracted(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@media screen { div { color: red; } }",
            skip_comments=True, skip_whitespace=True
        )
        _, at_rules, _ = css_parser._extract_components(rules)
        assert "media" in [a[0] for a in at_rules]

    def test_font_face_declarations(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@font-face { font-family: 'Test'; font-weight: bold; }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, _, _ = css_parser._extract_components(rules)
        prop_names = [d[0] for d in declarations]
        assert "font-family" in prop_names
        assert "font-weight" in prop_names

    def test_parse_error_handled(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@@invalid { }", skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        assert isinstance(declarations, list)

    def test_nested_media_extracts_inner(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@media screen { .inner { display: grid; } }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, _, selectors = css_parser._extract_components(rules)
        assert ".inner" in selectors
        assert "display" in [d[0] for d in declarations]


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 21: No-block @-rules (@import, @charset)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestNoBlockAtRules:
    def test_import_rule(self, parse_features):
        assert isinstance(parse_features("@import url('style.css');"), set)

    def test_namespace_rule(self, parse_features):
        assert "css-namespaces" in parse_features("@namespace svg url(http://www.w3.org/2000/svg);")

    def test_multiple_imports(self, parse_features):
        css = "@import url('reset.css'); @import url('base.css'); body { display: flex; }"
        assert "flexbox" in parse_features(css)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 22: Font Format Detection (from test_feature_gaps.py)
# ═══════════════════════════════════════════════════════════════════════════

FONT_FORMAT_FEATURES = [
    pytest.param("@font-face{font-family:'T';src:url('f.woff')format('woff')}", "woff", id="woff-format"),
    pytest.param("@font-face{font-family:'T';src:url('f.woff')}", "woff", id="woff-ext"),
    pytest.param("@font-face{font-family:'T';src:url('f.woff2')format('woff2')}", "woff2", id="woff2-format"),
    pytest.param("@font-face{font-family:'T';src:url('f.woff2')}", "woff2", id="woff2-ext"),
    pytest.param("@font-face{font-family:'T';src:url('f.ttf')}", "ttf", id="ttf-ext"),
    pytest.param("@font-face{font-family:'T';src:url('f.otf')}", "ttf", id="otf-ext"),
    pytest.param("@font-face{font-family:'T';src:url('f.ttf')format('truetype')}", "ttf", id="truetype-format"),
    pytest.param("@font-face{font-family:'T';src:url('f.eot')}", "eot", id="eot-ext"),
    pytest.param("@font-face{font-family:'T';src:url('f.eot')format('embedded-opentype')}", "eot", id="eot-format"),
    pytest.param("@font-face{font-family:'C';src:url('f.woff2')format('colr')}", "colr", id="colr-format"),
    pytest.param("@font-face{font-family:'C';src:url('f.woff2')format('colr-v1')}", "colr-v1", id="colr-v1"),
    pytest.param("@font-face{font-family:'T';src:url('f.svg#g')format('svg')}", "svg-fonts", id="svg-font-format"),
    pytest.param("@font-face{font-family:'T';src:url('f.svg#TestFont')}", "svg-fonts", id="svg-font-hash"),
]


@pytest.mark.unit
class TestFontFormatDetection:
    @pytest.mark.parametrize("css_input,expected_id", FONT_FORMAT_FEATURES)
    def test_font_format_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 23: Additional Feature Gap Tests
# ═══════════════════════════════════════════════════════════════════════════

FEATURE_GAP_PARAMS = [
    pytest.param("div{grid-template-columns:1fr;transition:grid-template-columns 0.3s}", "css-grid-animation", id="grid-animation-transition"),
    pytest.param("div{display:grid;animation:gridExpand 1s}", "css-grid-animation", id="grid-animation"),
    pytest.param("img{image-orientation:from-image}", "css-image-orientation", id="image-orientation"),
    pytest.param("div{background-position:right 10px from bottom 20px}", "css-background-offsets", id="bg-offsets"),
    pytest.param(":fullscreen{background:black}", "fullscreen", id="fullscreen"),
    pytest.param("::view-transition-group(root){animation-duration:0.3s}", "view-transitions", id="view-transition-group"),
]


@pytest.mark.unit
class TestFeatureGapDetection:
    @pytest.mark.parametrize("css_input,expected_id", FEATURE_GAP_PARAMS)
    def test_feature_gap_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 24: False Positive Prevention
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestFalsePositivePrevention:
    def test_keyframes_from_no_relative_colors(self, parse_features):
        css = "@keyframes fade { from { opacity: 0; } to { opacity: 1; } }"
        assert "css-relative-colors" not in parse_features(css)

    def test_actual_relative_colors_detected(self, parse_features):
        assert "css-relative-colors" in parse_features("div { color: oklch(from red l c h); }")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 25: Integration -- Real-World Scenarios
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestRealWorldScenarios:
    def test_modern_css_reset(self, parse_features):
        css = """
        *, *::before, *::after { box-sizing: border-box; }
        * { margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body { min-height: 100vh; line-height: 1.5; }
        """
        features = parse_features(css)
        assert "css3-boxsizing" in features
        assert "css-gencontent" in features
        assert "css-scroll-behavior" in features
        assert "viewport-units" in features

    def test_flexbox_card_layout(self, parse_features):
        css = """
        .cards { display: flex; flex-wrap: wrap; gap: 20px; }
        .card { border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s ease; }
        .card:hover { transform: translateY(-4px); }
        """
        features = parse_features(css)
        assert "flexbox" in features
        assert "flexbox-gap" in features
        assert "border-radius" in features
        assert "css-boxshadow" in features
        assert "css-transitions" in features
        assert "transforms2d" in features

    def test_css_grid_layout(self, parse_features):
        css = """
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
        .item { grid-column: span 2; }
        @media (max-width: 768px) { .item { grid-column: span 1; } }
        """
        features = parse_features(css)
        assert "css-grid" in features
        assert "flexbox-gap" not in features  # gap in grid context
        assert "rem" in features
        assert "css-mediaqueries" in features

    def test_dark_mode_support(self, parse_features):
        css = """
        :root { --bg: #fff; --fg: #1a1a1a; }
        @media (prefers-color-scheme: dark) { :root { --bg: #1a1a1a; --fg: #fff; } }
        body { background-color: var(--bg); color: var(--fg); }
        """
        features = parse_features(css)
        assert "css-variables" in features
        assert "prefers-color-scheme" in features

    def test_modern_button_styles(self, parse_features):
        css = """
        .button {
            appearance: none;
            border-radius: 0.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }
        .button:hover { transform: translateY(-2px); }
        .button:focus-visible { outline: 2px solid #667eea; }
        """
        features = parse_features(css)
        assert "css-appearance" in features
        assert "border-radius" in features
        assert "css-gradients" in features
        assert "css3-cursors" in features
        assert "css-transitions" in features
        assert "user-select-none" in features
        assert "css-focus-visible" in features

    def test_responsive_typography(self, parse_features):
        css = """
        html { font-size: clamp(1rem, 0.5rem + 1vw, 1.25rem); }
        .readable { max-width: 65ch; margin-inline: auto; }
        """
        features = parse_features(css)
        assert "css-math-functions" in features
        assert "rem" in features
        assert "viewport-units" in features
        assert "ch-unit" in features
        assert "css-logical-props" in features

    def test_container_queries_pattern(self, parse_features):
        css = """
        .container { container-type: inline-size; container-name: card; }
        @container card (min-width: 400px) {
            .card { display: flex; gap: 20px; }
            .card-image { width: 40cqi; }
        }
        """
        features = parse_features(css)
        assert "css-container-queries" in features
        assert "flexbox" in features
        assert "flexbox-gap" in features
        assert "css-container-query-units" in features

    def test_scroll_snap_gallery(self, parse_features):
        css = """
        .gallery { display: flex; overflow-x: auto; scroll-snap-type: x mandatory;
                   scroll-behavior: smooth; overscroll-behavior-x: contain; }
        .gallery-item { scroll-snap-align: start; }
        """
        features = parse_features(css)
        assert "flexbox" in features
        assert "css-snappoints" in features
        assert "css-scroll-behavior" in features
        assert "css-overscroll-behavior" in features

    def test_animation_keyframes(self, parse_features):
        css = """
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-in { animation: fadeInUp 0.5s ease-out forwards; }
        @media (prefers-reduced-motion: reduce) { .animate-in { animation: none; } }
        """
        features = parse_features(css)
        assert "css-animation" in features
        assert "css-opacity" in features
        assert "transforms2d" in features
        assert "prefers-reduced-motion" in features

    def test_glassmorphism_effect(self, parse_features):
        css = """
        .glass {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px;
        }
        """
        features = parse_features(css)
        assert "css3-colors" in features
        assert "css-backdrop-filter" in features
        assert "border-radius" in features

    def test_css_layers_pattern(self, parse_features):
        css = """
        @layer reset, base, components, utilities;
        @layer reset { *, *::before, *::after { box-sizing: border-box; margin: 0; } }
        @layer base { body { font-family: system-ui, sans-serif; } }
        """
        features = parse_features(css)
        assert "css-cascade-layers" in features
        assert "css3-boxsizing" in features
        assert "css-gencontent" in features
        assert "font-family-system-ui" in features

    def test_bootstrap_like_grid(self, parse_features):
        css = """
        .container { display: flex; flex-wrap: wrap; }
        .col { flex: 1 0 0%; }
        @media (min-width: 768px) { .col-md-6 { flex: 0 0 auto; width: 50%; } }
        """
        features = parse_features(css)
        assert "flexbox" in features
        assert "css-mediaqueries" in features

    def test_container_query_layout(self, parse_features):
        css = """
        .card-container { container-type: inline-size; container-name: card; }
        @container card (min-width: 400px) {
            .card { display: grid; grid-template-columns: 1fr 2fr; gap: 1rem; }
        }
        """
        features = parse_features(css)
        assert "css-container-queries" in features
        assert "css-grid" in features
