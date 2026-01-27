"""Tests for HTML5 form validation attribute detection.

Tests attributes: required, pattern, min, max, step, minlength, maxlength, novalidate, formnovalidate
"""

import pytest


class TestRequiredAttribute:
    """Tests for required attribute detection."""

    def test_required_on_input(self, parse_and_check):
        """Test required attribute on input."""
        html = '<input type="text" required>'
        assert parse_and_check(html, 'form-validation')

    def test_required_on_select(self, parse_and_check):
        """Test required attribute on select."""
        html = """
        <select required>
            <option value="">Choose</option>
            <option value="1">One</option>
        </select>
        """
        assert parse_and_check(html, 'form-validation')

    def test_required_on_textarea(self, parse_and_check):
        """Test required attribute on textarea."""
        html = '<textarea required></textarea>'
        assert parse_and_check(html, 'form-validation')

    def test_required_boolean(self, parse_and_check):
        """Test required as boolean attribute."""
        html = '<input type="email" required="required">'
        assert parse_and_check(html, 'form-validation')


class TestPatternAttribute:
    """Tests for pattern attribute detection."""

    def test_pattern_on_input(self, parse_and_check):
        """Test pattern attribute on input."""
        html = '<input type="text" pattern="[A-Za-z]{3}">'
        assert parse_and_check(html, 'input-pattern')

    def test_pattern_phone(self, parse_and_check):
        """Test pattern for phone number."""
        html = '<input type="tel" pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}">'
        assert parse_and_check(html, 'input-pattern')

    def test_pattern_zip_code(self, parse_and_check):
        """Test pattern for zip code."""
        html = '<input type="text" pattern="[0-9]{5}(-[0-9]{4})?">'
        assert parse_and_check(html, 'input-pattern')

    def test_pattern_with_title(self, parse_and_check):
        """Test pattern with title for error message."""
        html = '''
        <input type="text" pattern="[A-Za-z]+"
               title="Letters only, no spaces">
        '''
        assert parse_and_check(html, 'input-pattern')


class TestMinAttribute:
    """Tests for min attribute detection."""

    def test_min_on_number(self, parse_and_check):
        """Test min attribute on number input."""
        html = '<input type="number" min="0">'
        assert parse_and_check(html, 'form-validation')

    def test_min_on_date(self, parse_and_check):
        """Test min attribute on date input."""
        html = '<input type="date" min="2024-01-01">'
        assert parse_and_check(html, 'form-validation')

    def test_min_on_range(self, parse_and_check):
        """Test min attribute on range input."""
        html = '<input type="range" min="0" max="100">'
        assert parse_and_check(html, 'form-validation')


class TestMaxAttribute:
    """Tests for max attribute detection."""

    def test_max_on_number(self, parse_and_check):
        """Test max attribute on number input."""
        html = '<input type="number" max="100">'
        assert parse_and_check(html, 'form-validation')

    def test_max_on_date(self, parse_and_check):
        """Test max attribute on date input."""
        html = '<input type="date" max="2024-12-31">'
        assert parse_and_check(html, 'form-validation')

    def test_min_max_together(self, parse_and_check):
        """Test min and max together."""
        html = '<input type="number" min="1" max="10">'
        assert parse_and_check(html, 'form-validation')


class TestStepAttribute:
    """Tests for step attribute detection."""

    def test_step_on_number(self, parse_and_check):
        """Test step attribute on number input."""
        html = '<input type="number" step="0.01">'
        assert parse_and_check(html, 'form-validation')

    def test_step_on_range(self, parse_and_check):
        """Test step attribute on range input."""
        html = '<input type="range" step="5">'
        assert parse_and_check(html, 'form-validation')

    def test_step_any(self, parse_and_check):
        """Test step='any' value."""
        html = '<input type="number" step="any">'
        assert parse_and_check(html, 'form-validation')


class TestMinlengthAttribute:
    """Tests for minlength attribute detection."""

    def test_minlength_on_input(self, parse_and_check):
        """Test minlength attribute on input."""
        html = '<input type="text" minlength="3">'
        assert parse_and_check(html, 'input-minlength')

    def test_minlength_on_textarea(self, parse_and_check):
        """Test minlength attribute on textarea."""
        html = '<textarea minlength="10"></textarea>'
        assert parse_and_check(html, 'input-minlength')

    def test_minlength_on_password(self, parse_and_check):
        """Test minlength on password field."""
        html = '<input type="password" minlength="8">'
        assert parse_and_check(html, 'input-minlength')


class TestMaxlengthAttribute:
    """Tests for maxlength attribute detection."""

    def test_maxlength_on_input(self, parse_and_check):
        """Test maxlength attribute on input."""
        html = '<input type="text" maxlength="100">'
        assert parse_and_check(html, 'maxlength')

    def test_maxlength_on_textarea(self, parse_and_check):
        """Test maxlength attribute on textarea."""
        html = '<textarea maxlength="500"></textarea>'
        assert parse_and_check(html, 'maxlength')

    def test_minlength_maxlength_together(self, parse_html):
        """Test minlength and maxlength together."""
        html = '<input type="text" minlength="5" maxlength="50">'
        features = parse_html(html)
        assert 'input-minlength' in features
        assert 'maxlength' in features


class TestNovalidateAttribute:
    """Tests for novalidate attribute detection."""

    def test_novalidate_on_form(self, parse_and_check):
        """Test novalidate attribute on form."""
        html = '<form novalidate><input type="email"></form>'
        assert parse_and_check(html, 'form-validation')

    def test_novalidate_boolean(self, parse_and_check):
        """Test novalidate as boolean attribute."""
        html = '<form novalidate="novalidate"></form>'
        assert parse_and_check(html, 'form-validation')


class TestFormnovalidateAttribute:
    """Tests for formnovalidate attribute detection."""

    def test_formnovalidate_on_button(self, parse_and_check):
        """Test formnovalidate on submit button."""
        html = '<button type="submit" formnovalidate>Skip Validation</button>'
        assert parse_and_check(html, 'form-validation')

    def test_formnovalidate_on_input_submit(self, parse_and_check):
        """Test formnovalidate on input submit."""
        html = '<input type="submit" formnovalidate value="Save Draft">'
        assert parse_and_check(html, 'form-validation')


class TestCombinedFormAttributes:
    """Tests for combined form validation attributes."""

    def test_comprehensive_form(self, parse_html):
        """Test form with multiple validation attributes."""
        html = """
        <form>
            <input type="text" name="name" required minlength="2" maxlength="50">
            <input type="email" name="email" required>
            <input type="tel" name="phone" pattern="[0-9]{10}">
            <input type="number" name="age" min="18" max="120">
            <input type="password" name="password" required minlength="8">
            <textarea name="bio" maxlength="500"></textarea>
            <button type="submit">Submit</button>
            <button type="submit" formnovalidate>Save Draft</button>
        </form>
        """
        features = parse_html(html)
        assert 'form-validation' in features
        assert 'input-pattern' in features
        assert 'input-minlength' in features
        assert 'maxlength' in features

    def test_signup_form(self, parse_html):
        """Test realistic signup form."""
        html = """
        <form id="signup">
            <label>
                Username:
                <input type="text" name="username" required
                       minlength="3" maxlength="20" pattern="[a-z0-9_]+">
            </label>
            <label>
                Email:
                <input type="email" name="email" required>
            </label>
            <label>
                Password:
                <input type="password" name="password" required minlength="8">
            </label>
            <label>
                Age:
                <input type="number" name="age" min="13" max="120">
            </label>
            <button type="submit">Sign Up</button>
        </form>
        """
        features = parse_html(html)
        assert 'form-validation' in features
        assert 'input-pattern' in features
        assert 'input-minlength' in features
        assert 'maxlength' in features


class TestNoFormAttributes:
    """Tests for forms without validation attributes."""

    def test_basic_form(self, parse_html):
        """Test basic form without validation."""
        html = """
        <form>
            <input type="text" name="name">
            <input type="submit" value="Submit">
        </form>
        """
        features = parse_html(html)
        assert 'form-validation' not in features
        assert 'input-pattern' not in features
        assert 'input-minlength' not in features


class TestFormSubmitAttributes:
    """Tests for form-submit-attributes feature (formaction, formmethod, etc.)."""

    def test_formaction_on_button(self, parse_and_check):
        """Test formaction attribute on button."""
        html = '<button type="submit" formaction="/alternative">Alt Submit</button>'
        assert parse_and_check(html, 'form-submit-attributes')

    def test_formaction_on_input_submit(self, parse_and_check):
        """Test formaction attribute on input submit."""
        html = '<input type="submit" formaction="/draft" value="Save Draft">'
        assert parse_and_check(html, 'form-submit-attributes')

    def test_formmethod_get(self, parse_and_check):
        """Test formmethod attribute with GET."""
        html = '<button type="submit" formmethod="get">Get Request</button>'
        assert parse_and_check(html, 'form-submit-attributes')

    def test_formmethod_post(self, parse_and_check):
        """Test formmethod attribute with POST."""
        html = '<button type="submit" formmethod="post">Post Request</button>'
        assert parse_and_check(html, 'form-submit-attributes')

    def test_formenctype(self, parse_and_check):
        """Test formenctype attribute."""
        html = '<button type="submit" formenctype="multipart/form-data">Upload</button>'
        assert parse_and_check(html, 'form-submit-attributes')

    def test_formtarget(self, parse_and_check):
        """Test formtarget attribute."""
        html = '<button type="submit" formtarget="_blank">Submit New Tab</button>'
        assert parse_and_check(html, 'form-submit-attributes')

    def test_combined_form_submit_attributes(self, parse_html):
        """Test multiple form submit attributes together."""
        html = """
        <form action="/default">
            <input type="text" name="data">
            <button type="submit">Default</button>
            <button type="submit" formaction="/alternative" formmethod="get">Get Alt</button>
            <button type="submit" formaction="/upload" formenctype="multipart/form-data">Upload</button>
            <button type="submit" formtarget="_blank">New Tab</button>
        </form>
        """
        features = parse_html(html)
        assert 'form-submit-attributes' in features


class TestReversedAttribute:
    """Tests for ol reversed attribute detection."""

    def test_reversed_on_ol(self, parse_and_check):
        """Test reversed attribute on ordered list."""
        html = """
        <ol reversed>
            <li>Third</li>
            <li>Second</li>
            <li>First</li>
        </ol>
        """
        assert parse_and_check(html, 'ol-reversed')

    def test_reversed_boolean(self, parse_and_check):
        """Test reversed as boolean attribute."""
        html = '<ol reversed="reversed"><li>Item</li></ol>'
        assert parse_and_check(html, 'ol-reversed')

    def test_reversed_with_start(self, parse_and_check):
        """Test reversed with start attribute."""
        html = '<ol reversed start="10"><li>Ten</li><li>Nine</li></ol>'
        assert parse_and_check(html, 'ol-reversed')

    def test_no_reversed(self, parse_html):
        """Test ol without reversed attribute."""
        html = '<ol><li>One</li><li>Two</li></ol>'
        features = parse_html(html)
        assert 'ol-reversed' not in features


class TestFormAttribute:
    """Tests for form attribute (associate element with form by ID)."""

    def test_form_attribute_on_input(self, parse_and_check):
        """Test form attribute on input outside form."""
        html = """
        <form id="myform"></form>
        <input type="text" form="myform" name="external">
        """
        assert parse_and_check(html, 'form-attribute')

    def test_form_attribute_on_button(self, parse_and_check):
        """Test form attribute on button outside form."""
        html = """
        <form id="theform"><input type="text"></form>
        <button type="submit" form="theform">External Submit</button>
        """
        assert parse_and_check(html, 'form-attribute')

    def test_form_attribute_on_select(self, parse_and_check):
        """Test form attribute on select outside form."""
        html = """
        <form id="f1"></form>
        <select form="f1" name="choice">
            <option>A</option>
            <option>B</option>
        </select>
        """
        assert parse_and_check(html, 'form-attribute')

    def test_form_attribute_on_textarea(self, parse_and_check):
        """Test form attribute on textarea outside form."""
        html = """
        <form id="mainform"></form>
        <textarea form="mainform" name="notes"></textarea>
        """
        assert parse_and_check(html, 'form-attribute')
