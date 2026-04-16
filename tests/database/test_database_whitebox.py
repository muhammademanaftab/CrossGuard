"""Whitebox tests for database layer -- migrations, schema versioning, connection singleton.

Tests internal schema structure, migration mechanics, and connection management.
"""

import pytest
from unittest.mock import patch


# --- Helpers ----------------------------------------------------------------

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
