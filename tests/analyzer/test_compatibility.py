"""Tests for CompatibilityAnalyzer — analysis engine, severity, grading.

Validates the core pipeline that takes parser-detected features + target
browsers and produces CompatibilityReport with scores, grades, and issues.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.analyzer.compatibility import (
    CompatibilityAnalyzer,
    CompatibilityIssue,
    CompatibilityReport,
    BrowserScore,
    Severity,
)
from src.analyzer.database import get_database


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: analyze() — Full Report Generation
# ═══════════════════════════════════════════════════════════════════════════

class TestAnalyze:
    """Tests for analyze(features, target_browsers)."""

    def test_empty_features_score_100(self, analyzer, modern_browsers):
        report = analyzer.analyze(set(), modern_browsers)
        assert report.overall_score == 100.0
        assert report.features_analyzed == 0

    def test_well_supported_high_score(self, analyzer, modern_browsers, well_supported_features):
        report = analyzer.analyze(well_supported_features, modern_browsers)
        assert report.overall_score >= 80.0

    def test_report_structure(self, analyzer, modern_browsers):
        """Report has correct type, all browsers, and valid structure."""
        report = analyzer.analyze({'flexbox'}, modern_browsers)
        assert isinstance(report, CompatibilityReport)
        assert set(report.browser_scores.keys()) == set(modern_browsers.keys())

    def test_issue_severity_counts_are_consistent(self, analyzer, legacy_browsers, mixed_support_features):
        report = analyzer.analyze(mixed_support_features, legacy_browsers)
        assert report.critical_issues == sum(1 for i in report.issues if i.severity == Severity.CRITICAL)
        assert report.high_issues == sum(1 for i in report.issues if i.severity == Severity.HIGH)
        assert report.medium_issues == sum(1 for i in report.issues if i.severity == Severity.MEDIUM)
        assert report.low_issues == sum(1 for i in report.issues if i.severity == Severity.LOW)

    def test_features_analyzed_count(self, analyzer, modern_browsers):
        report = analyzer.analyze({'flexbox', 'css-grid', 'promises'}, modern_browsers)
        assert report.features_analyzed == 3

    def test_adding_ie_lowers_score(self, analyzer, well_supported_features):
        modern = {'chrome': '120', 'firefox': '121'}
        with_ie = {'chrome': '120', 'firefox': '121', 'ie': '11'}
        assert analyzer.analyze(well_supported_features, with_ie).overall_score < \
               analyzer.analyze(well_supported_features, modern).overall_score

    def test_single_feature_single_browser(self, analyzer):
        report = analyzer.analyze({'flexbox'}, {'chrome': '120'})
        assert report.features_analyzed == 1
        assert len(report.browser_scores) == 1


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: BrowserScore Calculation
# ═══════════════════════════════════════════════════════════════════════════

class TestBrowserScore:
    """Tests for _analyze_browser() via browser_scores in the report."""

    def test_browser_score_formula_and_fields(self, analyzer, modern_browsers):
        """Score formula correct, all fields valid, counts sum to total."""
        report = analyzer.analyze({'flexbox'}, modern_browsers)
        for browser, bs in report.browser_scores.items():
            assert isinstance(bs, BrowserScore)
            assert bs.browser == browser
            assert isinstance(bs.version, str)
            assert 0 <= bs.score <= 100
            assert bs.supported_count + bs.partial_count + bs.unsupported_count == bs.total_features
            if bs.total_features > 0:
                expected = ((bs.supported_count * 100) + (bs.partial_count * 50)) / bs.total_features
                assert abs(bs.score - expected) < 0.01

    def test_empty_features_score_100(self, analyzer):
        report = analyzer.analyze(set(), {'chrome': '120'})
        assert report.browser_scores['chrome'].score == 100.0

    def test_unknown_feature_counts_unsupported(self, analyzer):
        report = analyzer.analyze({'totally-fake-feature-xyz'}, {'chrome': '120'})
        assert report.browser_scores['chrome'].unsupported_count == 1
        assert report.browser_scores['chrome'].score == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Overall Score
# ═══════════════════════════════════════════════════════════════════════════

class TestOverallScore:
    """Tests for _calculate_overall_score()."""

    def test_average_of_browser_scores(self, analyzer):
        report = analyzer.analyze({'flexbox'}, {'chrome': '120', 'ie': '11'})
        expected = sum(bs.score for bs in report.browser_scores.values()) / len(report.browser_scores)
        assert abs(report.overall_score - expected) < 0.01

    def test_empty_browsers_score_0(self, analyzer):
        assert analyzer.analyze({'flexbox'}, {}).overall_score == 0.0

    def test_single_browser_equals_its_score(self, analyzer):
        report = analyzer.analyze({'flexbox'}, {'chrome': '120'})
        assert report.overall_score == report.browser_scores['chrome'].score


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Severity Classification
# ═══════════════════════════════════════════════════════════════════════════

class TestSeverity:
    """Tests for _calculate_severity()."""

    @pytest.mark.parametrize("status,total,expected", [
        ({'chrome': 'n', 'firefox': 'n', 'safari': 'n'}, 3, Severity.CRITICAL),
        ({'chrome': 'u', 'firefox': 'u'}, 2, Severity.CRITICAL),
        ({'chrome': 'n', 'firefox': 'n', 'safari': 'y'}, 3, Severity.HIGH),
        ({'chrome': 'n', 'firefox': 'y'}, 2, Severity.HIGH),
        ({'chrome': 'y', 'firefox': 'y', 'safari': 'y', 'ie': 'n'}, 4, Severity.MEDIUM),
        ({'chrome': 'y', 'firefox': 'x'}, 2, Severity.MEDIUM),
        ({'chrome': 'y', 'firefox': 'p'}, 2, Severity.MEDIUM),
        ({'chrome': 'y', 'firefox': 'y', 'safari': 'y'}, 3, Severity.LOW),
    ])
    def test_severity_classification(self, analyzer, status, total, expected):
        assert analyzer._calculate_severity(status, total) == expected

    @pytest.mark.parametrize("member,value", [
        (Severity.CRITICAL, "critical"),
        (Severity.HIGH, "high"),
        (Severity.MEDIUM, "medium"),
        (Severity.LOW, "low"),
        (Severity.INFO, "info"),
    ])
    def test_severity_enum_string_values(self, member, value):
        assert member.value == value


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: _score_to_grade() — 13-level Grading
# ═══════════════════════════════════════════════════════════════════════════

class TestScoreToGrade:
    """Tests for the 13-level grading scale (A+ to F)."""

    @pytest.mark.parametrize("score,expected", [
        (100, 'A+'), (97, 'A+'),
        (96.99, 'A'), (93, 'A'),
        (92.99, 'A-'), (90, 'A-'),
        (89.99, 'B+'), (87, 'B+'),
        (86.99, 'B'), (83, 'B'),
        (82.99, 'B-'), (80, 'B-'),
        (79.99, 'C+'), (77, 'C+'),
        (76.99, 'C'), (73, 'C'),
        (72.99, 'C-'), (70, 'C-'),
        (69.99, 'D+'), (67, 'D+'),
        (66.99, 'D'), (63, 'D'),
        (62.99, 'D-'), (60, 'D-'),
        (59.99, 'F'), (0, 'F'),
    ])
    def test_grade_boundary(self, analyzer, score, expected):
        """Each boundary maps to the correct grade."""
        assert analyzer._score_to_grade(score) == expected


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: get_detailed_issues()
# ═══════════════════════════════════════════════════════════════════════════

class TestGetDetailedIssues:
    """Tests for get_detailed_issues()."""

    def test_filters_and_sorts_issues(self, analyzer, legacy_browsers, mixed_support_features):
        """Excludes LOW/INFO, sorted CRITICAL first, returns CompatibilityIssue list."""
        issues = analyzer.get_detailed_issues(mixed_support_features, legacy_browsers)
        assert isinstance(issues, list)
        for issue in issues:
            assert isinstance(issue, CompatibilityIssue)
            assert issue.severity not in [Severity.LOW, Severity.INFO]
        if len(issues) >= 2:
            severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2}
            for i in range(len(issues) - 1):
                assert severity_order[issues[i].severity] <= severity_order[issues[i + 1].severity]

    def test_empty_features_returns_empty(self, analyzer, modern_browsers):
        assert analyzer.get_detailed_issues(set(), modern_browsers) == []

    def test_unknown_feature_produces_critical_issue(self, analyzer, modern_browsers):
        issues = analyzer.get_detailed_issues({'totally-fake-feature-xyz'}, modern_browsers)
        assert len(issues) == 1
        assert issues[0].severity == Severity.CRITICAL


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: analyze_feature()
# ═══════════════════════════════════════════════════════════════════════════

class TestAnalyzeFeature:
    """Tests for analyze_feature()."""

    def test_known_feature(self, analyzer, modern_browsers):
        """Known feature returns CompatibilityIssue with all fields populated."""
        issue = analyzer.analyze_feature('flexbox', modern_browsers)
        assert isinstance(issue, CompatibilityIssue)
        assert issue.feature_id == 'flexbox'
        assert set(issue.support_status.keys()) == set(modern_browsers.keys())
        assert len(issue.feature_name) > 0
        assert issue.feature_name != 'flexbox'
        assert isinstance(issue.category, str) and len(issue.category) > 0

    def test_browsers_affected_contains_ie(self, analyzer, legacy_browsers):
        issue = analyzer.analyze_feature('arrow-functions', legacy_browsers)
        assert 'ie' in issue.browsers_affected

    def test_unknown_feature_uses_fallback(self, analyzer, modern_browsers):
        issue = analyzer.analyze_feature('totally-fake-feature-xyz', modern_browsers)
        assert issue.feature_name == 'totally-fake-feature-xyz'
        assert issue.category == 'Unknown'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: suggest_workarounds()
# ═══════════════════════════════════════════════════════════════════════════

class TestSuggestWorkarounds:
    """Tests for suggest_workarounds()."""

    def _make_issue(self, feature_id='flexbox', support_status=None):
        """Helper to create a CompatibilityIssue for testing."""
        return CompatibilityIssue(
            feature_id=feature_id,
            feature_name='Test Feature',
            severity=Severity.MEDIUM,
            browsers_affected=['ie'],
            support_status=support_status or {'chrome': 'y'},
            description='test',
            category='CSS',
        )

    @pytest.mark.parametrize("status,expect_polyfill,expect_prefix", [
        ({'chrome': 'y', 'ie': 'p'}, True, False),
        ({'chrome': 'y', 'ie': 'x'}, False, True),
        ({'chrome': 'p', 'ie': 'x'}, True, True),
        ({'chrome': 'y', 'firefox': 'y'}, False, False),
    ])
    def test_workaround_suggestions(self, analyzer, status, expect_polyfill, expect_prefix):
        issue = self._make_issue(support_status=status)
        workarounds = analyzer.suggest_workarounds(issue)
        assert any('polyfill' in w.lower() for w in workarounds) == expect_polyfill
        assert any('prefix' in w.lower() for w in workarounds) == expect_prefix

    def test_returns_list_for_unknown(self, analyzer):
        """Always returns a list (even for unknown features)."""
        issue = self._make_issue(feature_id='totally-fake-xyz')
        assert isinstance(analyzer.suggest_workarounds(issue), list)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: get_summary_statistics()
# ═══════════════════════════════════════════════════════════════════════════

class TestSummaryStatistics:
    """Tests for get_summary_statistics()."""

    def test_summary_structure_and_values(self, analyzer, modern_browsers, well_supported_features):
        """Summary has all keys, valid grade, correct browser count, and formatted browser strings."""
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        expected_keys = {
            'overall_score', 'grade', 'features_analyzed', 'total_issues',
            'critical_issues', 'high_issues', 'medium_issues', 'low_issues',
            'browsers_tested', 'best_browser', 'worst_browser',
        }
        assert set(summary.keys()) == expected_keys
        valid_grades = {'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'}
        assert summary['grade'] in valid_grades
        assert summary['browsers_tested'] == len(modern_browsers)
        assert '(' in summary['best_browser'] and '%' in summary['best_browser']
        # Score rounding
        score_str = str(summary['overall_score'])
        if '.' in score_str:
            assert len(score_str.split('.')[1]) <= 2

    def test_empty_browsers_best_worst_none(self, analyzer):
        report = analyzer.analyze({'flexbox'}, {})
        summary = analyzer.get_summary_statistics(report)
        assert summary['best_browser'] == 'None'
        assert summary['worst_browser'] == 'None'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: get_browser_comparison()
# ═══════════════════════════════════════════════════════════════════════════

class TestBrowserComparison:
    """Tests for get_browser_comparison()."""

    def test_returns_all_browsers(self, analyzer, modern_browsers):
        """Returns an entry for each target browser."""
        comparison = analyzer.get_browser_comparison({'flexbox'}, modern_browsers)
        assert set(comparison.keys()) == set(modern_browsers.keys())

    def test_browser_entry_has_version_and_features(self, analyzer, modern_browsers):
        """Each browser entry has 'version' and 'features' keys."""
        comparison = analyzer.get_browser_comparison({'flexbox'}, modern_browsers)
        for browser, data in comparison.items():
            assert data['version'] == modern_browsers[browser]
            assert 'features' in data

    def test_feature_entry_has_status_and_name(self, analyzer, modern_browsers):
        """Each feature entry has status, status_text, and name."""
        comparison = analyzer.get_browser_comparison({'flexbox'}, modern_browsers)
        for browser, data in comparison.items():
            for feature_id, fdata in data['features'].items():
                assert set(fdata.keys()) == {'status', 'status_text', 'name'}

    def test_multiple_features_all_present(self, analyzer, modern_browsers):
        """Multiple features all appear in comparison for each browser."""
        features = {'flexbox', 'css-grid'}
        comparison = analyzer.get_browser_comparison(features, modern_browsers)
        for browser, data in comparison.items():
            assert set(data['features'].keys()) == features


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 11: Unit test with mocked database
# ═══════════════════════════════════════════════════════════════════════════

class TestAnalyzerWithMockedDB:
    """Unit tests using a mocked database to isolate analyzer logic."""

    def _make_analyzer_with_mock(self, support_map):
        """Create analyzer with mock DB returning predetermined support values.

        Args:
            support_map: dict of (feature, browser) -> status
        """
        mock_db = MagicMock()
        mock_db.check_support.side_effect = lambda f, b, v: support_map.get((f, b), 'u')
        mock_db.get_feature_info.return_value = None
        mock_db.get_feature.return_value = None

        analyzer = CompatibilityAnalyzer.__new__(CompatibilityAnalyzer)
        analyzer.database = mock_db
        return analyzer

    def test_all_supported_score_100(self):
        """Mock: all features supported => score 100 in all browsers."""
        analyzer = self._make_analyzer_with_mock({
            ('flexbox', 'chrome'): 'y',
            ('flexbox', 'firefox'): 'y',
        })
        report = analyzer.analyze({'flexbox'}, {'chrome': '120', 'firefox': '121'})
        assert report.overall_score == 100.0

    def test_mixed_support_correct_score(self):
        """Mock: supported in chrome, not in IE => correct per-browser scores."""
        analyzer = self._make_analyzer_with_mock({
            ('flexbox', 'chrome'): 'y',
            ('flexbox', 'ie'): 'n',
        })
        report = analyzer.analyze({'flexbox'}, {'chrome': '120', 'ie': '11'})
        assert report.browser_scores['chrome'].score == 100.0
        assert report.browser_scores['ie'].score == 0.0
        assert report.overall_score == 50.0

    def test_partial_support_score_50(self):
        """Mock: prefix-required status contributes 50 to score."""
        analyzer = self._make_analyzer_with_mock({
            ('flexbox', 'chrome'): 'x',
        })
        report = analyzer.analyze({'flexbox'}, {'chrome': '120'})
        assert report.browser_scores['chrome'].score == 50.0
        assert report.browser_scores['chrome'].partial_count == 1
