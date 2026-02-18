"""Tests for StatisticsService — aggregation queries against in-memory SQLite."""

import pytest
from datetime import datetime, timedelta

from src.database.models import Analysis, AnalysisFeature, BrowserResult
from tests.database.conftest import save_n_analyses


# =============================================================================
# Empty database
# =============================================================================

class TestEmptyDatabase:
    def test_total_analyses_zero(self, stats_service):
        assert stats_service.get_total_analyses() == 0

    def test_average_score_zero(self, stats_service):
        assert stats_service.get_average_score() == 0.0

    def test_best_score_zero(self, stats_service):
        assert stats_service.get_best_score() == 0.0

    def test_worst_score_zero(self, stats_service):
        assert stats_service.get_worst_score() == 0.0

    def test_summary_statistics_defaults(self, stats_service):
        summary = stats_service.get_summary_statistics()
        assert summary["total_analyses"] == 0
        assert summary["average_score"] == 0
        assert summary["best_score"] == 0
        assert summary["worst_score"] == 0
        assert summary["grade_distribution"] == {}
        assert summary["file_type_distribution"] == {}
        assert summary["top_problematic_features"] == []
        assert summary["most_analyzed_files"] == []


# =============================================================================
# Basic aggregations
# =============================================================================

class TestBasicAggregations:
    def test_total_analyses(self, stats_service, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 5)
        assert stats_service.get_total_analyses() == 5

    def test_average_score(self, stats_service, analysis_repo, sample_analysis):
        # Scores: 50, 60, 70, 80, 90
        save_n_analyses(analysis_repo, sample_analysis, 5)
        avg = stats_service.get_average_score()
        assert avg == 70.0

    def test_best_score(self, stats_service, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 5)
        assert stats_service.get_best_score() == 90.0

    def test_worst_score(self, stats_service, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 5)
        assert stats_service.get_worst_score() == 50.0

    def test_rounding(self, stats_service, analysis_repo):
        # Create scores that produce a non-round average
        for score in [33.3, 66.7]:
            a = Analysis(
                file_name="t.html", file_type="html",
                overall_score=score, grade="C", total_features=0,
            )
            analysis_repo.save_analysis(a)
        avg = stats_service.get_average_score()
        assert avg == 50.0  # (33.3 + 66.7) / 2 = 50.0


# =============================================================================
# Distributions
# =============================================================================

class TestDistributions:
    def test_grade_distribution(self, stats_service, analysis_repo, sample_analysis):
        for grade in ["A", "A", "B", "C"]:
            a = sample_analysis(grade=grade)
            analysis_repo.save_analysis(a)
        dist = stats_service.get_grade_distribution()
        assert dist["A"] == 2
        assert dist["B"] == 1
        assert dist["C"] == 1

    def test_file_type_distribution(self, stats_service, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="a.html", file_type="html"))
        analysis_repo.save_analysis(sample_analysis(file_name="b.html", file_type="html"))
        analysis_repo.save_analysis(sample_analysis(file_name="c.css", file_type="css"))
        analysis_repo.save_analysis(sample_analysis(file_name="d.js", file_type="js"))
        dist = stats_service.get_file_type_distribution()
        assert dist["html"] == 2
        assert dist["css"] == 1
        assert dist["js"] == 1

    def test_recent_activity(self, stats_service, analysis_repo, sample_analysis):
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        analysis_repo.save_analysis(sample_analysis(analyzed_at=today))
        analysis_repo.save_analysis(sample_analysis(analyzed_at=today))
        analysis_repo.save_analysis(sample_analysis(analyzed_at=yesterday))
        activity = stats_service.get_recent_activity(days=7)
        assert len(activity) >= 1  # At least today


# =============================================================================
# Trends
# =============================================================================

class TestTrends:
    def test_score_trend_groups_by_date(self, stats_service, analysis_repo, sample_analysis):
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        analysis_repo.save_analysis(sample_analysis(score=80, analyzed_at=today))
        analysis_repo.save_analysis(sample_analysis(score=60, analyzed_at=yesterday))
        trend = stats_service.get_score_trend(days=7)
        assert len(trend) >= 1

    def test_score_trend_respects_days(self, stats_service, analysis_repo, sample_analysis):
        old = datetime.now() - timedelta(days=30)
        recent = datetime.now() - timedelta(days=1)
        analysis_repo.save_analysis(sample_analysis(score=50, analyzed_at=old))
        analysis_repo.save_analysis(sample_analysis(score=90, analyzed_at=recent))
        trend = stats_service.get_score_trend(days=7)
        # Only the recent one should be in the 7-day window
        assert len(trend) >= 1
        dates = [t["date"] for t in trend]
        assert old.strftime("%Y-%m-%d") not in dates

    def test_score_trend_ordering(self, stats_service, analysis_repo, sample_analysis):
        today = datetime.now()
        for i in range(3):
            analysis_repo.save_analysis(
                sample_analysis(analyzed_at=today - timedelta(days=i))
            )
        trend = stats_service.get_score_trend(days=7)
        if len(trend) > 1:
            # DESC ordering
            assert trend[0]["date"] >= trend[-1]["date"]


# =============================================================================
# Feature analysis
# =============================================================================

class TestFeatureAnalysis:
    def test_top_problematic_features(self, stats_service, analysis_repo):
        """Features with 'n' browser status should show up as problematic."""
        feat = AnalysisFeature(
            feature_id="css-grid",
            feature_name="CSS Grid",
            category="css",
            browser_results=[
                BrowserResult(browser="ie", version="11", support_status="n"),
                BrowserResult(browser="chrome", version="120", support_status="y"),
            ],
        )
        a = Analysis(
            file_name="test.css", file_type="css",
            overall_score=70, grade="C", total_features=1,
            features=[feat],
        )
        analysis_repo.save_analysis(a)
        top = stats_service.get_top_problematic_features(limit=5)
        assert len(top) == 1
        assert top[0]["feature_id"] == "css-grid"
        assert top[0]["fail_count"] == 1

    def test_most_analyzed_files(self, stats_service, analysis_repo, sample_analysis):
        for _ in range(3):
            analysis_repo.save_analysis(sample_analysis(file_name="popular.html"))
        analysis_repo.save_analysis(sample_analysis(file_name="rare.html"))
        files = stats_service.get_most_analyzed_files(limit=5)
        assert files[0]["file_name"] == "popular.html"
        assert files[0]["analysis_count"] == 3
        assert len(files) == 2

    def test_most_analyzed_files_limit(self, stats_service, analysis_repo, sample_analysis):
        for i in range(10):
            analysis_repo.save_analysis(sample_analysis(file_name=f"f{i}.html"))
        files = stats_service.get_most_analyzed_files(limit=3)
        assert len(files) == 3


# =============================================================================
# Browser statistics
# =============================================================================

class TestBrowserStatistics:
    def test_support_counts(self, stats_service, analysis_repo):
        feat = AnalysisFeature(
            feature_id="flexbox",
            feature_name="Flexbox",
            category="css",
            browser_results=[
                BrowserResult(browser="chrome", version="120", support_status="y"),
                BrowserResult(browser="ie", version="11", support_status="n"),
            ],
        )
        a = Analysis(
            file_name="test.css", file_type="css",
            overall_score=50, grade="F", total_features=1,
            features=[feat],
        )
        analysis_repo.save_analysis(a)
        stats = stats_service.get_browser_statistics()
        assert stats["chrome"]["supported"] == 1
        assert stats["ie"]["unsupported"] == 1

    def test_percentage_calculation(self, stats_service, analysis_repo):
        """Percentage = (supported + partial * 0.5) / total * 100."""
        feat = AnalysisFeature(
            feature_id="feat1",
            feature_name="Feat 1",
            category="css",
            browser_results=[
                BrowserResult(browser="chrome", version="120", support_status="y"),
                BrowserResult(browser="chrome", version="120", support_status="a"),
            ],
        )
        # Need two features to get two chrome entries
        feat2 = AnalysisFeature(
            feature_id="feat2",
            feature_name="Feat 2",
            category="css",
            browser_results=[
                BrowserResult(browser="chrome", version="120", support_status="a"),
                BrowserResult(browser="chrome", version="120", support_status="n"),
            ],
        )
        a = Analysis(
            file_name="test.css", file_type="css",
            overall_score=50, grade="F", total_features=2,
            features=[feat, feat2],
        )
        analysis_repo.save_analysis(a)
        stats = stats_service.get_browser_statistics()
        chrome = stats["chrome"]
        # 1 supported + 2 partial + 1 unsupported = 4 total
        # percentage = (1 + 2*0.5) / 4 * 100 = 50.0
        assert chrome["total"] == 4
        assert chrome["supported"] == 1
        assert chrome["partial"] == 2
        assert chrome["unsupported"] == 1
        assert chrome["support_percentage"] == 50.0

    def test_empty_returns_empty_dict(self, stats_service):
        assert stats_service.get_browser_statistics() == {}


# =============================================================================
# Summary statistics
# =============================================================================

class TestSummaryStatistics:
    def test_all_keys_present_with_data(self, stats_service, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 3)
        summary = stats_service.get_summary_statistics()
        expected_keys = {
            "total_analyses", "average_score", "best_score", "worst_score",
            "grade_distribution", "file_type_distribution",
            "top_problematic_features", "most_analyzed_files",
            "browser_statistics",
        }
        assert set(summary.keys()) == expected_keys

    def test_summary_with_data(self, stats_service, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 3)
        summary = stats_service.get_summary_statistics()
        assert summary["total_analyses"] == 3
        assert summary["average_score"] > 0
        assert summary["best_score"] >= summary["average_score"]
        assert summary["worst_score"] <= summary["average_score"]

    def test_summary_empty_db_defaults(self, stats_service):
        summary = stats_service.get_summary_statistics()
        assert summary["total_analyses"] == 0
        assert summary["average_score"] == 0
        assert summary["grade_distribution"] == {}
        assert "browser_statistics" not in summary  # Not included when empty
