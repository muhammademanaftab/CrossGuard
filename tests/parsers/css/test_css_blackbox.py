"""CSS parser black box tests.

Tests the public API: CSS string input -> detected feature IDs.
No mocking, no internal imports, no internal state inspection.
"""

import pytest


# --- Feature Detection: representative samples per category ---

CSS_FEATURES = [
    # Layout
    pytest.param(".c{display:flex}", "flexbox", id="flexbox"),
    pytest.param(".c{display:grid}", "css-grid", id="css-grid"),
    # Variables & Selectors
    pytest.param(":root{--c:#007bff}", "css-variables", id="css-variables"),
    pytest.param("article:has(img){padding:20px}", "css-has", id="css-has"),
    # Modern CSS
    pytest.param("@container(min-width:400px){.c{display:flex}}", "css-container-queries", id="container-queries"),
    pytest.param(".c{&:hover{background:blue}}", "css-nesting", id="css-nesting"),
    # Transforms & Animation
    pytest.param(".c{transform:rotate(45deg)}", "transforms2d", id="transforms2d"),
    pytest.param("@keyframes f{from{opacity:0}to{opacity:1}}", "css-animation", id="animation"),
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


# --- Edge Cases ---

@pytest.mark.blackbox
class TestEmptyInput:
    def test_empty_string(self, parse_features):
        assert parse_features("") == set()


@pytest.mark.blackbox
class TestMalformedCSS:
    def test_missing_closing_brace(self, parse_features):
        assert "css-grid" in parse_features(".element { display: grid; ")

    def test_unclosed_string(self, parse_features):
        assert isinstance(parse_features('.element { content: "unclosed; }'), set)


# --- Validate CSS ---

@pytest.mark.blackbox
class TestValidateCSS:
    def test_valid_basic_css(self, css_parser):
        assert css_parser.validate_css("body { margin: 0; }") is True

    def test_invalid_empty_string(self, css_parser):
        assert css_parser.validate_css("") is False
