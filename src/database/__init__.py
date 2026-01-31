"""
Database module for Cross Guard - SQLite storage for analysis history and statistics.

This module provides persistent storage for:
- Analysis history (past analyses with scores and features)
- Statistics (aggregated insights from all analyses)
- Browser support results per analysis
"""

from .connection import get_connection, close_connection, get_db_path
from .models import Analysis, AnalysisFeature, BrowserResult
from .repositories import AnalysisRepository
from .statistics import StatisticsService
from .migrations import create_tables, drop_tables, reset_database

__all__ = [
    # Connection management
    'get_connection',
    'close_connection',
    'get_db_path',

    # Data models
    'Analysis',
    'AnalysisFeature',
    'BrowserResult',

    # Repository
    'AnalysisRepository',

    # Statistics
    'StatisticsService',

    # Migrations
    'create_tables',
    'drop_tables',
    'reset_database',
]
