"""Blackbox tests for database layer — CRUD operations, statistics, model behavior.

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
    Setting,
    Bookmark,
    Tag,
    AnalysisTag,
)
from tests.database.conftest import save_n_analyses


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mock_row(data: dict):
    """Create a mock sqlite3.Row-like object from a dict."""
    row = MagicMock()
    row.__getitem__ = lambda self, key: data[key]
    row.keys = lambda: data.keys()
    return row


# =============================================================================
# Model serialization — to_dict / from_row round-trips
# =============================================================================

class TestModelSerialization:
    """Verify to_dict and from_row produce correct data for each model."""

    @pytest.mark.blackbox
    def test_browser_result_to_dict(self):
        br = BrowserResult(browser="firefox", support_status="a", version="121", id=5, analysis_feature_id=3)
        d = br.to_dict()
        assert d["browser"] == "firefox"
        assert d["support_status"] == "a"
        assert d["version"] == "121"

    @pytest.mark.blackbox
    def test_browser_result_from_row(self):
        row = _mock_row({"id": 10, "analysis_feature_id": 2, "browser": "safari", "version": "17", "support_status": "n"})
        br = BrowserResult.from_row(row)
        assert br.browser == "safari" and br.version == "17" and br.support_status == "n"

    @pytest.mark.blackbox
    def test_browser_result_from_row_none_version(self):
        row = _mock_row({"id": 1, "analysis_feature_id": 1, "browser": "edge", "version": None, "support_status": "y"})
        assert BrowserResult.from_row(row).version == ""

    @pytest.mark.blackbox
    def test_analysis_feature_to_dict_nested(self):
        br = BrowserResult(browser="chrome", support_status="y", version="120")
        af = AnalysisFeature(feature_id="flexbox", category="css", feature_name="Flexbox", id=1, analysis_id=5, browser_results=[br])
        d = af.to_dict()
        assert d["feature_id"] == "flexbox"
        assert len(d["browser_results"]) == 1
        assert d["browser_results"][0]["browser"] == "chrome"

    @pytest.mark.blackbox
    def test_analysis_feature_from_row(self):
        row = _mock_row({"id": 3, "analysis_id": 7, "feature_id": "promises", "feature_name": "Promises", "category": "js"})
        af = AnalysisFeature.from_row(row)
        assert af.feature_id == "promises" and af.browser_results == []

    @pytest.mark.blackbox
    def test_analysis_feature_from_row_none_name(self):
        row = _mock_row({"id": 1, "analysis_id": 1, "feature_id": "unknown", "feature_name": None, "category": "html"})
        assert AnalysisFeature.from_row(row).feature_name == ""

    @pytest.mark.blackbox
    def test_analysis_to_dict_nested(self):
        br = BrowserResult(browser="chrome", support_status="y", version="120")
        feat = AnalysisFeature(feature_id="grid", category="css", browser_results=[br])
        a = Analysis(file_name="style.css", file_type="css", overall_score=88.0, grade="B+", total_features=5, id=1, features=[feat])
        d = a.to_dict()
        assert d["file_name"] == "style.css"
        assert len(d["features"]) == 1
        assert d["features"][0]["feature_id"] == "grid"

    @pytest.mark.blackbox
    def test_analysis_from_row_iso_format(self):
        ts = "2025-06-15T14:30:00"
        row = _mock_row({"id": 1, "file_name": "a.html", "file_path": "/tmp/a.html", "file_type": "html",
                         "overall_score": 75.0, "grade": "C", "total_features": 3, "analyzed_at": ts, "browsers_json": "{}"})
        a = Analysis.from_row(row)
        assert a.analyzed_at == datetime.fromisoformat(ts)

    @pytest.mark.blackbox
    def test_analysis_from_row_sqlite_format(self):
        row = _mock_row({"id": 2, "file_name": "b.css", "file_path": None, "file_type": "css",
                         "overall_score": 60.0, "grade": "D", "total_features": 1, "analyzed_at": "2025-06-15 14:30:00",
                         "browsers_json": None})
        a = Analysis.from_row(row)
        assert a.analyzed_at == datetime(2025, 6, 15, 14, 30, 0)
        assert a.file_path == ""
        assert a.browsers_json == "{}"

    @pytest.mark.blackbox
    def test_analysis_from_row_malformed_timestamp(self):
        row = _mock_row({"id": 3, "file_name": "c.js", "file_path": "", "file_type": "js",
                         "overall_score": 50.0, "grade": "F", "total_features": 0, "analyzed_at": "not-a-date",
                         "browsers_json": "{}"})
        assert isinstance(Analysis.from_row(row).analyzed_at, datetime)

    @pytest.mark.blackbox
    def test_setting_to_dict(self):
        ts = datetime(2025, 1, 1)
        s = Setting(key="k", value="v", updated_at=ts)
        d = s.to_dict()
        assert d["key"] == "k" and d["value"] == "v" and d["updated_at"] == ts.isoformat()

    @pytest.mark.blackbox
    def test_setting_to_dict_none_updated_at(self):
        assert Setting(key="k", value="v").to_dict()["updated_at"] is None

    @pytest.mark.blackbox
    def test_setting_from_row(self):
        row = _mock_row({"key": "lang", "value": "en", "updated_at": "2025-03-01T10:00:00"})
        s = Setting.from_row(row)
        assert s.key == "lang" and isinstance(s.updated_at, datetime)

    @pytest.mark.blackbox
    def test_bookmark_to_dict_without_analysis(self):
        d = Bookmark(analysis_id=1, note="test", id=5).to_dict()
        assert d["analysis_id"] == 1 and d["note"] == "test" and "analysis" not in d

    @pytest.mark.blackbox
    def test_bookmark_to_dict_with_analysis(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=90, grade="A", total_features=5)
        d = Bookmark(analysis_id=1, id=5, analysis=a).to_dict()
        assert d["analysis"]["file_name"] == "x.html"

    @pytest.mark.blackbox
    def test_bookmark_from_row(self):
        row = _mock_row({"id": 10, "analysis_id": 3, "note": "nice", "created_at": "2025-05-01T12:00:00"})
        b = Bookmark.from_row(row)
        assert b.analysis_id == 3 and b.note == "nice" and isinstance(b.created_at, datetime)

    @pytest.mark.blackbox
    def test_bookmark_from_row_none_note(self):
        row = _mock_row({"id": 1, "analysis_id": 1, "note": None, "created_at": None})
        b = Bookmark.from_row(row)
        assert b.note == "" and isinstance(b.created_at, datetime)

    @pytest.mark.blackbox
    def test_tag_to_dict(self):
        d = Tag(name="critical", color="#ff0000", id=3).to_dict()
        assert d["name"] == "critical" and d["color"] == "#ff0000"

    @pytest.mark.blackbox
    def test_tag_from_row(self):
        row = _mock_row({"id": 7, "name": "staging", "color": "#00ff00", "created_at": "2025-02-01T10:00:00"})
        t = Tag.from_row(row)
        assert t.name == "staging" and t.color == "#00ff00"

    @pytest.mark.blackbox
    def test_tag_from_row_none_color_defaults(self):
        row = _mock_row({"id": 1, "name": "x", "color": None, "created_at": None})
        t = Tag.from_row(row)
        assert t.color == "#58a6ff" and isinstance(t.created_at, datetime)

    @pytest.mark.blackbox
    def test_analysis_tag_to_dict(self):
        ts = datetime(2025, 3, 1)
        d = AnalysisTag(analysis_id=1, tag_id=2, created_at=ts).to_dict()
        assert d["analysis_id"] == 1 and d["tag_id"] == 2

    @pytest.mark.blackbox
    def test_analysis_tag_from_row(self):
        row = _mock_row({"analysis_id": 5, "tag_id": 8, "created_at": "2025-06-01T10:00:00"})
        at = AnalysisTag.from_row(row)
        assert at.analysis_id == 5 and isinstance(at.created_at, datetime)


# =============================================================================
# Model behavior — properties, __post_init__, helpers
# =============================================================================

class TestModelBehavior:
    """Test model properties, computed fields, and type-conversion helpers."""

    @pytest.mark.blackbox
    def test_analysis_post_init_sets_analyzed_at(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0)
        assert isinstance(a.analyzed_at, datetime)

    @pytest.mark.blackbox
    def test_analysis_post_init_preserves_analyzed_at(self):
        ts = datetime(2025, 1, 1, 12, 0, 0)
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0, analyzed_at=ts)
        assert a.analyzed_at == ts

    @pytest.mark.blackbox
    def test_analysis_browsers_property_roundtrip(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0)
        a.browsers = {"safari": "17", "chrome": "120"}
        assert a.browsers == {"safari": "17", "chrome": "120"}

    @pytest.mark.blackbox
    def test_analysis_browsers_property_invalid_json(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0, browsers_json="not json")
        assert a.browsers == {}

    @pytest.mark.blackbox
    @pytest.mark.parametrize("file_type,expected_icon", [
        ("html", "\u25B6"), ("css", "\u25C6"), ("js", "\u2605"), ("txt", "\u25A0"),
    ])
    def test_file_type_icon(self, file_type, expected_icon):
        a = Analysis(file_name=f"x.{file_type}", file_type=file_type, overall_score=0, grade="F", total_features=0)
        assert a.get_file_type_icon() == expected_icon

    @pytest.mark.blackbox
    def test_formatted_date_today(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0, analyzed_at=datetime.now())
        assert a.get_formatted_date().startswith("Today")

    @pytest.mark.blackbox
    def test_formatted_date_yesterday(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0,
                     analyzed_at=datetime.now() - timedelta(days=1))
        assert a.get_formatted_date() == "Yesterday"

    @pytest.mark.blackbox
    def test_formatted_date_days_ago(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0,
                     analyzed_at=datetime.now() - timedelta(days=3))
        assert a.get_formatted_date() == "3 days ago"

    @pytest.mark.blackbox
    def test_formatted_date_old(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0,
                     analyzed_at=datetime(2024, 1, 15))
        assert "Jan 15, 2024" in a.get_formatted_date()

    @pytest.mark.blackbox
    def test_formatted_date_none(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0)
        a.analyzed_at = None
        assert a.get_formatted_date() == "Unknown"

    @pytest.mark.blackbox
    @pytest.mark.parametrize("val,expected", [
        ("true", True), ("1", True), ("yes", True), ("on", True),
        ("false", False), ("0", False), ("no", False), ("off", False), ("random", False),
    ])
    def test_setting_get_as_bool(self, val, expected):
        assert Setting(key="k", value=val).get_as_bool() is expected

    @pytest.mark.blackbox
    def test_setting_get_as_int(self):
        assert Setting(key="limit", value="100").get_as_int() == 100

    @pytest.mark.blackbox
    def test_setting_get_as_int_invalid(self):
        assert Setting(key="limit", value="abc").get_as_int() == 0

    @pytest.mark.blackbox
    def test_setting_get_as_list(self):
        assert Setting(key="browsers", value="chrome, firefox, safari").get_as_list() == ["chrome", "firefox", "safari"]

    @pytest.mark.blackbox
    def test_setting_get_as_list_empty(self):
        assert Setting(key="browsers", value="").get_as_list() == []


# =============================================================================
# AnalysisRepository — CRUD
# =============================================================================

class TestAnalysisRepository:
    """Core CRUD operations for analyses, features, and browser results."""

    @pytest.mark.integration
    def test_save_returns_id(self, analysis_repo, sample_analysis):
        aid = analysis_repo.save_analysis(sample_analysis())
        assert isinstance(aid, int) and aid > 0

    @pytest.mark.integration
    def test_save_populates_nested_ids(self, analysis_repo, sample_analysis):
        a = sample_analysis()
        analysis_repo.save_analysis(a)
        assert a.id is not None
        for feat in a.features:
            assert feat.id is not None and feat.analysis_id == a.id
            for br in feat.browser_results:
                assert br.id is not None and br.analysis_feature_id == feat.id

    @pytest.mark.integration
    def test_save_cascades_features_and_results(self, analysis_repo, sample_analysis, db):
        a = sample_analysis(num_features=3)
        analysis_repo.save_analysis(a)
        assert db.execute("SELECT COUNT(*) FROM analysis_features WHERE analysis_id = ?", (a.id,)).fetchone()[0] == 3
        assert db.execute("SELECT COUNT(*) FROM browser_results").fetchone()[0] == 12  # 3 features * 4 browsers

    @pytest.mark.integration
    def test_save_no_features(self, analysis_repo):
        a = Analysis(file_name="empty.html", file_type="html", overall_score=100.0, grade="A+", total_features=0)
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        assert loaded.features == []

    @pytest.mark.integration
    def test_get_by_id_with_features(self, saved_analysis, analysis_repo):
        aid, _ = saved_analysis
        loaded = analysis_repo.get_analysis_by_id(aid, include_features=True)
        assert loaded.id == aid
        assert len(loaded.features) == 2
        assert len(loaded.features[0].browser_results) == 4

    @pytest.mark.integration
    def test_get_by_id_without_features(self, saved_analysis, analysis_repo):
        aid, _ = saved_analysis
        loaded = analysis_repo.get_analysis_by_id(aid, include_features=False)
        assert loaded.features == []

    @pytest.mark.integration
    def test_get_by_id_not_found(self, analysis_repo):
        assert analysis_repo.get_analysis_by_id(99999) is None

    @pytest.mark.integration
    def test_pagination(self, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 10)
        page1 = analysis_repo.get_all_analyses(limit=5, offset=0)
        page2 = analysis_repo.get_all_analyses(limit=5, offset=5)
        assert len(page1) == 5 and len(page2) == 5

    @pytest.mark.integration
    def test_ordering_desc(self, analysis_repo, sample_analysis):
        for i in range(3):
            analysis_repo.save_analysis(sample_analysis(file_name=f"f{i}.html", analyzed_at=datetime(2025, 1, 1 + i)))
        results = analysis_repo.get_all_analyses()
        assert results[0].file_name == "f2.html"

    @pytest.mark.integration
    def test_file_type_filter(self, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="a.html", file_type="html"))
        analysis_repo.save_analysis(sample_analysis(file_name="b.css", file_type="css"))
        css_only = analysis_repo.get_all_analyses(file_type="css")
        assert len(css_only) == 1 and css_only[0].file_name == "b.css"

    @pytest.mark.integration
    def test_empty_db_returns_empty_list(self, analysis_repo):
        assert analysis_repo.get_all_analyses() == []

    @pytest.mark.integration
    def test_search_like_match(self, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="my_app.html"))
        analysis_repo.save_analysis(sample_analysis(file_name="other.js"))
        assert len(analysis_repo.search_analyses("my_app")) == 1

    @pytest.mark.integration
    def test_get_count_with_filter(self, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="a.html", file_type="html"))
        analysis_repo.save_analysis(sample_analysis(file_name="b.css", file_type="css"))
        assert analysis_repo.get_count(file_type="html") == 1

    @pytest.mark.integration
    def test_delete_cascades(self, saved_analysis, analysis_repo, db):
        aid, _ = saved_analysis
        assert analysis_repo.delete_analysis(aid) is True
        assert db.execute("SELECT COUNT(*) FROM analysis_features WHERE analysis_id = ?", (aid,)).fetchone()[0] == 0

    @pytest.mark.integration
    def test_delete_not_found(self, analysis_repo):
        assert analysis_repo.delete_analysis(99999) is False

    @pytest.mark.integration
    def test_clear_all(self, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 5)
        assert analysis_repo.clear_all() == 5
        assert analysis_repo.get_count() == 0

    @pytest.mark.integration
    def test_full_round_trip(self, analysis_repo, sample_analysis):
        a = sample_analysis(file_name="app.js", file_type="js", score=72.5, grade="C", total_features=5, num_features=2)
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        assert loaded.file_name == "app.js" and loaded.overall_score == 72.5 and len(loaded.features) == 2

    @pytest.mark.integration
    def test_browser_statuses_preserved(self, analysis_repo):
        feat = AnalysisFeature(feature_id="test-feat", feature_name="Test", category="js", browser_results=[
            BrowserResult(browser="chrome", version="120", support_status="y"),
            BrowserResult(browser="firefox", version="121", support_status="n"),
            BrowserResult(browser="safari", version="17", support_status="a"),
            BrowserResult(browser="edge", version="120", support_status="u"),
        ])
        a = Analysis(file_name="test.js", file_type="js", overall_score=50, grade="F", total_features=1, features=[feat])
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        statuses = {br.browser: br.support_status for br in loaded.features[0].browser_results}
        assert statuses == {"chrome": "y", "firefox": "n", "safari": "a", "edge": "u"}

    @pytest.mark.integration
    def test_browsers_json_preserved(self, analysis_repo):
        a = Analysis(file_name="test.html", file_type="html", overall_score=80, grade="B", total_features=0)
        a.browsers = {"chrome": "120", "firefox": "121"}
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid, include_features=False)
        assert loaded.browsers == {"chrome": "120", "firefox": "121"}

    @pytest.mark.integration
    def test_get_analyses_for_file(self, analysis_repo, sample_analysis):
        for _ in range(3):
            analysis_repo.save_analysis(sample_analysis(file_name="same.html"))
        analysis_repo.save_analysis(sample_analysis(file_name="other.html"))
        results = analysis_repo.get_analyses_for_file("same.html")
        assert len(results) == 3 and all(r.file_name == "same.html" for r in results)


# =============================================================================
# SettingsRepository — CRUD
# =============================================================================

class TestSettingsRepository:
    @pytest.mark.integration
    def test_set_and_get(self, settings_repo):
        settings_repo.set("theme", "dark")
        assert settings_repo.get("theme") == "dark"

    @pytest.mark.integration
    def test_get_default(self, settings_repo):
        assert settings_repo.get("nonexistent", "fallback") == "fallback"

    @pytest.mark.integration
    def test_upsert(self, settings_repo):
        settings_repo.set("key", "v1")
        settings_repo.set("key", "v2")
        assert settings_repo.get("key") == "v2"

    @pytest.mark.integration
    def test_delete(self, settings_repo):
        settings_repo.set("temp", "value")
        assert settings_repo.delete("temp") is True
        assert settings_repo.get("temp") == ""

    @pytest.mark.integration
    def test_delete_not_found(self, settings_repo):
        assert settings_repo.delete("nonexistent") is False

    @pytest.mark.integration
    def test_get_all_includes_defaults(self, settings_repo):
        all_settings = settings_repo.get_all()
        assert "default_browsers" in all_settings and "history_limit" in all_settings

    @pytest.mark.integration
    def test_default_settings_from_migration(self, settings_repo):
        assert settings_repo.get("auto_save_history") == "true"
        assert settings_repo.get_as_int("history_limit") == 100
        assert settings_repo.get_as_list("default_browsers") == ["chrome", "firefox", "safari", "edge"]


# =============================================================================
# BookmarksRepository — CRUD
# =============================================================================

class TestBookmarksRepository:
    @pytest.mark.integration
    def test_add_and_check(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bid = bookmarks_repo.add_bookmark(aid, note="important")
        assert bid > 0
        assert bookmarks_repo.is_bookmarked(aid) is True

    @pytest.mark.integration
    def test_is_bookmarked_false(self, bookmarks_repo):
        assert bookmarks_repo.is_bookmarked(99999) is False

    @pytest.mark.integration
    def test_remove_bookmark(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid)
        assert bookmarks_repo.remove_bookmark(aid) is True
        assert bookmarks_repo.is_bookmarked(aid) is False

    @pytest.mark.integration
    def test_remove_not_found(self, bookmarks_repo):
        assert bookmarks_repo.remove_bookmark(99999) is False

    @pytest.mark.integration
    def test_get_bookmark(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid, note="test note")
        bm = bookmarks_repo.get_bookmark(aid)
        assert bm["analysis_id"] == aid and bm["note"] == "test note"

    @pytest.mark.integration
    def test_get_bookmark_not_found(self, bookmarks_repo):
        assert bookmarks_repo.get_bookmark(99999) is None

    @pytest.mark.integration
    def test_get_all_bookmarks_with_join(self, bookmarks_repo, analysis_repo, sample_analysis):
        id1 = analysis_repo.save_analysis(sample_analysis(file_name="one.html", score=90))
        id2 = analysis_repo.save_analysis(sample_analysis(file_name="two.css", file_type="css", score=80))
        bookmarks_repo.add_bookmark(id1, "first")
        bookmarks_repo.add_bookmark(id2, "second")
        all_bm = bookmarks_repo.get_all_bookmarks()
        assert len(all_bm) == 2
        file_names = {bm["analysis"]["file_name"] for bm in all_bm}
        assert file_names == {"one.html", "two.css"}

    @pytest.mark.integration
    def test_update_note(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid, note="old")
        bookmarks_repo.update_note(aid, "new")
        assert bookmarks_repo.get_bookmark(aid)["note"] == "new"

    @pytest.mark.integration
    def test_idempotent_add(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid, "v1")
        bookmarks_repo.add_bookmark(aid, "v2")
        assert bookmarks_repo.get_count() == 1
        assert bookmarks_repo.get_bookmark(aid)["note"] == "v2"

    @pytest.mark.integration
    def test_cascade_delete_when_analysis_deleted(self, bookmarks_repo, analysis_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid)
        analysis_repo.delete_analysis(aid)
        assert bookmarks_repo.is_bookmarked(aid) is False


# =============================================================================
# TagsRepository — CRUD
# =============================================================================

class TestTagsRepository:
    @pytest.mark.integration
    def test_create_and_get_by_name(self, tags_repo):
        tags_repo.create_tag("production", "#ff0000")
        tag = tags_repo.get_tag_by_name("production")
        assert tag["name"] == "production" and tag["color"] == "#ff0000"

    @pytest.mark.integration
    def test_get_tag_not_found(self, tags_repo):
        assert tags_repo.get_tag_by_name("nope") is None
        assert tags_repo.get_tag_by_id(99999) is None

    @pytest.mark.integration
    def test_get_all_tags_ordered(self, tags_repo):
        for name in ("beta", "alpha", "gamma"):
            tags_repo.create_tag(name)
        names = [t["name"] for t in tags_repo.get_all_tags()]
        assert names == ["alpha", "beta", "gamma"]

    @pytest.mark.integration
    def test_delete_tag(self, tags_repo):
        tid = tags_repo.create_tag("temp")
        assert tags_repo.delete_tag(tid) is True
        assert tags_repo.get_tag_by_id(tid) is None

    @pytest.mark.integration
    def test_delete_tag_not_found(self, tags_repo):
        assert tags_repo.delete_tag(99999) is False

    @pytest.mark.integration
    def test_update_tag(self, tags_repo):
        tid = tags_repo.create_tag("old")
        tags_repo.update_tag(tid, name="new", color="#000000")
        tag = tags_repo.get_tag_by_id(tid)
        assert tag["name"] == "new" and tag["color"] == "#000000"

    @pytest.mark.integration
    def test_update_tag_nothing_returns_false(self, tags_repo):
        tid = tags_repo.create_tag("x")
        assert tags_repo.update_tag(tid) is False

    @pytest.mark.integration
    def test_tag_analysis_link(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        assert tags_repo.add_tag_to_analysis(aid, tid) is True
        tags = tags_repo.get_tags_for_analysis(aid)
        assert len(tags) == 1 and tags[0]["name"] == "tag1"

    @pytest.mark.integration
    def test_remove_tag_from_analysis(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        tags_repo.add_tag_to_analysis(aid, tid)
        assert tags_repo.remove_tag_from_analysis(aid, tid) is True
        assert tags_repo.get_tags_for_analysis(aid) == []

    @pytest.mark.integration
    def test_remove_tag_not_linked(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        assert tags_repo.remove_tag_from_analysis(aid, tid) is False

    @pytest.mark.integration
    def test_get_analyses_by_tag(self, tags_repo, analysis_repo, sample_analysis):
        id1 = analysis_repo.save_analysis(sample_analysis(file_name="one.html"))
        id2 = analysis_repo.save_analysis(sample_analysis(file_name="two.html"))
        tid = tags_repo.create_tag("important")
        tags_repo.add_tag_to_analysis(id1, tid)
        tags_repo.add_tag_to_analysis(id2, tid)
        assert len(tags_repo.get_analyses_by_tag(tid)) == 2

    @pytest.mark.integration
    def test_get_tag_counts(self, tags_repo, analysis_repo, sample_analysis):
        id1 = analysis_repo.save_analysis(sample_analysis(file_name="one.html"))
        id2 = analysis_repo.save_analysis(sample_analysis(file_name="two.html"))
        t1 = tags_repo.create_tag("hot")
        t2 = tags_repo.create_tag("cold")
        tags_repo.add_tag_to_analysis(id1, t1)
        tags_repo.add_tag_to_analysis(id2, t1)
        tags_repo.add_tag_to_analysis(id1, t2)
        counts = tags_repo.get_tag_counts()
        assert counts["hot"] == 2 and counts["cold"] == 1

    @pytest.mark.integration
    def test_duplicate_tag_name_error(self, tags_repo):
        tags_repo.create_tag("unique")
        with pytest.raises(sqlite3.IntegrityError):
            tags_repo.create_tag("unique")

    @pytest.mark.integration
    def test_cascade_delete_analysis_removes_links(self, tags_repo, analysis_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        tags_repo.add_tag_to_analysis(aid, tid)
        analysis_repo.delete_analysis(aid)
        assert tags_repo.get_tag_by_id(tid) is not None  # tag survives
        assert tags_repo.get_tags_for_analysis(aid) == []  # link gone

    @pytest.mark.integration
    def test_cascade_delete_tag_removes_links(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        tags_repo.add_tag_to_analysis(aid, tid)
        tags_repo.delete_tag(tid)
        assert tags_repo.get_tags_for_analysis(aid) == []


# =============================================================================
# StatisticsService — aggregation queries
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
        # Scores: 50, 60, 70, 80, 90
        save_n_analyses(analysis_repo, sample_analysis, 5)
        assert stats_service.get_total_analyses() == 5
        assert stats_service.get_average_score() == 70.0
        assert stats_service.get_best_score() == 90.0
        assert stats_service.get_worst_score() == 50.0

    @pytest.mark.integration
    def test_grade_distribution(self, stats_service, analysis_repo, sample_analysis):
        for grade in ["A", "A", "B", "C"]:
            analysis_repo.save_analysis(sample_analysis(grade=grade))
        dist = stats_service.get_grade_distribution()
        assert dist["A"] == 2 and dist["B"] == 1 and dist["C"] == 1

    @pytest.mark.integration
    def test_file_type_distribution(self, stats_service, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="a.html", file_type="html"))
        analysis_repo.save_analysis(sample_analysis(file_name="b.html", file_type="html"))
        analysis_repo.save_analysis(sample_analysis(file_name="c.css", file_type="css"))
        dist = stats_service.get_file_type_distribution()
        assert dist["html"] == 2 and dist["css"] == 1

    @pytest.mark.integration
    def test_top_problematic_features(self, stats_service, analysis_repo):
        feat = AnalysisFeature(feature_id="css-grid", feature_name="CSS Grid", category="css", browser_results=[
            BrowserResult(browser="ie", version="11", support_status="n"),
            BrowserResult(browser="chrome", version="120", support_status="y"),
        ])
        a = Analysis(file_name="test.css", file_type="css", overall_score=70, grade="C", total_features=1, features=[feat])
        analysis_repo.save_analysis(a)
        top = stats_service.get_top_problematic_features(limit=5)
        assert len(top) == 1 and top[0]["feature_id"] == "css-grid"

    @pytest.mark.integration
    def test_most_analyzed_files(self, stats_service, analysis_repo, sample_analysis):
        for _ in range(3):
            analysis_repo.save_analysis(sample_analysis(file_name="popular.html"))
        analysis_repo.save_analysis(sample_analysis(file_name="rare.html"))
        files = stats_service.get_most_analyzed_files(limit=5)
        assert files[0]["file_name"] == "popular.html" and files[0]["analysis_count"] == 3

    @pytest.mark.integration
    def test_browser_support_counts(self, stats_service, analysis_repo):
        feat = AnalysisFeature(feature_id="flexbox", feature_name="Flexbox", category="css", browser_results=[
            BrowserResult(browser="chrome", version="120", support_status="y"),
            BrowserResult(browser="ie", version="11", support_status="n"),
        ])
        a = Analysis(file_name="test.css", file_type="css", overall_score=50, grade="F", total_features=1, features=[feat])
        analysis_repo.save_analysis(a)
        stats = stats_service.get_browser_statistics()
        assert stats["chrome"]["supported"] == 1 and stats["ie"]["unsupported"] == 1

    @pytest.mark.integration
    def test_browser_percentage_calculation(self, stats_service, analysis_repo):
        feat = AnalysisFeature(feature_id="feat1", feature_name="Feat 1", category="css", browser_results=[
            BrowserResult(browser="chrome", version="120", support_status="y"),
            BrowserResult(browser="chrome", version="120", support_status="a"),
        ])
        feat2 = AnalysisFeature(feature_id="feat2", feature_name="Feat 2", category="css", browser_results=[
            BrowserResult(browser="chrome", version="120", support_status="a"),
            BrowserResult(browser="chrome", version="120", support_status="n"),
        ])
        a = Analysis(file_name="test.css", file_type="css", overall_score=50, grade="F", total_features=2, features=[feat, feat2])
        analysis_repo.save_analysis(a)
        chrome = stats_service.get_browser_statistics()["chrome"]
        assert chrome["total"] == 4 and chrome["support_percentage"] == 50.0

    @pytest.mark.integration
    def test_score_trend_excludes_old(self, stats_service, analysis_repo, sample_analysis):
        old = datetime.now() - timedelta(days=30)
        recent = datetime.now() - timedelta(days=1)
        analysis_repo.save_analysis(sample_analysis(score=50, analyzed_at=old))
        analysis_repo.save_analysis(sample_analysis(score=90, analyzed_at=recent))
        trend = stats_service.get_score_trend(days=7)
        dates = [t["date"] for t in trend]
        assert old.strftime("%Y-%m-%d") not in dates

    @pytest.mark.integration
    def test_summary_all_keys_present(self, stats_service, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 3)
        summary = stats_service.get_summary_statistics()
        expected_keys = {"total_analyses", "average_score", "best_score", "worst_score",
                         "grade_distribution", "file_type_distribution", "top_problematic_features",
                         "most_analyzed_files", "browser_statistics"}
        assert set(summary.keys()) == expected_keys
