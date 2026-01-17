"""
Cross Guard Backend - Compatibility Analysis Engine.

This package contains the core analysis functionality for checking
browser compatibility of HTML, CSS, and JavaScript code.

IMPORTANT: Frontend code should NOT import directly from this package.
Use the API layer (src.api) instead for proper separation.

Internal Usage (for backend development):
    from src.analyzer import CrossGuardAnalyzer

    analyzer = CrossGuardAnalyzer()
    report = analyzer.analyze_project(
        html_files=['index.html'],
        css_files=['style.css'],
        target_browsers={'chrome': '120', 'firefox': '121'}
    )
"""

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
