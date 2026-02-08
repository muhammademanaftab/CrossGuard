"""Tests for the tinycss2 parsing pipeline and edge cases.

Covers: _extract_components, _build_matchable_text, _extract_block_contents,
block boundary preservation, @font-face declarations, @keyframes stops,
nested @media/@supports, CSS nesting, deep nesting, minified CSS,
comments stripping, malformed CSS recovery, vendor prefixes, encoding.
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
# SECTION 1: Block Boundary Preservation (flexbox-gap)
# ═══════════════════════════════════════════════════════════════════════════

class TestBlockBoundaryPreservation:
    """Verify that block boundaries are preserved correctly for patterns
    like flexbox-gap that use [^}]* to match within a single block."""

    def test_flex_and_gap_same_block(self, parse_css):
        css = ".container { display: flex; gap: 10px; }"
        assert 'flexbox-gap' in parse_css(css)

    def test_flex_and_gap_different_blocks(self, parse_css):
        """flex in one block, gap in another — should NOT detect flexbox-gap."""
        css = """
        .flex { display: flex; }
        .grid { display: grid; gap: 10px; }
        """
        features = parse_css(css)
        assert 'flexbox-gap' not in features

    def test_flex_and_row_gap_same_block(self, parse_css):
        css = ".container { display: flex; row-gap: 10px; }"
        assert 'flexbox-gap' in parse_css(css)

    def test_flex_and_column_gap_same_block(self, parse_css):
        css = ".container { display: flex; column-gap: 10px; }"
        assert 'flexbox-gap' in parse_css(css)

    def test_gap_before_flex_same_block(self, parse_css):
        """gap: declared before display: flex — should still detect."""
        css = ".container { gap: 10px; display: flex; }"
        assert 'flexbox-gap' in parse_css(css)

    def test_inline_flex_with_gap(self, parse_css):
        css = ".container { display: inline-flex; gap: 10px; }"
        assert 'flexbox-gap' in parse_css(css)

    def test_duplicate_selectors_separate_blocks(self, parse_css):
        """Same selector in two blocks — blocks should stay separate."""
        css = """
        .item { display: flex; }
        .item { gap: 10px; }
        """
        features = parse_css(css)
        # These are separate blocks, so flexbox-gap should NOT match
        assert 'flexbox-gap' not in features

    def test_grid_gap_not_detected_as_flexbox_gap(self, parse_css):
        css = ".grid { display: grid; gap: 10px; }"
        features = parse_css(css)
        assert 'flexbox-gap' not in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: @font-face Handling
# ═══════════════════════════════════════════════════════════════════════════

class TestFontFaceHandling:
    """Verify @font-face declarations are extracted correctly."""

    def test_font_face_basic(self, parse_css):
        css = """@font-face {
            font-family: 'MyFont';
            src: url('font.woff2') format('woff2');
        }"""
        features = parse_css(css)
        assert 'fontface' in features
        assert 'woff2' in features

    def test_font_face_multiple_sources(self, parse_css):
        css = """@font-face {
            font-family: 'MyFont';
            src: url('font.woff2') format('woff2'),
                 url('font.woff') format('woff');
        }"""
        features = parse_css(css)
        assert 'fontface' in features
        assert 'woff2' in features
        assert 'woff' in features

    def test_font_face_font_display(self, parse_css):
        css = """@font-face {
            font-family: 'MyFont';
            src: url('font.woff2');
            font-display: swap;
        }"""
        features = parse_css(css)
        assert 'css-font-rendering-controls' in features

    def test_font_face_unicode_range(self, parse_css):
        css = """@font-face {
            font-family: 'MyFont';
            src: url('font.woff2');
            unicode-range: U+0000-00FF;
        }"""
        features = parse_css(css)
        assert 'font-unicode-range' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: @keyframes Inner Stops
# ═══════════════════════════════════════════════════════════════════════════

class TestKeyframesHandling:
    """Verify @keyframes inner stops are parsed correctly."""

    def test_keyframes_basic(self, parse_css):
        css = """@keyframes slide {
            from { transform: translateX(0); }
            to { transform: translateX(100px); }
        }"""
        features = parse_css(css)
        assert 'css-animation' in features
        assert 'transforms2d' in features

    def test_keyframes_percentage_stops(self, parse_css):
        css = """@keyframes fade {
            0% { opacity: 0; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }"""
        features = parse_css(css)
        assert 'css-animation' in features

    def test_keyframes_with_modern_features(self, parse_css):
        css = """@keyframes expand {
            from { clip-path: circle(0%); }
            to { clip-path: circle(100%); }
        }"""
        features = parse_css(css)
        assert 'css-animation' in features
        assert 'css-clip-path' in features

    def test_keyframes_3d_transform(self, parse_css):
        css = """@keyframes rotate3d {
            from { transform: rotateY(0deg); }
            to { transform: rotateY(360deg); }
        }"""
        features = parse_css(css)
        assert 'transforms3d' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Nested @media and @supports
# ═══════════════════════════════════════════════════════════════════════════

class TestNestedAtRules:
    """Verify nested @-rules are parsed correctly."""

    def test_media_wrapping_rules(self, parse_css):
        css = """@media (max-width: 768px) {
            .container { display: flex; }
            .item { opacity: 0.5; }
        }"""
        features = parse_css(css)
        assert 'css-mediaqueries' in features
        assert 'flexbox' in features

    def test_supports_wrapping_rules(self, parse_css):
        css = """@supports (display: grid) {
            .container { display: grid; }
        }"""
        features = parse_css(css)
        assert 'css-featurequeries' in features
        assert 'css-grid' in features

    def test_media_inside_supports(self, parse_css):
        css = """@supports (display: grid) {
            @media (min-width: 768px) {
                .container { display: grid; }
            }
        }"""
        features = parse_css(css)
        assert 'css-featurequeries' in features
        assert 'css-mediaqueries' in features
        assert 'css-grid' in features

    def test_supports_inside_media(self, parse_css):
        css = """@media (min-width: 768px) {
            @supports (display: grid) {
                .grid { display: grid; }
            }
        }"""
        features = parse_css(css)
        assert 'css-mediaqueries' in features
        assert 'css-featurequeries' in features
        assert 'css-grid' in features

    def test_layer_with_rules(self, parse_css):
        css = """@layer utilities {
            .flex { display: flex; }
        }"""
        features = parse_css(css)
        assert 'css-cascade-layers' in features
        assert 'flexbox' in features

    def test_container_query_with_rules(self, parse_css):
        css = """@container (min-width: 400px) {
            .card { display: grid; }
        }"""
        features = parse_css(css)
        assert 'css-container-queries' in features
        assert 'css-grid' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: CSS Nesting with tinycss2
# ═══════════════════════════════════════════════════════════════════════════

class TestCSSNesting:
    """Verify CSS nesting is handled by tinycss2."""

    def test_nesting_hover(self, parse_css):
        css = """.parent {
            color: blue;
            &:hover { color: red; }
        }"""
        features = parse_css(css)
        assert 'css-nesting' in features

    def test_nesting_child_selector(self, parse_css):
        css = """.parent {
            color: blue;
            & .child { color: green; }
        }"""
        features = parse_css(css)
        assert 'css-nesting' in features

    def test_nesting_with_ampersand_block(self, parse_css):
        css = """.card {
            padding: 1rem;
            & {
                background: white;
            }
        }"""
        features = parse_css(css)
        assert 'css-nesting' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: Deep Nesting
# ═══════════════════════════════════════════════════════════════════════════

class TestDeepNesting:
    """Verify deeply nested CSS structures don't break the parser."""

    def test_three_levels_deep(self, parse_css):
        css = """@media (min-width: 768px) {
            @supports (display: grid) {
                @layer layout {
                    .grid { display: grid; }
                }
            }
        }"""
        features = parse_css(css)
        assert 'css-mediaqueries' in features
        assert 'css-featurequeries' in features
        assert 'css-cascade-layers' in features
        assert 'css-grid' in features

    def test_four_levels_deep(self, parse_css):
        css = """@layer base {
            @media screen {
                @supports (display: flex) {
                    @container (min-width: 400px) {
                        .item { display: flex; }
                    }
                }
            }
        }"""
        features = parse_css(css)
        assert 'css-cascade-layers' in features
        assert 'css-mediaqueries' in features
        assert 'css-featurequeries' in features
        assert 'css-container-queries' in features
        assert 'flexbox' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: Minified CSS
# ═══════════════════════════════════════════════════════════════════════════

class TestMinifiedCSS:
    """Verify minified (single-line, no whitespace) CSS works."""

    def test_minified_basic(self, parse_css):
        css = ".a{display:flex}.b{display:grid}.c{opacity:.5}"
        features = parse_css(css)
        assert 'flexbox' in features
        assert 'css-grid' in features

    def test_minified_media_query(self, parse_css):
        css = "@media(max-width:768px){.a{display:flex}}"
        features = parse_css(css)
        assert 'css-mediaqueries' in features
        assert 'flexbox' in features

    def test_minified_keyframes(self, parse_css):
        css = "@keyframes x{from{opacity:0}to{opacity:1}}"
        features = parse_css(css)
        assert 'css-animation' in features

    def test_minified_with_variables(self, parse_css):
        css = ":root{--c:red}div{color:var(--c)}"
        features = parse_css(css)
        assert 'css-variables' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: Comments Handling
# ═══════════════════════════════════════════════════════════════════════════

class TestCommentsHandling:
    """Verify that CSS comments are stripped by tinycss2 and don't cause
    false positive feature detections."""

    def test_feature_in_comment_not_detected(self, parse_css):
        css = """/* display: grid; */
        body { margin: 0; }"""
        features = parse_css(css)
        assert 'css-grid' not in features

    def test_comment_between_declarations(self, parse_css):
        css = """div {
            display: flex;
            /* gap: 10px; */
            color: red;
        }"""
        features = parse_css(css)
        assert 'flexbox' in features
        assert 'flexbox-gap' not in features

    def test_comment_before_rule(self, parse_css):
        css = """/* Layout styles */
        .container { display: grid; }"""
        features = parse_css(css)
        assert 'css-grid' in features

    def test_multiline_comment_with_features(self, parse_css):
        css = """/*
        @keyframes fade {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        */
        body { color: black; }"""
        features = parse_css(css)
        assert 'css-animation' not in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: Malformed CSS Recovery
# ═══════════════════════════════════════════════════════════════════════════

class TestMalformedCSS:
    """Verify the parser handles malformed CSS gracefully."""

    def test_missing_closing_brace(self, parse_css):
        css = "div { display: flex; "
        # tinycss2 should handle this gracefully
        features = parse_css(css)
        # Should still detect what it can
        assert isinstance(features, set)

    def test_missing_semicolon(self, parse_css):
        css = "div { display: flex }"
        features = parse_css(css)
        # tinycss2 may or may not parse this correctly
        assert isinstance(features, set)

    def test_extra_closing_brace(self, parse_css):
        css = "div { display: grid; } }"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_empty_rule(self, parse_css):
        css = "div { }"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_only_at_rule_no_block(self, parse_css):
        css = "@import url('style.css');"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_invalid_property_name(self, parse_css):
        css = "div { 123invalid: value; }"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_double_colon_in_value(self, parse_css):
        css = "div { content: '::'; }"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_unclosed_string(self, parse_css):
        css = "div { content: 'unclosed; }"
        features = parse_css(css)
        assert isinstance(features, set)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: Vendor Prefix Handling
# ═══════════════════════════════════════════════════════════════════════════

class TestVendorPrefixes:
    """Verify vendor-prefixed properties are detected by patterns."""

    def test_webkit_font_smoothing(self, parse_css):
        css = "body { -webkit-font-smoothing: antialiased; }"
        assert 'font-smooth' in parse_css(css)

    def test_moz_font_smoothing(self, parse_css):
        css = "body { -moz-osx-font-smoothing: grayscale; }"
        assert 'font-smooth' in parse_css(css)

    def test_webkit_text_stroke(self, parse_css):
        css = "h1 { -webkit-text-stroke: 1px black; }"
        assert 'text-stroke' in parse_css(css)

    def test_webkit_appearance(self, parse_css):
        css = "button { -webkit-appearance: none; }"
        assert 'css-appearance' in parse_css(css)

    def test_webkit_user_select(self, parse_css):
        css = "div { -webkit-user-select: none; }"
        assert 'user-select-none' in parse_css(css)

    def test_webkit_background_clip_text(self, parse_css):
        css = "h1 { -webkit-background-clip: text; }"
        assert 'background-clip-text' in parse_css(css)

    def test_webkit_box_reflect(self, parse_css):
        css = "img { -webkit-box-reflect: below; }"
        assert 'css-reflections' in parse_css(css)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 11: Empty and Edge Cases
# ═══════════════════════════════════════════════════════════════════════════

class TestEmptyAndEdgeCases:
    """Edge cases for input handling."""

    def test_empty_string(self, parse_css):
        assert len(parse_css("")) == 0

    def test_whitespace_only(self, parse_css):
        assert len(parse_css("   \n\t  ")) == 0

    def test_comment_only(self, parse_css):
        assert len(parse_css("/* comment */")) == 0

    def test_multiple_empty_rules(self, parse_css):
        css = "div {} span {} p {}"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_very_long_selector(self, parse_css):
        sel = " > ".join([f".level{i}" for i in range(50)])
        css = f"{sel} {{ display: flex; }}"
        features = parse_css(css)
        assert 'flexbox' in features

    def test_many_declarations_in_one_block(self, parse_css):
        props = "; ".join([f"--prop-{i}: value{i}" for i in range(100)])
        css = f":root {{ {props}; }}"
        features = parse_css(css)
        assert 'css-variables' in features

    def test_unicode_in_content(self, parse_css):
        css = "div::before { content: '\\2764'; }"
        features = parse_css(css)
        assert 'css-gencontent' in features

    def test_case_insensitive_properties(self, parse_css):
        """CSS properties are case-insensitive per spec."""
        css = "div { Display: FLEX; }"
        features = parse_css(css)
        assert 'flexbox' in features

    def test_case_insensitive_at_rules(self, parse_css):
        css = "@MEDIA screen { div { color: red; } }"
        features = parse_css(css)
        # tinycss2 normalizes at-rule keywords to lowercase
        assert 'css-mediaqueries' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 12: _build_matchable_text Internal Behavior
# ═══════════════════════════════════════════════════════════════════════════

class TestBuildMatchableText:
    """Verify the matchable text is reconstructed correctly."""

    def test_matchable_text_contains_selectors(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            ".container { display: flex; }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        assert '.container' in text

    def test_matchable_text_contains_properties(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "div { display: flex; gap: 10px; }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        assert 'display' in text
        assert 'flex' in text
        assert 'gap' in text

    def test_matchable_text_has_braces(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "div { color: red; }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        assert '{' in text
        assert '}' in text

    def test_matchable_text_at_rules(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@media screen { div { color: red; } }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        assert '@media' in text

    def test_matchable_text_block_separation(self, css_parser):
        """Two blocks with same selector should stay separate."""
        import tinycss2
        css = ".a { display: flex; } .a { gap: 10px; }"
        rules = tinycss2.parse_stylesheet(
            css, skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        text = css_parser._build_matchable_text(declarations, at_rules, selectors)
        # Should have two separate blocks for .a
        # Count occurrences of '.a {'
        import re
        blocks = re.findall(r'\.a\s*\{', text)
        assert len(blocks) == 2


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 13: _extract_components Structure
# ═══════════════════════════════════════════════════════════════════════════

class TestExtractComponents:
    """Verify _extract_components returns correct structured data."""

    def test_simple_declaration(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "div { color: red; }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        assert len(declarations) >= 1
        # Declaration: (property_name, value_string, selector, block_id)
        prop_names = [d[0] for d in declarations]
        assert 'color' in prop_names

    def test_selectors_extracted(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            ".foo { color: red; } #bar { color: blue; }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        assert '.foo' in selectors
        assert '#bar' in selectors

    def test_at_rules_extracted(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@media screen { div { color: red; } }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        at_keywords = [a[0] for a in at_rules]
        assert 'media' in at_keywords

    def test_font_face_declarations(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@font-face { font-family: 'Test'; font-weight: bold; }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        prop_names = [d[0] for d in declarations]
        assert 'font-family' in prop_names
        assert 'font-weight' in prop_names

    def test_keyframes_stops_as_selectors(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@keyframes fade { from { opacity: 0; } to { opacity: 1; } }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        # Keyframe stops (from, to) should appear as selectors
        assert any('from' in s for s in selectors)
        assert any('to' in s for s in selectors)

    def test_parse_error_handled(self, css_parser):
        """Parse errors should be logged and skipped, not crash."""
        import tinycss2
        # This produces a parse error node
        rules = tinycss2.parse_stylesheet(
            "@@invalid { }",
            skip_comments=True, skip_whitespace=True
        )
        # Should not raise
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        assert isinstance(declarations, list)

    def test_nested_media_extracts_inner(self, css_parser):
        import tinycss2
        rules = tinycss2.parse_stylesheet(
            "@media screen { .inner { display: grid; } }",
            skip_comments=True, skip_whitespace=True
        )
        declarations, at_rules, selectors = css_parser._extract_components(rules)
        # Inner selector should be extracted
        assert '.inner' in selectors
        # Inner declaration should be extracted
        prop_names = [d[0] for d in declarations]
        assert 'display' in prop_names


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 14: @import and @charset (no-block @-rules)
# ═══════════════════════════════════════════════════════════════════════════

class TestNoBlockAtRules:
    """Verify @-rules without blocks (@import, @charset) don't crash."""

    def test_import_rule(self, parse_css):
        css = "@import url('style.css');"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_charset_rule(self, parse_css):
        css = "@charset 'UTF-8';"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_import_with_media(self, parse_css):
        css = "@import url('print.css') print;"
        features = parse_css(css)
        assert isinstance(features, set)

    def test_namespace_rule(self, parse_css):
        css = "@namespace svg url(http://www.w3.org/2000/svg);"
        features = parse_css(css)
        assert 'css-namespaces' in features

    def test_multiple_imports(self, parse_css):
        css = """
        @import url('reset.css');
        @import url('base.css');
        body { display: flex; }
        """
        features = parse_css(css)
        assert 'flexbox' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 15: Real-World Complex CSS
# ═══════════════════════════════════════════════════════════════════════════

class TestRealWorldCSS:
    """Complex real-world CSS patterns."""

    def test_bootstrap_like_grid(self, parse_css):
        css = """
        .container { display: flex; flex-wrap: wrap; }
        .row { display: flex; flex-wrap: wrap; margin: -0.5rem; }
        .col { flex: 1 0 0%; }
        .col-6 { flex: 0 0 auto; width: 50%; }
        @media (min-width: 768px) {
            .col-md-6 { flex: 0 0 auto; width: 50%; }
        }
        """
        features = parse_css(css)
        assert 'flexbox' in features
        assert 'css-mediaqueries' in features

    def test_modern_css_reset(self, parse_css):
        css = """
        *, *::before, *::after { box-sizing: border-box; }
        body { min-height: 100vh; line-height: 1.5; }
        img, picture, video, canvas, svg { display: block; max-width: 100%; }
        input, button, textarea, select { font: inherit; }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation-duration: 0.01ms !important; }
        }
        """
        features = parse_css(css)
        assert 'css3-boxsizing' in features
        assert 'css-gencontent' in features
        assert 'prefers-reduced-motion' in features
        assert 'viewport-units' in features

    def test_dark_mode_theme(self, parse_css):
        css = """
        :root {
            --bg: #ffffff;
            --fg: #000000;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #1a1a1a;
                --fg: #ffffff;
            }
        }
        body { background: var(--bg); color: var(--fg); }
        """
        features = parse_css(css)
        assert 'css-variables' in features
        assert 'prefers-color-scheme' in features

    def test_container_query_layout(self, parse_css):
        css = """
        .card-container { container-type: inline-size; container-name: card; }
        @container card (min-width: 400px) {
            .card { display: grid; grid-template-columns: 1fr 2fr; gap: 1rem; }
        }
        @container card (min-width: 700px) {
            .card { grid-template-columns: 1fr 1fr 1fr; }
        }
        """
        features = parse_css(css)
        assert 'css-container-queries' in features
        assert 'css-grid' in features

    def test_complex_animation(self, parse_css):
        css = """
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        .skeleton {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
        }
        """
        features = parse_css(css)
        assert 'css-animation' in features
        assert 'css-gradients' in features

    def test_scroll_snap_gallery(self, parse_css):
        css = """
        .gallery {
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            scroll-behavior: smooth;
        }
        .gallery-item {
            flex: 0 0 100%;
            scroll-snap-align: start;
        }
        """
        features = parse_css(css)
        assert 'flexbox' in features
        assert 'css-snappoints' in features
        assert 'css-scroll-behavior' in features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 16: False Positive Detection (Known Bugs)
# ═══════════════════════════════════════════════════════════════════════════

class TestFalsePositives:
    """Document known false positive bugs in feature detection patterns."""

    def test_keyframes_from_no_relative_colors(self, parse_css):
        """@keyframes 'from' stop must NOT trigger css-relative-colors.

        The pattern requires a color function prefix like oklch(from ...)
        so bare 'from' in keyframes is correctly ignored.
        """
        css = """@keyframes fade {
            from { opacity: 0; }
            to { opacity: 1; }
        }"""
        features = parse_css(css)
        assert 'css-relative-colors' not in features

    def test_percentage_keyframes_no_false_positive(self, parse_css):
        """Percentage keyframes (no 'from' keyword) should NOT trigger."""
        css = """@keyframes slide {
            0% { transform: translateX(0); }
            100% { transform: translateX(100px); }
        }"""
        features = parse_css(css)
        assert 'css-relative-colors' not in features

    def test_actual_relative_colors_detected(self, parse_css):
        """Verify actual relative color syntax IS detected."""
        css = "div { color: oklch(from red l c h); }"
        assert 'css-relative-colors' in parse_css(css)

    def test_stats_css_has_correctly_categorized(self, parse_css):
        """css-has and other selector features are correctly categorized.

        Selector features like css-has, css-focus-within, css-focus-visible,
        css-any-link, etc. are now matched by an explicit set of selector
        feature IDs instead of fragile string heuristics.
        """
        parser = CSSParser()
        parser.parse_string("div:has(.child) { color: red; }")
        stats = parser.get_statistics()
        assert 'css-has' in stats['categories']['selectors']
