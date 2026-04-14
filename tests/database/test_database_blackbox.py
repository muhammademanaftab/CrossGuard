"""Blackbox tests for database layer -- CRUD operations, statistics, model behavior.

Tests repositories and statistics as a consumer would: save, load, query, delete.
Models tested via serialization (to_dict/from_row), property behavior, and helpers.
"""

import json
import sqlite3
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.database.models import (
    Analysis,
    AnalysisFeature,
    BrowserResult,
    Bookmark,
    Tag,
)
from tests.database.conftest import save_n_analyses


# --- Helpers ----------------------------------------------------------------

def _mock_row(data: dict):
    """Create a mock sqlite3.Row-like object from a dict."""
    row = MagicMock()
    row.__getitem__ = lambda self, key: data[key]
    row.keys = lambda: data.keys()
    return row


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

class TestModelBehavior:
    """Test model properties, computed fields, and type-conversion helpers."""

    @pytest.mark.blackbox
    def test_analysis_post_init_sets_analyzed_at(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0)
        assert isinstance(a.analyzed_at, datetime)

    @pytest.mark.blackbox
    def test_analysis_browsers_property_roundtrip(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0)
        a.browsers = {"safari": "17", "chrome": "120"}
        assert a.browsers == {"safari": "17", "chrome": "120"}


# =============================================================================
# AnalysisRepository -- CRUD
# =============================================================================

class TestAnalysisRepository:
    """Core CRUD operations for analyses, features, and browser results."""

    @pytest.mark.integration
    def test_save_returns_id(self, analysis_repo, sample_analysis):
        aid = analysis_repo.save_analysis(sample_analysis())
        assert isinstance(aid, int) and aid > 0

    @pytest.mark.integration
    def test_full_round_trip(self, analysis_repo, sample_analysis):
        a = sample_analysis(file_name="app.js", file_type="js", score=72.5, grade="C", total_features=5, num_features=2)
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        assert loaded.file_name == "app.js" and loaded.overall_score == 72.5 and len(loaded.features) == 2

    @pytest.mark.integration
    def test_delete_cascades(self, saved_analysis, analysis_repo, db):
        aid, _ = saved_analysis
        assert analysis_repo.delete_analysis(aid) is True
        assert db.execute("SELECT COUNT(*) FROM analysis_features WHERE analysis_id = ?", (aid,)).fetchone()[0] == 0


# =============================================================================
# SettingsRepository -- CRUD
# =============================================================================

class TestSettingsRepository:
    @pytest.mark.integration
    def test_set_and_get(self, settings_repo):
        settings_repo.set("theme", "dark")
        assert settings_repo.get("theme") == "dark"



# =============================================================================
# BookmarksRepository -- CRUD
# =============================================================================

class TestBookmarksRepository:
    @pytest.mark.integration
    def test_add_and_check(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bid = bookmarks_repo.add_bookmark(aid, note="important")
        assert bid > 0
        assert bookmarks_repo.is_bookmarked(aid) is True


# =============================================================================
# TagsRepository -- CRUD
# =============================================================================

class TestTagsRepository:
    @pytest.mark.integration
    def test_create_and_get_by_name(self, tags_repo):
        tags_repo.create_tag("production", "#ff0000")
        tag = tags_repo.get_tag_by_name("production")
        assert tag["name"] == "production" and tag["color"] == "#ff0000"

    @pytest.mark.integration
    def test_tag_analysis_link(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        assert tags_repo.add_tag_to_analysis(aid, tid) is True
        tags = tags_repo.get_tags_for_analysis(aid)
        assert len(tags) == 1 and tags[0]["name"] == "tag1"


# =============================================================================
# StatisticsService -- aggregation queries
# =============================================================================

class TestStatisticsService:
    @pytest.mark.integration
    def test_empty_db_defaults(self, stats_service):
        summary = stats_service.get_summary_statistics()
        assert summary["total_analyses"] == 0
        assert summary["average_score"] == 0
        assert summary["grade_distribution"] == {}

    @pytest.mark.integration
    def test_basic_aggregations(self, stats_service, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 5)
        assert stats_service.get_total_analyses() == 5
        assert stats_service.get_average_score() == 70.0
        assert stats_service.get_best_score() == 90.0
        assert stats_service.get_worst_score() == 50.0

