"""Tests for database models (pure dataclass tests — no DB, no I/O)."""

import json
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


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mock_row(data: dict):
    """Create a mock sqlite3.Row-like object from a dict."""
    row = MagicMock()
    row.__getitem__ = lambda self, key: data[key]
    row.keys = lambda: data.keys()
    return row


# =============================================================================
# BrowserResult
# =============================================================================

class TestBrowserResult:
    def test_fields(self):
        br = BrowserResult(browser="chrome", support_status="y", version="120")
        assert br.browser == "chrome"
        assert br.support_status == "y"
        assert br.version == "120"
        assert br.id is None
        assert br.analysis_feature_id is None

    def test_to_dict(self):
        br = BrowserResult(browser="firefox", support_status="a", version="121", id=5, analysis_feature_id=3)
        d = br.to_dict()
        assert d["browser"] == "firefox"
        assert d["support_status"] == "a"
        assert d["version"] == "121"
        assert d["id"] == 5
        assert d["analysis_feature_id"] == 3

    def test_from_row(self):
        row = _mock_row({
            "id": 10,
            "analysis_feature_id": 2,
            "browser": "safari",
            "version": "17",
            "support_status": "n",
        })
        br = BrowserResult.from_row(row)
        assert br.id == 10
        assert br.browser == "safari"
        assert br.version == "17"
        assert br.support_status == "n"

    def test_from_row_none_version(self):
        row = _mock_row({
            "id": 1,
            "analysis_feature_id": 1,
            "browser": "edge",
            "version": None,
            "support_status": "y",
        })
        br = BrowserResult.from_row(row)
        assert br.version == ""


# =============================================================================
# AnalysisFeature
# =============================================================================

class TestAnalysisFeature:
    def test_fields(self):
        af = AnalysisFeature(feature_id="css-grid", category="css")
        assert af.feature_id == "css-grid"
        assert af.category == "css"
        assert af.feature_name == ""
        assert af.id is None
        assert af.analysis_id is None
        assert af.browser_results == []

    def test_to_dict_with_nested_results(self):
        br = BrowserResult(browser="chrome", support_status="y", version="120")
        af = AnalysisFeature(
            feature_id="flexbox",
            category="css",
            feature_name="Flexbox",
            id=1,
            analysis_id=5,
            browser_results=[br],
        )
        d = af.to_dict()
        assert d["feature_id"] == "flexbox"
        assert d["feature_name"] == "Flexbox"
        assert len(d["browser_results"]) == 1
        assert d["browser_results"][0]["browser"] == "chrome"

    def test_from_row(self):
        row = _mock_row({
            "id": 3,
            "analysis_id": 7,
            "feature_id": "promises",
            "feature_name": "Promises",
            "category": "js",
        })
        af = AnalysisFeature.from_row(row)
        assert af.id == 3
        assert af.analysis_id == 7
        assert af.feature_id == "promises"
        assert af.browser_results == []

    def test_from_row_none_feature_name(self):
        row = _mock_row({
            "id": 1,
            "analysis_id": 1,
            "feature_id": "unknown",
            "feature_name": None,
            "category": "html",
        })
        af = AnalysisFeature.from_row(row)
        assert af.feature_name == ""


# =============================================================================
# Analysis
# =============================================================================

class TestAnalysis:
    def test_fields(self):
        a = Analysis(
            file_name="test.css",
            file_type="css",
            overall_score=92.5,
            grade="A",
            total_features=10,
        )
        assert a.file_name == "test.css"
        assert a.file_type == "css"
        assert a.overall_score == 92.5
        assert a.grade == "A"
        assert a.total_features == 10
        assert a.file_path == ""
        assert a.id is None
        assert a.features == []

    def test_post_init_sets_analyzed_at(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0)
        assert a.analyzed_at is not None
        assert isinstance(a.analyzed_at, datetime)

    def test_post_init_preserves_analyzed_at(self):
        ts = datetime(2025, 1, 1, 12, 0, 0)
        a = Analysis(
            file_name="x.html", file_type="html", overall_score=0,
            grade="F", total_features=0, analyzed_at=ts,
        )
        assert a.analyzed_at == ts

    def test_browsers_property_get(self):
        a = Analysis(
            file_name="x.html", file_type="html", overall_score=0,
            grade="F", total_features=0,
            browsers_json='{"chrome": "120", "firefox": "121"}',
        )
        assert a.browsers == {"chrome": "120", "firefox": "121"}

    def test_browsers_property_get_invalid_json(self):
        a = Analysis(
            file_name="x.html", file_type="html", overall_score=0,
            grade="F", total_features=0, browsers_json="not json",
        )
        assert a.browsers == {}

    def test_browsers_property_set(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0)
        a.browsers = {"safari": "17"}
        assert json.loads(a.browsers_json) == {"safari": "17"}

    def test_to_dict_nested(self):
        br = BrowserResult(browser="chrome", support_status="y", version="120")
        feat = AnalysisFeature(feature_id="grid", category="css", browser_results=[br])
        a = Analysis(
            file_name="style.css", file_type="css", overall_score=88.0,
            grade="B+", total_features=5, id=1, features=[feat],
        )
        d = a.to_dict()
        assert d["id"] == 1
        assert d["file_name"] == "style.css"
        assert len(d["features"]) == 1
        assert d["features"][0]["feature_id"] == "grid"
        assert "analyzed_at" in d

    def test_from_row_iso_format(self):
        ts = "2025-06-15T14:30:00"
        row = _mock_row({
            "id": 1,
            "file_name": "a.html",
            "file_path": "/tmp/a.html",
            "file_type": "html",
            "overall_score": 75.0,
            "grade": "C",
            "total_features": 3,
            "analyzed_at": ts,
            "browsers_json": "{}",
        })
        a = Analysis.from_row(row)
        assert a.id == 1
        assert a.analyzed_at == datetime.fromisoformat(ts)

    def test_from_row_sqlite_format(self):
        ts = "2025-06-15 14:30:00"
        row = _mock_row({
            "id": 2,
            "file_name": "b.css",
            "file_path": None,
            "file_type": "css",
            "overall_score": 60.0,
            "grade": "D",
            "total_features": 1,
            "analyzed_at": ts,
            "browsers_json": None,
        })
        a = Analysis.from_row(row)
        assert a.analyzed_at == datetime(2025, 6, 15, 14, 30, 0)
        assert a.file_path == ""
        assert a.browsers_json == "{}"

    def test_from_row_malformed_timestamp(self):
        row = _mock_row({
            "id": 3,
            "file_name": "c.js",
            "file_path": "",
            "file_type": "js",
            "overall_score": 50.0,
            "grade": "F",
            "total_features": 0,
            "analyzed_at": "not-a-date",
            "browsers_json": "{}",
        })
        a = Analysis.from_row(row)
        # Falls back to datetime.now()
        assert isinstance(a.analyzed_at, datetime)

    def test_from_row_none_timestamp(self):
        row = _mock_row({
            "id": 4,
            "file_name": "d.html",
            "file_path": "",
            "file_type": "html",
            "overall_score": 0.0,
            "grade": "F",
            "total_features": 0,
            "analyzed_at": None,
            "browsers_json": "{}",
        })
        a = Analysis.from_row(row)
        # __post_init__ sets analyzed_at to now() when None
        assert isinstance(a.analyzed_at, datetime)


class TestAnalysisFormattedDate:
    def test_today(self):
        a = Analysis(
            file_name="x.html", file_type="html", overall_score=0,
            grade="F", total_features=0, analyzed_at=datetime.now(),
        )
        result = a.get_formatted_date()
        assert result.startswith("Today")

    def test_yesterday(self):
        a = Analysis(
            file_name="x.html", file_type="html", overall_score=0,
            grade="F", total_features=0,
            analyzed_at=datetime.now() - timedelta(days=1),
        )
        assert a.get_formatted_date() == "Yesterday"

    def test_days_ago(self):
        a = Analysis(
            file_name="x.html", file_type="html", overall_score=0,
            grade="F", total_features=0,
            analyzed_at=datetime.now() - timedelta(days=3),
        )
        assert a.get_formatted_date() == "3 days ago"

    def test_old_date(self):
        a = Analysis(
            file_name="x.html", file_type="html", overall_score=0,
            grade="F", total_features=0,
            analyzed_at=datetime(2024, 1, 15),
        )
        assert "Jan 15, 2024" in a.get_formatted_date()

    def test_none_date(self):
        a = Analysis(
            file_name="x.html", file_type="html", overall_score=0,
            grade="F", total_features=0,
        )
        a.analyzed_at = None
        assert a.get_formatted_date() == "Unknown"


class TestAnalysisFileTypeIcon:
    def test_html_icon(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=0, grade="F", total_features=0)
        assert a.get_file_type_icon() == "\u25B6"

    def test_css_icon(self):
        a = Analysis(file_name="x.css", file_type="css", overall_score=0, grade="F", total_features=0)
        assert a.get_file_type_icon() == "\u25C6"

    def test_js_icon(self):
        a = Analysis(file_name="x.js", file_type="js", overall_score=0, grade="F", total_features=0)
        assert a.get_file_type_icon() == "\u2605"

    def test_unknown_icon(self):
        a = Analysis(file_name="x.txt", file_type="txt", overall_score=0, grade="F", total_features=0)
        assert a.get_file_type_icon() == "\u25A0"


# =============================================================================
# Setting
# =============================================================================

class TestSetting:
    def test_fields(self):
        s = Setting(key="theme", value="dark")
        assert s.key == "theme"
        assert s.value == "dark"
        assert s.updated_at is None

    def test_to_dict(self):
        ts = datetime(2025, 1, 1)
        s = Setting(key="k", value="v", updated_at=ts)
        d = s.to_dict()
        assert d["key"] == "k"
        assert d["value"] == "v"
        assert d["updated_at"] == ts.isoformat()

    def test_to_dict_none_updated_at(self):
        s = Setting(key="k", value="v")
        assert s.to_dict()["updated_at"] is None

    def test_from_row(self):
        row = _mock_row({"key": "lang", "value": "en", "updated_at": "2025-03-01T10:00:00"})
        s = Setting.from_row(row)
        assert s.key == "lang"
        assert s.value == "en"
        assert isinstance(s.updated_at, datetime)

    def test_from_row_none_updated_at(self):
        row = _mock_row({"key": "k", "value": "v", "updated_at": None})
        s = Setting.from_row(row)
        assert s.updated_at is None

    def test_get_as_bool_true_values(self):
        for val in ("true", "1", "yes", "on"):
            s = Setting(key="k", value=val)
            assert s.get_as_bool() is True, f"Expected True for '{val}'"

    def test_get_as_bool_false_values(self):
        for val in ("false", "0", "no", "off", "random"):
            s = Setting(key="k", value=val)
            assert s.get_as_bool() is False, f"Expected False for '{val}'"

    def test_get_as_int(self):
        s = Setting(key="limit", value="100")
        assert s.get_as_int() == 100

    def test_get_as_int_invalid(self):
        s = Setting(key="limit", value="abc")
        assert s.get_as_int() == 0

    def test_get_as_list(self):
        s = Setting(key="browsers", value="chrome, firefox, safari")
        assert s.get_as_list() == ["chrome", "firefox", "safari"]

    def test_get_as_list_empty(self):
        s = Setting(key="browsers", value="")
        assert s.get_as_list() == []


# =============================================================================
# Bookmark
# =============================================================================

class TestBookmark:
    def test_fields(self):
        b = Bookmark(analysis_id=1, note="important")
        assert b.analysis_id == 1
        assert b.note == "important"
        assert b.id is None
        assert b.analysis is None

    def test_post_init_sets_created_at(self):
        b = Bookmark(analysis_id=1)
        assert b.created_at is not None
        assert isinstance(b.created_at, datetime)

    def test_to_dict_without_analysis(self):
        b = Bookmark(analysis_id=1, note="test", id=5)
        d = b.to_dict()
        assert d["id"] == 5
        assert d["analysis_id"] == 1
        assert d["note"] == "test"
        assert "analysis" not in d

    def test_to_dict_with_analysis(self):
        a = Analysis(file_name="x.html", file_type="html", overall_score=90, grade="A", total_features=5)
        b = Bookmark(analysis_id=1, id=5, analysis=a)
        d = b.to_dict()
        assert "analysis" in d
        assert d["analysis"]["file_name"] == "x.html"

    def test_from_row(self):
        row = _mock_row({
            "id": 10,
            "analysis_id": 3,
            "note": "nice",
            "created_at": "2025-05-01T12:00:00",
        })
        b = Bookmark.from_row(row)
        assert b.id == 10
        assert b.analysis_id == 3
        assert b.note == "nice"
        assert isinstance(b.created_at, datetime)

    def test_from_row_none_note(self):
        row = _mock_row({
            "id": 1,
            "analysis_id": 1,
            "note": None,
            "created_at": None,
        })
        b = Bookmark.from_row(row)
        assert b.note == ""
        # __post_init__ sets created_at to now() when None
        assert isinstance(b.created_at, datetime)


# =============================================================================
# Tag
# =============================================================================

class TestTag:
    def test_fields(self):
        t = Tag(name="production")
        assert t.name == "production"
        assert t.color == "#58a6ff"
        assert t.id is None

    def test_post_init_sets_created_at(self):
        t = Tag(name="test")
        assert isinstance(t.created_at, datetime)

    def test_to_dict(self):
        t = Tag(name="critical", color="#ff0000", id=3)
        d = t.to_dict()
        assert d["name"] == "critical"
        assert d["color"] == "#ff0000"
        assert d["id"] == 3

    def test_from_row(self):
        row = _mock_row({
            "id": 7,
            "name": "staging",
            "color": "#00ff00",
            "created_at": "2025-02-01T10:00:00",
        })
        t = Tag.from_row(row)
        assert t.id == 7
        assert t.name == "staging"
        assert t.color == "#00ff00"

    def test_from_row_none_color(self):
        row = _mock_row({
            "id": 1,
            "name": "x",
            "color": None,
            "created_at": None,
        })
        t = Tag.from_row(row)
        assert t.color == "#58a6ff"
        # __post_init__ sets created_at to now() when None
        assert isinstance(t.created_at, datetime)


# =============================================================================
# AnalysisTag
# =============================================================================

class TestAnalysisTag:
    def test_fields(self):
        at = AnalysisTag(analysis_id=1, tag_id=2)
        assert at.analysis_id == 1
        assert at.tag_id == 2
        assert at.created_at is None

    def test_to_dict(self):
        ts = datetime(2025, 3, 1)
        at = AnalysisTag(analysis_id=1, tag_id=2, created_at=ts)
        d = at.to_dict()
        assert d["analysis_id"] == 1
        assert d["tag_id"] == 2
        assert d["created_at"] == ts.isoformat()

    def test_from_row(self):
        row = _mock_row({
            "analysis_id": 5,
            "tag_id": 8,
            "created_at": "2025-06-01T10:00:00",
        })
        at = AnalysisTag.from_row(row)
        assert at.analysis_id == 5
        assert at.tag_id == 8
        assert isinstance(at.created_at, datetime)

    def test_from_row_none_created_at(self):
        row = _mock_row({
            "analysis_id": 1,
            "tag_id": 1,
            "created_at": None,
        })
        at = AnalysisTag.from_row(row)
        assert at.created_at is None
