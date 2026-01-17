"""
Cross Guard API Layer.

This package provides a clean interface between the frontend (GUI)
and the backend (analyzer). All communication should go through
this API layer.

Frontend developers should only import from this package.
Backend developers should ensure their changes don't break
the contracts defined in schemas.py.

Usage:
    from src.api import get_analyzer_service, AnalysisRequest, AnalysisResult

    # Get the service
    service = get_analyzer_service()

    # Analyze files
    result = service.analyze_files(
        html_files=['index.html'],
        css_files=['style.css']
    )

    # Check result
    if result.success:
        print(f"Grade: {result.scores.grade}")
"""

from .service import AnalyzerService, get_analyzer_service
from .schemas import (
    # Enums
    AnalysisStatus,
    RiskLevel,
    # Request/Response
    AnalysisRequest,
    AnalysisResult,
    # Data structures
    BrowserTarget,
    FeatureSummary,
    CompatibilityScore,
    BrowserCompatibility,
    DatabaseInfo,
    DatabaseUpdateResult,
    # Types
    ProgressCallback,
)

__all__ = [
    # Service
    'AnalyzerService',
    'get_analyzer_service',
    # Enums
    'AnalysisStatus',
    'RiskLevel',
    # Request/Response
    'AnalysisRequest',
    'AnalysisResult',
    # Data structures
    'BrowserTarget',
    'FeatureSummary',
    'CompatibilityScore',
    'BrowserCompatibility',
    'DatabaseInfo',
    'DatabaseUpdateResult',
    # Types
    'ProgressCallback',
]
