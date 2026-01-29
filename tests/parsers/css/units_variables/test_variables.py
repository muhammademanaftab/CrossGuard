"""Tests for CSS Variables (Custom Properties) features.

Tests features: css-variables
"""

import pytest


class TestCSSVariables:
    """Tests for CSS Variables detection."""

    def test_custom_property_definition(self, parse_and_check):
        """Test custom property definition detection."""
        css = ":root { --primary-color: #007bff; }"
        assert parse_and_check(css, 'css-variables')

    def test_var_function(self, parse_and_check):
        """Test var() function detection."""
        css = ".element { color: var(--primary-color); }"
        assert parse_and_check(css, 'css-variables')

    def test_var_with_fallback(self, parse_and_check):
        """Test var() with fallback value detection."""
        css = ".element { color: var(--primary-color, blue); }"
        assert parse_and_check(css, 'css-variables')

    def test_multiple_custom_properties(self, parse_and_check):
        """Test multiple custom properties detection."""
        css = """
        :root {
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
        }
        """
        assert parse_and_check(css, 'css-variables')

    def test_custom_property_with_hyphen(self, parse_and_check):
        """Test custom property with hyphens in name."""
        css = ".element { margin: var(--space-between-items); }"
        assert parse_and_check(css, 'css-variables')

    def test_nested_var(self, parse_and_check):
        """Test nested var() function."""
        css = ".element { color: var(--color, var(--fallback-color, black)); }"
        assert parse_and_check(css, 'css-variables')

    def test_custom_property_in_calc(self, parse_and_check):
        """Test custom property in calc()."""
        css = ".element { width: calc(var(--base-width) * 2); }"
        assert parse_and_check(css, 'css-variables')

    def test_component_scoped_properties(self, parse_and_check):
        """Test component-scoped custom properties."""
        css = """
        .card {
            --card-padding: 16px;
            padding: var(--card-padding);
        }
        """
        assert parse_and_check(css, 'css-variables')
