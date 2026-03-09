"""Consolidated HTML input type detection tests.

Covers: datetime inputs (date, datetime-local, time, month, week),
text inputs (email, tel, url, search), and other inputs (color, range, number).
"""

import pytest


# ---------------------------------------------------------------------------
# Datetime inputs -> input-datetime
# ---------------------------------------------------------------------------

class TestDatetimeInputs:

    @pytest.mark.parametrize("input_type", [
        "date", "datetime-local", "time", "month", "week",
    ])
    @pytest.mark.unit
    def test_datetime_input(self, parse_features, input_type):
        html = f'<input type="{input_type}">'
        assert 'input-datetime' in parse_features(html)

    @pytest.mark.parametrize("input_type", [
        "Date", "DATE", "DaTe",
        "Datetime-Local", "DATETIME-LOCAL",
        "Time", "TIME",
        "Month", "MONTH",
        "Week", "WEEK",
    ])
    @pytest.mark.unit
    def test_datetime_case_insensitive(self, parse_features, input_type):
        html = f'<input type="{input_type}">'
        assert 'input-datetime' in parse_features(html)

    @pytest.mark.unit
    def test_datetime_in_form(self, parse_features):
        html = """
        <form>
            <input type="date" name="start">
            <input type="time" name="time">
            <input type="datetime-local" name="full">
        </form>
        """
        assert 'input-datetime' in parse_features(html)


# ---------------------------------------------------------------------------
# Text inputs -> input-email-tel-url / input-search
# ---------------------------------------------------------------------------

class TestTextInputs:

    @pytest.mark.parametrize("input_type", ["email", "tel", "url"])
    @pytest.mark.unit
    def test_email_tel_url(self, parse_features, input_type):
        html = f'<input type="{input_type}">'
        assert 'input-email-tel-url' in parse_features(html)

    @pytest.mark.parametrize("input_type", [
        "Email", "EMAIL", "Tel", "TEL", "Url", "URL",
    ])
    @pytest.mark.unit
    def test_email_tel_url_case_insensitive(self, parse_features, input_type):
        html = f'<input type="{input_type}">'
        assert 'input-email-tel-url' in parse_features(html)

    @pytest.mark.unit
    def test_search_input(self, parse_features):
        html = '<input type="search">'
        assert 'input-search' in parse_features(html)

    @pytest.mark.parametrize("input_type", ["Search", "SEARCH"])
    @pytest.mark.unit
    def test_search_case_insensitive(self, parse_features, input_type):
        html = f'<input type="{input_type}">'
        assert 'input-search' in parse_features(html)


# ---------------------------------------------------------------------------
# Other inputs -> input-color / input-range / input-number
# ---------------------------------------------------------------------------

class TestOtherInputs:

    @pytest.mark.parametrize("input_type, feature_id", [
        ("color", "input-color"),
        ("range", "input-range"),
        ("number", "input-number"),
    ])
    @pytest.mark.unit
    def test_other_input(self, parse_features, input_type, feature_id):
        html = f'<input type="{input_type}">'
        assert feature_id in parse_features(html)

    @pytest.mark.parametrize("input_type, feature_id", [
        ("Color", "input-color"), ("COLOR", "input-color"),
        ("Range", "input-range"), ("RANGE", "input-range"),
        ("Number", "input-number"), ("NUMBER", "input-number"),
    ])
    @pytest.mark.unit
    def test_other_input_case_insensitive(self, parse_features, input_type, feature_id):
        html = f'<input type="{input_type}">'
        assert feature_id in parse_features(html)


# ---------------------------------------------------------------------------
# File input type -> input-file-accept
# ---------------------------------------------------------------------------

class TestFileInput:

    @pytest.mark.parametrize("html", [
        '<input type="file" accept="image/*">',
        '<input type="file" accept=".pdf,.doc,.docx">',
        '<input type="file" accept="audio/*">',
    ])
    @pytest.mark.unit
    def test_file_accept(self, parse_features, html):
        assert 'input-file-accept' in parse_features(html)


# ---------------------------------------------------------------------------
# Combined / negative tests
# ---------------------------------------------------------------------------

class TestCombinedInputTypes:

    @pytest.mark.unit
    def test_all_input_types_in_form(self, parse_features):
        html = """
        <form>
            <input type="date">
            <input type="email">
            <input type="search">
            <input type="color">
            <input type="range">
            <input type="number">
        </form>
        """
        features = parse_features(html)
        assert 'input-datetime' in features
        assert 'input-email-tel-url' in features
        assert 'input-search' in features
        assert 'input-color' in features
        assert 'input-range' in features
        assert 'input-number' in features

    @pytest.mark.unit
    def test_standard_inputs_no_features(self, parse_features):
        """text, password, hidden, checkbox, radio -> no special feature ID."""
        html = """
        <input type="text">
        <input type="password">
        <input type="hidden">
        <input type="checkbox">
        <input type="radio">
        """
        features = parse_features(html)
        assert 'input-datetime' not in features
        assert 'input-email-tel-url' not in features
        assert 'input-search' not in features
        assert 'input-color' not in features
        assert 'input-range' not in features
        assert 'input-number' not in features
