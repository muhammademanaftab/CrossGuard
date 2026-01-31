"""
API Service Layer - Interface between Frontend and Backend.

This module provides a clean API for the GUI to interact with the
analyzer backend without knowing implementation details.

Frontend should ONLY import from this module and schemas.py.
"""

from typing import Callable, Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime

from .schemas import (
    AnalysisRequest,
    AnalysisResult,
    DatabaseInfo,
    DatabaseUpdateResult,
    ProgressCallback,
)
from src.utils.config import LATEST_VERSIONS, get_logger

logger = get_logger('api.service')


class AnalyzerService:
    """
    Service class providing analysis functionality to the frontend.

    This class acts as a facade over the backend analyzer components,
    providing a clean interface that doesn't expose implementation details.
    """

    # Default target browsers - uses centralized config
    DEFAULT_BROWSERS = {
        'chrome': LATEST_VERSIONS['chrome'],
        'firefox': LATEST_VERSIONS['firefox'],
        'safari': LATEST_VERSIONS['safari'],
        'edge': LATEST_VERSIONS['edge']
    }

    def __init__(self):
        """Initialize the analyzer service."""
        self._analyzer = None
        self._database_updater = None

    def _get_analyzer(self):
        """Lazy-load the analyzer to avoid import at module level."""
        if self._analyzer is None:
            from src.analyzer.main import CrossGuardAnalyzer
            self._analyzer = CrossGuardAnalyzer()
        return self._analyzer

    def _get_database_updater(self):
        """Lazy-load the database updater."""
        if self._database_updater is None:
            from src.analyzer.database_updater import DatabaseUpdater
            from src.utils.config import CANIUSE_DIR
            self._database_updater = DatabaseUpdater(Path(CANIUSE_DIR))
        return self._database_updater

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze files for browser compatibility.

        Args:
            request: AnalysisRequest containing files and target browsers

        Returns:
            AnalysisResult with compatibility information
        """
        if not request.has_files():
            return AnalysisResult(
                success=False,
                error="No files provided for analysis"
            )

        try:
            analyzer = self._get_analyzer()

            # Use default browsers if not specified
            target_browsers = request.target_browsers or self.DEFAULT_BROWSERS

            # Run analysis
            report = analyzer.analyze_project(
                html_files=request.html_files if request.html_files else None,
                css_files=request.css_files if request.css_files else None,
                js_files=request.js_files if request.js_files else None,
                target_browsers=target_browsers
            )

            # Convert backend report to schema
            return AnalysisResult.from_dict(report)

        except Exception as e:
            return AnalysisResult(
                success=False,
                error=str(e)
            )

    def analyze_files(
        self,
        html_files: List[str] = None,
        css_files: List[str] = None,
        js_files: List[str] = None,
        target_browsers: Dict[str, str] = None
    ) -> AnalysisResult:
        """
        Convenience method to analyze files directly.

        Args:
            html_files: List of HTML file paths
            css_files: List of CSS file paths
            js_files: List of JavaScript file paths
            target_browsers: Dict of browser names to versions

        Returns:
            AnalysisResult with compatibility information
        """
        request = AnalysisRequest(
            html_files=html_files or [],
            css_files=css_files or [],
            js_files=js_files or [],
            target_browsers=target_browsers or self.DEFAULT_BROWSERS
        )
        return self.analyze(request)

    def get_database_info(self) -> DatabaseInfo:
        """
        Get information about the current database.

        Returns:
            DatabaseInfo with database details
        """
        try:
            updater = self._get_database_updater()
            info = updater.get_database_info()

            # Format last updated date
            last_updated = info.get('last_updated', 'Unknown')
            if last_updated != 'Unknown' and isinstance(last_updated, (int, float)):
                last_updated = datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M')

            return DatabaseInfo(
                features_count=info.get('features_count', 0),
                last_updated=str(last_updated),
                is_git_repo=info.get('is_git_repo', False)
            )
        except Exception as e:
            return DatabaseInfo(
                features_count=0,
                last_updated=f"Error: {str(e)}",
                is_git_repo=False
            )

    def update_database(
        self,
        progress_callback: ProgressCallback = None
    ) -> DatabaseUpdateResult:
        """
        Update the Can I Use database.

        Args:
            progress_callback: Optional callback function(message: str, percentage: int)

        Returns:
            DatabaseUpdateResult with update status
        """
        try:
            updater = self._get_database_updater()

            # Run update with optional progress callback
            result = updater.update_database(progress_callback)

            if result.get('success'):
                # Reload database after successful update
                if not result.get('no_changes'):
                    self._reload_database()

                return DatabaseUpdateResult(
                    success=True,
                    message=result.get('message', 'Database updated successfully'),
                    no_changes=result.get('no_changes', False)
                )
            else:
                return DatabaseUpdateResult(
                    success=False,
                    message=result.get('message', 'Update failed'),
                    error=result.get('error')
                )

        except Exception as e:
            return DatabaseUpdateResult(
                success=False,
                message="An error occurred during update",
                error=str(e)
            )

    def _reload_database(self):
        """Reload the database after an update."""
        try:
            from src.analyzer.database import reload_database
            reload_database()
            # Reset analyzer to pick up new database
            self._analyzer = None
        except Exception:
            pass  # Silently fail, will be picked up on next analysis

    def reload_custom_rules(self):
        """Reload custom rules and reset analyzer to pick them up."""
        try:
            from src.parsers.custom_rules_loader import reload_custom_rules
            reload_custom_rules()
            # Reset analyzer to pick up new rules
            self._analyzer = None
        except Exception:
            pass

    def get_default_browsers(self) -> Dict[str, str]:
        """Get the default target browsers configuration."""
        return self.DEFAULT_BROWSERS.copy()

    def get_available_browsers(self) -> List[str]:
        """Get list of available browsers for analysis."""
        return list(self.DEFAULT_BROWSERS.keys())

    # =========================================================================
    # History Methods
    # =========================================================================

    def save_analysis_to_history(
        self,
        result: AnalysisResult,
        file_name: str = 'analysis',
        file_path: str = '',
        file_type: str = 'mixed'
    ) -> Optional[int]:
        """Save an analysis result to history database.

        Args:
            result: The AnalysisResult from analysis
            file_name: Name of the primary analyzed file
            file_path: Path to the file
            file_type: Type of file ('html', 'css', 'js', or 'mixed')

        Returns:
            The ID of the saved analysis, or None on error
        """
        if not result.success:
            logger.warning("Cannot save failed analysis to history")
            return None

        try:
            from src.database.repositories import save_analysis_from_result

            result_dict = result.to_dict()
            file_info = {
                'file_name': file_name,
                'file_path': file_path,
                'file_type': file_type,
            }

            analysis_id = save_analysis_from_result(result_dict, file_info)
            logger.info(f"Saved analysis to history: #{analysis_id}")
            return analysis_id

        except Exception as e:
            logger.error(f"Failed to save analysis to history: {e}")
            return None

    def get_analysis_history(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get analysis history from database.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)

        Returns:
            List of analysis records as dictionaries
        """
        try:
            from src.database.repositories import AnalysisRepository

            repo = AnalysisRepository()
            analyses = repo.get_all_analyses(limit=limit, offset=offset)

            return [analysis.to_dict() for analysis in analyses]

        except Exception as e:
            logger.error(f"Failed to get analysis history: {e}")
            return []

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific analysis by ID.

        Args:
            analysis_id: The analysis ID to retrieve

        Returns:
            Analysis record as dictionary, or None if not found
        """
        try:
            from src.database.repositories import AnalysisRepository

            repo = AnalysisRepository()
            analysis = repo.get_analysis_by_id(analysis_id, include_features=True)

            if analysis:
                return analysis.to_dict()
            return None

        except Exception as e:
            logger.error(f"Failed to get analysis #{analysis_id}: {e}")
            return None

    def delete_from_history(self, analysis_id: int) -> bool:
        """Delete an analysis from history.

        Args:
            analysis_id: The analysis ID to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            from src.database.repositories import AnalysisRepository

            repo = AnalysisRepository()
            return repo.delete_analysis(analysis_id)

        except Exception as e:
            logger.error(f"Failed to delete analysis #{analysis_id}: {e}")
            return False

    def clear_history(self) -> bool:
        """Clear all analysis history.

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            from src.database.repositories import AnalysisRepository

            repo = AnalysisRepository()
            count = repo.clear_all()
            logger.info(f"Cleared {count} analyses from history")
            return True

        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False

    def get_history_count(self) -> int:
        """Get total number of analyses in history.

        Returns:
            Number of analyses in history
        """
        try:
            from src.database.repositories import AnalysisRepository

            repo = AnalysisRepository()
            return repo.get_count()

        except Exception as e:
            logger.error(f"Failed to get history count: {e}")
            return 0

    # =========================================================================
    # Statistics Methods
    # =========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics from analysis history.

        Returns:
            Dictionary with statistics including:
            - total_analyses: Total count
            - average_score: Average compatibility score
            - best_score: Highest score
            - worst_score: Lowest score
            - top_problematic_features: Most failing features
            - most_analyzed_files: Frequently analyzed files
            - grade_distribution: Count per grade
            - file_type_distribution: Count per file type
        """
        try:
            from src.database.statistics import get_statistics_service

            service = get_statistics_service()
            return service.get_summary_statistics()

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                'total_analyses': 0,
                'average_score': 0,
                'best_score': 0,
                'worst_score': 0,
                'top_problematic_features': [],
                'most_analyzed_files': [],
                'error': str(e),
            }

    def get_score_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get score trend over time.

        Args:
            days: Number of days to look back

        Returns:
            List of {date, avg_score, count} dictionaries
        """
        try:
            from src.database.statistics import get_statistics_service

            service = get_statistics_service()
            return service.get_score_trend(days)

        except Exception as e:
            logger.error(f"Failed to get score trend: {e}")
            return []

    def get_top_problematic_features(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most frequently failing features.

        Args:
            limit: Maximum number of features to return

        Returns:
            List of feature info with fail counts
        """
        try:
            from src.database.statistics import get_statistics_service

            service = get_statistics_service()
            return service.get_top_problematic_features(limit)

        except Exception as e:
            logger.error(f"Failed to get problematic features: {e}")
            return []


# Singleton instance for convenience
_service_instance: Optional[AnalyzerService] = None


def get_analyzer_service() -> AnalyzerService:
    """
    Get the singleton analyzer service instance.

    Returns:
        AnalyzerService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = AnalyzerService()
    return _service_instance
