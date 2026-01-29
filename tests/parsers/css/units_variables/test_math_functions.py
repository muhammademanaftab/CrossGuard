"""Tests for CSS Math Functions.

Tests features: css-math-functions
"""

import pytest


class TestCSSMathFunctions:
    """Tests for CSS Math Functions (min, max, clamp) detection."""

    def test_min_function(self, parse_and_check):
        """Test min() function detection."""
        css = ".element { width: min(100%, 500px); }"
        assert parse_and_check(css, 'css-math-functions')

    def test_max_function(self, parse_and_check):
        """Test max() function detection."""
        css = ".element { width: max(200px, 50%); }"
        assert parse_and_check(css, 'css-math-functions')

    def test_clamp_function(self, parse_and_check):
        """Test clamp() function detection."""
        css = ".element { font-size: clamp(1rem, 2.5vw, 2rem); }"
        assert parse_and_check(css, 'css-math-functions')

    def test_min_multiple_values(self, parse_and_check):
        """Test min() with multiple values."""
        css = ".element { width: min(100%, 50vw, 500px); }"
        assert parse_and_check(css, 'css-math-functions')

    def test_max_multiple_values(self, parse_and_check):
        """Test max() with multiple values."""
        css = ".element { padding: max(1rem, 20px, 5%); }"
        assert parse_and_check(css, 'css-math-functions')

    def test_clamp_responsive_typography(self, parse_and_check):
        """Test clamp() for responsive typography."""
        css = """
        h1 { font-size: clamp(1.5rem, 4vw, 3rem); }
        p { font-size: clamp(1rem, 2vw, 1.25rem); }
        """
        assert parse_and_check(css, 'css-math-functions')

    def test_nested_math_functions(self, parse_and_check):
        """Test nested math functions."""
        css = ".element { width: min(max(200px, 50%), 100vw); }"
        assert parse_and_check(css, 'css-math-functions')

    def test_math_with_calc(self, parse_and_check):
        """Test math functions with calc()."""
        css = ".element { width: clamp(200px, calc(50% - 20px), 800px); }"
        assert parse_and_check(css, 'css-math-functions')
