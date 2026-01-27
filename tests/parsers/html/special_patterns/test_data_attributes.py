"""Tests for data-* attribute detection.

Tests pattern: data-* attributes (dataset feature)
"""

import pytest


class TestDataAttributes:
    """Tests for data-* attribute detection."""

    def test_single_data_attribute(self, parse_and_check):
        """Test single data attribute."""
        html = '<div data-id="123">Content</div>'
        assert parse_and_check(html, 'dataset')

    def test_multiple_data_attributes(self, parse_and_check):
        """Test multiple data attributes on same element."""
        html = '<div data-id="123" data-name="test" data-value="abc">Content</div>'
        assert parse_and_check(html, 'dataset')

    def test_data_attribute_empty_value(self, parse_and_check):
        """Test data attribute with empty value."""
        html = '<div data-empty="">Content</div>'
        assert parse_and_check(html, 'dataset')

    def test_data_attribute_no_value(self, parse_and_check):
        """Test data attribute without value (boolean-style)."""
        html = '<div data-active>Content</div>'
        assert parse_and_check(html, 'dataset')

    def test_data_attribute_with_hyphen(self, parse_and_check):
        """Test data attribute with hyphens in name."""
        html = '<div data-user-id="123" data-created-at="2024-01-15">Content</div>'
        assert parse_and_check(html, 'dataset')

    def test_data_attribute_complex_value(self, parse_and_check):
        """Test data attribute with complex value."""
        html = '<div data-config=\'{"key": "value", "num": 123}\'>Content</div>'
        assert parse_and_check(html, 'dataset')

    def test_data_attribute_on_various_elements(self, parse_html):
        """Test data attributes on various HTML elements."""
        html = """
        <div data-section="main">
            <button data-action="submit">Submit</button>
            <input data-validate="required" type="text">
            <span data-tooltip="Help text">?</span>
            <a href="#" data-target="modal">Open</a>
        </div>
        """
        features = parse_html(html)
        assert 'dataset' in features


class TestDataAttributePatterns:
    """Tests for common data attribute patterns."""

    def test_data_for_js_frameworks(self, parse_html):
        """Test data attributes commonly used with JS frameworks."""
        html = """
        <div data-controller="modal">
            <button data-action="click->modal#open">Open Modal</button>
            <div data-modal-target="content" hidden>
                Modal content
            </div>
        </div>
        """
        features = parse_html(html)
        assert 'dataset' in features

    def test_data_for_analytics(self, parse_html):
        """Test data attributes for analytics tracking."""
        html = """
        <button data-ga-event="click"
                data-ga-category="CTA"
                data-ga-label="signup-button">
            Sign Up
        </button>
        """
        features = parse_html(html)
        assert 'dataset' in features

    def test_data_for_testing(self, parse_html):
        """Test data attributes for testing (data-testid)."""
        html = """
        <form data-testid="login-form">
            <input data-testid="username-input" type="text">
            <input data-testid="password-input" type="password">
            <button data-testid="submit-button">Login</button>
        </form>
        """
        features = parse_html(html)
        assert 'dataset' in features

    def test_data_for_localization(self, parse_html):
        """Test data attributes for localization."""
        html = """
        <p data-i18n="greeting">Hello</p>
        <button data-i18n="submit-button" data-i18n-attr="title">Submit</button>
        """
        features = parse_html(html)
        assert 'dataset' in features

    def test_data_for_lazy_loading(self, parse_html):
        """Test data attributes for lazy loading."""
        html = """
        <img data-src="image.jpg"
             data-srcset="image-2x.jpg 2x"
             src="placeholder.jpg"
             alt="Lazy loaded image">
        """
        features = parse_html(html)
        assert 'dataset' in features

    def test_data_for_carousel(self, parse_html):
        """Test data attributes for carousel/slider."""
        html = """
        <div data-carousel="true" data-autoplay="true" data-interval="5000">
            <div data-slide="1">Slide 1</div>
            <div data-slide="2">Slide 2</div>
            <div data-slide="3">Slide 3</div>
        </div>
        """
        features = parse_html(html)
        assert 'dataset' in features


class TestDataAttributeWithOtherFeatures:
    """Tests for data attributes combined with other HTML5 features."""

    def test_data_with_custom_element(self, parse_html):
        """Test data attributes on custom elements."""
        html = '<my-component data-config="{}"></my-component>'
        features = parse_html(html)
        assert 'dataset' in features
        assert 'custom-elementsv1' in features

    def test_data_with_template(self, parse_html):
        """Test data attributes with template element."""
        html = """
        <template data-template-id="card-template">
            <div class="card" data-card-type="">
                <slot name="content"></slot>
            </div>
        </template>
        """
        features = parse_html(html)
        assert 'dataset' in features
        assert 'template' in features
        assert 'shadowdomv1' in features  # slot

    def test_data_with_dialog(self, parse_html):
        """Test data attributes with dialog element."""
        html = """
        <dialog data-dialog-id="confirm" data-closable="true">
            <h2>Confirm</h2>
            <button data-action="close">Close</button>
        </dialog>
        """
        features = parse_html(html)
        assert 'dataset' in features
        assert 'dialog' in features


class TestNoDataAttributes:
    """Tests for HTML without data attributes."""

    def test_no_data_attributes(self, parse_html):
        """Test HTML without any data attributes."""
        html = """
        <div id="main" class="container">
            <h1>Title</h1>
            <p>Paragraph</p>
        </div>
        """
        features = parse_html(html)
        assert 'dataset' not in features

    def test_aria_not_data(self, parse_html):
        """Test that aria-* attributes are not detected as data-*."""
        html = '<div aria-label="Label" aria-hidden="false">Content</div>'
        features = parse_html(html)
        assert 'wai-aria' in features
        assert 'dataset' not in features

    def test_standard_attributes(self, parse_html):
        """Test that standard attributes are not detected as data-*."""
        html = '<input type="text" name="field" value="test">'
        features = parse_html(html)
        assert 'dataset' not in features
