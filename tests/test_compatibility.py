"""
Test suite for CompatibilityAnalyzer.
Tests compatibility checking and issue detection.
"""

import pytest
from src.analyzer.compatibility import (
    CompatibilityAnalyzer,
    CompatibilityReport,
    CompatibilityIssue,
    BrowserScore,
    Severity
)


class TestCompatibilityAnalyzerBasic:
    """Basic tests for CompatibilityAnalyzer."""

    def test_analyzer_initialization(self, compatibility_analyzer):
        """Test compatibility analyzer initializes correctly."""
        assert compatibility_analyzer is not None
        assert hasattr(compatibility_analyzer, 'analyze')
        assert hasattr(compatibility_analyzer, 'database')

    def test_analyze_empty_features(self, compatibility_analyzer, default_browsers):
        """Test analyzing empty feature set."""
        result = compatibility_analyzer.analyze(set(), default_browsers)
        assert isinstance(result, CompatibilityReport)
        assert result.features_analyzed == 0

    def test_analyze_returns_report(self, compatibility_analyzer, default_browsers):
        """Test analyze returns CompatibilityReport."""
        features = {'flexbox', 'css-grid'}
        result = compatibility_analyzer.analyze(features, default_browsers)
        assert isinstance(result, CompatibilityReport)


class TestCompatibilityReport:
    """Test CompatibilityReport structure and content."""

    def test_report_has_overall_score(self, compatibility_analyzer, default_browsers):
        """Test report has overall score."""
        features = {'flexbox'}
        result = compatibility_analyzer.analyze(features, default_browsers)
        assert hasattr(result, 'overall_score')
        assert 0 <= result.overall_score <= 100

    def test_report_has_browser_scores(self, compatibility_analyzer, default_browsers):
        """Test report has browser scores."""
        features = {'flexbox'}
        result = compatibility_analyzer.analyze(features, default_browsers)
        assert hasattr(result, 'browser_scores')
        assert len(result.browser_scores) == len(default_browsers)

    def test_report_counts_features(self, compatibility_analyzer, default_browsers):
        """Test report counts analyzed features."""
        features = {'flexbox', 'css-grid', 'css-variables'}
        result = compatibility_analyzer.analyze(features, default_browsers)
        assert result.features_analyzed == 3


class TestSeverityLevels:
    """Test severity level calculations."""

    def test_severity_enum_values(self):
        """Test Severity enum has expected values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"

    def test_calculate_severity_all_unsupported(self, compatibility_analyzer):
        """Test critical severity when unsupported in all browsers."""
        support_status = {'chrome': 'n', 'firefox': 'n', 'safari': 'n', 'edge': 'n'}
        severity = compatibility_analyzer._calculate_severity(support_status, 4)
        assert severity == Severity.CRITICAL

    def test_calculate_severity_all_supported(self, compatibility_analyzer):
        """Test low severity when fully supported."""
        support_status = {'chrome': 'y', 'firefox': 'y', 'safari': 'y', 'edge': 'y'}
        severity = compatibility_analyzer._calculate_severity(support_status, 4)
        assert severity == Severity.LOW


class TestBrowserScore:
    """Test BrowserScore calculations."""

    def test_browser_score_for_each_browser(self, compatibility_analyzer, default_browsers):
        """Test each browser has a score."""
        features = {'flexbox', 'css-grid'}
        result = compatibility_analyzer.analyze(features, default_browsers)

        for browser in default_browsers.keys():
            assert browser in result.browser_scores
            score = result.browser_scores[browser]
            assert isinstance(score, BrowserScore)

    def test_browser_score_counts_sum_to_total(self, compatibility_analyzer, default_browsers):
        """Test support counts sum to total features."""
        features = {'flexbox', 'css-grid', 'css-variables'}
        result = compatibility_analyzer.analyze(features, default_browsers)

        for score in result.browser_scores.values():
            total = score.supported_count + score.partial_count + score.unsupported_count
            assert total == score.total_features


class TestGrading:
    """Test score to grade conversion."""

    def test_score_to_grade_a_plus(self, compatibility_analyzer):
        """Test A+ grade for high scores."""
        grade = compatibility_analyzer._score_to_grade(97)
        assert grade == 'A+'

    def test_score_to_grade_f(self, compatibility_analyzer):
        """Test F grade for low scores."""
        grade = compatibility_analyzer._score_to_grade(50)
        assert grade == 'F'


class TestSummaryStatistics:
    """Test summary statistics generation."""

    def test_get_summary_statistics(self, compatibility_analyzer, default_browsers):
        """Test getting summary statistics."""
        features = {'flexbox', 'css-grid'}
        report = compatibility_analyzer.analyze(features, default_browsers)
        summary = compatibility_analyzer.get_summary_statistics(report)

        assert 'overall_score' in summary
        assert 'grade' in summary
        assert 'features_analyzed' in summary
        assert 'best_browser' in summary
        assert 'worst_browser' in summary
