"""HTML parser white box tests.

Tests internal state, custom rules integration, and DOM traversal internals.
"""

import pytest
from unittest.mock import patch


# =====================================================================
# State Reset
# =====================================================================

@pytest.mark.whitebox
class TestStateReset:
    def test_features_reset_between_parses(self, html_parser):
        features1 = html_parser.parse_string('<video src="v.mp4"></video>')
        assert "video" in features1
        features2 = html_parser.parse_string("<div>No features</div>")
        assert "video" not in features2


# =====================================================================
# Parse String State Inspection
# =====================================================================

@pytest.mark.whitebox
class TestParseStringState:
    def test_return_matches_features_found(self, html_parser):
        result = html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        assert result == html_parser.features_found


# =====================================================================
# Custom Rules Integration (builtin rules inspection)
# =====================================================================

@pytest.mark.whitebox
class TestCustomRulesIntegration:
    def test_parser_has_rule_dicts(self, html_parser):
        for attr in ("_elements", "_input_types", "_attributes", "_attribute_values"):
            assert hasattr(html_parser, attr)


# =====================================================================
# Custom Rules Extended (mocked injection)
# =====================================================================

@pytest.fixture
def custom_html_rules():
    return {
        "elements": {"x-widget": "custom-elementsv1", "data-grid": "custom-elementsv1"},
        "attributes": {"x-bind": "custom-attr-feature"},
        "input_types": {"custom-date": "custom-input-feature"},
        "attribute_values": {"data-mode:advanced": "custom-value-feature"},
    }


@pytest.fixture
def parser_with_custom(custom_html_rules):
    with patch("src.parsers.html_parser.get_custom_html_rules", return_value=custom_html_rules):
        parser = __import__("src.parsers.html_parser", fromlist=["HTMLParser"]).HTMLParser()
        yield parser


@pytest.mark.whitebox
class TestCustomRulesExtended:
    def test_custom_element_detected(self, parser_with_custom):
        assert "custom-elementsv1" in parser_with_custom.parse_string("<x-widget>content</x-widget>")
