"""Blackbox tests for database layer -- CRUD operations, statistics, model behavior.

Tests repositories and statistics as a consumer would: save, load, query, delete.
Models tested via serialization (to_dict/from_row), property behavior, and helpers.
"""

import pytest

from src.database.models import (
    Analysis,
    AnalysisFeature,
    BrowserResult,
)
from tests.database.conftest import save_n_analyses


# =============================================================================
# Model serialization -- to_dict / from_row round-trips
# =============================================================================

class TestModelSerialization:
    """Verify to_dict and from_row produce correct data for each model."""

    @pytest.mark.blackbox
    def test_analysis_to_dict_nested(self):
        br = BrowserResult(browser="chrome", support_status="y", version="120")
        feat = AnalysisFeature(feature_id="grid", category="css", browser_results=[br])
        a = Analysis(file_name="style.css", file_type="css", overall_score=88.0, grade="B+", total_features=5, id=1, features=[feat])
        d = a.to_dict()
        assert d["file_name"] == "style.css"
        assert len(d["features"]) == 1
        assert d["features"][0]["feature_id"] == "grid"


# =============================================================================
# Model behavior -- properties, __post_init__, helpers
# =============================================================================

# =============================================================================
# AnalysisRepository -- CRUD
# =============================================================================

class TestAnalysisRepository:
    """Core CRUD operations for analyses, features, and browser results."""

    @pytest.mark.integration
    def test_full_round_trip(self, analysis_repo, sample_analysis):
        a = sample_analysis(file_name="app.js", file_type="js", score=72.5, grade="C", total_features=5, num_features=2)
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        assert loaded.file_name == "app.js" and loaded.overall_score == 72.5 and len(loaded.features) == 2


# =============================================================================
# StatisticsService -- aggregation queries
# =============================================================================

class TestStatisticsService:
    @pytest.mark.integration
    def test_basic_aggregations(self, stats_service, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 5)
        assert stats_service.get_total_analyses() == 5
        assert stats_service.get_average_score() == 70.0
        assert stats_service.get_best_score() == 90.0
        assert stats_service.get_worst_score() == 50.0
