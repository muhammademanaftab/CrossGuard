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

    def test_features_found_attr_reset(self, html_parser):
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert "video" in html_parser.features_found
        html_parser.parse_string("<audio src='a.mp3'></audio>")
        assert "audio" in html_parser.features_found
        assert "video" not in html_parser.features_found


# =====================================================================
# Parse String State Inspection
# =====================================================================

@pytest.mark.whitebox
class TestParseStringState:
    def test_return_matches_features_found(self, html_parser):
        result = html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        assert result == html_parser.features_found

    def test_state_updated_elements(self, html_parser):
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert "video" in html_parser.features_found
        assert any(e["element"] == "video" for e in html_parser.elements_found)


# =====================================================================
# Custom Rules Integration (builtin rules inspection)
# =====================================================================

@pytest.mark.whitebox
class TestCustomRulesIntegration:
    def test_parser_has_rule_dicts(self, html_parser):
        for attr in ("_elements", "_input_types", "_attributes", "_attribute_values"):
            assert hasattr(html_parser, attr)

    def test_builtin_elements_present(self, html_parser):
        for elem in ("video", "audio", "main"):
            assert elem in html_parser._elements


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

    def test_custom_and_builtin_mix(self, parser_with_custom):
        html = '<video src="v.mp4"></video><x-widget>t</x-widget><input type="email"><input type="custom-date">'
        features = parser_with_custom.parse_string(html)
        assert "video" in features
        assert "custom-elementsv1" in features
        assert "input-email-tel-url" in features
        assert "custom-input-feature" in features

    def test_empty_custom_rules(self):
        empty = {"elements": {}, "attributes": {}, "input_types": {}, "attribute_values": {}}
        with patch("src.parsers.html_parser.get_custom_html_rules", return_value=empty):
            from src.parsers.html_parser import HTMLParser
            assert "video" in HTMLParser().parse_string("<video src='v.mp4'></video>")

    def test_custom_rules_in_report(self, parser_with_custom):
        parser_with_custom.parse_string("<x-widget>content</x-widget>")
        report = parser_with_custom.get_detailed_report()
        assert "custom-elementsv1" in report["features"]
