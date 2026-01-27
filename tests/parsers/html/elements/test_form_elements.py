"""Tests for HTML5 form element detection.

Tests elements: datalist, meter, progress
"""

import pytest


class TestDatalistElement:
    """Tests for <datalist> element detection."""

    def test_datalist_basic(self, parse_and_check):
        """Test basic datalist element detection."""
        html = """
        <datalist id="browsers">
            <option value="Chrome">
            <option value="Firefox">
            <option value="Safari">
        </datalist>
        """
        assert parse_and_check(html, 'datalist')

    def test_datalist_with_input(self, parse_and_check):
        """Test datalist element linked to input."""
        html = """
        <input list="browsers" name="browser">
        <datalist id="browsers">
            <option value="Chrome">
            <option value="Firefox">
            <option value="Safari">
            <option value="Edge">
        </datalist>
        """
        assert parse_and_check(html, 'datalist')

    def test_datalist_with_labels(self, parse_and_check):
        """Test datalist with option labels."""
        html = """
        <datalist id="colors">
            <option value="#ff0000" label="Red">
            <option value="#00ff00" label="Green">
            <option value="#0000ff" label="Blue">
        </datalist>
        """
        assert parse_and_check(html, 'datalist')

    def test_datalist_with_fallback(self, parse_and_check):
        """Test datalist with fallback content."""
        html = """
        <datalist id="browsers">
            <label>Choose or type: <input list="browsers"></label>
            <select name="browser">
                <option value="Chrome">Chrome</option>
                <option value="Firefox">Firefox</option>
            </select>
        </datalist>
        """
        assert parse_and_check(html, 'datalist')

    def test_datalist_empty(self, parse_and_check):
        """Test empty datalist element."""
        html = '<datalist id="empty"></datalist>'
        assert parse_and_check(html, 'datalist')


class TestMeterElement:
    """Tests for <meter> element detection."""

    def test_meter_basic(self, parse_and_check):
        """Test basic meter element detection."""
        html = '<meter value="0.6">60%</meter>'
        assert parse_and_check(html, 'meter')

    def test_meter_with_min_max(self, parse_and_check):
        """Test meter element with min and max."""
        html = '<meter min="0" max="100" value="75">75%</meter>'
        assert parse_and_check(html, 'meter')

    def test_meter_with_low_high_optimum(self, parse_and_check):
        """Test meter element with low, high, and optimum."""
        html = '''
        <meter
            min="0"
            max="100"
            low="25"
            high="75"
            optimum="50"
            value="80">
            80%
        </meter>
        '''
        assert parse_and_check(html, 'meter')

    def test_meter_disk_usage(self, parse_and_check):
        """Test meter element for disk usage display."""
        html = '''
        <p>Disk Usage:
            <meter min="0" max="1" value="0.6" low="0.7" high="0.9">
                60% used
            </meter>
        </p>
        '''
        assert parse_and_check(html, 'meter')

    def test_meter_rating(self, parse_and_check):
        """Test meter element for rating display."""
        html = '''
        <p>Rating: <meter min="0" max="5" value="4.5">4.5 out of 5</meter></p>
        '''
        assert parse_and_check(html, 'meter')

    def test_multiple_meters(self, parse_html):
        """Test multiple meter elements."""
        html = """
        <div>
            <p>CPU: <meter value="0.3">30%</meter></p>
            <p>Memory: <meter value="0.7">70%</meter></p>
            <p>Disk: <meter value="0.5">50%</meter></p>
        </div>
        """
        features = parse_html(html)
        assert 'meter' in features


class TestProgressElement:
    """Tests for <progress> element detection."""

    def test_progress_basic(self, parse_and_check):
        """Test basic progress element detection."""
        html = '<progress value="70" max="100">70%</progress>'
        assert parse_and_check(html, 'progress')

    def test_progress_indeterminate(self, parse_and_check):
        """Test indeterminate progress element (no value)."""
        html = '<progress>Loading...</progress>'
        assert parse_and_check(html, 'progress')

    def test_progress_with_max(self, parse_and_check):
        """Test progress element with max attribute."""
        html = '<progress value="30" max="100">30%</progress>'
        assert parse_and_check(html, 'progress')

    def test_progress_download(self, parse_and_check):
        """Test progress element for download progress."""
        html = '''
        <label for="download">Download progress:</label>
        <progress id="download" value="50" max="100">50%</progress>
        '''
        assert parse_and_check(html, 'progress')

    def test_progress_file_upload(self, parse_and_check):
        """Test progress element for file upload."""
        html = """
        <form>
            <input type="file" id="file">
            <progress id="upload-progress" value="0" max="100">0%</progress>
        </form>
        """
        assert parse_and_check(html, 'progress')

    def test_progress_with_id(self, parse_and_check):
        """Test progress element with id for JavaScript control."""
        html = '<progress id="task-progress" max="10" value="3">3 of 10</progress>'
        assert parse_and_check(html, 'progress')

    def test_multiple_progress_bars(self, parse_html):
        """Test multiple progress elements."""
        html = """
        <div>
            <p>Task 1: <progress value="100" max="100">Complete</progress></p>
            <p>Task 2: <progress value="50" max="100">50%</progress></p>
            <p>Task 3: <progress value="0" max="100">Not started</progress></p>
        </div>
        """
        features = parse_html(html)
        assert 'progress' in features


class TestCombinedFormElements:
    """Tests for combinations of form elements."""

    def test_all_form_elements(self, parse_html):
        """Test page with all special form elements."""
        html = """
        <form>
            <label>Browser:
                <input list="browsers">
                <datalist id="browsers">
                    <option value="Chrome">
                    <option value="Firefox">
                </datalist>
            </label>

            <p>Battery: <meter value="0.8">80%</meter></p>
            <p>Download: <progress value="50" max="100">50%</progress></p>
        </form>
        """
        features = parse_html(html)
        assert 'datalist' in features
        assert 'meter' in features
        assert 'progress' in features

    def test_form_with_validation_and_elements(self, parse_html):
        """Test form with validation attributes and form elements."""
        html = """
        <form>
            <input type="text" list="names" required>
            <datalist id="names">
                <option value="John">
                <option value="Jane">
            </datalist>

            <meter id="strength" min="0" max="100" value="60">
                Password strength: 60%
            </meter>

            <progress id="submit-progress" max="100">
                Submitting...
            </progress>

            <button type="submit">Submit</button>
        </form>
        """
        features = parse_html(html)
        assert 'datalist' in features
        assert 'meter' in features
        assert 'progress' in features


class TestMeterVsProgress:
    """Tests distinguishing meter from progress."""

    def test_meter_for_static_measurement(self, parse_html):
        """Test meter for static measurement (not a task)."""
        html = '<meter min="0" max="100" value="25">25% fuel</meter>'
        features = parse_html(html)
        assert 'meter' in features
        assert 'progress' not in features

    def test_progress_for_task(self, parse_html):
        """Test progress for task completion."""
        html = '<progress value="25" max="100">25% complete</progress>'
        features = parse_html(html)
        assert 'progress' in features
        assert 'meter' not in features


class TestNoFormElements:
    """Tests for HTML without special form elements."""

    def test_no_special_form_elements(self, parse_html):
        """Test HTML with basic form but no special elements."""
        html = """
        <form>
            <input type="text" name="name">
            <select name="option">
                <option value="1">One</option>
                <option value="2">Two</option>
            </select>
            <button type="submit">Submit</button>
        </form>
        """
        features = parse_html(html)
        assert 'datalist' not in features
        assert 'meter' not in features
        assert 'progress' not in features
