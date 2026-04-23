"""Schema migrations for the SQLite database (versioned)."""

import sqlite3
from typing import Optional

from src.utils.config import get_logger

logger = get_logger('database.migrations')

SCHEMA_VERSION = 2

# --- V1 tables (core analysis data) ---

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

# --- V2 tables (settings, bookmarks, tags) ---

CREATE_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_BOOKMARKS_TABLE = """
CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL UNIQUE,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);
"""

CREATE_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#58a6ff',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_ANALYSIS_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS analysis_tags (
    analysis_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (analysis_id, tag_id),
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
"""

# --- Indexes ---

CREATE_INDEXES_V1 = [
    "CREATE INDEX IF NOT EXISTS idx_analyses_date ON analyses(analyzed_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_analyses_file ON analyses(file_name);",
    "CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(file_type);",
    "CREATE INDEX IF NOT EXISTS idx_features_analysis ON analysis_features(analysis_id);",
    "CREATE INDEX IF NOT EXISTS idx_features_feature_id ON analysis_features(feature_id);",
    "CREATE INDEX IF NOT EXISTS idx_browser_feature ON browser_results(analysis_feature_id);",
    "CREATE INDEX IF NOT EXISTS idx_browser_status ON browser_results(support_status);",
]

CREATE_INDEXES_V2 = [
    "CREATE INDEX IF NOT EXISTS idx_bookmarks_analysis ON bookmarks(analysis_id);",
    "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);",
    "CREATE INDEX IF NOT EXISTS idx_analysis_tags_analysis ON analysis_tags(analysis_id);",
    "CREATE INDEX IF NOT EXISTS idx_analysis_tags_tag ON analysis_tags(tag_id);",
]

CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def create_tables(conn: Optional[sqlite3.Connection] = None):
    """Creates tables and applies any pending schema migrations"""
    if conn is None:
        from .connection import get_connection
        conn = get_connection()

    logger.info("Creating database tables...")

    conn.execute(CREATE_SCHEMA_VERSION_TABLE)

    cursor = conn.execute("SELECT MAX(version) FROM schema_version")
    row = cursor.fetchone()
    current_version = row[0] if row and row[0] else 0

    if current_version >= SCHEMA_VERSION:
        logger.debug(f"Database schema is up to date (version {current_version})")
        return

    if current_version < 1:
        _migrate_to_v1(conn)

    if current_version < 2:
        _migrate_to_v2(conn)

    conn.execute(
        "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
        (SCHEMA_VERSION,)
    )

    logger.info(f"Database schema initialized (version {SCHEMA_VERSION})")


def _migrate_to_v1(conn: sqlite3.Connection):
    """V1: core analysis tables."""
    logger.info("Applying migration: version 1")

    conn.execute(CREATE_ANALYSES_TABLE)
    logger.debug("Created analyses table")

    conn.execute(CREATE_ANALYSIS_FEATURES_TABLE)
    logger.debug("Created analysis_features table")

    conn.execute(CREATE_BROWSER_RESULTS_TABLE)
    logger.debug("Created browser_results table")

    for index_sql in CREATE_INDEXES_V1:
        conn.execute(index_sql)
    logger.debug("Created v1 indexes")


def _migrate_to_v2(conn: sqlite3.Connection):
    """V2: settings, bookmarks, tags."""
    logger.info("Applying migration: version 2")

    conn.execute(CREATE_SETTINGS_TABLE)
    logger.debug("Created settings table")

    conn.execute(CREATE_BOOKMARKS_TABLE)
    logger.debug("Created bookmarks table")

    conn.execute(CREATE_TAGS_TABLE)
    logger.debug("Created tags table")

    conn.execute(CREATE_ANALYSIS_TAGS_TABLE)
    logger.debug("Created analysis_tags junction table")

    for index_sql in CREATE_INDEXES_V2:
        conn.execute(index_sql)
    logger.debug("Created v2 indexes")

    default_settings = [
        ('default_browsers', 'chrome,firefox,safari,edge'),
        ('history_limit', '100'),
        ('auto_save_history', 'true'),
    ]
    for key, value in default_settings:
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    logger.debug("Inserted default settings")


def drop_tables(conn: Optional[sqlite3.Connection] = None):
    """Drops all tables — destroys all data"""
    if conn is None:
        from .connection import get_connection
        conn = get_connection()

    logger.warning("Dropping all database tables...")

    conn.execute("PRAGMA foreign_keys = OFF")

    # drop in reverse dependency order so FK constraints don't fire
    conn.execute("DROP TABLE IF EXISTS analysis_tags")
    conn.execute("DROP TABLE IF EXISTS tags")
    conn.execute("DROP TABLE IF EXISTS bookmarks")
    conn.execute("DROP TABLE IF EXISTS settings")
    conn.execute("DROP TABLE IF EXISTS browser_results")
    conn.execute("DROP TABLE IF EXISTS analysis_features")
    conn.execute("DROP TABLE IF EXISTS analyses")
    conn.execute("DROP TABLE IF EXISTS schema_version")

    conn.execute("PRAGMA foreign_keys = ON")

    logger.info("All tables dropped")


def reset_database(conn: Optional[sqlite3.Connection] = None):
    """Drops and recreates everything — destroys all data"""
    if conn is None:
        from .connection import get_connection
        conn = get_connection()

    logger.warning("Resetting database...")
    drop_tables(conn)
    create_tables(conn)
    logger.info("Database reset complete")
