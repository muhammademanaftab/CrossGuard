"""Black-box tests for the analyzer public API -- scoring, compatibility, version ranges.

Tests the CompatibilityAnalyzer, CompatibilityScorer, and version_ranges modules
through their public interfaces with real and mocked data.
"""

import pytest
from unittest.mock import MagicMock

from src.analyzer.compatibility import (
    CompatibilityAnalyzer,
    CompatibilityIssue,
    CompatibilityReport,
    Severity,
)
from src.analyzer.scorer import CompatibilityScorer, WeightedScore
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
    def test_empty_features_score_100(self, analyzer, modern_browsers):
        report = analyzer.analyze(set(), modern_browsers)
        assert report.overall_score == 100.0
        assert report.features_analyzed == 0

    @pytest.mark.blackbox
    def test_well_supported_high_score(self, analyzer, modern_browsers, well_supported_features):
        report = analyzer.analyze(well_supported_features, modern_browsers)
        assert report.overall_score >= 80.0

    @pytest.mark.blackbox
    def test_adding_ie_lowers_score(self, analyzer, well_supported_features):
        modern = {'chrome': '120', 'firefox': '121'}
        with_ie = {'chrome': '120', 'firefox': '121', 'ie': '11'}
        assert analyzer.analyze(well_supported_features, with_ie).overall_score < \
               analyzer.analyze(well_supported_features, modern).overall_score


# ============================================================================
# SECTION 3: Severity and Grading
# ============================================================================

class TestSeverity:
    """Tests for _calculate_severity()."""

    @pytest.mark.blackbox
    @pytest.mark.parametrize("status,total,expected", [
        ({'chrome': 'n', 'firefox': 'n', 'safari': 'n'}, 3, Severity.CRITICAL),
        ({'chrome': 'y', 'firefox': 'y', 'safari': 'y'}, 3, Severity.LOW),
    ])
    def test_severity_classification(self, analyzer, status, total, expected):
        assert analyzer._calculate_severity(status, total) == expected


class TestAnalyzerGrade:
    """Tests for the analyzer's 13-level grading scale (A+ to F)."""

    @pytest.mark.blackbox
    @pytest.mark.parametrize("score,expected", [
        (100, 'A+'), (0, 'F'),
    ])
    def test_grade_boundary(self, analyzer, score, expected):
        assert analyzer._score_to_grade(score) == expected


# ============================================================================
# SECTION 4: get_detailed_issues() and analyze_feature()
# ============================================================================

class TestDetailedIssuesAndAnalyzeFeature:

    @pytest.mark.blackbox
    def test_filters_and_sorts_issues(self, analyzer, legacy_browsers, mixed_support_features):
        """Excludes LOW/INFO, sorted CRITICAL first."""
        issues = analyzer.get_detailed_issues(mixed_support_features, legacy_browsers)
        for issue in issues:
            assert issue.severity not in [Severity.LOW, Severity.INFO]

    @pytest.mark.blackbox
    def test_known_feature_returns_populated_issue(self, analyzer, modern_browsers):
        issue = analyzer.analyze_feature('flexbox', modern_browsers)
        assert isinstance(issue, CompatibilityIssue)
        assert issue.feature_id == 'flexbox' and issue.feature_name != 'flexbox'


# ============================================================================
# SECTION 5: suggest_workarounds()
# ============================================================================

class TestSuggestWorkarounds:

    def _make_issue(self, support_status):
        return CompatibilityIssue(
            feature_id='flexbox', feature_name='Test', severity=Severity.MEDIUM,
            browsers_affected=['ie'], support_status=support_status,
            description='test', category='CSS',
        )

    @pytest.mark.blackbox
    def test_workaround_suggestions(self, analyzer):
        workarounds = analyzer.suggest_workarounds(
            self._make_issue({'chrome': 'y', 'ie': 'p'}))
        assert any('polyfill' in w.lower() for w in workarounds) is True


# ============================================================================
# SECTION 6: Summary and Comparison
# ============================================================================

class TestSummaryAndComparison:

    @pytest.mark.blackbox
    def test_summary_structure(self, analyzer, modern_browsers, well_supported_features):
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        assert {'overall_score', 'grade', 'features_analyzed', 'total_issues',
                'critical_issues', 'high_issues', 'medium_issues', 'low_issues',
                'browsers_tested', 'best_browser', 'worst_browser'} == set(summary.keys())

    @pytest.mark.blackbox
    def test_browser_comparison_structure(self, analyzer, modern_browsers):
        comparison = analyzer.get_browser_comparison({'flexbox', 'css-grid'}, modern_browsers)
        assert set(comparison.keys()) == set(modern_browsers.keys())
        for data in comparison.values():
            assert set(data['features'].keys()) == {'flexbox', 'css-grid'}


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
        assert report.browser_scores['chrome'].score == 100.0
        assert report.browser_scores['ie'].score == 0.0
        assert report.overall_score == 50.0


# ============================================================================
# SECTION 8: CompatibilityScorer -- Constants and Weights
# ============================================================================

class TestScorerConstants:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("status,expected", [
        ('y', 100), ('n', 0),
    ])
    def test_status_score_values(self, scorer, status, expected):
        assert scorer.STATUS_SCORES[status] == expected

    @pytest.mark.blackbox
    def test_custom_weights_override_defaults(self, scorer_custom):
        s = scorer_custom({'chrome': 0.9, 'firefox': 0.8})
        assert s.browser_weights == {'chrome': 0.9, 'firefox': 0.8}


# ============================================================================
# SECTION 10: calculate_weighted_score()
# ============================================================================

class TestWeightedScore:

    @pytest.mark.blackbox
    def test_all_supported_weighted_100(self, scorer):
        result = scorer.calculate_weighted_score({'chrome': 'y', 'firefox': 'y'})
        assert isinstance(result, WeightedScore) and result.weighted_score == 100.0



# ============================================================================
# SECTION 13: Progressive, Trend, and Compare
# ============================================================================

class TestProgressiveAndTrendScores:

    @pytest.mark.blackbox
    def test_modern_vs_legacy_split(self, scorer):
        result = scorer.calculate_progressive_score(
            {'chrome': 'y', 'firefox': 'y', 'ie': 'n'}, {'chrome', 'firefox'})
        assert result['modern'] == 100.0 and result['legacy'] == 0.0



# ============================================================================
# SECTION 14: Market Share and Feature Importance
# ============================================================================

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

    @pytest.mark.blackbox
    def test_unknown_feature_and_browser_return_empty(self):
        assert get_version_ranges('totally-fake-feature-xyz', 'chrome') == []
        assert get_version_ranges('flexbox', 'netscape') == []


# ============================================================================
# SECTION 16: Status Text, Format, Summary, Browser Names
# ============================================================================

class TestStatusTextAndFormat:

    @pytest.mark.blackbox
    def test_known_status_code(self):
        assert _get_status_text('y') == 'Supported'


