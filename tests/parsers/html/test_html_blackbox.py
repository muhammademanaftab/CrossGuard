"""HTML parser black box tests.

Tests public API: HTML string input -> detected feature IDs.
No mocking, no internal state inspection.
"""

import pytest


# --- Element Detection ---

HTML_ELEMENT_FEATURES = [
    pytest.param("<main>Content</main>", "html5semantic", id="semantic"),
    pytest.param("<dialog>Content</dialog>", "dialog", id="dialog"),
    pytest.param("<details><summary>S</summary></details>", "details", id="details"),
    pytest.param("<template>Content</template>", "template", id="template"),
    pytest.param('<datalist id="b"><option value="Chrome"></datalist>', "datalist", id="datalist"),
    pytest.param('<meter value="0.6">60%</meter>', "meter", id="meter"),
    pytest.param('<progress value="70" max="100">70%</progress>', "progress", id="progress"),
    pytest.param('<video src="v.mp4"></video>', "video", id="video"),
    pytest.param('<audio src="a.mp3"></audio>', "audio", id="audio"),
    pytest.param('<picture><img src="f.jpg" alt="t"></picture>', "picture", id="picture"),
    pytest.param('<video><track src="c.vtt" kind="captions"></video>', "webvtt", id="webvtt"),
    pytest.param("<canvas></canvas>", "canvas", id="canvas"),
    pytest.param("<svg></svg>", "svg", id="svg"),
    pytest.param('<template><slot name="c"></slot></template>', "shadowdomv1", id="shadowdom"),
    pytest.param("<p>long<wbr>word</p>", "wbr-element", id="wbr"),
    pytest.param("<ruby>漢<rt>kan</rt></ruby>", "ruby", id="ruby"),
    pytest.param("<math><mi>x</mi></math>", "mathml", id="mathml"),
]

HTML_ATTRIBUTE_FEATURES = [
    pytest.param('<div role="button">Click</div>', "wai-aria", id="aria-role"),
    pytest.param('<input type="text" required>', "form-validation", id="required"),
    pytest.param('<input pattern="[A-Z]">', "input-pattern", id="pattern"),
    pytest.param('<input minlength="3">', "input-minlength", id="minlength"),
    pytest.param('<input maxlength="100">', "maxlength", id="maxlength"),
    pytest.param('<button type="submit" formaction="/alt">Alt</button>', "form-submit-attributes", id="formaction"),
    pytest.param('<form id="f"></form><input form="f">', "form-attribute", id="form-attr"),
    pytest.param("<ol reversed><li>A</li></ol>", "ol-reversed", id="ol-reversed"),
    pytest.param('<div contenteditable="true">Edit</div>', "contenteditable", id="contenteditable"),
    pytest.param('<div draggable="true">Drag</div>', "dragndrop", id="draggable"),
    pytest.param("<div hidden>Hidden</div>", "hidden", id="hidden"),
    pytest.param('<a href="f.pdf" download>Download</a>', "download", id="download"),
    pytest.param('<div ontouchstart="h()">Touch</div>', "touch", id="touch"),
    pytest.param('<div onpointerdown="h()">Ptr</div>', "pointer", id="pointer"),
    pytest.param('<img src="i.jpg" loading="lazy" alt="t">', "loading-lazy-attr", id="loading-lazy"),
    pytest.param('<script src="a.js" async></script>', "script-async", id="script-async"),
    pytest.param('<input placeholder="Name">', "input-placeholder", id="placeholder"),
    pytest.param("<input autofocus>", "autofocus", id="autofocus"),
    pytest.param('<iframe sandbox src="p.html"></iframe>', "iframe-sandbox", id="iframe-sandbox"),
    pytest.param('<div tabindex="0">Focusable</div>', "tabindex-attr", id="tabindex"),
]

HTML_INPUT_TYPE_FEATURES = [
    pytest.param('<input type="date">', "input-datetime", id="input-date"),
    pytest.param('<input type="email">', "input-email-tel-url", id="input-email"),
    pytest.param('<input type="search">', "input-search", id="input-search"),
    pytest.param('<input type="color">', "input-color", id="input-color"),
    pytest.param('<input type="range">', "input-range", id="input-range"),
    pytest.param('<input type="number">', "input-number", id="input-number"),
]

HTML_ATTR_VALUE_FEATURES = [
    pytest.param('<link rel="preload" href="s.css" as="style">', "link-rel-preload", id="rel-preload"),
    pytest.param('<a href="https://x.com" rel="noopener">L</a>', "rel-noopener", id="rel-noopener"),
    pytest.param('<link rel="modulepreload" href="app.js">', "link-rel-modulepreload", id="modulepreload"),
    pytest.param('<script type="module" src="app.js"></script>', "es6-module", id="es6-module"),
    pytest.param('<link rel="icon" type="image/svg+xml" href="f.svg">', "link-icon-svg", id="svg-icon"),
    pytest.param('<source type="video/webm" src="v.webm">', "webm", id="webm"),
    pytest.param('<source type="image/webp" srcset="i.webp">', "webp", id="webp"),
    pytest.param('<source type="image/avif" srcset="i.avif">', "avif", id="avif"),
    pytest.param('<source type="audio/opus" src="a.opus">', "opus", id="opus"),
    pytest.param('<img src="i.jpg" crossorigin="anonymous" alt="t">', "cors", id="cors"),
    pytest.param('<a href="x.com" referrerpolicy="no-referrer">L</a>', "referrer-policy", id="referrer-policy"),
    pytest.param("<meta http-equiv=\"content-security-policy\" content=\"default-src 'self'\">", "contentsecuritypolicy2", id="csp2"),
]

HTML_SPECIAL_FEATURES = [
    pytest.param('<img src="s.jpg" srcset="m.jpg 2x" alt="t">', "srcset", id="srcset"),
    pytest.param('<img src="icon.svg" alt="Icon">', "svg-img", id="svg-img"),
    pytest.param('<svg><use href="#icon-home"></use></svg>', "svg-fragment", id="svg-fragment"),
    pytest.param('<video src="v.mp4#t=10,20"></video>', "media-fragments", id="media-fragments"),
    pytest.param("<my-component>Content</my-component>", "custom-elementsv1", id="custom-element"),
    pytest.param('<div data-id="123">Content</div>', "dataset", id="dataset"),
    pytest.param('<img src="data:image/png;base64,iVBOR..." alt="t">', "datauri", id="datauri"),
    pytest.param('<meta name="theme-color" content="#4285f4">', "meta-theme-color", id="theme-color"),
    pytest.param('<meta name="viewport" content="width=device-width">', "viewport-units", id="viewport"),
    pytest.param("<fieldset disabled><input></fieldset>", "fieldset-disabled", id="fieldset-disabled"),
]


@pytest.mark.blackbox
class TestElementDetection:
    @pytest.mark.parametrize("html,expected_id", HTML_ELEMENT_FEATURES)
    def test_element_detected(self, parse_features, html, expected_id):
        assert expected_id in parse_features(html)


@pytest.mark.blackbox
class TestAttributeDetection:
    @pytest.mark.parametrize("html,expected_id", HTML_ATTRIBUTE_FEATURES)
    def test_attribute_detected(self, parse_features, html, expected_id):
        assert expected_id in parse_features(html)


@pytest.mark.blackbox
class TestInputTypeDetection:
    @pytest.mark.parametrize("html,expected_id", HTML_INPUT_TYPE_FEATURES)
    def test_input_type_detected(self, parse_features, html, expected_id):
        assert expected_id in parse_features(html)


@pytest.mark.blackbox
class TestAttributeValueDetection:
    @pytest.mark.parametrize("html,expected_id", HTML_ATTR_VALUE_FEATURES)
    def test_attr_value_detected(self, parse_features, html, expected_id):
        assert expected_id in parse_features(html)


@pytest.mark.blackbox
class TestSpecialPatternDetection:
    @pytest.mark.parametrize("html,expected_id", HTML_SPECIAL_FEATURES)
    def test_special_pattern_detected(self, parse_features, html, expected_id):
        assert expected_id in parse_features(html)


# --- Combined Feature Tests ---

@pytest.mark.blackbox
class TestCombinedFeatures:
    def test_all_media_elements(self, parse_features):
        html = '<video src="v.mp4"></video><audio src="a.mp3"></audio><picture><img src="i.jpg" alt="t"></picture>'
        features = parse_features(html)
        assert "video" in features
        assert "audio" in features
        assert "picture" in features

    def test_source_in_video_no_picture(self, parse_features):
        html = '<video><source src="v.mp4" type="video/mp4"></video>'
        features = parse_features(html)
        assert "video" in features
        assert "picture" not in features

    def test_source_in_audio_no_picture(self, parse_features):
        html = '<audio><source src="a.mp3" type="audio/mpeg"></audio>'
        features = parse_features(html)
        assert "audio" in features
        assert "picture" not in features

    def test_meter_vs_progress_no_cross(self, parse_features):
        assert "progress" not in parse_features('<meter value="0.5">50%</meter>')
        assert "meter" not in parse_features('<progress value="50" max="100">50%</progress>')

    def test_all_input_types_in_form(self, parse_features):
        html = '<form><input type="date"><input type="email"><input type="search"><input type="color"><input type="range"><input type="number"></form>'
        features = parse_features(html)
        for f in ("input-datetime", "input-email-tel-url", "input-search", "input-color", "input-range", "input-number"):
            assert f in features


# --- Edge Cases ---

@pytest.mark.blackbox
class TestEmptyInput:
    @pytest.mark.parametrize("html", ["", "     ", "\n\n\n"], ids=["empty", "spaces", "newlines"])
    def test_empty_returns_empty_set(self, parse_features, html):
        assert parse_features(html) == set()

    @pytest.mark.parametrize("html", [
        "<!DOCTYPE html>", "<html></html>", "<div></div>", "Just some text",
    ], ids=["doctype", "html-only", "empty-div", "text-only"])
    def test_minimal_html_no_features(self, parse_features, html):
        assert parse_features(html) == set()


@pytest.mark.blackbox
class TestEmptyElements:
    @pytest.mark.parametrize("html,feature_id", [
        ("<video></video>", "video"),
        ("<audio></audio>", "audio"),
        ("<canvas></canvas>", "canvas"),
        ("<dialog></dialog>", "dialog"),
    ])
    def test_empty_element_detected(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)


@pytest.mark.blackbox
class TestMalformedHTML:
    @pytest.mark.parametrize("html,expected_features", [
        ("<main><section><article>Content", {"html5semantic"}),
        ('<video src="v.mp4">', {"video"}),
        ("<main><div>Content</main></div>", {"html5semantic"}),
    ], ids=["unclosed-nested", "unclosed-video", "mismatched-close"])
    def test_malformed_still_detects(self, parse_features, html, expected_features):
        for f in expected_features:
            assert f in parse_features(html)

    @pytest.mark.parametrize("html", [
        "<div>Content", '<input type=text placeholder=test>', "<unknownelement>C</unknownelement>",
    ], ids=["unclosed-div", "missing-quotes", "unknown-element"])
    def test_graceful_handling(self, parse_features, html):
        assert isinstance(parse_features(html), set)

    def test_mixed_quote_styles(self, parse_features):
        assert "input-placeholder" in parse_features("""<input type="text" placeholder='Enter name'>""")


@pytest.mark.blackbox
class TestFalsePositives:
    def test_element_in_comment_not_detected(self, parse_features):
        assert "video" not in parse_features('<!-- <video src="v.mp4"></video> --><div>Content</div>')

    def test_style_selectors_not_detected(self, parse_features):
        html = "<style>video { width: 100%; } [contenteditable] { border: 1px solid; }</style><div>Content</div>"
        features = parse_features(html)
        assert "video" not in features
        assert "contenteditable" not in features

    def test_element_name_in_text(self, parse_features):
        assert "video" not in parse_features("<p>The video element is used for embedding videos.</p>")

    def test_video_in_class_name(self, parse_features):
        assert "video" not in parse_features('<div class="video-container">Content</div>')

    def test_real_element_with_feature_class(self, parse_features):
        assert "video" in parse_features('<video class="video-player" src="v.mp4"></video>')


@pytest.mark.blackbox
class TestCaseSensitivity:
    @pytest.mark.parametrize("input_type", ["Date", "DATE", "DaTe"])
    def test_datetime_case_insensitive(self, parse_features, input_type):
        assert "input-datetime" in parse_features(f'<input type="{input_type}">')


# --- Validate HTML ---

@pytest.mark.blackbox
class TestValidateHtml:
    def test_valid_html(self, html_parser):
        assert html_parser.validate_html("<html><head></head><body><p>Hello</p></body></html>") is True

    def test_fragment(self, html_parser):
        assert html_parser.validate_html("<div><p>Paragraph</p></div>") is True

    def test_self_closing(self, html_parser):
        assert html_parser.validate_html("<br><hr><img src='t.jpg' alt='t'>") is True

    @pytest.mark.parametrize("html", [
        "<div>Unclosed", "<div><span></div></span>",
    ])
    def test_malformed_still_parseable(self, html_parser, html):
        assert isinstance(html_parser.validate_html(html), bool)


# --- Convenience Functions ---

@pytest.mark.blackbox
class TestConvenienceFunctions:
    def test_parse_html_string(self):
        from src.parsers.html_parser import parse_html_string
        assert "html5semantic" in parse_html_string("<main>Content</main>")

    def test_parse_html_string_empty(self):
        from src.parsers.html_parser import parse_html_string
        assert parse_html_string("") == set()
