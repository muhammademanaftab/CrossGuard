"""Tests for HTML5 text-related input type detection.

Tests input types: email, tel, url, search
"""

import pytest


class TestEmailInput:
    """Tests for input[type="email"] detection."""

    def test_email_basic(self, parse_and_check):
        """Test basic email input detection."""
        html = '<input type="email">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_email_with_name(self, parse_and_check):
        """Test email input with name attribute."""
        html = '<input type="email" name="userEmail">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_email_required(self, parse_and_check):
        """Test required email input."""
        html = '<input type="email" required>'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_email_with_pattern(self, parse_and_check):
        """Test email input with pattern validation."""
        html = '<input type="email" pattern=".+@company\.com">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_email_multiple(self, parse_and_check):
        """Test email input with multiple attribute."""
        html = '<input type="email" multiple>'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_email_with_placeholder(self, parse_and_check):
        """Test email input with placeholder."""
        html = '<input type="email" placeholder="name@example.com">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_email_in_form(self, parse_and_check):
        """Test email input within registration form."""
        html = """
        <form>
            <label for="email">Email Address:</label>
            <input type="email" id="email" name="email" required>
        </form>
        """
        assert parse_and_check(html, 'input-email-tel-url')


class TestTelInput:
    """Tests for input[type="tel"] detection."""

    def test_tel_basic(self, parse_and_check):
        """Test basic tel input detection."""
        html = '<input type="tel">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_tel_with_pattern(self, parse_and_check):
        """Test tel input with phone pattern."""
        html = '<input type="tel" pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_tel_with_placeholder(self, parse_and_check):
        """Test tel input with placeholder."""
        html = '<input type="tel" placeholder="123-456-7890">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_tel_international(self, parse_and_check):
        """Test tel input for international numbers."""
        html = '<input type="tel" pattern="\+[0-9]{1,3}[0-9]{10}">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_tel_in_contact_form(self, parse_and_check):
        """Test tel input in contact form."""
        html = """
        <form>
            <label for="phone">Phone Number:</label>
            <input type="tel" id="phone" name="phone"
                   placeholder="(555) 555-5555"
                   pattern="\([0-9]{3}\) [0-9]{3}-[0-9]{4}">
        </form>
        """
        assert parse_and_check(html, 'input-email-tel-url')


class TestUrlInput:
    """Tests for input[type="url"] detection."""

    def test_url_basic(self, parse_and_check):
        """Test basic url input detection."""
        html = '<input type="url">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_url_with_placeholder(self, parse_and_check):
        """Test url input with placeholder."""
        html = '<input type="url" placeholder="https://example.com">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_url_required(self, parse_and_check):
        """Test required url input."""
        html = '<input type="url" required>'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_url_with_pattern(self, parse_and_check):
        """Test url input with pattern for https only."""
        html = '<input type="url" pattern="https://.*">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_url_in_profile_form(self, parse_and_check):
        """Test url input in profile form."""
        html = """
        <form>
            <label for="website">Website:</label>
            <input type="url" id="website" name="website"
                   placeholder="https://yoursite.com">

            <label for="linkedin">LinkedIn:</label>
            <input type="url" id="linkedin" name="linkedin">
        </form>
        """
        assert parse_and_check(html, 'input-email-tel-url')


class TestSearchInput:
    """Tests for input[type="search"] detection."""

    def test_search_basic(self, parse_and_check):
        """Test basic search input detection."""
        html = '<input type="search">'
        assert parse_and_check(html, 'input-search')

    def test_search_with_placeholder(self, parse_and_check):
        """Test search input with placeholder."""
        html = '<input type="search" placeholder="Search...">'
        assert parse_and_check(html, 'input-search')

    def test_search_with_autofocus(self, parse_and_check):
        """Test search input with autofocus."""
        html = '<input type="search" autofocus>'
        assert parse_and_check(html, 'input-search')

    def test_search_with_results(self, parse_and_check):
        """Test search input with results attribute (Safari)."""
        html = '<input type="search" results="5">'
        assert parse_and_check(html, 'input-search')

    def test_search_in_header(self, parse_and_check):
        """Test search input in header navigation."""
        html = """
        <header>
            <nav>
                <a href="/">Home</a>
                <form role="search">
                    <input type="search" name="q" placeholder="Search site...">
                    <button type="submit">Search</button>
                </form>
            </nav>
        </header>
        """
        assert parse_and_check(html, 'input-search')

    def test_search_with_datalist(self, parse_html):
        """Test search input with datalist suggestions."""
        html = """
        <input type="search" list="search-suggestions">
        <datalist id="search-suggestions">
            <option value="HTML">
            <option value="CSS">
            <option value="JavaScript">
        </datalist>
        """
        features = parse_html(html)
        assert 'input-search' in features
        assert 'datalist' in features


class TestMultipleTextInputs:
    """Tests for multiple text input types together."""

    def test_contact_form_all_types(self, parse_html):
        """Test contact form with email, tel, and url."""
        html = """
        <form id="contact">
            <input type="email" name="email" placeholder="Email" required>
            <input type="tel" name="phone" placeholder="Phone">
            <input type="url" name="website" placeholder="Website">
            <button type="submit">Submit</button>
        </form>
        """
        features = parse_html(html)
        assert 'input-email-tel-url' in features

    def test_search_and_contact(self, parse_html):
        """Test search alongside contact inputs."""
        html = """
        <header>
            <form>
                <input type="search" name="q">
            </form>
        </header>
        <main>
            <form>
                <input type="email" name="email">
                <input type="tel" name="phone">
            </form>
        </main>
        """
        features = parse_html(html)
        assert 'input-search' in features
        assert 'input-email-tel-url' in features


class TestCaseInsensitivity:
    """Tests for case insensitivity of type values."""

    def test_email_uppercase(self, parse_and_check):
        """Test EMAIL type in uppercase."""
        html = '<input type="EMAIL">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_tel_mixed_case(self, parse_and_check):
        """Test Tel type in mixed case."""
        html = '<input type="Tel">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_url_uppercase(self, parse_and_check):
        """Test URL type in uppercase."""
        html = '<input type="URL">'
        assert parse_and_check(html, 'input-email-tel-url')

    def test_search_mixed_case(self, parse_and_check):
        """Test Search type in mixed case."""
        html = '<input type="Search">'
        assert parse_and_check(html, 'input-search')


class TestNoTextInputFeatures:
    """Tests for inputs that should NOT match text input types."""

    def test_text_input(self, parse_html):
        """Test that plain text input doesn't match special types."""
        html = '<input type="text">'
        features = parse_html(html)
        assert 'input-email-tel-url' not in features
        assert 'input-search' not in features

    def test_password_input(self, parse_html):
        """Test password input doesn't match."""
        html = '<input type="password">'
        features = parse_html(html)
        assert 'input-email-tel-url' not in features

    def test_no_type_input(self, parse_html):
        """Test input without type doesn't match."""
        html = '<input name="field">'
        features = parse_html(html)
        assert 'input-email-tel-url' not in features
        assert 'input-search' not in features
