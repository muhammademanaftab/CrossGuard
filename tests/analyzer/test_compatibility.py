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
        """No features to check => perfect score (nothing can fail)."""
        report = analyzer.analyze(set(), modern_browsers)
        assert report.overall_score == 100.0
        assert report.features_analyzed == 0

    def test_well_supported_high_score(self, analyzer, modern_browsers, well_supported_features):
        """Well-supported features produce a high score in modern browsers."""
        report = analyzer.analyze(well_supported_features, modern_browsers)
        assert report.overall_score >= 80.0

    def test_report_has_all_browsers(self, analyzer, modern_browsers):
        """Report contains a BrowserScore for every target browser."""
        report = analyzer.analyze({'flexbox'}, modern_browsers)
        assert set(report.browser_scores.keys()) == set(modern_browsers.keys())

    def test_report_is_dataclass(self, analyzer, modern_browsers):
        """analyze() returns a CompatibilityReport dataclass."""
        report = analyzer.analyze({'flexbox'}, modern_browsers)
        assert isinstance(report, CompatibilityReport)

    def test_issue_severity_counts_are_consistent(self, analyzer, legacy_browsers, mixed_support_features):
        """Severity counts in report match the actual issues list."""
        report = analyzer.analyze(mixed_support_features, legacy_browsers)
        actual_critical = sum(1 for i in report.issues if i.severity == Severity.CRITICAL)
        actual_high = sum(1 for i in report.issues if i.severity == Severity.HIGH)
        actual_medium = sum(1 for i in report.issues if i.severity == Severity.MEDIUM)
        actual_low = sum(1 for i in report.issues if i.severity == Severity.LOW)
        assert report.critical_issues == actual_critical
        assert report.high_issues == actual_high
        assert report.medium_issues == actual_medium
        assert report.low_issues == actual_low

    def test_features_analyzed_count(self, analyzer, modern_browsers):
        """features_analyzed matches input set size."""
        features = {'flexbox', 'css-grid', 'promises'}
        report = analyzer.analyze(features, modern_browsers)
        assert report.features_analyzed == 3

    def test_adding_ie_lowers_score(self, analyzer, well_supported_features):
        """Adding IE 11 to targets lowers score for modern features."""
        modern = {'chrome': '120', 'firefox': '121'}
        with_ie = {'chrome': '120', 'firefox': '121', 'ie': '11'}
        report_modern = analyzer.analyze(well_supported_features, modern)
        report_ie = analyzer.analyze(well_supported_features, with_ie)
        assert report_ie.overall_score < report_modern.overall_score

    def test_single_feature_single_browser(self, analyzer):
        """Minimal case: one feature, one browser."""
        report = analyzer.analyze({'flexbox'}, {'chrome': '120'})
        assert report.features_analyzed == 1
        assert len(report.browser_scores) == 1


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: BrowserScore Calculation
# ═══════════════════════════════════════════════════════════════════════════

class TestBrowserScore:
    """Tests for _analyze_browser() via browser_scores in the report."""

    def test_browser_score_formula(self, analyzer):
        """Score formula: ((supported*100) + (partial*50)) / total."""
        report = analyzer.analyze({'flexbox'}, {'chrome': '120'})
        bs = report.browser_scores['chrome']
        expected = ((bs.supported_count * 100) + (bs.partial_count * 50)) / bs.total_features
        assert abs(bs.score - expected) < 0.01

    def test_browser_score_fields_complete(self, analyzer, modern_browsers):
        """BrowserScore has all required fields and counts sum to total."""
        report = analyzer.analyze({'flexbox'}, modern_browsers)
        for browser, bs in report.browser_scores.items():
            assert isinstance(bs, BrowserScore)
            assert bs.browser == browser
            assert isinstance(bs.version, str)
            assert isinstance(bs.score, float)
            assert 0 <= bs.score <= 100
            assert bs.supported_count + bs.partial_count + bs.unsupported_count == bs.total_features

    def test_empty_features_score_100(self, analyzer):
        """No features => BrowserScore is 100."""
        report = analyzer.analyze(set(), {'chrome': '120'})
        assert report.browser_scores['chrome'].score == 100.0

    def test_unknown_feature_counts_unsupported(self, analyzer):
        """Unknown feature counted as unsupported (score 0 contribution)."""
        report = analyzer.analyze({'totally-fake-feature-xyz'}, {'chrome': '120'})
        bs = report.browser_scores['chrome']
        assert bs.unsupported_count == 1
        assert bs.score == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Overall Score
# ═══════════════════════════════════════════════════════════════════════════

class TestOverallScore:
    """Tests for _calculate_overall_score()."""

    def test_average_of_browser_scores(self, analyzer):
        """Overall score is the mean of all browser scores."""
        report = analyzer.analyze({'flexbox'}, {'chrome': '120', 'ie': '11'})
        expected = sum(bs.score for bs in report.browser_scores.values()) / len(report.browser_scores)
        assert abs(report.overall_score - expected) < 0.01

    def test_empty_browsers_score_0(self, analyzer):
        """No browsers => overall score 0."""
        report = analyzer.analyze({'flexbox'}, {})
        assert report.overall_score == 0.0

    def test_single_browser_equals_its_score(self, analyzer):
        """Single browser => overall equals that browser's score."""
        report = analyzer.analyze({'flexbox'}, {'chrome': '120'})
        assert report.overall_score == report.browser_scores['chrome'].score

    def test_uniform_scores_equal_individual(self, analyzer):
        """When all browsers have the same score, overall equals individual."""
        report = analyzer.analyze({'flexbox'}, {'chrome': '120', 'firefox': '121'})
        scores = [bs.score for bs in report.browser_scores.values()]
        if scores[0] == scores[1]:  # Both should be 100 for flexbox
            assert report.overall_score == scores[0]


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Severity Classification
# ═══════════════════════════════════════════════════════════════════════════

class TestSeverity:
    """Tests for _calculate_severity()."""

    def test_critical_all_unsupported(self, analyzer):
        """All browsers unsupported => CRITICAL."""
        severity = analyzer._calculate_severity({'chrome': 'n', 'firefox': 'n', 'safari': 'n'}, 3)
        assert severity == Severity.CRITICAL

    def test_critical_all_unknown(self, analyzer):
        """All browsers unknown ('u') => CRITICAL (counted as unsupported)."""
        severity = analyzer._calculate_severity({'chrome': 'u', 'firefox': 'u'}, 2)
        assert severity == Severity.CRITICAL

    def test_high_half_plus_unsupported(self, analyzer):
        """50%+ unsupported => HIGH."""
        severity = analyzer._calculate_severity({'chrome': 'n', 'firefox': 'n', 'safari': 'y'}, 3)
        assert severity == Severity.HIGH

    def test_high_exactly_half_unsupported(self, analyzer):
        """Exactly 50% unsupported => HIGH (>= threshold)."""
        severity = analyzer._calculate_severity({'chrome': 'n', 'firefox': 'y'}, 2)
        assert severity == Severity.HIGH

    def test_medium_some_unsupported(self, analyzer):
        """< 50% unsupported => MEDIUM."""
        severity = analyzer._calculate_severity(
            {'chrome': 'y', 'firefox': 'y', 'safari': 'y', 'ie': 'n'}, 4
        )
        assert severity == Severity.MEDIUM

    def test_medium_partial_only(self, analyzer):
        """Only partial support (no unsupported) => MEDIUM."""
        severity = analyzer._calculate_severity({'chrome': 'y', 'firefox': 'x'}, 2)
        assert severity == Severity.MEDIUM

    def test_medium_polyfill(self, analyzer):
        """Polyfill status ('p') counted as partial => MEDIUM."""
        severity = analyzer._calculate_severity({'chrome': 'y', 'firefox': 'p'}, 2)
        assert severity == Severity.MEDIUM

    def test_low_all_supported(self, analyzer):
        """All fully supported => LOW."""
        severity = analyzer._calculate_severity({'chrome': 'y', 'firefox': 'y', 'safari': 'y'}, 3)
        assert severity == Severity.LOW

    def test_severity_enum_string_values(self):
        """Severity enum has correct string values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"


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

    def test_excludes_low_and_info(self, analyzer, modern_browsers, well_supported_features):
        """LOW and INFO severity issues are excluded from results."""
        issues = analyzer.get_detailed_issues(well_supported_features, modern_browsers)
        for issue in issues:
            assert issue.severity not in [Severity.LOW, Severity.INFO]

    def test_sorted_critical_first(self, analyzer, legacy_browsers, mixed_support_features):
        """Issues are sorted: CRITICAL -> HIGH -> MEDIUM."""
        issues = analyzer.get_detailed_issues(mixed_support_features, legacy_browsers)
        if len(issues) >= 2:
            severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2}
            for i in range(len(issues) - 1):
                assert severity_order[issues[i].severity] <= severity_order[issues[i + 1].severity]

    def test_returns_list_of_compatibility_issues(self, analyzer, modern_browsers):
        """Returns a list of CompatibilityIssue objects."""
        issues = analyzer.get_detailed_issues({'flexbox'}, modern_browsers)
        assert isinstance(issues, list)
        for issue in issues:
            assert isinstance(issue, CompatibilityIssue)

    def test_empty_features_returns_empty(self, analyzer, modern_browsers):
        """No features => no issues."""
        assert analyzer.get_detailed_issues(set(), modern_browsers) == []

    def test_unknown_feature_produces_critical_issue(self, analyzer, modern_browsers):
        """Unknown feature is unsupported in all browsers => CRITICAL issue."""
        issues = analyzer.get_detailed_issues({'totally-fake-feature-xyz'}, modern_browsers)
        assert len(issues) == 1
        assert issues[0].severity == Severity.CRITICAL


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: analyze_feature()
# ═══════════════════════════════════════════════════════════════════════════

class TestAnalyzeFeature:
    """Tests for analyze_feature()."""

    def test_returns_compatibility_issue(self, analyzer, modern_browsers):
        """Returns a CompatibilityIssue for the feature."""
        issue = analyzer.analyze_feature('flexbox', modern_browsers)
        assert isinstance(issue, CompatibilityIssue)
        assert issue.feature_id == 'flexbox'

    def test_browsers_affected_contains_ie(self, analyzer, legacy_browsers):
        """browsers_affected lists browsers with 'n' or 'u' status."""
        issue = analyzer.analyze_feature('arrow-functions', legacy_browsers)
        assert 'ie' in issue.browsers_affected

    def test_support_status_covers_all_browsers(self, analyzer, modern_browsers):
        """support_status dict has entry for each target browser."""
        issue = analyzer.analyze_feature('flexbox', modern_browsers)
        assert set(issue.support_status.keys()) == set(modern_browsers.keys())

    def test_feature_name_is_human_readable(self, analyzer, modern_browsers):
        """feature_name is a human-readable title, not the raw ID."""
        issue = analyzer.analyze_feature('flexbox', modern_browsers)
        assert len(issue.feature_name) > 0
        assert issue.feature_name != 'flexbox'  # Should be a readable title

    def test_category_populated(self, analyzer, modern_browsers):
        """Category is populated from database."""
        issue = analyzer.analyze_feature('flexbox', modern_browsers)
        assert isinstance(issue.category, str)
        assert len(issue.category) > 0

    def test_unknown_feature_uses_fallback(self, analyzer, modern_browsers):
        """Unknown feature uses feature_id as fallback name."""
        issue = analyzer.analyze_feature('totally-fake-feature-xyz', modern_browsers)
        assert issue.feature_id == 'totally-fake-feature-xyz'
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

    def test_polyfill_suggestion(self, analyzer):
        """Polyfill status triggers polyfill suggestion."""
        issue = self._make_issue(support_status={'chrome': 'y', 'ie': 'p'})
        workarounds = analyzer.suggest_workarounds(issue)
        assert any('polyfill' in w.lower() for w in workarounds)

    def test_prefix_suggestion(self, analyzer):
        """Prefix status triggers prefix suggestion."""
        issue = self._make_issue(support_status={'chrome': 'y', 'ie': 'x'})
        workarounds = analyzer.suggest_workarounds(issue)
        assert any('prefix' in w.lower() for w in workarounds)

    def test_both_polyfill_and_prefix(self, analyzer):
        """Both 'p' and 'x' status produces both suggestions."""
        issue = self._make_issue(support_status={'chrome': 'p', 'ie': 'x'})
        workarounds = analyzer.suggest_workarounds(issue)
        assert any('polyfill' in w.lower() for w in workarounds)
        assert any('prefix' in w.lower() for w in workarounds)

    def test_no_workarounds_when_fully_supported(self, analyzer):
        """All 'y' produces no polyfill/prefix suggestions."""
        issue = self._make_issue(support_status={'chrome': 'y', 'firefox': 'y'})
        workarounds = analyzer.suggest_workarounds(issue)
        assert not any('polyfill' in w.lower() for w in workarounds)
        assert not any('prefix' in w.lower() for w in workarounds)

    def test_returns_list(self, analyzer):
        """Always returns a list (even for unknown features)."""
        issue = self._make_issue(feature_id='totally-fake-xyz')
        assert isinstance(analyzer.suggest_workarounds(issue), list)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: get_summary_statistics()
# ═══════════════════════════════════════════════════════════════════════════

class TestSummaryStatistics:
    """Tests for get_summary_statistics()."""

    def test_all_required_keys(self, analyzer, modern_browsers, well_supported_features):
        """Summary contains all expected keys."""
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        expected_keys = {
            'overall_score', 'grade', 'features_analyzed', 'total_issues',
            'critical_issues', 'high_issues', 'medium_issues', 'low_issues',
            'browsers_tested', 'best_browser', 'worst_browser',
        }
        assert set(summary.keys()) == expected_keys

    def test_grade_is_valid(self, analyzer, modern_browsers, well_supported_features):
        """Grade is a valid 1-2 character letter grade."""
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        valid_grades = {'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'}
        assert summary['grade'] in valid_grades

    def test_best_worst_browser_format(self, analyzer, modern_browsers, well_supported_features):
        """Best/worst browser includes name and percentage."""
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        assert '(' in summary['best_browser'] and '%' in summary['best_browser']
        assert '(' in summary['worst_browser'] and '%' in summary['worst_browser']

    def test_browsers_tested_count(self, analyzer, modern_browsers, well_supported_features):
        """browsers_tested matches number of target browsers."""
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        assert summary['browsers_tested'] == len(modern_browsers)

    def test_empty_browsers_best_worst_none(self, analyzer):
        """No browsers => best/worst are 'None'."""
        report = analyzer.analyze({'flexbox'}, {})
        summary = analyzer.get_summary_statistics(report)
        assert summary['best_browser'] == 'None'
        assert summary['worst_browser'] == 'None'

    def test_overall_score_rounded(self, analyzer, modern_browsers, well_supported_features):
        """Overall score in summary is rounded to 2 decimal places."""
        report = analyzer.analyze(well_supported_features, modern_browsers)
        summary = analyzer.get_summary_statistics(report)
        score_str = str(summary['overall_score'])
        if '.' in score_str:
            decimals = len(score_str.split('.')[1])
            assert decimals <= 2


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
