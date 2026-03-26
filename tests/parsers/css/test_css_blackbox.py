"""CSS parser black box tests.

Tests the public API: CSS string input -> detected feature IDs.
No mocking, no internal imports, no internal state inspection.
"""

import pytest
from src.parsers.css_parser import parse_css_string


# --- Feature Detection: representative samples per category ---

CSS_FEATURES = [
    # Layout
    pytest.param(".c{display:inline-block}", "inline-block", id="inline-block"),
    pytest.param(".c{display:flex}", "flexbox", id="flexbox"),
    pytest.param(".c{display:flex;gap:20px}", "flexbox-gap", id="flexbox-gap"),
    pytest.param(".c{display:grid}", "css-grid", id="css-grid"),
    pytest.param(".c{column-count:3}", "multicolumn", id="multicolumn"),
    # Colors
    pytest.param(".c{color:rgba(255,0,0,.5)}", "css3-colors", id="css3-colors"),
    pytest.param(".c{color:lch(50% 100 180)}", "css-lch-lab", id="css-lch-lab"),
    pytest.param(".c{color:rgb(from red r g b / 50%)}", "css-relative-colors", id="relative-colors"),
    # Backgrounds
    pytest.param(".c{background:linear-gradient(to right,red,blue)}", "css-gradients", id="css-gradients"),
    pytest.param(".c{background:url(a.png),url(b.png)}", "multibackgrounds", id="multibackgrounds"),
    pytest.param(".c{background-clip:text}", "background-clip-text", id="bg-clip-text"),
    pytest.param('.c{background-image:image-set("i.png" 1x)}', "css-image-set", id="css-image-set"),
    # Filters
    pytest.param(".c{filter:blur(5px)}", "css-filter-function", id="filter-function"),
    pytest.param(".c{backdrop-filter:blur(10px)}", "css-backdrop-filter", id="backdrop-filter"),
    pytest.param(".c{mix-blend-mode:multiply}", "css-mixblendmode", id="mix-blend-mode"),
    # Fonts
    pytest.param("@font-face{font-family:F;src:local(T)}", "fontface", id="fontface"),
    pytest.param(".c{font-variation-settings:'wght' 700}", "variable-fonts", id="variable-fonts"),
    pytest.param(".c{font-family:system-ui,sans-serif}", "font-family-system-ui", id="system-ui"),
    pytest.param("@font-face{font-display:swap}", "css-font-rendering-controls", id="font-display"),
    # Text
    pytest.param(".c{text-overflow:ellipsis}", "text-overflow", id="text-overflow"),
    pytest.param(".c{text-decoration-line:underline}", "text-decoration", id="text-decoration"),
    pytest.param(".c{hyphens:auto}", "css-hyphens", id="hyphens"),
    pytest.param(".c{line-clamp:3}", "css-line-clamp", id="line-clamp"),
    pytest.param(".c{text-box-trim:both}", "css-text-box-trim", id="text-box-trim"),
    # Box Model
    pytest.param("*{box-sizing:border-box}", "css3-boxsizing", id="box-sizing"),
    pytest.param("img{object-fit:cover}", "object-fit", id="object-fit"),
    pytest.param(".c{border-radius:10px}", "border-radius", id="border-radius"),
    pytest.param(".c{box-shadow:0 2px 4px rgba(0,0,0,0.1)}", "css-boxshadow", id="box-shadow"),
    # Units & Variables
    pytest.param("body{font-size:1rem}", "rem", id="rem"),
    pytest.param(".c{width:100vw}", "viewport-units", id="viewport-units"),
    pytest.param(".c{width:calc(100% - 20px)}", "calc", id="calc"),
    pytest.param(":root{--c:#007bff}", "css-variables", id="css-variables"),
    # Misc
    pytest.param(".c{opacity:0.5}", "css-opacity", id="opacity"),
    pytest.param(".c{position:sticky;top:0}", "css-sticky", id="sticky"),
    pytest.param(".c{all:unset}", "css-all", id="css-all"),
    pytest.param(".c{background:url(icon.svg)}", "svg-css", id="svg-css"),
    pytest.param("p::first-letter{initial-letter:3}", "css-initial-letter", id="initial-letter"),
    # Interaction
    pytest.param(".c{pointer-events:none}", "pointer-events", id="pointer-events"),
    pytest.param(".c{user-select:none}", "user-select-none", id="user-select"),
    pytest.param("button{appearance:none}", "css-appearance", id="appearance"),
    pytest.param(".c{scroll-snap-type:x mandatory}", "css-snappoints", id="scroll-snap"),
    # Transforms & Animation
    pytest.param(".c{transform:rotate(45deg)}", "transforms2d", id="transforms2d"),
    pytest.param(".c{transform:translate3d(50px,100px,20px)}", "transforms3d", id="transforms3d"),
    pytest.param("@keyframes f{from{opacity:0}to{opacity:1}}", "css-animation", id="animation"),
    pytest.param(".c{transition:all 0.3s ease}", "css-transitions", id="transitions"),
    pytest.param(".c{will-change:transform}", "will-change", id="will-change"),
    # Selectors
    pytest.param("li:nth-child(odd){background:#eee}", "css-sel3", id="css-sel3"),
    pytest.param(".c::before{content:'x'}", "css-gencontent", id="gencontent"),
    pytest.param("article:has(img){padding:20px}", "css-has", id="css-has"),
    pytest.param("button:focus-visible{outline:2px solid blue}", "css-focus-visible", id="focus-visible"),
    pytest.param(":is(h1,h2,h3){margin-top:1em}", "css-matches-pseudo", id="matches-pseudo"),
    # At-rules
    pytest.param("@supports(display:grid){.g{display:grid}}", "css-featurequeries", id="feature-queries"),
    pytest.param("body{counter-reset:section}", "css-counters", id="counters"),
    pytest.param("@layer base{body{margin:0}}", "css-cascade-layers", id="cascade-layers"),
    pytest.param("@scope(.card){h2{color:blue}}", "css-cascade-scope", id="cascade-scope"),
    # Media Queries
    pytest.param("@media screen{body{color:black}}", "css-mediaqueries", id="media-queries"),
    pytest.param("@media(prefers-color-scheme:dark){body{background:#1a1a1a}}", "prefers-color-scheme", id="color-scheme"),
    pytest.param("@media(prefers-reduced-motion:reduce){*{animation:none!important}}", "prefers-reduced-motion", id="reduced-motion"),
    pytest.param("@media(width < 600px){.m{display:block}}", "css-media-range-syntax", id="range-syntax"),
    # Modern CSS
    pytest.param("@container(min-width:400px){.c{display:flex}}", "css-container-queries", id="container-queries"),
    pytest.param(".c{&:hover{background:blue}}", "css-nesting", id="css-nesting"),
    pytest.param(".c{anchor-name:--my-anchor}", "css-anchor-positioning", id="anchor-positioning"),
    pytest.param(".c{margin-inline:auto}", "css-logical-props", id="logical-props"),
    pytest.param("::view-transition-old(root){animation:fade-out 0.5s}", "view-transitions", id="view-transitions"),
    # Font Formats
    pytest.param("@font-face{font-family:'T';src:url('f.woff')format('woff')}", "woff", id="woff"),
    pytest.param("@font-face{font-family:'T';src:url('f.woff2')format('woff2')}", "woff2", id="woff2"),
    pytest.param("@font-face{font-family:'T';src:url('f.ttf')format('truetype')}", "ttf", id="ttf"),
    # Feature Gaps
    pytest.param("div{grid-template-columns:1fr;transition:grid-template-columns 0.3s}", "css-grid-animation", id="grid-animation"),
    pytest.param(":fullscreen{background:black}", "fullscreen", id="fullscreen"),
]


@pytest.mark.blackbox
class TestFeatureDetection:
    """One representative test per caniuse feature ID, across all categories."""

    @pytest.mark.parametrize("css_input,expected_id", CSS_FEATURES)
    def test_feature_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.blackbox
class TestCombinedFeatures:
    """Multiple features detected simultaneously."""

    def test_flex_and_gap_both_detected(self, parse_features):
        features = parse_features(".c{display:flex;gap:1rem}")
        assert "flexbox" in features
        assert "flexbox-gap" in features

    def test_grid_and_subgrid_detected(self, parse_features):
        features = parse_features(".c{display:grid;grid-template-columns:subgrid}")
        assert "css-grid" in features
        assert "css-subgrid" in features


@pytest.mark.blackbox
class TestFalsePositivePrevention:
    def test_keyframes_from_no_relative_colors(self, parse_features):
        css = "@keyframes fade { from { opacity: 0; } to { opacity: 1; } }"
        assert "css-relative-colors" not in parse_features(css)

    def test_actual_relative_colors_detected(self, parse_features):
        assert "css-relative-colors" in parse_features("div { color: oklch(from red l c h); }")


# --- Edge Cases ---

@pytest.mark.blackbox
class TestCommentHandling:
    def test_feature_in_comment_not_detected(self, parse_features):
        assert "css-grid" not in parse_features("/* display: grid; */ .element { color: red; }")

    def test_feature_after_comment(self, parse_features):
        assert "css-grid" in parse_features("/* comment */ .element { display: grid; }")

    def test_multiline_comment(self, parse_features):
        css = "/* display: flex; \n display: grid; */ .element { color: red; }"
        features = parse_features(css)
        assert "flexbox" not in features
        assert "css-grid" not in features

    def test_comment_between_features(self, parse_features):
        css = ".flex { display: flex; } /* comment */ .grid { display: grid; }"
        features = parse_features(css)
        assert "flexbox" in features
        assert "css-grid" in features


@pytest.mark.blackbox
class TestEmptyInput:
    def test_empty_string(self, parse_features):
        assert parse_features("") == set()

    def test_whitespace_only(self, parse_features):
        assert parse_features("   \n\t  ") == set()

    def test_comment_only(self, parse_features):
        assert parse_features("/* just a comment */") == set()


@pytest.mark.blackbox
class TestMalformedCSS:
    def test_missing_closing_brace(self, parse_features):
        assert "css-grid" in parse_features(".element { display: grid; ")

    def test_missing_semicolon(self, parse_features):
        assert "css-grid" in parse_features(".element { display: grid }")

    def test_extra_braces(self, parse_features):
        assert "css-grid" in parse_features(".element {{ display: grid; }}")

    def test_unclosed_string(self, parse_features):
        assert isinstance(parse_features('.element { content: "unclosed; }'), set)


@pytest.mark.blackbox
class TestStringHandling:
    def test_feature_in_url_string(self, parse_features):
        parse_features('.element { background: url("grid-pattern.png"); }')


@pytest.mark.blackbox
class TestMultipleFeatures:
    def test_multiple_features_same_rule(self, parse_features):
        features = parse_features(".element { display: flex; gap: 20px; border-radius: 10px; }")
        assert "flexbox" in features
        assert "flexbox-gap" in features
        assert "border-radius" in features

    def test_many_features(self, parse_features):
        css = """
        :root { --primary: blue; }
        .container { display: grid; gap: 20px; }
        .card { border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.3s; }
        .card:hover { transform: scale(1.05); }
        @media (prefers-color-scheme: dark) { body { background: #1a1a1a; } }
        """
        features = parse_features(css)
        assert "css-variables" in features
        assert "css-grid" in features
        assert "border-radius" in features
        assert "css-boxshadow" in features
        assert "css-transitions" in features
        assert "transforms2d" in features
        assert "prefers-color-scheme" in features


@pytest.mark.blackbox
class TestCaseSensitivity:
    def test_uppercase_property(self, parse_features):
        assert "css-grid" in parse_features(".element { DISPLAY: GRID; }")

    def test_mixed_case_property(self, parse_features):
        assert "css-grid" in parse_features(".element { Display: Grid; }")

    def test_uppercase_value(self, parse_features):
        assert "css-sticky" in parse_features(".element { position: STICKY; }")


@pytest.mark.blackbox
class TestWhitespaceHandling:
    def test_no_space_around_colon(self, parse_features):
        assert "css-grid" in parse_features(".element{display:grid}")

    def test_extra_whitespace(self, parse_features):
        assert "css-grid" in parse_features(".element  {   display  :   grid   ;   }")

    def test_newlines_in_rule(self, parse_features):
        css = ".element\n{\n    display\n    :\n    grid\n    ;\n}"
        assert "css-grid" in parse_features(css)


# --- Validate CSS ---

@pytest.mark.blackbox
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


# --- Convenience Functions ---

@pytest.mark.blackbox
class TestConvenienceFunctions:
    def test_parse_css_string_basic(self):
        assert "css-grid" in parse_css_string("div { display: grid; }")

    def test_parse_css_string_empty(self):
        assert len(parse_css_string("")) == 0
