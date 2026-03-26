"""Whitebox tests for database layer — migrations, schema versioning, connection singleton.

Tests internal schema structure, migration mechanics, and connection management.
"""

import sqlite3
import pytest
from unittest.mock import patch, MagicMock

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
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return {row[0] for row in cursor.fetchall()}


def _index_names(conn):
    """Return set of index names in the database."""
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
    return {row[0] for row in cursor.fetchall()}


# =============================================================================
# create_tables — schema creation
# =============================================================================

class TestCreateTables:
    @pytest.mark.whitebox
    def test_all_eight_tables_created(self, db):
        expected = {"schema_version", "analyses", "analysis_features", "browser_results",
                    "settings", "bookmarks", "tags", "analysis_tags"}
        assert _table_names(db) == expected

    @pytest.mark.whitebox
    def test_indexes_created(self, db):
        indexes = _index_names(db)
        expected_indexes = {"idx_analyses_date", "idx_analyses_file", "idx_analyses_type",
                            "idx_features_analysis", "idx_bookmarks_analysis", "idx_tags_name",
                            "idx_analysis_tags_analysis", "idx_analysis_tags_tag"}
        assert expected_indexes.issubset(indexes)

    @pytest.mark.whitebox
    def test_schema_version_is_current(self, db):
        assert get_schema_version(db) == SCHEMA_VERSION

    @pytest.mark.whitebox
    def test_idempotent(self, db):
        create_tables(db)
        create_tables(db)
        assert get_schema_version(db) == SCHEMA_VERSION
        assert len(_table_names(db)) == 8


# =============================================================================
# Schema versioning
# =============================================================================

class TestSchemaVersioning:
    @pytest.mark.whitebox
    def test_fresh_db_version_zero(self):
        conn = _fresh_conn()
        assert get_schema_version(conn) == 0
        conn.close()

    @pytest.mark.whitebox
    def test_after_create_version_is_2(self, db):
        assert get_schema_version(db) == 2

    @pytest.mark.whitebox
    def test_schema_version_constant(self):
        assert SCHEMA_VERSION == 2


# =============================================================================
# drop_tables
# =============================================================================

class TestDropTables:
    @pytest.mark.whitebox
    def test_all_tables_gone(self, db):
        drop_tables(db)
        assert len(_table_names(db)) == 0

    @pytest.mark.whitebox
    def test_table_info_after_drop(self, db):
        drop_tables(db)
        info = get_table_info(db)
        for count in info.values():
            assert count == -1


# =============================================================================
# reset_database
# =============================================================================

class TestResetDatabase:
    @pytest.mark.whitebox
    def test_tables_recreated(self, db):
        db.execute("INSERT INTO analyses (file_name, file_type, overall_score, grade, total_features) "
                   "VALUES ('x.html', 'html', 90, 'A', 5)")
        reset_database(db)
        assert _table_names(db) == {"schema_version", "analyses", "analysis_features", "browser_results",
                                     "settings", "bookmarks", "tags", "analysis_tags"}

    @pytest.mark.whitebox
    def test_data_wiped(self, db):
        db.execute("INSERT INTO analyses (file_name, file_type, overall_score, grade, total_features) "
                   "VALUES ('x.html', 'html', 90, 'A', 5)")
        reset_database(db)
        assert db.execute("SELECT COUNT(*) FROM analyses").fetchone()[0] == 0


# =============================================================================
# get_table_info
# =============================================================================

class TestGetTableInfo:
    @pytest.mark.whitebox
    def test_correct_table_names(self, db):
        expected = {"analyses", "analysis_features", "browser_results", "settings", "bookmarks", "tags", "analysis_tags"}
        assert set(get_table_info(db).keys()) == expected

    @pytest.mark.whitebox
    def test_row_counts(self, db):
        db.execute("INSERT INTO analyses (file_name, file_type, overall_score, grade, total_features) "
                   "VALUES ('x.html', 'html', 90, 'A', 5)")
        info = get_table_info(db)
        assert info["analyses"] == 1 and info["analysis_features"] == 0

    @pytest.mark.whitebox
    def test_empty_db_counts(self, db):
        info = get_table_info(db)
        assert info["settings"] == 3  # defaults from v2 migration
        assert info["analyses"] == 0


# =============================================================================
# Default settings from v2 migration
# =============================================================================

class TestDefaultSettings:
    @pytest.mark.whitebox
    def test_three_defaults_inserted(self, db):
        assert db.execute("SELECT COUNT(*) FROM settings").fetchone()[0] == 3

    @pytest.mark.whitebox
    def test_default_values(self, db):
        cursor = db.execute("SELECT key, value FROM settings ORDER BY key")
        rows = {row["key"]: row["value"] for row in cursor.fetchall()}
        assert rows == {"auto_save_history": "true", "default_browsers": "chrome,firefox,safari,edge", "history_limit": "100"}


# =============================================================================
# Connection singleton
# =============================================================================

class TestConnectionSingleton:
    @pytest.mark.whitebox
    def test_get_connection_returns_same_object(self):
        """get_connection() returns the same connection on repeated calls."""
        import src.database.connection as conn_mod
        original = conn_mod._connection
        try:
            conn_mod._connection = None
            with patch.object(conn_mod, 'get_db_path', return_value=':memory:'):
                c1 = conn_mod.get_connection()
                c2 = conn_mod.get_connection()
                assert c1 is c2
        finally:
            if conn_mod._connection is not None and conn_mod._connection is not original:
                conn_mod._connection.close()
            conn_mod._connection = original

    @pytest.mark.whitebox
    def test_close_connection_sets_none(self):
        """close_connection() closes and nullifies the singleton."""
        import src.database.connection as conn_mod
        original = conn_mod._connection
        try:
            conn_mod._connection = None
            with patch.object(conn_mod, 'get_db_path', return_value=':memory:'):
                conn_mod.get_connection()
                assert conn_mod._connection is not None
                conn_mod.close_connection()
                assert conn_mod._connection is None
        finally:
            conn_mod._connection = original

    @pytest.mark.whitebox
    def test_close_when_already_none(self):
        """close_connection() is safe to call when no connection exists."""
        import src.database.connection as conn_mod
        original = conn_mod._connection
        try:
            conn_mod._connection = None
            conn_mod.close_connection()  # should not raise
            assert conn_mod._connection is None
        finally:
            conn_mod._connection = original
