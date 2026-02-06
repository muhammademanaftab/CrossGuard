"""Tests for get_custom_html_rules() output."""

import json
import pytest
from src.parsers.custom_rules_loader import CustomRulesLoader


class TestHTMLRulesLoading:

    def test_returns_dict_with_all_subsections(self, tmp_rules_file):
        """Output has elements, attributes, input_types, attribute_values."""
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert isinstance(html, dict)
        assert 'elements' in html
        assert 'attributes' in html
        assert 'input_types' in html
        assert 'attribute_values' in html

    def test_custom_element_rule_extracted(self, tmp_rules_file):
        """Known element from JSON is present."""
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert "test-element" in html['elements']
        assert html['elements']['test-element'] == "test-feature-id"

    def test_custom_attribute_rule_extracted(self, tmp_rules_file):
        """Attribute rules loaded correctly."""
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert "test-attr" in html['attributes']
        assert html['attributes']['test-attr'] == "test-attr-feature"

    def test_custom_input_type_rule_extracted(self, tmp_rules_file):
        """Input type rules loaded."""
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert "test-type" in html['input_types']
        assert html['input_types']['test-type'] == "test-input-feature"

    def test_custom_attribute_value_rule_extracted(self, tmp_rules_file):
        """Attribute value rules present (as string keys from loader)."""
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert "data-test:value1" in html['attribute_values']
        assert html['attribute_values']['data-test:value1'] == "test-value-feature"

    def test_attribute_values_converted_to_tuples_by_parser(self, tmp_rules_file):
        """HTMLParser converts 'attr:value' string keys to (attr, value) tuples."""
        from src.parsers.html_parser import HTMLParser
        with pytest.MonkeyPatch.context() as m:
            # Patch get_custom_html_rules to return our test data
            m.setattr(
                'src.parsers.html_parser.get_custom_html_rules',
                lambda: {
                    'elements': {},
                    'attributes': {},
                    'input_types': {},
                    'attribute_values': {'data-test:value1': 'test-value-feature'}
                }
            )
            parser = HTMLParser()
            assert ('data-test', 'value1') in parser._attribute_values

    def test_empty_html_section(self, mock_custom_rules_path):
        """Returns empty sub-dicts when html section is empty."""
        data = {"css": {}, "javascript": {}, "html": {}}
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert html['elements'] == {}
        assert html['attributes'] == {}
        assert html['input_types'] == {}
        assert html['attribute_values'] == {}

    def test_partial_html_section(self, mock_custom_rules_path):
        """Only some sub-sections present still works."""
        data = {
            "css": {},
            "javascript": {},
            "html": {
                "elements": {"my-elem": "elem-feature"}
            }
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding='utf-8')
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert "my-elem" in html['elements']
        assert html['attributes'] == {}
        assert html['input_types'] == {}
        assert html['attribute_values'] == {}
