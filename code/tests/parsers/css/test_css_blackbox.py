"""CSS parser black box tests.

Tests the public API: CSS string input -> detected feature IDs.
No mocking, no internal imports, no internal state inspection.
"""

import pytest


# --- Feature Detection: representative samples per category ---

CSS_FEATURES = [
    pytest.param(".c{display:grid}", "css-grid", id="css-grid"),
    pytest.param(".c{display:flex}", "flexbox", id="flexbox"),
    pytest.param("@container(min-width:400px){.c{display:flex}}", "css-container-queries", id="container-queries"),
    pytest.param(":root{--c:#007bff}", "css-variables", id="css-variables"),
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


@pytest.mark.blackbox
class TestMalformedCSS:
    def test_missing_closing_brace(self, parse_features):
        assert "css-grid" in parse_features(".element { display: grid; ")
