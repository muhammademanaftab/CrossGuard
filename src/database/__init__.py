"""
Database module for Cross Guard - SQLite storage for analysis history and statistics.

This module provides persistent storage for:
- Analysis history (past analyses with scores and features)
- Statistics (aggregated insights from all analyses)
- Browser support results per analysis
- User settings and preferences
- Bookmarks for important analyses
- Tags for categorizing analyses
"""

from .connection import get_connection, close_connection, get_db_path
from .models import (
    Analysis,
    AnalysisFeature,
    BrowserResult,
    Setting,
    Bookmark,
    Tag,
    AnalysisTag,
)
from .repositories import (
    AnalysisRepository,
    SettingsRepository,
    BookmarksRepository,
    TagsRepository,
)
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
    'Setting',
    'Bookmark',
    'Tag',
    'AnalysisTag',

    # Repositories
    'AnalysisRepository',
    'SettingsRepository',
    'BookmarksRepository',
    'TagsRepository',

    # Statistics
    'StatisticsService',

    # Migrations
    'create_tables',
    'drop_tables',
    'reset_database',
]
