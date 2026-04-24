"""Whitebox tests for database layer -- migrations and schema versioning.

Tests internal schema structure.
"""

import pytest


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
