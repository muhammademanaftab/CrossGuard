"""Tests for CSS At-Rules features.

Tests features: css-featurequeries, css-counters, css-page-break, css-paged-media,
                css-when-else, css-cascade-layers, css-namespaces, css-at-counter-style,
                css-deviceadaptation, css-cascade-scope

Note: css-counters patterns include: counter-reset, counter-increment, counter(
The pattern counter( matches counter() but NOT counters() since it requires the
opening parenthesis immediately after "counter".
"""

import pytest


class TestFeatureQueries:
    """Tests for @supports (feature queries) detection."""

    def test_supports_basic(self, parse_and_check):
        """Test @supports rule detection."""
        css = "@supports (display: grid) { .grid { display: grid; } }"
        assert parse_and_check(css, 'css-featurequeries')

    def test_supports_not(self, parse_and_check):
        """Test @supports not detection."""
        css = "@supports not (display: grid) { .fallback { display: flex; } }"
        assert parse_and_check(css, 'css-featurequeries')

    def test_supports_and(self, parse_and_check):
        """Test @supports and detection."""
        css = "@supports (display: grid) and (gap: 20px) { .modern { gap: 20px; } }"
        assert parse_and_check(css, 'css-featurequeries')

    def test_supports_or(self, parse_and_check):
        """Test @supports or detection."""
        css = "@supports (display: flex) or (display: grid) { .layout { margin: 0; } }"
        assert parse_and_check(css, 'css-featurequeries')

    def test_supports_selector(self, parse_and_check):
        """Test @supports selector() detection."""
        css = "@supports selector(:has(*)) { .parent:has(img) { padding: 10px; } }"
        assert parse_and_check(css, 'css-featurequeries')


class TestCSSCounters:
    """Tests for CSS Counters detection."""

    def test_counter_reset(self, parse_and_check):
        """Test counter-reset detection."""
        css = "body { counter-reset: section; }"
        assert parse_and_check(css, 'css-counters')

    def test_counter_increment(self, parse_and_check):
        """Test counter-increment detection."""
        css = "h2 { counter-increment: section; }"
        assert parse_and_check(css, 'css-counters')

    def test_counter_function(self, parse_and_check):
        """Test counter() function detection."""
        css = "h2::before { content: counter(section) '. '; }"
        assert parse_and_check(css, 'css-counters')


class TestPageBreak:
    """Tests for page-break properties detection."""

    def test_page_break_before(self, parse_and_check):
        """Test page-break-before detection."""
        css = ".chapter { page-break-before: always; }"
        assert parse_and_check(css, 'css-page-break')

    def test_page_break_after(self, parse_and_check):
        """Test page-break-after detection."""
        css = ".section { page-break-after: avoid; }"
        assert parse_and_check(css, 'css-page-break')

    def test_page_break_inside(self, parse_and_check):
        """Test page-break-inside detection."""
        css = "table { page-break-inside: avoid; }"
        assert parse_and_check(css, 'css-page-break')


class TestPagedMedia:
    """Tests for @page rule detection."""

    def test_page_rule(self, parse_and_check):
        """Test @page rule detection."""
        css = "@page { margin: 1in; }"
        assert parse_and_check(css, 'css-paged-media')

    def test_page_first(self, parse_and_check):
        """Test @page :first detection."""
        css = "@page :first { margin-top: 2in; }"
        assert parse_and_check(css, 'css-paged-media')

    def test_page_left_right(self, parse_and_check):
        """Test @page :left/:right detection."""
        css = "@page :left { margin-left: 1.5in; }"
        assert parse_and_check(css, 'css-paged-media')


class TestWhenElse:
    """Tests for @when/@else rules detection."""

    def test_when_rule(self, parse_and_check):
        """Test @when rule detection."""
        css = "@when media(width >= 400px) { .element { display: block; } }"
        assert parse_and_check(css, 'css-when-else')

    def test_else_rule(self, parse_and_check):
        """Test @else rule detection."""
        css = "@else { .element { display: none; } }"
        assert parse_and_check(css, 'css-when-else')


class TestCascadeLayers:
    """Tests for @layer rule detection."""

    def test_layer_rule(self, parse_and_check):
        """Test @layer rule detection."""
        css = "@layer base { body { margin: 0; } }"
        assert parse_and_check(css, 'css-cascade-layers')

    def test_layer_order(self, parse_and_check):
        """Test @layer order declaration."""
        css = "@layer reset, base, components, utilities;"
        assert parse_and_check(css, 'css-cascade-layers')

    def test_nested_layers(self, parse_and_check):
        """Test nested @layer rules."""
        css = "@layer framework { @layer base { h1 { margin: 0; } } }"
        assert parse_and_check(css, 'css-cascade-layers')


class TestNamespaces:
    """Tests for @namespace rule detection."""

    def test_namespace_rule(self, parse_and_check):
        """Test @namespace rule detection."""
        css = '@namespace svg url("http://www.w3.org/2000/svg");'
        assert parse_and_check(css, 'css-namespaces')


class TestCounterStyle:
    """Tests for @counter-style rule detection."""

    def test_counter_style_rule(self, parse_and_check):
        """Test @counter-style rule detection."""
        css = """
        @counter-style thumbs {
            system: cyclic;
            symbols: '\\1F44D';
        }
        """
        assert parse_and_check(css, 'css-at-counter-style')


class TestDeviceAdaptation:
    """Tests for @viewport rule detection."""

    def test_viewport_rule(self, parse_and_check):
        """Test @viewport rule detection."""
        css = "@viewport { width: device-width; }"
        assert parse_and_check(css, 'css-deviceadaptation')


class TestScopeRule:
    """Tests for @scope rule detection."""

    def test_scope_rule(self, parse_and_check):
        """Test @scope rule detection."""
        css = "@scope (.card) { h2 { color: blue; } }"
        assert parse_and_check(css, 'css-cascade-scope')

    def test_scope_with_limit(self, parse_and_check):
        """Test @scope with limit detection."""
        css = "@scope (.card) to (.card-footer) { p { margin: 0; } }"
        assert parse_and_check(css, 'css-cascade-scope')
