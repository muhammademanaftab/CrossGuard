"""Tests for get_custom_html_rules() output."""

import json
import pytest
from src.parsers.custom_rules_loader import CustomRulesLoader


class TestHTMLRulesLoading:

    def test_returns_dict_with_all_subsections(self, tmp_rules_file):
        """Output has elements, attributes, input_types, attribute_values."""
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert set(html.keys()) >= {'elements', 'attributes', 'input_types', 'attribute_values'}

    @pytest.mark.parametrize("subsection,key,expected_value", [
        ("elements", "test-element", "test-feature-id"),
        ("attributes", "test-attr", "test-attr-feature"),
        ("input_types", "test-type", "test-input-feature"),
        ("attribute_values", "data-test:value1", "test-value-feature"),
    ])
    def test_custom_rule_extracted(self, tmp_rules_file, subsection, key, expected_value):
        """HTML rules for all subsection types are loaded correctly."""
        loader = CustomRulesLoader()
        html = loader.get_custom_html_rules()
        assert key in html[subsection]
        assert html[subsection][key] == expected_value

    def test_attribute_values_converted_to_tuples_by_parser(self, tmp_rules_file):
        """HTMLParser converts 'attr:value' string keys to (attr, value) tuples."""
        from src.parsers.html_parser import HTMLParser
        with pytest.MonkeyPatch.context() as m:
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
        for key in ('elements', 'attributes', 'input_types', 'attribute_values'):
            assert html[key] == {}

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
