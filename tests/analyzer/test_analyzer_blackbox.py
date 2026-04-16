"""Black-box tests for the analyzer public API -- scoring, compatibility, version ranges.

Tests the CompatibilityAnalyzer, CompatibilityScorer, and version_ranges modules
through their public interfaces with real and mocked data.
"""

import pytest
from unittest.mock import MagicMock

from src.analyzer.compatibility import CompatibilityAnalyzer
from src.analyzer.version_ranges import (
    get_version_ranges,
    _get_status_text,
)


# ============================================================================
# SECTION 1: analyze() -- Full Report Generation
# ============================================================================

class TestAnalyze:
    """Tests for analyze(features, target_browsers)."""

    @pytest.mark.blackbox
    def test_well_supported_high_score(self, analyzer, modern_browsers, well_supported_features):
        report = analyzer.analyze(well_supported_features, modern_browsers)
        assert report['overall_score'] >= 80.0

    @pytest.mark.blackbox
    def test_adding_ie_lowers_score(self, analyzer, well_supported_features):
        modern = {'chrome': '120', 'firefox': '121'}
        with_ie = {'chrome': '120', 'firefox': '121', 'ie': '11'}
        assert analyzer.analyze(well_supported_features, with_ie)['overall_score'] < \
               analyzer.analyze(well_supported_features, modern)['overall_score']


# ============================================================================
# SECTION 3: Severity and Grading
# ============================================================================

class TestAnalyzerGrade:
    """Tests for the analyzer's 13-level grading scale (A+ to F)."""

    @pytest.mark.blackbox
    @pytest.mark.parametrize("score,expected", [
        (100, 'A+'),
    ])
    def test_grade_boundary(self, analyzer, score, expected):
        assert analyzer._score_to_grade(score) == expected


# ============================================================================
# SECTION 7: Mocked Database Unit Tests
# ============================================================================

class TestAnalyzerWithMockedDB:

    def _make_analyzer_with_mock(self, support_map):
        mock_db = MagicMock()
        mock_db.check_support.side_effect = lambda f, b, v: support_map.get((f, b), 'u')
        mock_db.get_feature_info.return_value = None
        mock_db.get_feature.return_value = None
        a = CompatibilityAnalyzer.__new__(CompatibilityAnalyzer)
        a.database = mock_db
        return a

    @pytest.mark.blackbox
    def test_mixed_support_correct_score(self):
        a = self._make_analyzer_with_mock({('flexbox', 'chrome'): 'y', ('flexbox', 'ie'): 'n'})
        report = a.analyze({'flexbox'}, {'chrome': '120', 'ie': '11'})
        assert report['browser_scores']['chrome']['score'] == 100.0
        assert report['browser_scores']['ie']['score'] == 0.0
        assert report['overall_score'] == 50.0


# ============================================================================
# SECTION 15: Version Ranges
# ============================================================================

class TestGetVersionRanges:

    @pytest.mark.blackbox
    def test_flexbox_chrome_ranges(self):
        ranges = get_version_ranges('flexbox', 'chrome')
        assert len(ranges) > 0
        for r in ranges:
            assert set(r.keys()) == {'start', 'end', 'status', 'status_text'}
        assert ranges[-1]['status'] == 'y'


# ============================================================================
# SECTION 16: Status Text, Format, Summary, Browser Names
# ============================================================================

class TestStatusTextAndFormat:

    @pytest.mark.blackbox
    def test_known_status_code(self):
        assert _get_status_text('y') == 'Supported'
