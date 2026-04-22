"""Thread-safe singleton SQLite connection with auto table init."""

import sqlite3
from pathlib import Path
from typing import Optional
import threading

from src.utils.config import get_logger

logger = get_logger('database.connection')

_DB_NAME = 'crossguard.db'
_connection: Optional[sqlite3.Connection] = None
_lock = threading.Lock()


def get_db_path() -> Path:
    from src.utils.config import PROJECT_ROOT
    return PROJECT_ROOT / _DB_NAME


def get_connection() -> sqlite3.Connection:
    """Returns the singleton connection, creating it on first call"""
    global _connection

    with _lock:
        if _connection is None:
            db_path = get_db_path()
            logger.info(f"Opening database connection: {db_path}")

            _connection = sqlite3.connect(
                str(db_path),
                check_same_thread=False,
                isolation_level=None,  # autocommit — repositories manage transactions manually
            )

            _connection.execute("PRAGMA foreign_keys = ON")
            _connection.row_factory = sqlite3.Row

            _init_tables(_connection)

        return _connection


def close_connection():
    global _connection

    with _lock:
        if _connection is not None:
            logger.info("Closing database connection")
            _connection.close()
            _connection = None


def _init_tables(conn: sqlite3.Connection):
    from .migrations import create_tables
    create_tables(conn)


def execute_query(query: str, params: tuple = ()) -> sqlite3.Cursor:
    conn = get_connection()
    return conn.execute(query, params)


def execute_many(query: str, params_list: list) -> sqlite3.Cursor:
    conn = get_connection()
    return conn.executemany(query, params_list)
