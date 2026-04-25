"""HTML parser black box tests.

Tests public API: HTML string input -> detected feature IDs.
No mocking, no internal state inspection.
"""

import pytest


# --- Element Detection ---

HTML_ELEMENT_FEATURES = [
    pytest.param("<main>Content</main>", "html5semantic", id="semantic"),
    pytest.param("<dialog>Content</dialog>", "dialog", id="dialog"),
]

HTML_ATTRIBUTE_FEATURES = [
    pytest.param('<img src="i.jpg" loading="lazy" alt="t">', "loading-lazy-attr", id="loading-lazy"),
]

HTML_INPUT_TYPE_FEATURES = [
    pytest.param('<input type="date">', "input-datetime", id="input-date"),
]

HTML_ATTR_VALUE_FEATURES = [
    pytest.param('<script type="module" src="app.js"></script>', "es6-module", id="es6-module"),
]

HTML_SPECIAL_FEATURES = [
    pytest.param("<my-component>Content</my-component>", "custom-elementsv1", id="custom-element"),
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


@pytest.mark.blackbox
class TestMalformedHTML:
    @pytest.mark.parametrize("html,expected_features", [
        ("<main><section><article>Content", {"html5semantic"}),
    ], ids=["unclosed-nested"])
    def test_malformed_still_detects(self, parse_features, html, expected_features):
        for f in expected_features:
            assert f in parse_features(html)
