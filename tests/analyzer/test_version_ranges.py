"""Tests for version_ranges module — range generation, status text, formatting.

Validates the logic that groups consecutive browser versions with the same
support status into human-readable ranges (e.g., "37-143: Supported").
"""

import pytest

from src.analyzer.version_ranges import (
    get_version_ranges,
    _get_status_text,
    format_ranges_for_display,
    get_support_summary,
    get_all_browser_ranges,
    BROWSER_NAMES,
)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: get_version_ranges()
# ═══════════════════════════════════════════════════════════════════════════

class TestGetVersionRanges:
    """Tests for get_version_ranges(feature_id, browser)."""

    def test_flexbox_chrome_has_ranges(self):
        """Flexbox in Chrome returns non-empty range list."""
        ranges = get_version_ranges('flexbox', 'chrome')
        assert len(ranges) > 0

    def test_range_dict_has_required_keys(self):
        """Each range has start, end, status, status_text keys."""
        ranges = get_version_ranges('flexbox', 'chrome')
        for r in ranges:
            assert set(r.keys()) == {'start', 'end', 'status', 'status_text'}

    def test_no_adjacent_ranges_with_same_status(self):
        """Adjacent ranges must have different statuses (proper grouping)."""
        ranges = get_version_ranges('flexbox', 'chrome')
        for i in range(len(ranges) - 1):
            assert ranges[i]['status'] != ranges[i + 1]['status'], \
                f"Adjacent ranges {i} and {i+1} both have status '{ranges[i]['status']}'"

    def test_unknown_feature_returns_empty(self):
        """Unknown feature returns empty list."""
        assert get_version_ranges('totally-fake-feature-xyz', 'chrome') == []

    def test_unknown_browser_returns_empty(self):
        """Unknown browser returns empty list."""
        assert get_version_ranges('flexbox', 'netscape') == []

    def test_flexbox_eventually_supported_in_chrome(self):
        """Flexbox ends as 'y' (supported) in Chrome."""
        ranges = get_version_ranges('flexbox', 'chrome')
        assert ranges[-1]['status'] == 'y'

    def test_css_grid_has_ranges(self):
        """CSS Grid has non-empty ranges in Chrome."""
        assert len(get_version_ranges('css-grid', 'chrome')) > 0

    def test_arrow_functions_never_supported_in_ie(self):
        """Arrow functions in IE: no 'y' status in any range."""
        ranges = get_version_ranges('arrow-functions', 'ie')
        if ranges:
            assert all(r['status'] != 'y' for r in ranges)

    def test_start_end_are_strings(self):
        """Start and end are version strings."""
        ranges = get_version_ranges('flexbox', 'chrome')
        for r in ranges:
            assert isinstance(r['start'], str)
            assert isinstance(r['end'], str)

    def test_status_text_matches_status(self):
        """status_text is consistent with status code."""
        ranges = get_version_ranges('flexbox', 'chrome')
        for r in ranges:
            assert r['status_text'] == _get_status_text(r['status'])


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: _get_status_text()
# ═══════════════════════════════════════════════════════════════════════════

class TestStatusText:
    """Tests for _get_status_text() — status code to human text."""

    @pytest.mark.parametrize("code,expected", [
        ('y', 'Supported'),
        ('n', 'Not Supported'),
        ('a', 'Supported'),
        ('x', 'Requires Prefix'),
        ('p', 'Partial Support'),
        ('u', 'Unknown'),
        ('d', 'Disabled by Default'),
    ])
    def test_known_status_codes(self, code, expected):
        """Known status codes map to human-readable text."""
        assert _get_status_text(code) == expected

    def test_unknown_code_returns_itself(self):
        """Unknown status code returns the code itself (fallback)."""
        assert _get_status_text('z') == 'z'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: format_ranges_for_display()
# ═══════════════════════════════════════════════════════════════════════════

class TestFormatRanges:
    """Tests for format_ranges_for_display()."""

    def test_flexbox_chrome_format(self):
        """Returns non-empty string with 'Supported' text, pipe-separated ranges with colons."""
        result = format_ranges_for_display('flexbox', 'chrome')
        assert isinstance(result, str)
        assert 'Supported' in result
        parts = result.split(' | ')
        assert len(parts) >= 2
        for part in parts:
            assert ':' in part

    @pytest.mark.parametrize("feature,browser", [
        ('totally-fake-xyz', 'chrome'),
        ('flexbox', 'netscape'),
    ])
    def test_unknown_returns_no_data(self, feature, browser):
        assert format_ranges_for_display(feature, browser) == "No data available"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: get_support_summary()
# ═══════════════════════════════════════════════════════════════════════════

class TestSupportSummary:
    """Tests for get_support_summary()."""

    def test_flexbox_summary_structure(self):
        """Returns dict with major browsers, correct keys, and current status."""
        summary = get_support_summary('flexbox')
        assert isinstance(summary, dict)
        assert 'chrome' in summary
        assert 'firefox' in summary
        for browser, data in summary.items():
            assert set(data.keys()) == {'current_status', 'current_status_text', 'supported_since', 'ranges'}
            # current_status matches last range
            assert data['current_status'] == data['ranges'][-1]['status']
        assert summary['chrome']['current_status'] == 'y'
        assert summary['chrome']['supported_since'] is not None

    def test_unknown_feature_returns_empty(self):
        assert get_support_summary('totally-fake-feature-xyz') == {}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: get_all_browser_ranges()
# ═══════════════════════════════════════════════════════════════════════════

class TestAllBrowserRanges:
    """Tests for get_all_browser_ranges()."""

    def test_flexbox_returns_multiple_browsers_with_ranges(self):
        result = get_all_browser_ranges('flexbox')
        assert len(result) > 3
        assert 'chrome' in result
        for browser, ranges in result.items():
            assert isinstance(ranges, list)
            assert len(ranges) > 0

    def test_unknown_feature_returns_empty(self):
        assert get_all_browser_ranges('totally-fake-feature-xyz') == {}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: BROWSER_NAMES constant
# ═══════════════════════════════════════════════════════════════════════════

class TestBrowserNames:
    """Tests for the BROWSER_NAMES display mapping."""

    @pytest.mark.parametrize("code,name", [
        ('chrome', 'Chrome'),
        ('firefox', 'Firefox'),
        ('safari', 'Safari'),
        ('edge', 'Edge'),
        ('ie', 'Internet Explorer'),
        ('ios_saf', 'Safari on iOS'),
        ('samsung', 'Samsung Internet'),
    ])
    def test_browser_display_names(self, code, name):
        """Browser codes map to human-readable display names."""
        assert BROWSER_NAMES[code] == name
