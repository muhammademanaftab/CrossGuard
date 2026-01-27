"""Integration tests for custom rules functionality.

Tests: Custom rules loading, custom element detection, custom attribute detection
"""

import pytest
import json
from pathlib import Path


class TestCustomRulesIntegration:
    """Tests for custom rules integration with HTMLParser."""

    def test_parser_loads_custom_rules(self, html_parser):
        """Test that parser loads custom rules on initialization."""
        # Parser should have merged dictionaries
        assert hasattr(html_parser, '_elements')
        assert hasattr(html_parser, '_input_types')
        assert hasattr(html_parser, '_attributes')
        assert hasattr(html_parser, '_attribute_values')

    def test_builtin_rules_work(self, html_parser):
        """Test that built-in rules still work."""
        features = html_parser.parse_string("<video src='v.mp4'></video>")
        assert 'video' in features

    def test_builtin_attributes_work(self, html_parser):
        """Test that built-in attribute rules work."""
        features = html_parser.parse_string('<input placeholder="test">')
        assert 'input-placeholder' in features


class TestCustomElementRules:
    """Tests for custom element rule integration."""

    def test_custom_element_rule_format(self, html_parser):
        """Test that custom elements dict has correct format."""
        # _elements should be a dict mapping element names to feature IDs
        assert isinstance(html_parser._elements, dict)

        # Check some known elements exist
        assert 'video' in html_parser._elements
        assert 'audio' in html_parser._elements
        assert 'main' in html_parser._elements

    def test_element_detection_with_merged_rules(self, html_parser):
        """Test element detection with merged rules."""
        # Test multiple built-in elements
        html = """
        <main>
            <video></video>
            <audio></audio>
            <canvas></canvas>
            <dialog></dialog>
        </main>
        """
        features = html_parser.parse_string(html)

        assert 'html5semantic' in features
        assert 'video' in features
        assert 'audio' in features
        assert 'canvas' in features
        assert 'dialog' in features


class TestCustomInputTypeRules:
    """Tests for custom input type rule integration."""

    def test_custom_input_types_format(self, html_parser):
        """Test that input types dict has correct format."""
        assert isinstance(html_parser._input_types, dict)

        # Check some known input types
        assert 'date' in html_parser._input_types
        assert 'email' in html_parser._input_types
        assert 'color' in html_parser._input_types

    def test_input_type_detection_with_merged_rules(self, html_parser):
        """Test input type detection with merged rules."""
        html = """
        <input type="date">
        <input type="email">
        <input type="color">
        <input type="range">
        """
        features = html_parser.parse_string(html)

        assert 'input-datetime' in features
        assert 'input-email-tel-url' in features
        assert 'input-color' in features
        assert 'input-range' in features


class TestCustomAttributeRules:
    """Tests for custom attribute rule integration."""

    def test_custom_attributes_format(self, html_parser):
        """Test that attributes dict has correct format."""
        assert isinstance(html_parser._attributes, dict)

        # Check some known attributes
        assert 'placeholder' in html_parser._attributes
        assert 'required' in html_parser._attributes
        assert 'contenteditable' in html_parser._attributes

    def test_attribute_detection_with_merged_rules(self, html_parser):
        """Test attribute detection with merged rules."""
        html = """
        <input placeholder="test" required autofocus>
        <div contenteditable="true" draggable="true"></div>
        """
        features = html_parser.parse_string(html)

        assert 'input-placeholder' in features
        assert 'form-validation' in features
        assert 'autofocus' in features
        assert 'contenteditable' in features
        assert 'dragndrop' in features


class TestCustomAttributeValueRules:
    """Tests for custom attribute value rule integration."""

    def test_custom_attribute_values_format(self, html_parser):
        """Test that attribute values dict has correct format."""
        assert isinstance(html_parser._attribute_values, dict)

        # Check some known attribute values (tuple format)
        assert ('rel', 'preload') in html_parser._attribute_values
        assert ('type', 'module') in html_parser._attribute_values

    def test_attribute_value_detection_with_merged_rules(self, html_parser):
        """Test attribute value detection with merged rules."""
        html = """
        <link rel="preload" href="style.css" as="style">
        <script type="module" src="app.js"></script>
        <source type="video/webm" src="video.webm">
        """
        features = html_parser.parse_string(html)

        assert 'link-rel-preload' in features
        assert 'es6-module' in features
        assert 'webm' in features


class TestRuleMerging:
    """Tests for rule merging behavior."""

    def test_builtin_rules_not_overwritten(self, html_parser):
        """Test that built-in rules are not accidentally overwritten."""
        # Built-in video element should still map to 'video'
        assert html_parser._elements.get('video') == 'video'

        # Built-in date input should still map to 'input-datetime'
        assert html_parser._input_types.get('date') == 'input-datetime'

    def test_multiple_elements_same_feature(self, html_parser):
        """Test multiple elements mapping to same feature."""
        # Multiple semantic elements should map to html5semantic
        html = "<main><article><section><header><footer></footer></header></section></article></main>"
        features = html_parser.parse_string(html)

        # Should only have one 'html5semantic' in the set
        assert 'html5semantic' in features

    def test_aria_attributes_merged(self, html_parser):
        """Test that ARIA attributes are properly merged."""
        # ARIA attributes should be in the merged _attributes dict
        assert 'role' in html_parser._attributes
        assert 'aria-label' in html_parser._attributes
        assert 'aria-hidden' in html_parser._attributes


class TestCustomRulesFile:
    """Tests related to custom rules file loading."""

    def test_custom_rules_loader_exists(self):
        """Test that custom rules loader module exists."""
        from src.parsers.custom_rules_loader import get_custom_html_rules
        assert callable(get_custom_html_rules)

    def test_custom_rules_returns_dict(self):
        """Test that custom rules returns a dictionary."""
        from src.parsers.custom_rules_loader import get_custom_html_rules
        rules = get_custom_html_rules()
        assert isinstance(rules, dict)

    def test_custom_rules_has_expected_keys(self):
        """Test that custom rules has expected keys."""
        from src.parsers.custom_rules_loader import get_custom_html_rules
        rules = get_custom_html_rules()

        # May be empty but should be dict with these potential keys
        for key in rules:
            assert key in ['elements', 'input_types', 'attributes', 'attribute_values']


class TestParserWithCustomRulesState:
    """Tests for parser state with custom rules."""

    def test_fresh_parser_has_rules(self):
        """Test that fresh parser instance has rules."""
        from src.parsers.html_parser import HTMLParser

        parser1 = HTMLParser()
        parser2 = HTMLParser()

        # Both should have same built-in rules
        assert parser1._elements == parser2._elements
        assert parser1._input_types == parser2._input_types

    def test_parser_rules_independent_of_parsing(self, html_parser):
        """Test that rules don't change after parsing."""
        elements_before = html_parser._elements.copy()

        html_parser.parse_string("<video></video><my-custom></my-custom>")

        elements_after = html_parser._elements

        # Rules should not change
        assert elements_before == elements_after


class TestCompleteIntegration:
    """Complete integration tests for custom rules."""

    def test_full_page_with_all_rule_types(self, html_parser):
        """Test full page using all types of rules."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <link rel="preload" href="style.css" as="style">
            <script type="module" src="app.js"></script>
        </head>
        <body>
            <main>
                <video src="video.mp4">
                    <source type="video/webm" src="video.webm">
                </video>

                <form>
                    <input type="date" required placeholder="Select date">
                    <input type="email" autocomplete="email">
                </form>

                <div contenteditable="true" role="textbox" aria-label="Editor">
                    Edit me
                </div>
            </main>
        </body>
        </html>
        """
        features = html_parser.parse_string(html)

        # Element rules
        assert 'html5semantic' in features  # main
        assert 'video' in features

        # Input type rules
        assert 'input-datetime' in features  # date
        assert 'input-email-tel-url' in features  # email

        # Attribute rules
        assert 'form-validation' in features  # required
        assert 'input-placeholder' in features
        assert 'input-autocomplete-onoff' in features
        assert 'contenteditable' in features
        assert 'wai-aria' in features  # role, aria-label

        # Attribute value rules
        assert 'link-rel-preload' in features
        assert 'es6-module' in features  # type="module"
        assert 'webm' in features  # type="video/webm"
