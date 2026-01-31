"""
Database migrations for Cross Guard.

Provides functions to create, update, and reset database tables.
"""

import sqlite3
from typing import Optional

from src.utils.config import get_logger

logger = get_logger('database.migrations')

# Current schema version
SCHEMA_VERSION = 1

# SQL statements for table creation
CREATE_ANALYSES_TABLE = """
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    file_path TEXT,
    file_type TEXT NOT NULL,
    overall_score REAL NOT NULL,
    grade TEXT NOT NULL,
    total_features INTEGER NOT NULL,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    browsers_json TEXT
);
"""

CREATE_ANALYSIS_FEATURES_TABLE = """
CREATE TABLE IF NOT EXISTS analysis_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    feature_id TEXT NOT NULL,
    feature_name TEXT,
    category TEXT,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);
"""

CREATE_BROWSER_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS browser_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_feature_id INTEGER NOT NULL,
    browser TEXT NOT NULL,
    version TEXT,
    support_status TEXT NOT NULL,
    FOREIGN KEY (analysis_feature_id) REFERENCES analysis_features(id) ON DELETE CASCADE
);
"""

# Indexes for performance
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_analyses_date ON analyses(analyzed_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_analyses_file ON analyses(file_name);",
    "CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(file_type);",
    "CREATE INDEX IF NOT EXISTS idx_features_analysis ON analysis_features(analysis_id);",
    "CREATE INDEX IF NOT EXISTS idx_features_feature_id ON analysis_features(feature_id);",
    "CREATE INDEX IF NOT EXISTS idx_browser_feature ON browser_results(analysis_feature_id);",
    "CREATE INDEX IF NOT EXISTS idx_browser_status ON browser_results(support_status);",
]

# Schema version table
CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def create_tables(conn: Optional[sqlite3.Connection] = None):
    """Create all database tables and indexes.

    Args:
        conn: Optional database connection. If not provided, gets a new connection.
    """
    if conn is None:
        from .connection import get_connection
        conn = get_connection()

    logger.info("Creating database tables...")

    # Create schema version table first
    conn.execute(CREATE_SCHEMA_VERSION_TABLE)

    # Check current schema version
    cursor = conn.execute("SELECT MAX(version) FROM schema_version")
    row = cursor.fetchone()
    current_version = row[0] if row and row[0] else 0

    if current_version >= SCHEMA_VERSION:
        logger.debug(f"Database schema is up to date (version {current_version})")
        return

    # Create main tables
    conn.execute(CREATE_ANALYSES_TABLE)
    logger.debug("Created analyses table")

    conn.execute(CREATE_ANALYSIS_FEATURES_TABLE)
    logger.debug("Created analysis_features table")

    conn.execute(CREATE_BROWSER_RESULTS_TABLE)
    logger.debug("Created browser_results table")

    # Create indexes
    for index_sql in CREATE_INDEXES:
        conn.execute(index_sql)
    logger.debug("Created indexes")

    # Update schema version
    conn.execute(
        "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
        (SCHEMA_VERSION,)
    )

    logger.info(f"Database schema initialized (version {SCHEMA_VERSION})")


def drop_tables(conn: Optional[sqlite3.Connection] = None):
    """Drop all database tables.

    Warning: This will delete all data!

    Args:
        conn: Optional database connection. If not provided, gets a new connection.
    """
    if conn is None:
        from .connection import get_connection
        conn = get_connection()

    logger.warning("Dropping all database tables...")

    # Disable foreign keys temporarily
    conn.execute("PRAGMA foreign_keys = OFF")

    # Drop tables in reverse order of dependencies
    conn.execute("DROP TABLE IF EXISTS browser_results")
    conn.execute("DROP TABLE IF EXISTS analysis_features")
    conn.execute("DROP TABLE IF EXISTS analyses")
    conn.execute("DROP TABLE IF EXISTS schema_version")

    # Re-enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    logger.info("All tables dropped")


def reset_database(conn: Optional[sqlite3.Connection] = None):
    """Reset the database by dropping and recreating all tables.

    Warning: This will delete all data!

    Args:
        conn: Optional database connection. If not provided, gets a new connection.
    """
    if conn is None:
        from .connection import get_connection
        conn = get_connection()

    logger.warning("Resetting database...")
    drop_tables(conn)
    create_tables(conn)
    logger.info("Database reset complete")


def get_schema_version(conn: Optional[sqlite3.Connection] = None) -> int:
    """Get the current schema version.

    Args:
        conn: Optional database connection.

    Returns:
        Current schema version number, or 0 if not initialized.
    """
    if conn is None:
        from .connection import get_connection
        conn = get_connection()

    try:
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        return row[0] if row and row[0] else 0
    except sqlite3.OperationalError:
        return 0


def get_table_info(conn: Optional[sqlite3.Connection] = None) -> dict:
    """Get information about database tables.

    Args:
        conn: Optional database connection.

    Returns:
        Dictionary with table names and their row counts.
    """
    if conn is None:
        from .connection import get_connection
        conn = get_connection()

    tables = ['analyses', 'analysis_features', 'browser_results']
    info = {}

    for table in tables:
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            row = cursor.fetchone()
            info[table] = row[0] if row else 0
        except sqlite3.OperationalError:
            info[table] = -1  # Table doesn't exist

    return info
