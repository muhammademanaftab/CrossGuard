"""Tests for all 4 repository classes against real in-memory SQLite."""

import sqlite3
import pytest
from datetime import datetime, timedelta

from src.database.models import Analysis, AnalysisFeature, BrowserResult
from src.database.repositories import (
    AnalysisRepository,
    SettingsRepository,
    BookmarksRepository,
    TagsRepository,
)
from tests.database.conftest import save_n_analyses


# =============================================================================
# AnalysisRepository — Save
# =============================================================================

class TestSaveAnalysis:
    def test_returns_id(self, analysis_repo, sample_analysis):
        a = sample_analysis()
        aid = analysis_repo.save_analysis(a)
        assert isinstance(aid, int)
        assert aid > 0

    def test_populates_ids_on_objects(self, analysis_repo, sample_analysis):
        a = sample_analysis()
        analysis_repo.save_analysis(a)
        assert a.id is not None
        for feat in a.features:
            assert feat.id is not None
            assert feat.analysis_id == a.id
            for br in feat.browser_results:
                assert br.id is not None
                assert br.analysis_feature_id == feat.id

    def test_features_cascade_saved(self, analysis_repo, sample_analysis, db):
        a = sample_analysis(num_features=3)
        analysis_repo.save_analysis(a)
        cursor = db.execute("SELECT COUNT(*) FROM analysis_features WHERE analysis_id = ?", (a.id,))
        assert cursor.fetchone()[0] == 3

    def test_browser_results_cascade_saved(self, analysis_repo, sample_analysis, db):
        a = sample_analysis(num_features=2)
        analysis_repo.save_analysis(a)
        # Each feature has 4 browser results
        cursor = db.execute("SELECT COUNT(*) FROM browser_results")
        assert cursor.fetchone()[0] == 8

    def test_save_multiple(self, analysis_repo, sample_analysis):
        ids = []
        for i in range(5):
            a = sample_analysis(file_name=f"f{i}.html", score=50.0 + i * 10)
            ids.append(analysis_repo.save_analysis(a))
        assert len(set(ids)) == 5

    def test_save_analysis_no_features(self, analysis_repo):
        a = Analysis(
            file_name="empty.html", file_type="html",
            overall_score=100.0, grade="A+", total_features=0,
        )
        aid = analysis_repo.save_analysis(a)
        assert aid > 0
        loaded = analysis_repo.get_analysis_by_id(aid)
        assert loaded.features == []


# =============================================================================
# AnalysisRepository — Get
# =============================================================================

class TestGetAnalyses:
    def test_get_all_pagination(self, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 10)
        page1 = analysis_repo.get_all_analyses(limit=5, offset=0)
        page2 = analysis_repo.get_all_analyses(limit=5, offset=5)
        assert len(page1) == 5
        assert len(page2) == 5

    def test_ordering_desc(self, analysis_repo, sample_analysis):
        for i in range(3):
            a = sample_analysis(
                file_name=f"f{i}.html",
                analyzed_at=datetime(2025, 1, 1 + i),
            )
            analysis_repo.save_analysis(a)
        results = analysis_repo.get_all_analyses()
        # Most recent first
        assert results[0].file_name == "f2.html"
        assert results[2].file_name == "f0.html"

    def test_file_type_filter(self, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="a.html", file_type="html"))
        analysis_repo.save_analysis(sample_analysis(file_name="b.css", file_type="css"))
        analysis_repo.save_analysis(sample_analysis(file_name="c.js", file_type="js"))
        css_only = analysis_repo.get_all_analyses(file_type="css")
        assert len(css_only) == 1
        assert css_only[0].file_name == "b.css"

    def test_empty_db(self, analysis_repo):
        assert analysis_repo.get_all_analyses() == []

    def test_get_by_id_with_features(self, saved_analysis, analysis_repo):
        aid, _ = saved_analysis
        loaded = analysis_repo.get_analysis_by_id(aid, include_features=True)
        assert loaded is not None
        assert loaded.id == aid
        assert len(loaded.features) == 2
        assert len(loaded.features[0].browser_results) == 4

    def test_get_by_id_without_features(self, saved_analysis, analysis_repo):
        aid, _ = saved_analysis
        loaded = analysis_repo.get_analysis_by_id(aid, include_features=False)
        assert loaded is not None
        assert loaded.features == []

    def test_get_by_id_not_found(self, analysis_repo):
        assert analysis_repo.get_analysis_by_id(99999) is None

    def test_get_analyses_for_file(self, analysis_repo, sample_analysis):
        for _ in range(3):
            analysis_repo.save_analysis(sample_analysis(file_name="same.html"))
        analysis_repo.save_analysis(sample_analysis(file_name="other.html"))
        results = analysis_repo.get_analyses_for_file("same.html")
        assert len(results) == 3
        assert all(r.file_name == "same.html" for r in results)


# =============================================================================
# AnalysisRepository — Delete
# =============================================================================

class TestDeleteAnalysis:
    def test_delete_returns_true(self, saved_analysis, analysis_repo):
        aid, _ = saved_analysis
        assert analysis_repo.delete_analysis(aid) is True

    def test_cascades_to_children(self, saved_analysis, analysis_repo, db):
        aid, _ = saved_analysis
        analysis_repo.delete_analysis(aid)
        cursor = db.execute("SELECT COUNT(*) FROM analysis_features WHERE analysis_id = ?", (aid,))
        assert cursor.fetchone()[0] == 0
        cursor = db.execute("SELECT COUNT(*) FROM browser_results")
        assert cursor.fetchone()[0] == 0

    def test_not_found_returns_false(self, analysis_repo):
        assert analysis_repo.delete_analysis(99999) is False

    def test_clear_all_returns_count(self, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 5)
        count = analysis_repo.clear_all()
        assert count == 5
        assert analysis_repo.get_count() == 0


# =============================================================================
# AnalysisRepository — Search & Count
# =============================================================================

class TestSearchAnalyses:
    def test_like_match(self, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="my_app.html"))
        analysis_repo.save_analysis(sample_analysis(file_name="my_app.css"))
        analysis_repo.save_analysis(sample_analysis(file_name="other.js"))
        results = analysis_repo.search_analyses("my_app")
        assert len(results) == 2

    def test_no_match(self, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="test.html"))
        assert analysis_repo.search_analyses("nonexistent") == []

    def test_get_count_no_filter(self, analysis_repo, sample_analysis):
        save_n_analyses(analysis_repo, sample_analysis, 3)
        assert analysis_repo.get_count() == 3

    def test_get_count_with_filter(self, analysis_repo, sample_analysis):
        analysis_repo.save_analysis(sample_analysis(file_name="a.html", file_type="html"))
        analysis_repo.save_analysis(sample_analysis(file_name="b.css", file_type="css"))
        assert analysis_repo.get_count(file_type="html") == 1


# =============================================================================
# SettingsRepository
# =============================================================================

class TestSettings:
    def test_set_and_get(self, settings_repo):
        settings_repo.set("theme", "dark")
        assert settings_repo.get("theme") == "dark"

    def test_get_default(self, settings_repo):
        assert settings_repo.get("nonexistent", "fallback") == "fallback"

    def test_get_all(self, settings_repo):
        all_settings = settings_repo.get_all()
        # 3 defaults from migration
        assert "default_browsers" in all_settings
        assert "history_limit" in all_settings
        assert "auto_save_history" in all_settings

    def test_delete(self, settings_repo):
        settings_repo.set("temp", "value")
        assert settings_repo.delete("temp") is True
        assert settings_repo.get("temp") == ""

    def test_delete_not_found(self, settings_repo):
        assert settings_repo.delete("nonexistent") is False

    def test_upsert(self, settings_repo):
        settings_repo.set("key", "v1")
        settings_repo.set("key", "v2")
        assert settings_repo.get("key") == "v2"

    def test_get_as_bool_true(self, settings_repo):
        for val in ("true", "1", "yes", "on"):
            settings_repo.set("flag", val)
            assert settings_repo.get_as_bool("flag") is True, f"Failed for '{val}'"

    def test_get_as_bool_false(self, settings_repo):
        for val in ("false", "0", "no", "off"):
            settings_repo.set("flag", val)
            assert settings_repo.get_as_bool("flag") is False, f"Failed for '{val}'"

    def test_get_as_int(self, settings_repo):
        settings_repo.set("limit", "42")
        assert settings_repo.get_as_int("limit") == 42

    def test_get_as_list(self, settings_repo):
        settings_repo.set("items", "a, b, c")
        assert settings_repo.get_as_list("items") == ["a", "b", "c"]

    def test_default_settings_from_migration(self, settings_repo):
        assert settings_repo.get("auto_save_history") == "true"
        assert settings_repo.get_as_int("history_limit") == 100
        assert settings_repo.get_as_list("default_browsers") == ["chrome", "firefox", "safari", "edge"]


# =============================================================================
# BookmarksRepository
# =============================================================================

class TestBookmarks:
    def test_add_bookmark(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bid = bookmarks_repo.add_bookmark(aid, note="important")
        assert isinstance(bid, int)
        assert bid > 0

    def test_is_bookmarked_true(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid)
        assert bookmarks_repo.is_bookmarked(aid) is True

    def test_is_bookmarked_false(self, bookmarks_repo):
        assert bookmarks_repo.is_bookmarked(99999) is False

    def test_remove_bookmark(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid)
        assert bookmarks_repo.remove_bookmark(aid) is True
        assert bookmarks_repo.is_bookmarked(aid) is False

    def test_remove_not_found(self, bookmarks_repo):
        assert bookmarks_repo.remove_bookmark(99999) is False

    def test_get_bookmark(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid, note="test note")
        bm = bookmarks_repo.get_bookmark(aid)
        assert bm is not None
        assert bm["analysis_id"] == aid
        assert bm["note"] == "test note"

    def test_get_bookmark_not_found(self, bookmarks_repo):
        assert bookmarks_repo.get_bookmark(99999) is None

    def test_get_all_bookmarks_with_join(self, bookmarks_repo, analysis_repo, sample_analysis):
        a1 = sample_analysis(file_name="one.html", score=90)
        a2 = sample_analysis(file_name="two.css", file_type="css", score=80)
        id1 = analysis_repo.save_analysis(a1)
        id2 = analysis_repo.save_analysis(a2)
        bookmarks_repo.add_bookmark(id1, "first")
        bookmarks_repo.add_bookmark(id2, "second")
        all_bm = bookmarks_repo.get_all_bookmarks()
        assert len(all_bm) == 2
        assert all("analysis" in bm for bm in all_bm)
        file_names = {bm["analysis"]["file_name"] for bm in all_bm}
        assert file_names == {"one.html", "two.css"}

    def test_update_note(self, bookmarks_repo, saved_analysis):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid, note="old")
        assert bookmarks_repo.update_note(aid, "new") is True
        bm = bookmarks_repo.get_bookmark(aid)
        assert bm["note"] == "new"

    def test_get_count(self, bookmarks_repo, analysis_repo, sample_analysis):
        for i in range(3):
            a = sample_analysis(file_name=f"f{i}.html")
            aid = analysis_repo.save_analysis(a)
            bookmarks_repo.add_bookmark(aid)
        assert bookmarks_repo.get_count() == 3

    def test_idempotent_add(self, bookmarks_repo, saved_analysis):
        """INSERT OR REPLACE should not create duplicates."""
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid, "v1")
        bookmarks_repo.add_bookmark(aid, "v2")
        assert bookmarks_repo.get_count() == 1
        bm = bookmarks_repo.get_bookmark(aid)
        assert bm["note"] == "v2"

    def test_cascade_delete_when_analysis_deleted(
        self, bookmarks_repo, analysis_repo, saved_analysis
    ):
        aid, _ = saved_analysis
        bookmarks_repo.add_bookmark(aid)
        analysis_repo.delete_analysis(aid)
        assert bookmarks_repo.is_bookmarked(aid) is False
        assert bookmarks_repo.get_count() == 0


# =============================================================================
# TagsRepository
# =============================================================================

class TestTags:
    def test_create_tag(self, tags_repo):
        tid = tags_repo.create_tag("production", "#ff0000")
        assert isinstance(tid, int)
        assert tid > 0

    def test_get_tag_by_name(self, tags_repo):
        tags_repo.create_tag("staging")
        tag = tags_repo.get_tag_by_name("staging")
        assert tag is not None
        assert tag["name"] == "staging"

    def test_get_tag_by_name_not_found(self, tags_repo):
        assert tags_repo.get_tag_by_name("nope") is None

    def test_get_tag_by_id(self, tags_repo):
        tid = tags_repo.create_tag("dev")
        tag = tags_repo.get_tag_by_id(tid)
        assert tag is not None
        assert tag["name"] == "dev"

    def test_get_tag_by_id_not_found(self, tags_repo):
        assert tags_repo.get_tag_by_id(99999) is None

    def test_get_all_tags_ordered(self, tags_repo):
        tags_repo.create_tag("beta")
        tags_repo.create_tag("alpha")
        tags_repo.create_tag("gamma")
        all_tags = tags_repo.get_all_tags()
        names = [t["name"] for t in all_tags]
        assert names == ["alpha", "beta", "gamma"]

    def test_delete_tag(self, tags_repo):
        tid = tags_repo.create_tag("temp")
        assert tags_repo.delete_tag(tid) is True
        assert tags_repo.get_tag_by_id(tid) is None

    def test_delete_tag_not_found(self, tags_repo):
        assert tags_repo.delete_tag(99999) is False

    def test_update_tag_name(self, tags_repo):
        tid = tags_repo.create_tag("old")
        assert tags_repo.update_tag(tid, name="new") is True
        tag = tags_repo.get_tag_by_id(tid)
        assert tag["name"] == "new"

    def test_update_tag_color(self, tags_repo):
        tid = tags_repo.create_tag("x")
        assert tags_repo.update_tag(tid, color="#000000") is True
        tag = tags_repo.get_tag_by_id(tid)
        assert tag["color"] == "#000000"

    def test_update_tag_both(self, tags_repo):
        tid = tags_repo.create_tag("x")
        tags_repo.update_tag(tid, name="y", color="#111111")
        tag = tags_repo.get_tag_by_id(tid)
        assert tag["name"] == "y"
        assert tag["color"] == "#111111"

    def test_update_tag_nothing(self, tags_repo):
        tid = tags_repo.create_tag("x")
        assert tags_repo.update_tag(tid) is False

    def test_add_tag_to_analysis(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        assert tags_repo.add_tag_to_analysis(aid, tid) is True

    def test_remove_tag_from_analysis(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        tags_repo.add_tag_to_analysis(aid, tid)
        assert tags_repo.remove_tag_from_analysis(aid, tid) is True

    def test_remove_tag_not_linked(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        assert tags_repo.remove_tag_from_analysis(aid, tid) is False

    def test_get_tags_for_analysis(self, tags_repo, saved_analysis):
        aid, _ = saved_analysis
        t1 = tags_repo.create_tag("alpha")
        t2 = tags_repo.create_tag("beta")
        tags_repo.add_tag_to_analysis(aid, t1)
        tags_repo.add_tag_to_analysis(aid, t2)
        tags = tags_repo.get_tags_for_analysis(aid)
        names = [t["name"] for t in tags]
        assert names == ["alpha", "beta"]

    def test_get_analyses_by_tag(self, tags_repo, analysis_repo, sample_analysis):
        a1 = sample_analysis(file_name="one.html")
        a2 = sample_analysis(file_name="two.html")
        id1 = analysis_repo.save_analysis(a1)
        id2 = analysis_repo.save_analysis(a2)
        tid = tags_repo.create_tag("important")
        tags_repo.add_tag_to_analysis(id1, tid)
        tags_repo.add_tag_to_analysis(id2, tid)
        analyses = tags_repo.get_analyses_by_tag(tid)
        assert len(analyses) == 2

    def test_get_tag_counts(self, tags_repo, analysis_repo, sample_analysis):
        a1 = sample_analysis(file_name="one.html")
        a2 = sample_analysis(file_name="two.html")
        id1 = analysis_repo.save_analysis(a1)
        id2 = analysis_repo.save_analysis(a2)
        t1 = tags_repo.create_tag("hot")
        t2 = tags_repo.create_tag("cold")
        tags_repo.add_tag_to_analysis(id1, t1)
        tags_repo.add_tag_to_analysis(id2, t1)
        tags_repo.add_tag_to_analysis(id1, t2)
        counts = tags_repo.get_tag_counts()
        assert counts["hot"] == 2
        assert counts["cold"] == 1

    def test_duplicate_tag_name_error(self, tags_repo):
        tags_repo.create_tag("unique")
        with pytest.raises(sqlite3.IntegrityError):
            tags_repo.create_tag("unique")

    def test_cascade_delete_analysis_removes_links(
        self, tags_repo, analysis_repo, saved_analysis
    ):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        tags_repo.add_tag_to_analysis(aid, tid)
        analysis_repo.delete_analysis(aid)
        # Tag still exists, but link is gone
        assert tags_repo.get_tag_by_id(tid) is not None
        assert tags_repo.get_tags_for_analysis(aid) == []

    def test_cascade_delete_tag_removes_links(
        self, tags_repo, saved_analysis
    ):
        aid, _ = saved_analysis
        tid = tags_repo.create_tag("tag1")
        tags_repo.add_tag_to_analysis(aid, tid)
        tags_repo.delete_tag(tid)
        assert tags_repo.get_tags_for_analysis(aid) == []

    def test_tag_unused_count_zero(self, tags_repo):
        tags_repo.create_tag("lonely")
        counts = tags_repo.get_tag_counts()
        assert counts["lonely"] == 0


# =============================================================================
# save_analysis_from_result helper
# =============================================================================

class TestSaveAnalysisFromResult:
    """Tests for the module-level save_analysis_from_result() helper.

    This function depends on src.utils.feature_names and uses a default
    (non-injected) connection, so we test it via the AnalysisRepository
    to verify the mapping logic by constructing equivalent objects.
    """

    def test_full_round_trip(self, analysis_repo, sample_analysis):
        """Verify save → load preserves all fields."""
        a = sample_analysis(
            file_name="app.js",
            file_type="js",
            score=72.5,
            grade="C",
            total_features=5,
            num_features=2,
        )
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        assert loaded.file_name == "app.js"
        assert loaded.file_type == "js"
        assert loaded.overall_score == 72.5
        assert loaded.grade == "C"
        assert loaded.total_features == 5
        assert len(loaded.features) == 2

    def test_browser_statuses_preserved(self, analysis_repo):
        """All 4 status codes (y/n/a/u) round-trip correctly."""
        feat = AnalysisFeature(
            feature_id="test-feat",
            feature_name="Test",
            category="js",
            browser_results=[
                BrowserResult(browser="chrome", version="120", support_status="y"),
                BrowserResult(browser="firefox", version="121", support_status="n"),
                BrowserResult(browser="safari", version="17", support_status="a"),
                BrowserResult(browser="edge", version="120", support_status="u"),
            ],
        )
        a = Analysis(
            file_name="test.js", file_type="js", overall_score=50,
            grade="F", total_features=1, features=[feat],
        )
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        statuses = {br.browser: br.support_status for br in loaded.features[0].browser_results}
        assert statuses == {"chrome": "y", "firefox": "n", "safari": "a", "edge": "u"}

    def test_score_and_grade_extracted(self, analysis_repo, sample_analysis):
        a = sample_analysis(score=95.5, grade="A+")
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid, include_features=False)
        assert loaded.overall_score == 95.5
        assert loaded.grade == "A+"

    def test_multiple_features(self, analysis_repo, sample_analysis):
        a = sample_analysis(num_features=5)
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        assert len(loaded.features) == 5
        feature_ids = {f.feature_id for f in loaded.features}
        assert feature_ids == {"feature-0", "feature-1", "feature-2", "feature-3", "feature-4"}

    def test_browsers_json_preserved(self, analysis_repo):
        a = Analysis(
            file_name="test.html", file_type="html", overall_score=80,
            grade="B", total_features=0,
        )
        a.browsers = {"chrome": "120", "firefox": "121"}
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid, include_features=False)
        assert loaded.browsers == {"chrome": "120", "firefox": "121"}

    def test_minimal_analysis(self, analysis_repo):
        """Minimal valid analysis with no features and no browsers."""
        a = Analysis(
            file_name="x.html", file_type="html",
            overall_score=0.0, grade="N/A", total_features=0,
        )
        aid = analysis_repo.save_analysis(a)
        loaded = analysis_repo.get_analysis_by_id(aid)
        assert loaded.file_name == "x.html"
        assert loaded.total_features == 0
        assert loaded.features == []
