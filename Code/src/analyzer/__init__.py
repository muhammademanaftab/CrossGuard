"""Compatibility analysis engine. Frontends should use src.api instead."""

from .main import CrossGuardAnalyzer
from .compatibility import CompatibilityAnalyzer
from .scorer import CompatibilityScorer
from .database import get_database, reload_database

__all__ = [
    'CrossGuardAnalyzer',
    'CompatibilityAnalyzer',
    'CompatibilityScorer',
    'get_database',
    'reload_database',
]
