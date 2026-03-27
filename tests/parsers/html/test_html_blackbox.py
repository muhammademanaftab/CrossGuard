"""HTML parser black box tests.

Tests public API: HTML string input -> detected feature IDs.
No mocking, no internal state inspection.
"""

import pytest


# --- Element Detection ---

HTML_ELEMENT_FEATURES = [
    pytest.param("<main>Content</main>", "html5semantic", id="semantic"),
    pytest.param("<dialog>Content</dialog>", "dialog", id="dialog"),
    pytest.param('<video src="v.mp4"></video>', "video", id="video"),
    pytest.param("<canvas></canvas>", "canvas", id="canvas"),
    pytest.param("<svg></svg>", "svg", id="svg"),
]

HTML_ATTRIBUTE_FEATURES = [
    pytest.param('<div role="button">Click</div>', "wai-aria", id="aria-role"),
    pytest.param('<input type="text" required>', "form-validation", id="required"),
    pytest.param('<div contenteditable="true">Edit</div>', "contenteditable", id="contenteditable"),
    pytest.param('<img src="i.jpg" loading="lazy" alt="t">', "loading-lazy-attr", id="loading-lazy"),
    pytest.param('<input placeholder="Name">', "input-placeholder", id="placeholder"),
]

HTML_INPUT_TYPE_FEATURES = [
    pytest.param('<input type="date">', "input-datetime", id="input-date"),
    pytest.param('<input type="email">', "input-email-tel-url", id="input-email"),
]

HTML_ATTR_VALUE_FEATURES = [
    pytest.param('<script type="module" src="app.js"></script>', "es6-module", id="es6-module"),
    pytest.param('<source type="image/webp" srcset="i.webp">', "webp", id="webp"),
    pytest.param('<img src="i.jpg" crossorigin="anonymous" alt="t">', "cors", id="cors"),
]

HTML_SPECIAL_FEATURES = [
    pytest.param('<img src="s.jpg" srcset="m.jpg 2x" alt="t">', "srcset", id="srcset"),
    pytest.param("<my-component>Content</my-component>", "custom-elementsv1", id="custom-element"),
    pytest.param('<meta name="viewport" content="width=device-width">', "viewport-units", id="viewport"),
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


# --- Edge Cases ---

@pytest.mark.blackbox
class TestEmptyInput:
    @pytest.mark.parametrize("html", ["", "     "], ids=["empty", "whitespace"])
    def test_empty_returns_empty_set(self, parse_features, html):
        assert parse_features(html) == set()


@pytest.mark.blackbox
class TestMalformedHTML:
    @pytest.mark.parametrize("html,expected_features", [
        ("<main><section><article>Content", {"html5semantic"}),
    ], ids=["unclosed-nested"])
    def test_malformed_still_detects(self, parse_features, html, expected_features):
        for f in expected_features:
            assert f in parse_features(html)

    @pytest.mark.parametrize("html", [
        "<div>Content",
    ], ids=["unclosed-div"])
    def test_graceful_handling(self, parse_features, html):
        assert isinstance(parse_features(html), set)


@pytest.mark.blackbox
class TestFalsePositives:
    def test_element_in_comment_not_detected(self, parse_features):
        assert "video" not in parse_features('<!-- <video src="v.mp4"></video> --><div>Content</div>')

    def test_element_name_in_text(self, parse_features):
        assert "video" not in parse_features("<p>The video element is used for embedding videos.</p>")
