"""Tests for HTML5 datetime input type detection.

Tests input types: date, datetime-local, time, month, week
All map to feature ID: input-datetime
"""

import pytest


class TestDateInput:
    """Tests for input[type="date"] detection."""

    def test_date_basic(self, parse_and_check):
        """Test basic date input detection."""
        html = '<input type="date">'
        assert parse_and_check(html, 'input-datetime')

    def test_date_with_name(self, parse_and_check):
        """Test date input with name attribute."""
        html = '<input type="date" name="birthdate">'
        assert parse_and_check(html, 'input-datetime')

    def test_date_with_value(self, parse_and_check):
        """Test date input with preset value."""
        html = '<input type="date" value="2024-01-15">'
        assert parse_and_check(html, 'input-datetime')

    def test_date_with_min_max(self, parse_and_check):
        """Test date input with min and max constraints."""
        html = '<input type="date" min="2024-01-01" max="2024-12-31">'
        assert parse_and_check(html, 'input-datetime')

    def test_date_required(self, parse_and_check):
        """Test required date input."""
        html = '<input type="date" required>'
        assert parse_and_check(html, 'input-datetime')

    def test_date_in_form(self, parse_and_check):
        """Test date input within a form."""
        html = """
        <form>
            <label for="event-date">Event Date:</label>
            <input type="date" id="event-date" name="eventDate">
        </form>
        """
        assert parse_and_check(html, 'input-datetime')


class TestDatetimeLocalInput:
    """Tests for input[type="datetime-local"] detection."""

    def test_datetime_local_basic(self, parse_and_check):
        """Test basic datetime-local input detection."""
        html = '<input type="datetime-local">'
        assert parse_and_check(html, 'input-datetime')

    def test_datetime_local_with_value(self, parse_and_check):
        """Test datetime-local input with preset value."""
        html = '<input type="datetime-local" value="2024-01-15T14:30">'
        assert parse_and_check(html, 'input-datetime')

    def test_datetime_local_with_min_max(self, parse_and_check):
        """Test datetime-local input with constraints."""
        html = '''
        <input type="datetime-local"
               min="2024-01-01T00:00"
               max="2024-12-31T23:59">
        '''
        assert parse_and_check(html, 'input-datetime')

    def test_datetime_local_appointment(self, parse_and_check):
        """Test datetime-local for appointment scheduling."""
        html = """
        <form>
            <label>Appointment:
                <input type="datetime-local" name="appointment" required>
            </label>
        </form>
        """
        assert parse_and_check(html, 'input-datetime')


class TestTimeInput:
    """Tests for input[type="time"] detection."""

    def test_time_basic(self, parse_and_check):
        """Test basic time input detection."""
        html = '<input type="time">'
        assert parse_and_check(html, 'input-datetime')

    def test_time_with_value(self, parse_and_check):
        """Test time input with preset value."""
        html = '<input type="time" value="14:30">'
        assert parse_and_check(html, 'input-datetime')

    def test_time_with_step(self, parse_and_check):
        """Test time input with step (seconds)."""
        html = '<input type="time" step="1">'
        assert parse_and_check(html, 'input-datetime')

    def test_time_with_min_max(self, parse_and_check):
        """Test time input with time range."""
        html = '<input type="time" min="09:00" max="17:00">'
        assert parse_and_check(html, 'input-datetime')

    def test_time_business_hours(self, parse_and_check):
        """Test time input for business hours."""
        html = """
        <form>
            <label>Opening time: <input type="time" name="openTime" min="06:00" max="12:00"></label>
            <label>Closing time: <input type="time" name="closeTime" min="12:00" max="22:00"></label>
        </form>
        """
        assert parse_and_check(html, 'input-datetime')


class TestMonthInput:
    """Tests for input[type="month"] detection."""

    def test_month_basic(self, parse_and_check):
        """Test basic month input detection."""
        html = '<input type="month">'
        assert parse_and_check(html, 'input-datetime')

    def test_month_with_value(self, parse_and_check):
        """Test month input with preset value."""
        html = '<input type="month" value="2024-01">'
        assert parse_and_check(html, 'input-datetime')

    def test_month_with_min_max(self, parse_and_check):
        """Test month input with constraints."""
        html = '<input type="month" min="2024-01" max="2025-12">'
        assert parse_and_check(html, 'input-datetime')

    def test_month_credit_card_expiry(self, parse_and_check):
        """Test month input for credit card expiry."""
        html = """
        <form>
            <label>Card Expiry:
                <input type="month" name="cardExpiry" min="2024-01">
            </label>
        </form>
        """
        assert parse_and_check(html, 'input-datetime')


class TestWeekInput:
    """Tests for input[type="week"] detection."""

    def test_week_basic(self, parse_and_check):
        """Test basic week input detection."""
        html = '<input type="week">'
        assert parse_and_check(html, 'input-datetime')

    def test_week_with_value(self, parse_and_check):
        """Test week input with preset value."""
        html = '<input type="week" value="2024-W03">'
        assert parse_and_check(html, 'input-datetime')

    def test_week_with_min_max(self, parse_and_check):
        """Test week input with constraints."""
        html = '<input type="week" min="2024-W01" max="2024-W52">'
        assert parse_and_check(html, 'input-datetime')

    def test_week_schedule(self, parse_and_check):
        """Test week input for weekly scheduling."""
        html = """
        <form>
            <label>Select Week:
                <input type="week" name="scheduleWeek" required>
            </label>
        </form>
        """
        assert parse_and_check(html, 'input-datetime')


class TestMultipleDatetimeInputs:
    """Tests for multiple datetime inputs in same document."""

    def test_all_datetime_types(self, parse_html):
        """Test all datetime input types together."""
        html = """
        <form>
            <input type="date" name="date">
            <input type="datetime-local" name="datetime">
            <input type="time" name="time">
            <input type="month" name="month">
            <input type="week" name="week">
        </form>
        """
        features = parse_html(html)
        assert 'input-datetime' in features

    def test_event_scheduling_form(self, parse_html):
        """Test realistic event scheduling form."""
        html = """
        <form id="event-form">
            <h2>Create Event</h2>

            <label for="event-date">Date:</label>
            <input type="date" id="event-date" name="date" required>

            <label for="start-time">Start Time:</label>
            <input type="time" id="start-time" name="startTime" required>

            <label for="end-time">End Time:</label>
            <input type="time" id="end-time" name="endTime" required>

            <button type="submit">Create Event</button>
        </form>
        """
        features = parse_html(html)
        assert 'input-datetime' in features


class TestCaseInsensitivity:
    """Tests for case insensitivity of type attribute."""

    def test_date_uppercase(self, parse_and_check):
        """Test DATE type in uppercase."""
        html = '<input type="DATE">'
        assert parse_and_check(html, 'input-datetime')

    def test_time_mixed_case(self, parse_and_check):
        """Test Time type in mixed case."""
        html = '<input type="Time">'
        assert parse_and_check(html, 'input-datetime')

    def test_datetime_local_uppercase(self, parse_and_check):
        """Test DATETIME-LOCAL in uppercase."""
        html = '<input type="DATETIME-LOCAL">'
        assert parse_and_check(html, 'input-datetime')


class TestNoDatetimeInputs:
    """Tests for inputs that should NOT match datetime."""

    def test_text_input(self, parse_html):
        """Test that text input doesn't match datetime."""
        html = '<input type="text">'
        features = parse_html(html)
        assert 'input-datetime' not in features

    def test_no_type_input(self, parse_html):
        """Test input without type attribute."""
        html = '<input name="something">'
        features = parse_html(html)
        assert 'input-datetime' not in features

    def test_hidden_input(self, parse_html):
        """Test hidden input."""
        html = '<input type="hidden" value="2024-01-15">'
        features = parse_html(html)
        assert 'input-datetime' not in features
