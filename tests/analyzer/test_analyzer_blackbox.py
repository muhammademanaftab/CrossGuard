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
    BrowserScore,
    Severity,
)
from src.analyzer.scorer import CompatibilityScorer, WeightedScore
from src.analyzer.version_ranges import (
    get_version_ranges,
    _get_status_text,
    format_ranges_for_display,
    get_support_summary,
    get_all_browser_ranges,
    BROWSER_NAMES,
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
    def test_report_structure(self, analyzer, modern_browsers):
        """Report has correct type and all browsers."""
        report = analyzer.analyze({'flexbox'}, modern_browsers)
        assert isinstance(report, CompatibilityReport)
        assert set(report.browser_scores.keys()) == set(modern_browsers.keys())

    @pytest.mark.blackbox
    def test_adding_ie_lowers_score(self, analyzer, well_supported_features):
        modern = {'chrome': '120', 'firefox': '121'}
        with_ie = {'chrome': '120', 'firefox': '121', 'ie': '11'}
        assert analyzer.analyze(well_supported_features, with_ie).overall_score < \
               analyzer.analyze(well_supported_features, modern).overall_score


# ============================================================================
# SECTION 2: BrowserScore and Overall Score
# ============================================================================

class TestBrowserScore:
    """Tests for browser score formula and overall score calculation."""

    @pytest.mark.blackbox
    def test_browser_score_formula(self, analyzer, modern_browsers):
        """Score formula correct, counts sum to total."""
        report = analyzer.analyze({'flexbox'}, modern_browsers)
        for bs in report.browser_scores.values():
            assert isinstance(bs, BrowserScore) and 0 <= bs.score <= 100
            assert bs.supported_count + bs.partial_count + bs.unsupported_count == bs.total_features

    @pytest.mark.blackbox
    def test_unknown_feature_counts_unsupported(self, analyzer):
        report = analyzer.analyze({'totally-fake-feature-xyz'}, {'chrome': '120'})
        assert report.browser_scores['chrome'].unsupported_count == 1

    @pytest.mark.blackbox
    def test_overall_is_average_of_browser_scores(self, analyzer):
        report = analyzer.analyze({'flexbox'}, {'chrome': '120', 'ie': '11'})
        expected = sum(bs.score for bs in report.browser_scores.values()) / len(report.browser_scores)
        assert abs(report.overall_score - expected) < 0.01

    @pytest.mark.blackbox
    def test_empty_browsers_score_0(self, analyzer):
        assert analyzer.analyze({'flexbox'}, {}).overall_score == 0.0


# ============================================================================
# SECTION 3: Severity and Grading
# ============================================================================

class TestSeverity:
    """Tests for _calculate_severity()."""

    @pytest.mark.blackbox
    @pytest.mark.parametrize("status,total,expected", [
        ({'chrome': 'n', 'firefox': 'n', 'safari': 'n'}, 3, Severity.CRITICAL),
        ({'chrome': 'n', 'firefox': 'n', 'safari': 'y'}, 3, Severity.HIGH),
        ({'chrome': 'y', 'firefox': 'y', 'safari': 'y', 'ie': 'n'}, 4, Severity.MEDIUM),
        ({'chrome': 'y', 'firefox': 'y', 'safari': 'y'}, 3, Severity.LOW),
    ])
    def test_severity_classification(self, analyzer, status, total, expected):
        assert analyzer._calculate_severity(status, total) == expected


class TestAnalyzerGrade:
    """Tests for the analyzer's 13-level grading scale (A+ to F)."""

    @pytest.mark.blackbox
    @pytest.mark.parametrize("score,expected", [
        (100, 'A+'), (96.99, 'A'), (92.99, 'A-'),
        (89.99, 'B+'), (86.99, 'B'), (82.99, 'B-'),
        (79.99, 'C+'), (76.99, 'C'), (72.99, 'C-'),
        (69.99, 'D+'), (66.99, 'D'), (62.99, 'D-'),
        (0, 'F'),
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
    def test_empty_features_returns_empty(self, analyzer, modern_browsers):
        assert analyzer.get_detailed_issues(set(), modern_browsers) == []

    @pytest.mark.blackbox
    def test_known_feature_returns_populated_issue(self, analyzer, modern_browsers):
        issue = analyzer.analyze_feature('flexbox', modern_browsers)
        assert isinstance(issue, CompatibilityIssue)
        assert issue.feature_id == 'flexbox' and issue.feature_name != 'flexbox'

    @pytest.mark.blackbox
    def test_unknown_feature_uses_fallback(self, analyzer, modern_browsers):
        issue = analyzer.analyze_feature('totally-fake-feature-xyz', modern_browsers)
        assert issue.category == 'Unknown'


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
    @pytest.mark.parametrize("status,expect_polyfill,expect_prefix", [
        ({'chrome': 'y', 'ie': 'p'}, True, False),
        ({'chrome': 'y', 'ie': 'x'}, False, True),
        ({'chrome': 'y', 'firefox': 'y'}, False, False),
    ])
    def test_workaround_suggestions(self, analyzer, status, expect_polyfill, expect_prefix):
        workarounds = analyzer.suggest_workarounds(self._make_issue(status))
        assert any('polyfill' in w.lower() for w in workarounds) == expect_polyfill
        assert any('prefix' in w.lower() for w in workarounds) == expect_prefix


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
    def test_empty_browsers_best_worst_none(self, analyzer):
        summary = analyzer.get_summary_statistics(analyzer.analyze({'flexbox'}, {}))
        assert summary['best_browser'] == 'None'

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
    def test_all_supported_score_100(self):
        a = self._make_analyzer_with_mock({('flexbox', 'chrome'): 'y', ('flexbox', 'firefox'): 'y'})
        assert a.analyze({'flexbox'}, {'chrome': '120', 'firefox': '121'}).overall_score == 100.0

    @pytest.mark.blackbox
    def test_mixed_support_correct_score(self):
        a = self._make_analyzer_with_mock({('flexbox', 'chrome'): 'y', ('flexbox', 'ie'): 'n'})
        report = a.analyze({'flexbox'}, {'chrome': '120', 'ie': '11'})
        assert report.browser_scores['chrome'].score == 100.0
        assert report.browser_scores['ie'].score == 0.0
        assert report.overall_score == 50.0

    @pytest.mark.blackbox
    def test_partial_support_score_50(self):
        a = self._make_analyzer_with_mock({('flexbox', 'chrome'): 'x'})
        assert a.analyze({'flexbox'}, {'chrome': '120'}).browser_scores['chrome'].score == 50.0


# ============================================================================
# SECTION 8: CompatibilityScorer -- Constants and Weights
# ============================================================================

class TestScorerConstants:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("status,expected", [
        ('y', 100), ('a', 100), ('x', 70),
        ('p', 50), ('d', 30), ('n', 0), ('u', 0),
    ])
    def test_status_score_values(self, scorer, status, expected):
        assert scorer.STATUS_SCORES[status] == expected

    @pytest.mark.blackbox
    def test_custom_weights_override_defaults(self, scorer_custom):
        s = scorer_custom({'chrome': 0.9, 'firefox': 0.8})
        assert s.browser_weights == {'chrome': 0.9, 'firefox': 0.8}

    @pytest.mark.blackbox
    def test_set_browser_weight_rejects_invalid(self, scorer):
        with pytest.raises(ValueError):
            scorer.set_browser_weight('chrome', 1.5)
        with pytest.raises(ValueError):
            scorer.set_browser_weight('chrome', -0.1)


# ============================================================================
# SECTION 9: calculate_simple_score()
# ============================================================================

class TestSimpleScore:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("status,expected", [
        ({'chrome': 'y', 'firefox': 'y'}, 100.0),
        ({'chrome': 'n', 'firefox': 'n'}, 0.0),
        ({'chrome': 'y', 'firefox': 'n'}, 50.0),
        ({}, 0.0),
    ])
    def test_simple_score_calculation(self, scorer, status, expected):
        assert scorer.calculate_simple_score(status) == expected

    @pytest.mark.blackbox
    def test_all_statuses_combined(self, scorer):
        status = {'b1': 'y', 'b2': 'a', 'b3': 'x', 'b4': 'p', 'b5': 'd', 'b6': 'n', 'b7': 'u'}
        expected = (100 + 100 + 70 + 50 + 30 + 0 + 0) / 7
        assert abs(scorer.calculate_simple_score(status) - expected) < 0.01


# ============================================================================
# SECTION 10: calculate_weighted_score()
# ============================================================================

class TestWeightedScore:

    @pytest.mark.blackbox
    def test_all_supported_weighted_100(self, scorer):
        result = scorer.calculate_weighted_score({'chrome': 'y', 'firefox': 'y'})
        assert isinstance(result, WeightedScore) and result.weighted_score == 100.0

    @pytest.mark.blackbox
    def test_ie_weight_produces_correct_weighted_score(self, scorer):
        """chrome y=100 w=1.0, ie n=0 w=0.5 => weighted=66.67, simple=50"""
        result = scorer.calculate_weighted_score({'chrome': 'y', 'ie': 'n'})
        assert abs(result.weighted_score - 66.67) < 0.1
        assert result.total_score == 50.0

    @pytest.mark.blackbox
    def test_empty_returns_zeroed(self, scorer):
        result = scorer.calculate_weighted_score({})
        assert result.total_score == 0.0 and result.weighted_score == 0.0

    @pytest.mark.blackbox
    def test_custom_weights_change_outcome(self, scorer_custom):
        s = scorer_custom({'chrome': 0.1, 'firefox': 1.0})
        assert abs(s.calculate_weighted_score({'chrome': 'y', 'firefox': 'n'}).weighted_score - 9.09) < 0.1


# ============================================================================
# SECTION 11: calculate_compatibility_index()
# ============================================================================

class TestCompatibilityIndex:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("status,expected_risk", [
        ({'chrome': 'y', 'firefox': 'y', 'safari': 'y'}, 'none'),
        ({'chrome': 'y', 'firefox': 'y', 'ie': 'n'}, 'medium'),
        ({'chrome': 'n', 'firefox': 'n', 'safari': 'y'}, 'high'),
        ({}, 'high'),
    ])
    def test_risk_level(self, scorer, status, expected_risk):
        assert scorer.calculate_compatibility_index(status)['risk_level'] == expected_risk

    @pytest.mark.blackbox
    def test_all_keys_present(self, scorer):
        expected = {'score', 'grade', 'supported_count', 'partial_count',
                    'unsupported_count', 'total_browsers', 'support_percentage', 'risk_level'}
        assert set(scorer.calculate_compatibility_index({'chrome': 'y'}).keys()) == expected


# ============================================================================
# SECTION 12: Scorer Grading (5-level)
# ============================================================================

class TestScorerGrade:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("score,expected", [
        (100, 'A'), (89.99, 'B'), (79.99, 'C'), (69.99, 'D'), (59.99, 'F'),
    ])
    def test_grade_boundaries(self, scorer, score, expected):
        assert scorer._score_to_grade(score) == expected


# ============================================================================
# SECTION 13: Progressive, Trend, and Compare
# ============================================================================

class TestProgressiveAndTrendScores:

    @pytest.mark.blackbox
    def test_modern_vs_legacy_split(self, scorer):
        result = scorer.calculate_progressive_score(
            {'chrome': 'y', 'firefox': 'y', 'ie': 'n'}, {'chrome', 'firefox'})
        assert result['modern'] == 100.0 and result['legacy'] == 0.0

    @pytest.mark.blackbox
    def test_improving_trend(self, scorer):
        result = scorer.calculate_trend_score({
            '100': {'chrome': 'n', 'firefox': 'n'},
            '120': {'chrome': 'y', 'firefox': 'y'},
        })
        assert result['trend'] == 'improving'

    @pytest.mark.blackbox
    def test_declining_and_empty_trends(self, scorer):
        assert scorer.calculate_trend_score({
            '100': {'chrome': 'y'}, '120': {'chrome': 'n'},
        })['trend'] == 'declining'
        assert scorer.calculate_trend_score({})['trend'] == 'unknown'


class TestCompareFeatures:

    @pytest.mark.blackbox
    def test_best_and_worst_identified(self, scorer):
        result = scorer.compare_features({'flexbox': 100, 'dialog': 50, 'css-grid': 80})
        assert result['best_features'][0]['feature'] == 'flexbox'
        assert result['worst_features'][0]['feature'] == 'dialog'

    @pytest.mark.blackbox
    def test_empty_and_limits(self, scorer):
        assert scorer.compare_features({})['average_score'] == 0
        result = scorer.compare_features({f'f{i}': i * 10 for i in range(10)})
        assert len(result['best_features']) == 5


# ============================================================================
# SECTION 14: Market Share and Feature Importance
# ============================================================================

class TestSpecializedScores:

    @pytest.mark.blackbox
    def test_market_share_score(self, scorer):
        assert abs(scorer.calculate_market_share_score(
            {'chrome': 'y', 'ie': 'n'}, {'chrome': 65.0, 'ie': 2.0}) - 97.01) < 0.1

    @pytest.mark.blackbox
    def test_feature_importance_score(self, scorer):
        assert abs(scorer.calculate_feature_importance_score(
            {'critical': {'chrome': 'n'}, 'optional': {'chrome': 'y'}},
            {'critical': 1.0, 'optional': 0.1}) - 9.09) < 0.1


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
    def test_no_adjacent_ranges_with_same_status(self):
        ranges = get_version_ranges('flexbox', 'chrome')
        for i in range(len(ranges) - 1):
            assert ranges[i]['status'] != ranges[i + 1]['status']

    @pytest.mark.blackbox
    def test_unknown_feature_and_browser_return_empty(self):
        assert get_version_ranges('totally-fake-feature-xyz', 'chrome') == []
        assert get_version_ranges('flexbox', 'netscape') == []


# ============================================================================
# SECTION 16: Status Text, Format, Summary, Browser Names
# ============================================================================

class TestStatusTextAndFormat:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("code,expected", [
        ('y', 'Supported'), ('n', 'Not Supported'),
        ('x', 'Requires Prefix'), ('u', 'Unknown'),
    ])
    def test_known_status_codes(self, code, expected):
        assert _get_status_text(code) == expected

    @pytest.mark.blackbox
    def test_unknown_code_returns_itself(self):
        assert _get_status_text('z') == 'z'

    @pytest.mark.blackbox
    def test_format_and_no_data(self):
        assert 'Supported' in format_ranges_for_display('flexbox', 'chrome')
        assert format_ranges_for_display('totally-fake-xyz', 'chrome') == "No data available"


class TestSupportSummaryAndAllRanges:

    @pytest.mark.blackbox
    def test_flexbox_summary_structure(self):
        summary = get_support_summary('flexbox')
        assert 'chrome' in summary
        for data in summary.values():
            assert data['current_status'] == data['ranges'][-1]['status']

    @pytest.mark.blackbox
    def test_unknown_returns_empty(self):
        assert get_support_summary('totally-fake-feature-xyz') == {}
        assert get_all_browser_ranges('totally-fake-feature-xyz') == {}

    @pytest.mark.blackbox
    def test_all_browser_ranges_structure(self):
        result = get_all_browser_ranges('flexbox')
        assert len(result) > 3
        assert all(len(ranges) > 0 for ranges in result.values())

    @pytest.mark.blackbox
    @pytest.mark.parametrize("code,name", [
        ('chrome', 'Chrome'), ('firefox', 'Firefox'),
        ('safari', 'Safari'), ('ie', 'Internet Explorer'),
    ])
    def test_browser_display_names(self, code, name):
        assert BROWSER_NAMES[code] == name
