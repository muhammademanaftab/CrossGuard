"""Tests for other HTML5 input type detection.

Tests input types: color, range, number, file
"""

import pytest


class TestColorInput:
    """Tests for input[type="color"] detection."""

    def test_color_basic(self, parse_and_check):
        """Test basic color input detection."""
        html = '<input type="color">'
        assert parse_and_check(html, 'input-color')

    def test_color_with_value(self, parse_and_check):
        """Test color input with preset value."""
        html = '<input type="color" value="#ff0000">'
        assert parse_and_check(html, 'input-color')

    def test_color_with_name(self, parse_and_check):
        """Test color input with name attribute."""
        html = '<input type="color" name="bgcolor">'
        assert parse_and_check(html, 'input-color')

    def test_color_with_label(self, parse_and_check):
        """Test color input with label."""
        html = """
        <label for="bg-color">Background Color:</label>
        <input type="color" id="bg-color" name="bgColor" value="#ffffff">
        """
        assert parse_and_check(html, 'input-color')

    def test_color_multiple(self, parse_html):
        """Test multiple color inputs."""
        html = """
        <form>
            <label>Primary: <input type="color" name="primary" value="#0066cc"></label>
            <label>Secondary: <input type="color" name="secondary" value="#cc6600"></label>
            <label>Accent: <input type="color" name="accent" value="#00cc66"></label>
        </form>
        """
        features = parse_html(html)
        assert 'input-color' in features

    def test_color_theme_selector(self, parse_and_check):
        """Test color input in theme selector."""
        html = """
        <fieldset>
            <legend>Theme Colors</legend>
            <input type="color" name="header" value="#333333">
            <input type="color" name="footer" value="#666666">
        </fieldset>
        """
        assert parse_and_check(html, 'input-color')


class TestRangeInput:
    """Tests for input[type="range"] detection."""

    def test_range_basic(self, parse_and_check):
        """Test basic range input detection."""
        html = '<input type="range">'
        assert parse_and_check(html, 'input-range')

    def test_range_with_min_max(self, parse_and_check):
        """Test range input with min and max."""
        html = '<input type="range" min="0" max="100">'
        assert parse_and_check(html, 'input-range')

    def test_range_with_value(self, parse_and_check):
        """Test range input with preset value."""
        html = '<input type="range" min="0" max="100" value="50">'
        assert parse_and_check(html, 'input-range')

    def test_range_with_step(self, parse_and_check):
        """Test range input with step."""
        html = '<input type="range" min="0" max="100" step="10">'
        assert parse_and_check(html, 'input-range')

    def test_range_volume_slider(self, parse_and_check):
        """Test range input as volume slider."""
        html = """
        <label for="volume">Volume:</label>
        <input type="range" id="volume" name="volume"
               min="0" max="100" value="80">
        """
        assert parse_and_check(html, 'input-range')

    def test_range_with_list(self, parse_html):
        """Test range input with datalist for tick marks."""
        html = """
        <input type="range" min="0" max="100" list="tickmarks">
        <datalist id="tickmarks">
            <option value="0">
            <option value="25">
            <option value="50">
            <option value="75">
            <option value="100">
        </datalist>
        """
        features = parse_html(html)
        assert 'input-range' in features
        assert 'datalist' in features

    def test_range_with_output(self, parse_and_check):
        """Test range input with output element."""
        html = """
        <form oninput="result.value=parseInt(slider.value)">
            <input type="range" id="slider" name="slider" min="0" max="100" value="50">
            <output name="result" for="slider">50</output>
        </form>
        """
        assert parse_and_check(html, 'input-range')


class TestNumberInput:
    """Tests for input[type="number"] detection."""

    def test_number_basic(self, parse_and_check):
        """Test basic number input detection."""
        html = '<input type="number">'
        assert parse_and_check(html, 'input-number')

    def test_number_with_min_max(self, parse_and_check):
        """Test number input with min and max."""
        html = '<input type="number" min="1" max="10">'
        assert parse_and_check(html, 'input-number')

    def test_number_with_step(self, parse_and_check):
        """Test number input with step."""
        html = '<input type="number" step="0.01">'
        assert parse_and_check(html, 'input-number')

    def test_number_quantity(self, parse_and_check):
        """Test number input for quantity selection."""
        html = """
        <label for="qty">Quantity:</label>
        <input type="number" id="qty" name="quantity"
               min="1" max="99" value="1">
        """
        assert parse_and_check(html, 'input-number')

    def test_number_price(self, parse_and_check):
        """Test number input for price entry."""
        html = """
        <label for="price">Price ($):</label>
        <input type="number" id="price" name="price"
               min="0" step="0.01" placeholder="0.00">
        """
        assert parse_and_check(html, 'input-number')

    def test_number_with_placeholder(self, parse_and_check):
        """Test number input with placeholder."""
        html = '<input type="number" placeholder="Enter a number">'
        assert parse_and_check(html, 'input-number')

    def test_number_required(self, parse_and_check):
        """Test required number input."""
        html = '<input type="number" required>'
        assert parse_and_check(html, 'input-number')


class TestFileInput:
    """Tests for input[type="file"] detection."""

    def test_file_basic(self, parse_and_check):
        """Test basic file input detection."""
        html = '<input type="file">'
        assert parse_and_check(html, 'input-file-accept')

    def test_file_with_accept(self, parse_and_check):
        """Test file input with accept attribute."""
        html = '<input type="file" accept="image/*">'
        assert parse_and_check(html, 'input-file-accept')

    def test_file_accept_specific(self, parse_and_check):
        """Test file input accepting specific types."""
        html = '<input type="file" accept=".pdf,.doc,.docx">'
        assert parse_and_check(html, 'input-file-accept')

    def test_file_multiple(self, parse_html):
        """Test file input with multiple attribute."""
        html = '<input type="file" multiple>'
        features = parse_html(html)
        assert 'input-file-accept' in features
        assert 'input-file-multiple' in features

    def test_file_image_upload(self, parse_html):
        """Test file input for image upload."""
        html = """
        <label for="photo">Upload Photo:</label>
        <input type="file" id="photo" name="photo"
               accept="image/png, image/jpeg, image/gif">
        """
        features = parse_html(html)
        assert 'input-file-accept' in features

    def test_file_with_capture(self, parse_html):
        """Test file input with capture attribute (camera)."""
        html = '<input type="file" accept="image/*" capture="environment">'
        features = parse_html(html)
        assert 'input-file-accept' in features
        assert 'html-media-capture' in features

    def test_file_multiple_images(self, parse_html):
        """Test file input for multiple images."""
        html = """
        <input type="file" accept="image/*" multiple>
        """
        features = parse_html(html)
        assert 'input-file-accept' in features
        assert 'input-file-multiple' in features

    def test_file_in_form(self, parse_and_check):
        """Test file input in form with enctype."""
        html = """
        <form enctype="multipart/form-data">
            <input type="file" name="document" accept=".pdf">
            <button type="submit">Upload</button>
        </form>
        """
        assert parse_and_check(html, 'input-file-accept')


class TestCombinedOtherInputs:
    """Tests for combinations of input types."""

    def test_settings_form(self, parse_html):
        """Test settings form with multiple input types."""
        html = """
        <form id="settings">
            <label>Theme Color: <input type="color" name="theme" value="#336699"></label>
            <label>Volume: <input type="range" name="volume" min="0" max="100" value="75"></label>
            <label>Font Size: <input type="number" name="fontSize" min="8" max="72" value="14"></label>
        </form>
        """
        features = parse_html(html)
        assert 'input-color' in features
        assert 'input-range' in features
        assert 'input-number' in features

    def test_product_form(self, parse_html):
        """Test product form with number and file inputs."""
        html = """
        <form id="product">
            <input type="text" name="name" placeholder="Product Name">
            <input type="number" name="price" min="0" step="0.01">
            <input type="number" name="quantity" min="0">
            <input type="file" name="images" accept="image/*" multiple>
        </form>
        """
        features = parse_html(html)
        assert 'input-number' in features
        assert 'input-file-accept' in features
        assert 'input-file-multiple' in features


class TestCaseInsensitivity:
    """Tests for case insensitivity of type values."""

    def test_color_uppercase(self, parse_and_check):
        """Test COLOR type in uppercase."""
        html = '<input type="COLOR">'
        assert parse_and_check(html, 'input-color')

    def test_range_mixed_case(self, parse_and_check):
        """Test Range type in mixed case."""
        html = '<input type="Range">'
        assert parse_and_check(html, 'input-range')

    def test_number_uppercase(self, parse_and_check):
        """Test NUMBER type in uppercase."""
        html = '<input type="NUMBER">'
        assert parse_and_check(html, 'input-number')

    def test_file_mixed_case(self, parse_and_check):
        """Test File type in mixed case."""
        html = '<input type="File">'
        assert parse_and_check(html, 'input-file-accept')


class TestNoOtherInputFeatures:
    """Tests for inputs that should NOT match."""

    def test_text_input(self, parse_html):
        """Test that plain text input doesn't match special types."""
        html = '<input type="text">'
        features = parse_html(html)
        assert 'input-color' not in features
        assert 'input-range' not in features
        assert 'input-number' not in features
        assert 'input-file-accept' not in features

    def test_checkbox_input(self, parse_html):
        """Test checkbox input doesn't match."""
        html = '<input type="checkbox">'
        features = parse_html(html)
        assert 'input-color' not in features
        assert 'input-range' not in features

    def test_radio_input(self, parse_html):
        """Test radio input doesn't match."""
        html = '<input type="radio">'
        features = parse_html(html)
        assert 'input-number' not in features
        assert 'input-file-accept' not in features
