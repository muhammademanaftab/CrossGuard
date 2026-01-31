"""
Database connection manager for Cross Guard.

Provides a singleton pattern for SQLite database connections with
automatic table initialization on first connection.
"""

import sqlite3
from pathlib import Path
from typing import Optional
import threading

from src.utils.config import get_logger

logger = get_logger('database.connection')

# Database configuration
_DB_NAME = 'crossguard.db'
_connection: Optional[sqlite3.Connection] = None
_lock = threading.Lock()


def get_db_path() -> Path:
    """Get the path to the database file.

    Returns:
        Path to the SQLite database file
    """
    from src.utils.config import PROJECT_ROOT
    return PROJECT_ROOT / _DB_NAME


def get_connection() -> sqlite3.Connection:
    """Get the database connection (singleton pattern).

    Creates the database file and initializes tables if they don't exist.
    Uses thread-safe singleton pattern.

    Returns:
        SQLite database connection
    """
    global _connection

    with _lock:
        if _connection is None:
            db_path = get_db_path()
            logger.info(f"Opening database connection: {db_path}")

            # Create connection with row factory for dict-like access
            _connection = sqlite3.connect(
                str(db_path),
                check_same_thread=False,  # Allow multi-threaded access
                isolation_level=None,  # Autocommit mode by default
            )

            # Enable foreign keys
            _connection.execute("PRAGMA foreign_keys = ON")

            # Use Row factory for dict-like access
            _connection.row_factory = sqlite3.Row

            # Initialize tables on first connection
            _init_tables(_connection)

        return _connection


def close_connection():
    """Close the database connection.

    Should be called when the application exits.
    """
    global _connection

    with _lock:
        if _connection is not None:
            logger.info("Closing database connection")
            _connection.close()
            _connection = None


def _init_tables(conn: sqlite3.Connection):
    """Initialize database tables if they don't exist.

    Args:
        conn: Database connection
    """
    from .migrations import create_tables
    create_tables(conn)


def execute_query(query: str, params: tuple = ()) -> sqlite3.Cursor:
    """Execute a query and return the cursor.

    Args:
        query: SQL query string
        params: Query parameters

    Returns:
        Cursor with query results
    """
    conn = get_connection()
    return conn.execute(query, params)


def execute_many(query: str, params_list: list) -> sqlite3.Cursor:
    """Execute a query with multiple parameter sets.

    Args:
        query: SQL query string
        params_list: List of parameter tuples

    Returns:
        Cursor after execution
    """
    conn = get_connection()
    return conn.executemany(query, params_list)
