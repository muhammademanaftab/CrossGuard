"""Whitebox tests for database layer -- migrations, schema versioning, connection singleton.

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


# --- Helpers ----------------------------------------------------------------

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


# =============================================================================
# create_tables -- schema creation
# =============================================================================

class TestCreateTables:
    @pytest.mark.whitebox
    def test_all_eight_tables_created(self, db):
        expected = {"schema_version", "analyses", "analysis_features", "browser_results",
                    "settings", "bookmarks", "tags", "analysis_tags"}
        assert _table_names(db) == expected

    @pytest.mark.whitebox
    def test_schema_version_is_current(self, db):
        assert get_schema_version(db) == SCHEMA_VERSION



# =============================================================================
# Schema versioning
# =============================================================================

class TestSchemaVersioning:
    @pytest.mark.whitebox
    def test_after_create_version_is_2(self, db):
        assert get_schema_version(db) == 2



# =============================================================================
# drop_tables and reset_database
# =============================================================================

class TestDropAndReset:
    @pytest.mark.whitebox
    def test_reset_recreates_tables(self, db):
        db.execute("INSERT INTO analyses (file_name, file_type, overall_score, grade, total_features) "
                   "VALUES ('x.html', 'html', 90, 'A', 5)")
        reset_database(db)
        assert _table_names(db) == {"schema_version", "analyses", "analysis_features", "browser_results",
                                     "settings", "bookmarks", "tags", "analysis_tags"}
        assert db.execute("SELECT COUNT(*) FROM analyses").fetchone()[0] == 0


# =============================================================================
# get_table_info
# =============================================================================

class TestGetTableInfo:
    @pytest.mark.whitebox
    def test_correct_table_names(self, db):
        expected = {"analyses", "analysis_features", "browser_results", "settings", "bookmarks", "tags", "analysis_tags"}
        assert set(get_table_info(db).keys()) == expected



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
