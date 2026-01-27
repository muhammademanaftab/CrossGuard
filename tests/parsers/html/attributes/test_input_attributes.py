"""Tests for HTML5 input-related attribute detection.

Tests attributes: placeholder, autocomplete, autofocus, inputmode, multiple, accept, readonly
"""

import pytest


class TestPlaceholderAttribute:
    """Tests for placeholder attribute detection."""

    def test_placeholder_on_input(self, parse_and_check):
        """Test placeholder on text input."""
        html = '<input type="text" placeholder="Enter your name">'
        assert parse_and_check(html, 'input-placeholder')

    def test_placeholder_on_email(self, parse_and_check):
        """Test placeholder on email input."""
        html = '<input type="email" placeholder="name@example.com">'
        assert parse_and_check(html, 'input-placeholder')

    def test_placeholder_on_textarea(self, parse_and_check):
        """Test placeholder on textarea."""
        html = '<textarea placeholder="Enter your message"></textarea>'
        assert parse_and_check(html, 'input-placeholder')

    def test_placeholder_on_search(self, parse_and_check):
        """Test placeholder on search input."""
        html = '<input type="search" placeholder="Search...">'
        assert parse_and_check(html, 'input-placeholder')

    def test_placeholder_empty(self, parse_and_check):
        """Test placeholder with empty string."""
        html = '<input type="text" placeholder="">'
        assert parse_and_check(html, 'input-placeholder')


class TestAutocompleteAttribute:
    """Tests for autocomplete attribute detection."""

    def test_autocomplete_on(self, parse_and_check):
        """Test autocomplete=on."""
        html = '<input type="text" autocomplete="on">'
        assert parse_and_check(html, 'input-autocomplete-onoff')

    def test_autocomplete_off(self, parse_and_check):
        """Test autocomplete=off."""
        html = '<input type="text" autocomplete="off">'
        assert parse_and_check(html, 'input-autocomplete-onoff')

    def test_autocomplete_name(self, parse_and_check):
        """Test autocomplete=name."""
        html = '<input type="text" autocomplete="name">'
        assert parse_and_check(html, 'input-autocomplete-onoff')

    def test_autocomplete_email(self, parse_and_check):
        """Test autocomplete=email."""
        html = '<input type="email" autocomplete="email">'
        assert parse_and_check(html, 'input-autocomplete-onoff')

    def test_autocomplete_current_password(self, parse_and_check):
        """Test autocomplete=current-password."""
        html = '<input type="password" autocomplete="current-password">'
        assert parse_and_check(html, 'input-autocomplete-onoff')

    def test_autocomplete_new_password(self, parse_and_check):
        """Test autocomplete=new-password."""
        html = '<input type="password" autocomplete="new-password">'
        assert parse_and_check(html, 'input-autocomplete-onoff')

    def test_autocomplete_address(self, parse_and_check):
        """Test autocomplete for address fields."""
        html = """
        <input type="text" autocomplete="street-address">
        <input type="text" autocomplete="city">
        <input type="text" autocomplete="postal-code">
        """
        assert parse_and_check(html, 'input-autocomplete-onoff')

    def test_autocomplete_on_form(self, parse_and_check):
        """Test autocomplete on form element."""
        html = '<form autocomplete="off"><input type="text"></form>'
        assert parse_and_check(html, 'input-autocomplete-onoff')


class TestAutofocusAttribute:
    """Tests for autofocus attribute detection."""

    def test_autofocus_on_input(self, parse_and_check):
        """Test autofocus on input."""
        html = '<input type="text" autofocus>'
        assert parse_and_check(html, 'autofocus')

    def test_autofocus_on_textarea(self, parse_and_check):
        """Test autofocus on textarea."""
        html = '<textarea autofocus></textarea>'
        assert parse_and_check(html, 'autofocus')

    def test_autofocus_on_button(self, parse_and_check):
        """Test autofocus on button."""
        html = '<button autofocus>Click me</button>'
        assert parse_and_check(html, 'autofocus')

    def test_autofocus_on_select(self, parse_and_check):
        """Test autofocus on select."""
        html = """
        <select autofocus>
            <option>Option 1</option>
            <option>Option 2</option>
        </select>
        """
        assert parse_and_check(html, 'autofocus')

    def test_autofocus_with_value(self, parse_and_check):
        """Test autofocus with explicit value."""
        html = '<input type="text" autofocus="autofocus">'
        assert parse_and_check(html, 'autofocus')


class TestInputmodeAttribute:
    """Tests for inputmode attribute detection."""

    def test_inputmode_numeric(self, parse_and_check):
        """Test inputmode=numeric."""
        html = '<input type="text" inputmode="numeric">'
        assert parse_and_check(html, 'input-inputmode')

    def test_inputmode_decimal(self, parse_and_check):
        """Test inputmode=decimal."""
        html = '<input type="text" inputmode="decimal">'
        assert parse_and_check(html, 'input-inputmode')

    def test_inputmode_tel(self, parse_and_check):
        """Test inputmode=tel."""
        html = '<input type="text" inputmode="tel">'
        assert parse_and_check(html, 'input-inputmode')

    def test_inputmode_email(self, parse_and_check):
        """Test inputmode=email."""
        html = '<input type="text" inputmode="email">'
        assert parse_and_check(html, 'input-inputmode')

    def test_inputmode_url(self, parse_and_check):
        """Test inputmode=url."""
        html = '<input type="text" inputmode="url">'
        assert parse_and_check(html, 'input-inputmode')

    def test_inputmode_search(self, parse_and_check):
        """Test inputmode=search."""
        html = '<input type="text" inputmode="search">'
        assert parse_and_check(html, 'input-inputmode')

    def test_inputmode_none(self, parse_and_check):
        """Test inputmode=none (suppress virtual keyboard)."""
        html = '<input type="text" inputmode="none">'
        assert parse_and_check(html, 'input-inputmode')

    def test_inputmode_on_contenteditable(self, parse_and_check):
        """Test inputmode on contenteditable element."""
        html = '<div contenteditable="true" inputmode="numeric">123</div>'
        assert parse_and_check(html, 'input-inputmode')


class TestMultipleAttribute:
    """Tests for multiple attribute detection."""

    def test_multiple_on_file(self, parse_and_check):
        """Test multiple on file input."""
        html = '<input type="file" multiple>'
        assert parse_and_check(html, 'input-file-multiple')

    def test_multiple_on_email(self, parse_and_check):
        """Test multiple on email input."""
        html = '<input type="email" multiple>'
        assert parse_and_check(html, 'input-file-multiple')

    def test_multiple_with_value(self, parse_and_check):
        """Test multiple with explicit value."""
        html = '<input type="file" multiple="multiple">'
        assert parse_and_check(html, 'input-file-multiple')

    def test_multiple_file_upload(self, parse_and_check):
        """Test multiple file upload form."""
        html = """
        <form enctype="multipart/form-data">
            <label>Select files:
                <input type="file" name="files" multiple>
            </label>
        </form>
        """
        assert parse_and_check(html, 'input-file-multiple')


class TestAcceptAttribute:
    """Tests for accept attribute detection."""

    def test_accept_image(self, parse_and_check):
        """Test accept for images."""
        html = '<input type="file" accept="image/*">'
        assert parse_and_check(html, 'input-file-accept')

    def test_accept_video(self, parse_and_check):
        """Test accept for video."""
        html = '<input type="file" accept="video/*">'
        assert parse_and_check(html, 'input-file-accept')

    def test_accept_audio(self, parse_and_check):
        """Test accept for audio."""
        html = '<input type="file" accept="audio/*">'
        assert parse_and_check(html, 'input-file-accept')

    def test_accept_specific_types(self, parse_and_check):
        """Test accept with specific MIME types."""
        html = '<input type="file" accept=".pdf,.doc,.docx">'
        assert parse_and_check(html, 'input-file-accept')

    def test_accept_image_types(self, parse_and_check):
        """Test accept with specific image types."""
        html = '<input type="file" accept="image/png, image/jpeg, image/gif">'
        assert parse_and_check(html, 'input-file-accept')


class TestReadonlyAttribute:
    """Tests for readonly attribute detection."""

    def test_readonly_on_input(self, parse_and_check):
        """Test readonly on text input."""
        html = '<input type="text" readonly>'
        assert parse_and_check(html, 'readonly-attr')

    def test_readonly_on_textarea(self, parse_and_check):
        """Test readonly on textarea."""
        html = '<textarea readonly>Read only content</textarea>'
        assert parse_and_check(html, 'readonly-attr')

    def test_readonly_with_value(self, parse_and_check):
        """Test readonly with value attribute."""
        html = '<input type="text" value="Cannot change" readonly>'
        assert parse_and_check(html, 'readonly-attr')

    def test_readonly_vs_disabled(self, parse_html):
        """Test readonly (value submitted) vs disabled (not submitted)."""
        html = '<input type="text" readonly value="submitted">'
        features = parse_html(html)
        assert 'readonly-attr' in features


class TestCombinedInputAttributes:
    """Tests for combined input attributes."""

    def test_search_form(self, parse_html):
        """Test search form with multiple attributes."""
        html = """
        <form>
            <input type="search"
                   placeholder="Search..."
                   autofocus
                   autocomplete="off">
        </form>
        """
        features = parse_html(html)
        assert 'input-placeholder' in features
        assert 'autofocus' in features
        assert 'input-autocomplete-onoff' in features

    def test_file_upload_form(self, parse_html):
        """Test file upload with accept and multiple."""
        html = """
        <input type="file"
               accept="image/*"
               multiple>
        """
        features = parse_html(html)
        assert 'input-file-accept' in features
        assert 'input-file-multiple' in features

    def test_mobile_optimized_form(self, parse_html):
        """Test mobile-optimized form with inputmode."""
        html = """
        <form>
            <label>Phone:
                <input type="text" inputmode="tel" autocomplete="tel"
                       placeholder="(555) 555-5555">
            </label>
            <label>Credit Card:
                <input type="text" inputmode="numeric" autocomplete="cc-number"
                       placeholder="1234 5678 9012 3456">
            </label>
        </form>
        """
        features = parse_html(html)
        assert 'input-inputmode' in features
        assert 'input-autocomplete-onoff' in features
        assert 'input-placeholder' in features


class TestNoInputAttributes:
    """Tests for inputs without special attributes."""

    def test_basic_input(self, parse_html):
        """Test basic input without special attributes."""
        html = '<input type="text" name="field">'
        features = parse_html(html)
        assert 'input-placeholder' not in features
        assert 'autofocus' not in features
        assert 'input-autocomplete-onoff' not in features
        assert 'input-inputmode' not in features
