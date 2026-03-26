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

    def test_elements_found_reset(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        count1 = len(html_parser.elements_found)
        html_parser.parse_string("<div>Basic</div>")
        count2 = len(html_parser.elements_found)
        assert count2 == 0 or count2 != count1

    def test_attributes_found_reset(self, html_parser):
        html_parser.parse_string('<input required placeholder="test">')
        count1 = len(html_parser.attributes_found)
        html_parser.parse_string('<input type="text">')
        count2 = len(html_parser.attributes_found)
        assert count2 < count1

    def test_features_found_attr_reset(self, html_parser):
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert "video" in html_parser.features_found
        html_parser.parse_string("<audio src='a.mp3'></audio>")
        assert "audio" in html_parser.features_found
        assert "video" not in html_parser.features_found


# =====================================================================
# Parser Reuse
# =====================================================================

@pytest.mark.whitebox
class TestParserReuse:
    def test_reuse_multiple_times(self, html_parser):
        for i in range(10):
            features = html_parser.parse_string(f"<main>Content {i}</main>")
            assert "html5semantic" in features

    def test_reuse_different_content(self, html_parser):
        features1 = html_parser.parse_string('<video src="v.mp4"></video>')
        assert "video" in features1
        features2 = html_parser.parse_string("<main>Content</main>")
        assert "html5semantic" in features2
        assert "video" not in features2


# =====================================================================
# Parse String State Inspection
# =====================================================================

@pytest.mark.whitebox
class TestParseStringState:
    def test_return_matches_features_found(self, html_parser):
        result = html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        assert result == html_parser.features_found

    def test_no_duplicates(self, html_parser):
        result = html_parser.parse_string("<main></main><main></main><main></main>")
        assert sum(1 for f in result if f == "html5semantic") == 1

    def test_state_updated_elements(self, html_parser):
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert "video" in html_parser.features_found
        assert any(e["element"] == "video" for e in html_parser.elements_found)

    def test_state_updated_attributes(self, html_parser):
        html_parser.parse_string('<input placeholder="test">')
        assert any(a["attribute"] == "placeholder" for a in html_parser.attributes_found)


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

    def test_builtin_input_types_present(self, html_parser):
        for t in ("date", "email", "color"):
            assert t in html_parser._input_types

    def test_builtin_not_overwritten(self, html_parser):
        assert html_parser._elements.get("video") == "video"
        assert html_parser._input_types.get("date") == "input-datetime"

    def test_rules_independent_of_parsing(self, html_parser):
        elements_before = html_parser._elements.copy()
        html_parser.parse_string("<video></video><my-custom></my-custom>")
        assert elements_before == html_parser._elements

    def test_aria_attributes_merged(self, html_parser):
        for attr in ("role", "aria-label", "aria-hidden"):
            assert attr in html_parser._attributes

    def test_attribute_values_format(self, html_parser):
        assert ("rel", "preload") in html_parser._attribute_values
        assert ("type", "module") in html_parser._attribute_values


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

    def test_custom_attribute_detected(self, parser_with_custom):
        assert "custom-attr-feature" in parser_with_custom.parse_string('<div x-bind="value">text</div>')

    def test_custom_input_type_detected(self, parser_with_custom):
        assert "custom-input-feature" in parser_with_custom.parse_string('<input type="custom-date">')

    def test_custom_attribute_value_detected(self, parser_with_custom):
        assert "custom-value-feature" in parser_with_custom.parse_string('<div data-mode="advanced">c</div>')

    def test_all_custom_rules_in_one_file(self, parser_with_custom):
        html = '<x-widget x-bind="v">t</x-widget><input type="custom-date"><div data-mode="advanced">c</div>'
        features = parser_with_custom.parse_string(html)
        assert "custom-elementsv1" in features
        assert "custom-attr-feature" in features
        assert "custom-input-feature" in features
        assert "custom-value-feature" in features

    def test_custom_dont_override_builtin(self, parser_with_custom):
        assert parser_with_custom._elements.get("video") == "video"

    def test_custom_and_builtin_mix(self, parser_with_custom):
        html = '<video src="v.mp4"></video><x-widget>t</x-widget><input type="email"><input type="custom-date">'
        features = parser_with_custom.parse_string(html)
        assert "video" in features
        assert "custom-elementsv1" in features
        assert "input-email-tel-url" in features
        assert "custom-input-feature" in features

    def test_custom_element_not_in_text(self, parser_with_custom):
        assert "custom-elementsv1" not in parser_with_custom.parse_string("<p>The x-widget component</p>")

    def test_custom_rules_in_report(self, parser_with_custom):
        parser_with_custom.parse_string("<x-widget>content</x-widget>")
        report = parser_with_custom.get_detailed_report()
        assert "custom-elementsv1" in report["features"]

    def test_empty_custom_rules(self):
        empty = {"elements": {}, "attributes": {}, "input_types": {}, "attribute_values": {}}
        with patch("src.parsers.html_parser.get_custom_html_rules", return_value=empty):
            from src.parsers.html_parser import HTMLParser
            assert "video" in HTMLParser().parse_string("<video src='v.mp4'></video>")


# =====================================================================
# Custom Rules Loader
# =====================================================================

@pytest.mark.whitebox
class TestCustomRulesLoader:
    def test_loader_returns_dict(self):
        from src.parsers.custom_rules_loader import get_custom_html_rules
        assert isinstance(get_custom_html_rules(), dict)

    def test_has_expected_keys(self):
        from src.parsers.custom_rules_loader import get_custom_html_rules
        rules = get_custom_html_rules()
        for key in rules:
            assert key in ["elements", "input_types", "attributes", "attribute_values"]

    def test_fresh_parsers_share_rules(self):
        from src.parsers.html_parser import HTMLParser
        p1 = HTMLParser()
        p2 = HTMLParser()
        assert p1._elements == p2._elements
