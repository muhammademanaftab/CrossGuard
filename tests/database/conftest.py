"""Shared fixtures for database tests.

All tests use in-memory SQLite — zero disk I/O, zero pollution of crossguard.db.
"""

import sqlite3
import pytest
from datetime import datetime, timedelta

from src.database.migrations import create_tables
from src.database.models import Analysis, AnalysisFeature, BrowserResult
from src.database.repositories import (
    AnalysisRepository,
    SettingsRepository,
    BookmarksRepository,
    TagsRepository,
)
from src.database.statistics import StatisticsService


@pytest.fixture
def db():
    """Fresh in-memory SQLite database with all tables created."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)
    yield conn
    conn.close()


@pytest.fixture
def analysis_repo(db):
    """AnalysisRepository backed by in-memory DB."""
    return AnalysisRepository(conn=db)


@pytest.fixture
def settings_repo(db):
    """SettingsRepository backed by in-memory DB."""
    return SettingsRepository(conn=db)


@pytest.fixture
def bookmarks_repo(db):
    """BookmarksRepository backed by in-memory DB."""
    return BookmarksRepository(conn=db)


@pytest.fixture
def tags_repo(db):
    """TagsRepository backed by in-memory DB."""
    return TagsRepository(conn=db)


@pytest.fixture
def stats_service(db):
    """StatisticsService backed by in-memory DB."""
    return StatisticsService(conn=db)


@pytest.fixture
def sample_analysis():
    """Factory that creates Analysis objects with features and browser results."""
    def _make(
        file_name="test.html",
        file_type="html",
        score=85.0,
        grade="B",
        total_features=3,
        num_features=2,
        analyzed_at=None,
    ):
        features = []
        for i in range(num_features):
            feature = AnalysisFeature(
                feature_id=f"feature-{i}",
                feature_name=f"Feature {i}",
                category=file_type if file_type != "htm" else "html",
                browser_results=[
                    BrowserResult(browser="chrome", version="120", support_status="y"),
                    BrowserResult(browser="firefox", version="121", support_status="y"),
                    BrowserResult(browser="safari", version="17", support_status="a"),
                    BrowserResult(browser="edge", version="120", support_status="n"),
                ],
            )
            features.append(feature)

        analysis = Analysis(
            file_name=file_name,
            file_type=file_type,
            overall_score=score,
            grade=grade,
            total_features=total_features,
            file_path=f"/path/to/{file_name}",
            features=features,
        )
        if analyzed_at is not None:
            analysis.analyzed_at = analyzed_at
        return analysis

    return _make


@pytest.fixture
def saved_analysis(analysis_repo, sample_analysis):
    """Pre-saved analysis — returns (analysis_id, Analysis object)."""
    analysis = sample_analysis()
    aid = analysis_repo.save_analysis(analysis)
    return aid, analysis


def save_n_analyses(repo, factory, n, **overrides):
    """Helper: save N analyses and return their IDs."""
    ids = []
    for i in range(n):
        kw = {
            "file_name": f"file_{i}.html",
            "score": 50.0 + i * 10,
            "grade": ["F", "D", "C", "B", "A"][min(i, 4)],
        }
        kw.update(overrides)
        a = factory(**kw)
        ids.append(repo.save_analysis(a))
    return ids
