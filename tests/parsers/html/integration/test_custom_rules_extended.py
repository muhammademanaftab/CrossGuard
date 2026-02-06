"""Extended HTML custom rules tests.

Additional edge cases beyond the existing test_custom_rules.py.
"""

import pytest
from unittest.mock import patch
from src.parsers.html_parser import HTMLParser


@pytest.fixture
def custom_html_rules():
    """Custom HTML rules for testing."""
    return {
        'elements': {
            'x-widget': 'custom-elementsv1',
            'data-grid': 'custom-elementsv1',
        },
        'attributes': {
            'x-bind': 'custom-attr-feature',
        },
        'input_types': {
            'custom-date': 'custom-input-feature',
        },
        'attribute_values': {
            'data-mode:advanced': 'custom-value-feature',
            'data-special:val<1>': 'custom-special-feature',
        }
    }


@pytest.fixture
def html_parser_with_custom(custom_html_rules):
    """HTMLParser with injected custom rules."""
    with patch('src.parsers.html_parser.get_custom_html_rules', return_value=custom_html_rules):
        parser = HTMLParser()
        yield parser


class TestCustomElementEdgeCases:

    def test_custom_element_in_nested_html(self, html_parser_with_custom):
        """Custom element deep in DOM tree."""
        html = """
        <html><body>
            <div><section><article>
                <x-widget>content</x-widget>
            </article></section></div>
        </body></html>
        """
        features = html_parser_with_custom.parse_string(html)
        assert 'custom-elementsv1' in features

    def test_custom_element_self_closing(self, html_parser_with_custom):
        """Self-closing custom element detected."""
        html = "<div><x-widget /></div>"
        features = html_parser_with_custom.parse_string(html)
        assert 'custom-elementsv1' in features

    def test_custom_element_with_attributes(self, html_parser_with_custom):
        """Custom element with attributes detected."""
        html = '<x-widget data-x="y" class="main">content</x-widget>'
        features = html_parser_with_custom.parse_string(html)
        assert 'custom-elementsv1' in features


class TestCustomAttributeEdgeCases:

    def test_custom_attribute_on_standard_element(self, html_parser_with_custom):
        """Custom attr on standard element."""
        html = '<div x-bind="value">text</div>'
        features = html_parser_with_custom.parse_string(html)
        assert 'custom-attr-feature' in features

    def test_custom_attribute_value_case_sensitivity(self, html_parser_with_custom):
        """Attribute values are lowercased for matching."""
        # The parser lowercases attribute values before checking
        html = '<div data-mode="Advanced">text</div>'
        features = html_parser_with_custom.parse_string(html)
        assert 'custom-value-feature' in features


class TestCustomInputTypeEdgeCases:

    def test_custom_input_type_in_form(self, html_parser_with_custom):
        """Custom input type within form."""
        html = """
        <form>
            <input type="custom-date" name="date">
            <button>Submit</button>
        </form>
        """
        features = html_parser_with_custom.parse_string(html)
        assert 'custom-input-feature' in features


class TestMixedRules:

    def test_multiple_custom_rules_single_file(self, html_parser_with_custom):
        """All rule types detected in one HTML file."""
        html = """
        <html><body>
            <x-widget x-bind="val">text</x-widget>
            <form><input type="custom-date"></form>
            <div data-mode="advanced">content</div>
        </body></html>
        """
        features = html_parser_with_custom.parse_string(html)
        assert 'custom-elementsv1' in features
        assert 'custom-attr-feature' in features
        assert 'custom-input-feature' in features
        assert 'custom-value-feature' in features

    def test_custom_rules_dont_override_builtin(self, html_parser_with_custom):
        """Built-in mappings preserved."""
        # 'video' is a built-in element
        assert html_parser_with_custom._elements.get('video') == 'video'
        # Built-in input type 'date' still maps correctly
        assert html_parser_with_custom._input_types.get('date') == 'input-datetime'

    def test_custom_and_builtin_mix(self, html_parser_with_custom):
        """Both custom and built-in features in same analysis."""
        html = """
        <html><body>
            <video src="v.mp4"></video>
            <x-widget>text</x-widget>
            <input type="email">
            <input type="custom-date">
        </body></html>
        """
        features = html_parser_with_custom.parse_string(html)
        assert 'video' in features
        assert 'custom-elementsv1' in features
        assert 'input-email-tel-url' in features
        assert 'custom-input-feature' in features


class TestAttributeValueParsing:

    def test_attribute_value_colon_parsing(self, html_parser_with_custom):
        """'attr:value' to tuple conversion in parser."""
        # The parser should have converted 'data-mode:advanced' to ('data-mode', 'advanced')
        assert ('data-mode', 'advanced') in html_parser_with_custom._attribute_values

    def test_custom_attribute_value_with_special_chars(self, html_parser_with_custom):
        """Special chars in values are handled."""
        # 'data-special:val<1>' should be converted to ('data-special', 'val<1>')
        assert ('data-special', 'val<1>') in html_parser_with_custom._attribute_values


class TestEmptyAndNoCustomRules:

    def test_empty_html_custom_rules(self):
        """Parser works with no HTML custom rules."""
        empty_rules = {
            'elements': {},
            'attributes': {},
            'input_types': {},
            'attribute_values': {}
        }
        with patch('src.parsers.html_parser.get_custom_html_rules', return_value=empty_rules):
            parser = HTMLParser()
            html = "<video src='v.mp4'></video>"
            features = parser.parse_string(html)
            assert 'video' in features

    def test_html_builtin_still_detected(self, html_parser_with_custom):
        """Standard features still found with custom rules active."""
        html = """
        <video src="v.mp4"></video>
        <audio src="a.mp3"></audio>
        <canvas></canvas>
        """
        features = html_parser_with_custom.parse_string(html)
        assert 'video' in features
        assert 'audio' in features
        assert 'canvas' in features


class TestReportOutput:

    def test_custom_rules_in_report_output(self, html_parser_with_custom):
        """Custom rules show up in detailed report."""
        html = '<x-widget>content</x-widget>'
        html_parser_with_custom.parse_string(html)
        report = html_parser_with_custom.get_detailed_report()
        assert 'custom-elementsv1' in report['features']

    def test_custom_element_not_detected_in_text(self, html_parser_with_custom):
        """Text content 'x-widget' doesn't trigger element detection."""
        html = "<p>The x-widget component is great</p>"
        features = html_parser_with_custom.parse_string(html)
        # BeautifulSoup parses by tags, not text content
        # 'x-widget' in text should NOT trigger element detection
        # However, custom-elementsv1 may be triggered by hyphenated tag detection
        # Let's check that 'custom-elementsv1' is NOT triggered by text
        # The text doesn't contain an <x-widget> tag
        assert 'custom-elementsv1' not in features
