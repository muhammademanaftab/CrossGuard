"""Tests for database migrations — schema creation, versioning, drop, reset."""

import sqlite3
import pytest

from src.database.migrations import (
    create_tables,
    drop_tables,
    reset_database,
    get_schema_version,
    get_table_info,
    SCHEMA_VERSION,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _fresh_conn():
    """In-memory connection with row_factory and foreign keys."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_names(conn):
    """Return set of user table names in the database."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    return {row[0] for row in cursor.fetchall()}


def _index_names(conn):
    """Return set of index names in the database."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
    )
    return {row[0] for row in cursor.fetchall()}


# =============================================================================
# create_tables
# =============================================================================

class TestCreateTables:
    def test_all_tables_created(self, db):
        expected = {
            "schema_version",
            "analyses",
            "analysis_features",
            "browser_results",
            "settings",
            "bookmarks",
            "tags",
            "analysis_tags",
        }
        assert _table_names(db) == expected

    def test_indexes_created(self, db):
        indexes = _index_names(db)
        assert "idx_analyses_date" in indexes
        assert "idx_analyses_file" in indexes
        assert "idx_analyses_type" in indexes
        assert "idx_features_analysis" in indexes
        assert "idx_bookmarks_analysis" in indexes
        assert "idx_tags_name" in indexes
        assert "idx_analysis_tags_analysis" in indexes
        assert "idx_analysis_tags_tag" in indexes

    def test_schema_version_is_current(self, db):
        assert get_schema_version(db) == SCHEMA_VERSION

    def test_idempotent(self, db):
        """Calling create_tables twice should not error or change schema."""
        create_tables(db)
        create_tables(db)
        assert get_schema_version(db) == SCHEMA_VERSION
        assert len(_table_names(db)) == 8


# =============================================================================
# Schema versioning
# =============================================================================

class TestMigrationVersioning:
    def test_fresh_db_version_zero(self):
        conn = _fresh_conn()
        # No schema_version table yet
        assert get_schema_version(conn) == 0
        conn.close()

    def test_after_create_version_is_current(self, db):
        assert get_schema_version(db) == 2

    def test_schema_version_constant(self):
        assert SCHEMA_VERSION == 2


# =============================================================================
# drop_tables
# =============================================================================

class TestDropTables:
    def test_all_tables_gone(self, db):
        drop_tables(db)
        remaining = _table_names(db)
        assert len(remaining) == 0

    def test_get_table_info_after_drop(self, db):
        drop_tables(db)
        info = get_table_info(db)
        for table_name, count in info.items():
            assert count == -1, f"Table '{table_name}' should not exist"


# =============================================================================
# reset_database
# =============================================================================

class TestResetDatabase:
    def test_tables_recreated(self, db):
        # Insert some data
        db.execute(
            "INSERT INTO analyses (file_name, file_type, overall_score, grade, total_features) "
            "VALUES ('x.html', 'html', 90, 'A', 5)"
        )
        reset_database(db)
        assert _table_names(db) == {
            "schema_version", "analyses", "analysis_features", "browser_results",
            "settings", "bookmarks", "tags", "analysis_tags",
        }

    def test_data_wiped(self, db):
        db.execute(
            "INSERT INTO analyses (file_name, file_type, overall_score, grade, total_features) "
            "VALUES ('x.html', 'html', 90, 'A', 5)"
        )
        reset_database(db)
        cursor = db.execute("SELECT COUNT(*) FROM analyses")
        assert cursor.fetchone()[0] == 0


# =============================================================================
# get_table_info
# =============================================================================

class TestGetTableInfo:
    def test_correct_table_names(self, db):
        info = get_table_info(db)
        expected_tables = {
            "analyses", "analysis_features", "browser_results",
            "settings", "bookmarks", "tags", "analysis_tags",
        }
        assert set(info.keys()) == expected_tables

    def test_row_counts_match(self, db):
        # Insert one analysis
        db.execute(
            "INSERT INTO analyses (file_name, file_type, overall_score, grade, total_features) "
            "VALUES ('x.html', 'html', 90, 'A', 5)"
        )
        info = get_table_info(db)
        assert info["analyses"] == 1
        assert info["analysis_features"] == 0

    def test_empty_db_counts(self, db):
        info = get_table_info(db)
        # settings has 3 defaults from migration v2
        assert info["settings"] == 3
        assert info["analyses"] == 0
        assert info["tags"] == 0


# =============================================================================
# Default settings from v2 migration
# =============================================================================

class TestDefaultSettings:
    def test_three_defaults_inserted(self, db):
        cursor = db.execute("SELECT COUNT(*) FROM settings")
        assert cursor.fetchone()[0] == 3

    def test_default_values(self, db):
        cursor = db.execute("SELECT key, value FROM settings ORDER BY key")
        rows = {row["key"]: row["value"] for row in cursor.fetchall()}
        assert rows["auto_save_history"] == "true"
        assert rows["default_browsers"] == "chrome,firefox,safari,edge"
        assert rows["history_limit"] == "100"
