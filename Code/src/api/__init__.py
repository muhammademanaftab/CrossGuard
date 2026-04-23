"""Frontends import exclusively from here — nothing else in src/ is public."""

from .service import AnalyzerService, get_analyzer_service
from .schemas import (
    AnalysisRequest,
    AnalysisResult,
    BrowserCompatibility,
    DatabaseInfo,
    DatabaseUpdateResult,
    ProgressCallback,
)

__all__ = [
    'AnalyzerService',
    'get_analyzer_service',
    'AnalysisRequest',
    'AnalysisResult',
    'BrowserCompatibility',
    'DatabaseInfo',
    'DatabaseUpdateResult',
    'ProgressCallback',
]
