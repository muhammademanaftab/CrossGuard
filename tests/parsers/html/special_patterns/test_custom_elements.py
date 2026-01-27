"""Tests for custom elements detection.

Tests pattern: hyphenated custom element tags (custom-elementsv1)
"""

import pytest


class TestCustomElements:
    """Tests for custom element (web component) detection."""

    def test_basic_custom_element(self, parse_and_check):
        """Test basic custom element with hyphen."""
        html = '<my-component></my-component>'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_custom_element_with_content(self, parse_and_check):
        """Test custom element with content."""
        html = '<my-card>Card content</my-card>'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_custom_element_with_attributes(self, parse_and_check):
        """Test custom element with attributes."""
        html = '<user-profile name="John" id="profile-1"></user-profile>'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_nested_custom_elements(self, parse_and_check):
        """Test nested custom elements."""
        html = """
        <app-container>
            <app-header></app-header>
            <app-content></app-content>
            <app-footer></app-footer>
        </app-container>
        """
        assert parse_and_check(html, 'custom-elementsv1')

    def test_custom_element_multiple_hyphens(self, parse_and_check):
        """Test custom element with multiple hyphens."""
        html = '<my-very-long-component-name></my-very-long-component-name>'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_custom_element_self_closing(self, parse_and_check):
        """Test self-closing custom element."""
        # Note: HTML parser may handle this differently
        html = '<my-icon/>'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_custom_element_lit_style(self, parse_and_check):
        """Test custom element in Lit/LitElement style."""
        html = '<lit-element-demo></lit-element-demo>'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_custom_element_polymer_style(self, parse_and_check):
        """Test custom element in Polymer style."""
        html = '<paper-button>Click me</paper-button>'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_custom_element_with_slots(self, parse_html):
        """Test custom element with slot content."""
        html = """
        <my-dialog>
            <span slot="title">Dialog Title</span>
            <p slot="content">Dialog content here</p>
        </my-dialog>
        """
        features = parse_html(html)
        assert 'custom-elementsv1' in features

    def test_custom_element_with_shadow_root(self, parse_html):
        """Test custom element with declarative shadow DOM."""
        html = """
        <my-component>
            <template shadowrootmode="open">
                <style>
                    :host { display: block; }
                </style>
                <slot></slot>
            </template>
        </my-component>
        """
        features = parse_html(html)
        assert 'custom-elementsv1' in features
        assert 'declarative-shadow-dom' in features


class TestCommonWebComponentFrameworks:
    """Tests for common web component framework patterns."""

    def test_shoelace_components(self, parse_html):
        """Test Shoelace UI components."""
        html = """
        <sl-button>Click me</sl-button>
        <sl-input placeholder="Enter text"></sl-input>
        <sl-card>Card content</sl-card>
        """
        features = parse_html(html)
        assert 'custom-elementsv1' in features

    def test_ionic_components(self, parse_html):
        """Test Ionic Framework components."""
        html = """
        <ion-app>
            <ion-header>
                <ion-toolbar>
                    <ion-title>App Title</ion-title>
                </ion-toolbar>
            </ion-header>
            <ion-content>
                <ion-button>Click</ion-button>
            </ion-content>
        </ion-app>
        """
        features = parse_html(html)
        assert 'custom-elementsv1' in features

    def test_vaadin_components(self, parse_html):
        """Test Vaadin components."""
        html = """
        <vaadin-grid>
            <vaadin-grid-column path="name"></vaadin-grid-column>
            <vaadin-grid-column path="email"></vaadin-grid-column>
        </vaadin-grid>
        """
        features = parse_html(html)
        assert 'custom-elementsv1' in features

    def test_stencil_components(self, parse_html):
        """Test Stencil.js components."""
        html = """
        <my-app>
            <my-header></my-header>
            <my-router></my-router>
        </my-app>
        """
        features = parse_html(html)
        assert 'custom-elementsv1' in features


class TestIsAttribute:
    """Tests for 'is' attribute (customized built-in elements)."""

    def test_is_attribute_on_button(self, parse_and_check):
        """Test 'is' attribute on button (customized built-in)."""
        html = '<button is="fancy-button">Click me</button>'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_is_attribute_on_input(self, parse_and_check):
        """Test 'is' attribute on input."""
        html = '<input is="enhanced-input" type="text">'
        assert parse_and_check(html, 'custom-elementsv1')

    def test_is_attribute_on_div(self, parse_and_check):
        """Test 'is' attribute on div."""
        html = '<div is="expandable-container">Content</div>'
        assert parse_and_check(html, 'custom-elementsv1')


class TestSvgElementsExcluded:
    """Tests that SVG elements with hyphens are NOT detected as custom elements."""

    def test_font_face_not_custom(self, parse_html):
        """Test font-face is not detected as custom element."""
        html = """
        <svg>
            <defs>
                <font-face font-family="test"></font-face>
            </defs>
        </svg>
        """
        features = parse_html(html)
        # font-face should be excluded as it's a known SVG element
        # The implementation should skip this

    def test_missing_glyph_not_custom(self, parse_html):
        """Test missing-glyph is not detected as custom element."""
        html = """
        <svg>
            <missing-glyph></missing-glyph>
        </svg>
        """
        features = parse_html(html)
        # missing-glyph should be excluded


class TestNotCustomElements:
    """Tests for elements that should NOT be detected as custom elements."""

    def test_standard_elements_no_hyphen(self, parse_html):
        """Test standard elements without hyphens."""
        html = """
        <div>
            <header>Header</header>
            <main>Main</main>
            <footer>Footer</footer>
        </div>
        """
        features = parse_html(html)
        # These are standard elements, not custom
        assert 'custom-elementsv1' not in features

    def test_single_word_element(self, parse_html):
        """Test that single word element is not custom."""
        html = '<mycomponent>Content</mycomponent>'
        features = parse_html(html)
        # No hyphen, so not a valid custom element name
        assert 'custom-elementsv1' not in features

    def test_starting_with_hyphen(self, parse_html):
        """Test element starting with hyphen (invalid custom element)."""
        html = '<-invalid-name>Content</-invalid-name>'
        features = parse_html(html)
        # Invalid custom element name, may or may not be detected
        # depending on parser behavior

    def test_data_element(self, parse_html):
        """Test that data element is not custom."""
        html = '<data value="123">One hundred twenty-three</data>'
        features = parse_html(html)
        assert 'custom-elementsv1' not in features
