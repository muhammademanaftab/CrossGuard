"""Consolidated CSS feature detection tests.

Merged from: layout/, colors_backgrounds/, typography/, box_model/,
units_variables/, misc/, interaction/, transforms_animation/

Uses parametrize tables grouped by feature category. One representative
input per property; value-variants collapsed.
"""

import pytest


# --- Layout Features ---

CSS_LAYOUT_FEATURES = [
    # display values
    pytest.param(".c{display:inline-block}", "inline-block", id="inline-block"),
    pytest.param(".c{display:flow-root}", "flow-root", id="flow-root"),
    pytest.param(".c{display:run-in}", "run-in", id="run-in"),
    pytest.param(".c{display:contents}", "css-display-contents", id="display-contents"),
    pytest.param(".c{display:table}", "css-table", id="table"),
    pytest.param(".c{display:table-cell}", "css-table", id="table-cell"),
    # flexbox
    pytest.param(".c{display:flex}", "flexbox", id="flex"),
    pytest.param(".c{flex-direction:column}", "flexbox", id="flex-direction"),
    pytest.param(".c{flex-wrap:wrap}", "flexbox", id="flex-wrap"),
    # flexbox-gap (context-aware)
    pytest.param(".c{display:flex;gap:20px}", "flexbox-gap", id="flexbox-gap"),
    pytest.param(".c{display:flex;row-gap:20px}", "flexbox-gap", id="flexbox-row-gap"),
    pytest.param(".c{display:flex;column-gap:10px}", "flexbox-gap", id="flexbox-col-gap"),
    # grid
    pytest.param(".c{display:grid}", "css-grid", id="grid"),
    pytest.param(".c{grid-template-columns:1fr 1fr}", "css-grid", id="grid-template-cols"),
    pytest.param(".c{grid-template-rows:auto 1fr}", "css-grid", id="grid-template-rows"),
    pytest.param('.c{grid-template-areas:"a b"}', "css-grid", id="grid-template-areas"),
    pytest.param(".c{grid-column:1/3}", "css-grid", id="grid-column"),
    pytest.param(".c{grid-row:1/3}", "css-grid", id="grid-row"),
    # subgrid
    pytest.param(".c{grid-template-columns:subgrid}", "css-subgrid", id="subgrid-cols"),
    pytest.param(".c{grid-template-rows:subgrid}", "css-subgrid", id="subgrid-rows"),
    # multicolumn
    pytest.param(".c{column-count:3}", "multicolumn", id="column-count"),
    pytest.param(".c{column-width:200px}", "multicolumn", id="column-width"),
    pytest.param(".c{column-rule:1px solid #ccc}", "multicolumn", id="column-rule"),
]


# --- Color & Background Features ---

CSS_COLOR_FEATURES = [
    # css3-colors
    pytest.param(".c{color:rgb(255,0,0)}", "css3-colors", id="rgb"),
    pytest.param(".c{color:rgba(255,0,0,.5)}", "css3-colors", id="rgba"),
    pytest.param(".c{color:hsl(120,100%,50%)}", "css3-colors", id="hsl"),
    pytest.param(".c{color:#ff0000}", "css3-colors", id="hex"),
    # currentcolor
    pytest.param(".c{border-color:currentColor}", "currentcolor", id="currentcolor"),
    # 8-digit hex
    pytest.param(".c{background-color:#ff000080}", "css-rrggbbaa", id="rrggbbaa"),
    # lch/lab
    pytest.param(".c{color:lch(50% 100 180)}", "css-lch-lab", id="lch"),
    pytest.param(".c{color:lab(50% 50 50)}", "css-lch-lab", id="lab"),
    pytest.param(".c{color:oklch(70% 0.15 180)}", "css-lch-lab", id="oklch"),
    pytest.param(".c{color:oklab(70% 0.1 -0.1)}", "css-lch-lab", id="oklab"),
    # color()
    pytest.param(".c{color:color(display-p3 1 0 0)}", "css-color-function", id="color-fn"),
    # rebeccapurple
    pytest.param(".c{color:rebeccapurple}", "css-rebeccapurple", id="rebeccapurple"),
    # relative colors
    pytest.param(".c{color:rgb(from red r g b / 50%)}", "css-relative-colors", id="relative-colors"),
]

CSS_BACKGROUND_FEATURES = [
    # gradients
    pytest.param(".c{background:linear-gradient(to right,red,blue)}", "css-gradients", id="linear-gradient"),
    pytest.param(".c{background:radial-gradient(circle,red,blue)}", "css-gradients", id="radial-gradient"),
    # conic
    pytest.param(".c{background:conic-gradient(red,yellow,green)}", "css-conic-gradients", id="conic-gradient"),
    pytest.param(".c{background:repeating-conic-gradient(red 10%,blue 20%)}", "css-conic-gradients", id="repeating-conic"),
    # repeating
    pytest.param(".c{background:repeating-linear-gradient(45deg,red,blue 10px)}", "css-repeating-gradients", id="repeating-linear"),
    pytest.param(".c{background:repeating-radial-gradient(circle,red,blue 10px)}", "css-repeating-gradients", id="repeating-radial"),
    # multi backgrounds
    pytest.param(".c{background:url(a.png),url(b.png)}", "multibackgrounds", id="multi-bg"),
    # background options
    pytest.param(".c{background-size:cover}", "background-img-opts", id="bg-size"),
    pytest.param(".c{background-origin:content-box}", "background-img-opts", id="bg-origin"),
    pytest.param(".c{background-clip:padding-box}", "background-img-opts", id="bg-clip"),
    # background-clip: text
    pytest.param(".c{background-clip:text}", "background-clip-text", id="bg-clip-text"),
    pytest.param(".c{-webkit-background-clip:text}", "background-clip-text", id="webkit-bg-clip-text"),
    # blend mode
    pytest.param(".c{background-blend-mode:multiply}", "css-backgroundblendmode", id="bg-blend-mode"),
    # position-x/y
    pytest.param(".c{background-position-x:center}", "background-position-x-y", id="bg-pos-x"),
    pytest.param(".c{background-position-y:50%}", "background-position-x-y", id="bg-pos-y"),
    # repeat round/space
    pytest.param(".c{background-repeat:round}", "background-repeat-round-space", id="bg-repeat-round"),
    pytest.param(".c{background-repeat:space}", "background-repeat-round-space", id="bg-repeat-space"),
    # attachment
    pytest.param(".c{background-attachment:fixed}", "background-attachment", id="bg-attachment"),
    # image-set
    pytest.param('.c{background-image:image-set("i.png" 1x)}', "css-image-set", id="image-set"),
    pytest.param('.c{background-image:-webkit-image-set("i.png" 1x)}', "css-image-set", id="webkit-image-set"),
]

CSS_FILTER_FEATURES = [
    # filter function
    pytest.param(".c{filter:blur(5px)}", "css-filter-function", id="filter-blur"),
    pytest.param(".c{filter:brightness(150%)}", "css-filter-function", id="filter-brightness"),
    pytest.param(".c{filter:drop-shadow(2px 2px 4px black)}", "css-filter-function", id="filter-drop-shadow"),
    # backdrop-filter
    pytest.param(".c{backdrop-filter:blur(10px)}", "css-backdrop-filter", id="backdrop-filter"),
    pytest.param(".c{-webkit-backdrop-filter:blur(10px)}", "css-backdrop-filter", id="webkit-backdrop-filter"),
    # css-filters
    pytest.param(".c{filter:none}", "css-filters", id="filter-none"),
    pytest.param(".c{filter:url(#blur)}", "css-filters", id="filter-url"),
    # mix-blend-mode
    pytest.param(".c{mix-blend-mode:multiply}", "css-mixblendmode", id="mix-blend-mode"),
]


# --- Typography Features ---

CSS_FONT_FEATURES = [
    # @font-face
    pytest.param("@font-face{font-family:F;src:local(T)}", "fontface", id="fontface"),
    # variable fonts
    pytest.param(".c{font-variation-settings:'wght' 700}", "variable-fonts", id="variable-fonts"),
    pytest.param(".c{font-optical-sizing:auto}", "variable-fonts", id="font-optical-sizing"),
    # font-feature-settings
    pytest.param(".c{font-feature-settings:'liga' 1}", "font-feature", id="font-feature"),
    pytest.param(".c{font-variant-ligatures:common-ligatures}", "font-feature", id="font-variant-ligatures"),
    # font-kerning
    pytest.param(".c{font-kerning:auto}", "font-kerning", id="font-kerning"),
    # font-size-adjust
    pytest.param(".c{font-size-adjust:0.5}", "font-size-adjust", id="font-size-adjust"),
    # font-smooth
    pytest.param(".c{-webkit-font-smoothing:antialiased}", "font-smooth", id="webkit-font-smooth"),
    pytest.param(".c{-moz-osx-font-smoothing:grayscale}", "font-smooth", id="moz-font-smooth"),
    # font-variant-alternates
    pytest.param(".c{font-variant-alternates:stylistic(alt)}", "font-variant-alternates", id="font-variant-alt"),
    # font-variant-numeric
    pytest.param(".c{font-variant-numeric:tabular-nums}", "font-variant-numeric", id="font-variant-numeric"),
    # unicode-range
    pytest.param("@font-face{unicode-range:U+0000-00FF}", "font-unicode-range", id="unicode-range"),
    # system-ui
    pytest.param(".c{font-family:system-ui,sans-serif}", "font-family-system-ui", id="system-ui"),
    # extended system fonts
    pytest.param(".c{font-family:ui-serif,serif}", "extended-system-fonts", id="ui-serif"),
    pytest.param(".c{font-family:ui-monospace,monospace}", "extended-system-fonts", id="ui-monospace"),
    # font-stretch
    pytest.param(".c{font-stretch:condensed}", "css-font-stretch", id="font-stretch"),
    # font-palette
    pytest.param(".c{font-palette:dark}", "css-font-palette", id="font-palette"),
    # font-display
    pytest.param("@font-face{font-display:swap}", "css-font-rendering-controls", id="font-display"),
]

CSS_TEXT_FEATURES = [
    pytest.param(".c{text-overflow:ellipsis}", "text-overflow", id="text-overflow"),
    pytest.param(".c{text-decoration-line:underline}", "text-decoration", id="text-decoration"),
    pytest.param(".c{text-decoration-style:wavy}", "text-decoration", id="text-decoration-style"),
    pytest.param(".c{text-emphasis:filled dot}", "text-emphasis", id="text-emphasis"),
    pytest.param(".c{-webkit-text-stroke:1px black}", "text-stroke", id="text-stroke"),
    pytest.param("body{text-size-adjust:100%}", "text-size-adjust", id="text-size-adjust"),
    pytest.param(".c{word-break:break-all}", "word-break", id="word-break"),
    pytest.param(".c{word-wrap:break-word}", "wordwrap", id="wordwrap"),
    pytest.param(".c{overflow-wrap:break-word}", "wordwrap", id="overflow-wrap"),
    pytest.param("pre{tab-size:4}", "css3-tabsize", id="tab-size"),
    pytest.param(".c{letter-spacing:0.05em}", "css-letter-spacing", id="letter-spacing"),
    pytest.param(".c{text-align-last:justify}", "css-text-align-last", id="text-align-last"),
    pytest.param("p{text-indent:2em}", "css-text-indent", id="text-indent"),
    pytest.param(".c{text-justify:inter-word}", "css-text-justify", id="text-justify"),
    pytest.param(".c{text-orientation:upright}", "css-text-orientation", id="text-orientation"),
    pytest.param(".c{text-spacing:trim-start}", "css-text-spacing", id="text-spacing"),
    pytest.param("h1{text-wrap:balance}", "css-text-wrap-balance", id="text-wrap-balance"),
    pytest.param(".c{hyphens:auto}", "css-hyphens", id="hyphens"),
    pytest.param(".c{hanging-punctuation:first}", "css-hanging-punctuation", id="hanging-punct"),
    pytest.param(".c{line-clamp:3}", "css-line-clamp", id="line-clamp"),
    pytest.param(".c{-webkit-line-clamp:3}", "css-line-clamp", id="webkit-line-clamp"),
    pytest.param(".c{text-rendering:optimizeLegibility}", "kerning-pairs-ligatures", id="kerning-pairs"),
    pytest.param(".c{text-box-trim:both}", "css-text-box-trim", id="text-box-trim"),
    pytest.param(".c{leading-trim:both}", "css-text-box-trim", id="leading-trim"),
]


# --- Box Model Features ---

CSS_BOX_MODEL_FEATURES = [
    pytest.param("*{box-sizing:border-box}", "css3-boxsizing", id="box-sizing"),
    pytest.param(".c{min-width:200px}", "minmaxwh", id="min-width"),
    pytest.param(".c{max-width:1200px}", "minmaxwh", id="max-width"),
    pytest.param(".c{min-height:100vh}", "minmaxwh", id="min-height"),
    pytest.param(".c{max-height:500px}", "minmaxwh", id="max-height"),
    pytest.param(".c{width:min-content}", "intrinsic-width", id="min-content"),
    pytest.param(".c{width:max-content}", "intrinsic-width", id="max-content"),
    pytest.param(".c{width:fit-content}", "intrinsic-width", id="fit-content"),
    pytest.param("img{object-fit:cover}", "object-fit", id="object-fit"),
    pytest.param("img{object-position:center top}", "object-fit", id="object-position"),
    pytest.param(".c{border-image:url(b.png) 30 round}", "border-image", id="border-image"),
    pytest.param(".c{border-radius:10px}", "border-radius", id="border-radius"),
    pytest.param(".c{outline:2px solid blue}", "outline", id="outline"),
    pytest.param(".c{outline-width:3px}", "outline", id="outline-width"),
    pytest.param(".c{box-decoration-break:clone}", "css-boxdecorationbreak", id="box-decoration-break"),
    pytest.param(".c{box-shadow:0 2px 4px rgba(0,0,0,0.1)}", "css-boxshadow", id="box-shadow"),
    pytest.param(".c{text-shadow:2px 2px 4px black}", "css-textshadow", id="text-shadow"),
]


# --- Units & Variables ---

CSS_UNITS_FEATURES = [
    # rem
    pytest.param("body{font-size:1rem}", "rem", id="rem"),
    # viewport units
    pytest.param(".c{width:100vw}", "viewport-units", id="vw"),
    pytest.param(".c{height:100vh}", "viewport-units", id="vh"),
    pytest.param(".c{font-size:5vmin}", "viewport-units", id="vmin"),
    pytest.param(".c{width:50vmax}", "viewport-units", id="vmax"),
    # viewport variants
    pytest.param(".c{width:100svw}", "viewport-unit-variants", id="svw"),
    pytest.param(".c{height:100svh}", "viewport-unit-variants", id="svh"),
    pytest.param(".c{width:100lvw}", "viewport-unit-variants", id="lvw"),
    pytest.param(".c{height:100dvh}", "viewport-unit-variants", id="dvh"),
    # calc
    pytest.param(".c{width:calc(100% - 20px)}", "calc", id="calc"),
    # ch
    pytest.param(".c{width:20ch}", "ch-unit", id="ch"),
    # container query units
    pytest.param(".c{width:50cqw}", "css-container-query-units", id="cqw"),
    pytest.param(".c{height:50cqh}", "css-container-query-units", id="cqh"),
    pytest.param(".c{width:50cqi}", "css-container-query-units", id="cqi"),
    # css variables
    pytest.param(":root{--c:#007bff}", "css-variables", id="css-var-def"),
    pytest.param(".c{color:var(--c)}", "css-variables", id="css-var-usage"),
    pytest.param(".c{color:var(--c,blue)}", "css-variables", id="css-var-fallback"),
    # math functions
    pytest.param(".c{width:min(100%,500px)}", "css-math-functions", id="min-fn"),
    pytest.param(".c{width:max(200px,50%)}", "css-math-functions", id="max-fn"),
    pytest.param(".c{font-size:clamp(1rem,2.5vw,2rem)}", "css-math-functions", id="clamp-fn"),
]


# --- Misc Features ---

CSS_MISC_FEATURES = [
    pytest.param(".c{opacity:0.5}", "css-opacity", id="opacity"),
    pytest.param(".c{zoom:1.5}", "css-zoom", id="zoom"),
    pytest.param(".c{all:unset}", "css-all", id="all-unset"),
    pytest.param(".c{color:unset}", "css-unset-value", id="unset-value"),
    pytest.param(".c{font-size:initial}", "css-initial-value", id="initial-value"),
    pytest.param(".c{color:revert}", "css-revert-value", id="revert-value"),
    pytest.param("p{widows:3}", "css-widows-orphans", id="widows"),
    pytest.param("p{orphans:2}", "css-widows-orphans", id="orphans"),
    pytest.param(".c{writing-mode:vertical-rl}", "css-writing-mode", id="writing-mode"),
    pytest.param(".c{print-color-adjust:exact}", "css-color-adjust", id="print-color-adjust"),
    pytest.param(".c{color-adjust:exact}", "css-color-adjust", id="color-adjust"),
    pytest.param(".c{background:element(#el)}", "css-element-function", id="element-fn"),
    pytest.param(".c{background-image:cross-fade(url(a.png),url(b.png),50%)}", "css-cross-fade", id="cross-fade"),
    pytest.param("img{image-rendering:crisp-edges}", "css-crisp-edges", id="crisp-edges"),
    pytest.param("img{image-rendering:pixelated}", "css-crisp-edges", id="pixelated"),
    pytest.param(".c{unicode-bidi:bidi-override}", "css-unicode-bidi", id="unicode-bidi"),
    pytest.param(".c::after{content:attr(data-tooltip)}", "css3-attr", id="attr-fn"),
    pytest.param(".c{justify-content:space-evenly}", "justify-content-space-evenly", id="space-evenly"),
    pytest.param(".c{position:sticky;top:0}", "css-sticky", id="sticky"),
    pytest.param(".c{position:fixed}", "css-fixed", id="fixed"),
    pytest.param(".c{overflow:auto}", "css-overflow", id="overflow"),
    pytest.param(".c{overflow-x:scroll}", "css-overflow", id="overflow-x"),
    pytest.param(".c{overflow-anchor:none}", "css-overflow-anchor", id="overflow-anchor"),
    pytest.param(".c{overflow:overlay}", "css-overflow-overlay", id="overflow-overlay"),
    pytest.param("p::first-letter{initial-letter:3}", "css-initial-letter", id="initial-letter"),
    pytest.param(".c{-webkit-box-reflect:below 10px}", "css-reflections", id="reflections"),
    pytest.param(".c{flow-into:myFlow}", "css-regions", id="flow-into"),
    pytest.param(".c{flow-from:myFlow}", "css-regions", id="flow-from"),
    pytest.param(".c{wrap-flow:both}", "css-exclusions", id="wrap-flow"),
    pytest.param(".c{wrap-through:none}", "css-exclusions", id="wrap-through"),
    pytest.param("div >> p{color:blue}", "css-descendant-gtgt", id="descendant-gtgt"),
    pytest.param(".c{background:-webkit-canvas(myCanvas)}", "css-canvas", id="webkit-canvas"),
    pytest.param(".c{color:if(style(--dark:true),white,black)}", "css-if", id="if-fn"),
    pytest.param("img{-webkit-user-drag:none}", "webkit-user-drag", id="webkit-user-drag"),
    pytest.param(".c{background:url(icon.svg)}", "svg-css", id="svg-css"),
]


# --- Interaction Features ---

CSS_INTERACTION_FEATURES = [
    pytest.param("textarea{resize:both}", "css-resize", id="resize"),
    pytest.param(".c{pointer-events:none}", "pointer-events", id="pointer-events"),
    pytest.param(".c{user-select:none}", "user-select-none", id="user-select"),
    pytest.param(".c{-webkit-user-select:none}", "user-select-none", id="webkit-user-select"),
    pytest.param("button{appearance:none}", "css-appearance", id="appearance"),
    pytest.param("button{-webkit-appearance:none}", "css-appearance", id="webkit-appearance"),
    pytest.param("input{caret-color:red}", "css-caret-color", id="caret-color"),
    pytest.param(".c{touch-action:none}", "css-touch-action", id="touch-action"),
    pytest.param("html{scroll-behavior:smooth}", "css-scroll-behavior", id="scroll-behavior"),
    pytest.param(".c{cursor:pointer}", "css3-cursors", id="cursor-pointer"),
    pytest.param(".c{cursor:grab}", "css3-cursors-grab", id="cursor-grab"),
    pytest.param(".c{cursor:grabbing}", "css3-cursors-grab", id="cursor-grabbing"),
    pytest.param(".c{cursor:zoom-in}", "css3-cursors-newer", id="cursor-zoom-in"),
    pytest.param(".c{cursor:zoom-out}", "css3-cursors-newer", id="cursor-zoom-out"),
    pytest.param(".c{overscroll-behavior:contain}", "css-overscroll-behavior", id="overscroll"),
    pytest.param(".c{scrollbar-width:thin}", "css-scrollbar", id="scrollbar-width"),
    pytest.param(".c{scrollbar-color:gray lightgray}", "css-scrollbar", id="scrollbar-color"),
    pytest.param(".c{scroll-snap-type:x mandatory}", "css-snappoints", id="scroll-snap-type"),
    pytest.param(".c{scroll-snap-align:start}", "css-snappoints", id="scroll-snap-align"),
]


# --- Transform & Animation Features ---

CSS_TRANSFORM_FEATURES = [
    # 2D transforms
    pytest.param(".c{transform:rotate(45deg)}", "transforms2d", id="rotate"),
    pytest.param(".c{transform:translate(50px,100px)}", "transforms2d", id="translate"),
    pytest.param(".c{transform:scale(1.5)}", "transforms2d", id="scale"),
    pytest.param(".c{transform:skew(30deg,20deg)}", "transforms2d", id="skew"),
    pytest.param(".c{transform:matrix(1,0,0,1,50,50)}", "transforms2d", id="matrix"),
    # 3D transforms
    pytest.param(".c{transform:translate3d(50px,100px,20px)}", "transforms3d", id="translate3d"),
    pytest.param(".c{transform:rotateX(45deg)}", "transforms3d", id="rotateX"),
    pytest.param(".c{transform:rotateY(45deg)}", "transforms3d", id="rotateY"),
    pytest.param(".c{transform:rotateZ(45deg)}", "transforms3d", id="rotateZ"),
    pytest.param(".c{perspective:1000px}", "transforms3d", id="perspective"),
    # animations
    pytest.param("@keyframes f{from{opacity:0}to{opacity:1}}", "css-animation", id="keyframes"),
    pytest.param(".c{animation:fadeIn 1s ease}", "css-animation", id="animation-shorthand"),
    pytest.param(".c{animation-name:fadeIn}", "css-animation", id="animation-name"),
    pytest.param(".c{animation-duration:2s}", "css-animation", id="animation-duration"),
    # transitions
    pytest.param(".c{transition:all 0.3s ease}", "css-transitions", id="transition"),
    pytest.param(".c{transition-property:opacity,transform}", "css-transitions", id="transition-prop"),
    pytest.param(".c{transition-duration:0.3s}", "css-transitions", id="transition-duration"),
    # will-change
    pytest.param(".c{will-change:transform}", "will-change", id="will-change"),
]


# --- All parametrize tests ---

@pytest.mark.unit
class TestLayoutDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_LAYOUT_FEATURES)
    def test_layout_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestColorDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_COLOR_FEATURES)
    def test_color_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestBackgroundDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_BACKGROUND_FEATURES)
    def test_background_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestFilterDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_FILTER_FEATURES)
    def test_filter_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestFontDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_FONT_FEATURES)
    def test_font_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestTextDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_TEXT_FEATURES)
    def test_text_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestBoxModelDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_BOX_MODEL_FEATURES)
    def test_box_model_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestUnitsDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_UNITS_FEATURES)
    def test_units_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestMiscDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_MISC_FEATURES)
    def test_misc_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestInteractionDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_INTERACTION_FEATURES)
    def test_interaction_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestTransformAnimationDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_TRANSFORM_FEATURES)
    def test_transform_animation_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


# --- Multi-feature combination tests ---

@pytest.mark.unit
class TestCombinedFeatures:
    """Tests that verify multiple features detected simultaneously."""

    def test_flex_and_gap_both_detected(self, parse_features):
        css = ".c{display:flex;gap:1rem}"
        features = parse_features(css)
        assert "flexbox" in features
        assert "flexbox-gap" in features

    def test_grid_and_subgrid_detected(self, parse_features):
        css = ".c{display:grid;grid-template-columns:subgrid;grid-template-rows:subgrid}"
        features = parse_features(css)
        assert "css-grid" in features
        assert "css-subgrid" in features
