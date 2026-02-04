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
from .project_schemas import (
    ScanConfig,
    ScanResult,
    ProjectInfo,
    ProjectAnalysisResult,
    FileAnalysisResult,
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

    # =========================================================================
    # Settings Methods
    # =========================================================================

    def get_setting(self, key: str, default: str = '') -> str:
        """Get a user setting value.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value
        """
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            return repo.get(key, default)
        except Exception as e:
            logger.error(f"Failed to get setting '{key}': {e}")
            return default

    def set_setting(self, key: str, value: str) -> bool:
        """Set a user setting value.

        Args:
            key: Setting key
            value: Setting value

        Returns:
            True if successful
        """
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            repo.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Failed to set setting '{key}': {e}")
            return False

    def get_all_settings(self) -> Dict[str, str]:
        """Get all user settings.

        Returns:
            Dictionary of all settings
        """
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            return repo.get_all()
        except Exception as e:
            logger.error(f"Failed to get all settings: {e}")
            return {}

    def get_setting_as_bool(self, key: str, default: bool = False) -> bool:
        """Get a setting as boolean."""
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            return repo.get_as_bool(key, default)
        except Exception:
            return default

    def get_setting_as_list(self, key: str, default: List[str] = None) -> List[str]:
        """Get a setting as list (comma-separated)."""
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            return repo.get_as_list(key, default)
        except Exception:
            return default or []

    # =========================================================================
    # Bookmarks Methods
    # =========================================================================

    def add_bookmark(self, analysis_id: int, note: str = '') -> bool:
        """Add a bookmark for an analysis.

        Args:
            analysis_id: Analysis ID to bookmark
            note: Optional note

        Returns:
            True if successful
        """
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            repo.add_bookmark(analysis_id, note)
            return True
        except Exception as e:
            logger.error(f"Failed to add bookmark for analysis #{analysis_id}: {e}")
            return False

    def remove_bookmark(self, analysis_id: int) -> bool:
        """Remove a bookmark from an analysis.

        Args:
            analysis_id: Analysis ID to unbookmark

        Returns:
            True if removed
        """
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.remove_bookmark(analysis_id)
        except Exception as e:
            logger.error(f"Failed to remove bookmark from analysis #{analysis_id}: {e}")
            return False

    def is_bookmarked(self, analysis_id: int) -> bool:
        """Check if an analysis is bookmarked.

        Args:
            analysis_id: Analysis ID to check

        Returns:
            True if bookmarked
        """
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.is_bookmarked(analysis_id)
        except Exception:
            return False

    def toggle_bookmark(self, analysis_id: int, note: str = '') -> bool:
        """Toggle bookmark status for an analysis.

        Args:
            analysis_id: Analysis ID
            note: Note to add if bookmarking

        Returns:
            True if now bookmarked, False if unbookmarked
        """
        if self.is_bookmarked(analysis_id):
            self.remove_bookmark(analysis_id)
            return False
        else:
            self.add_bookmark(analysis_id, note)
            return True

    def get_all_bookmarks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all bookmarks with their analysis info.

        Args:
            limit: Maximum number to return

        Returns:
            List of bookmark dictionaries
        """
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.get_all_bookmarks(limit)
        except Exception as e:
            logger.error(f"Failed to get bookmarks: {e}")
            return []

    def update_bookmark_note(self, analysis_id: int, note: str) -> bool:
        """Update the note for a bookmark.

        Args:
            analysis_id: Analysis ID
            note: New note text

        Returns:
            True if updated
        """
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.update_note(analysis_id, note)
        except Exception as e:
            logger.error(f"Failed to update bookmark note: {e}")
            return False

    def get_bookmarks_count(self) -> int:
        """Get total number of bookmarks."""
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.get_count()
        except Exception:
            return 0

    # =========================================================================
    # Tags Methods
    # =========================================================================

    def create_tag(self, name: str, color: str = '#58a6ff') -> Optional[int]:
        """Create a new tag.

        Args:
            name: Tag name
            color: Hex color code

        Returns:
            Tag ID or None on error
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.create_tag(name, color)
        except Exception as e:
            logger.error(f"Failed to create tag '{name}': {e}")
            return None

    def get_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags.

        Returns:
            List of tag dictionaries
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.get_all_tags()
        except Exception as e:
            logger.error(f"Failed to get tags: {e}")
            return []

    def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag.

        Args:
            tag_id: Tag ID to delete

        Returns:
            True if deleted
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.delete_tag(tag_id)
        except Exception as e:
            logger.error(f"Failed to delete tag #{tag_id}: {e}")
            return False

    def update_tag(self, tag_id: int, name: str = None, color: str = None) -> bool:
        """Update a tag's properties.

        Args:
            tag_id: Tag ID
            name: New name (optional)
            color: New color (optional)

        Returns:
            True if updated
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.update_tag(tag_id, name, color)
        except Exception as e:
            logger.error(f"Failed to update tag #{tag_id}: {e}")
            return False

    def add_tag_to_analysis(self, analysis_id: int, tag_id: int) -> bool:
        """Add a tag to an analysis.

        Args:
            analysis_id: Analysis ID
            tag_id: Tag ID

        Returns:
            True if added
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.add_tag_to_analysis(analysis_id, tag_id)
        except Exception as e:
            logger.error(f"Failed to add tag to analysis: {e}")
            return False

    def remove_tag_from_analysis(self, analysis_id: int, tag_id: int) -> bool:
        """Remove a tag from an analysis.

        Args:
            analysis_id: Analysis ID
            tag_id: Tag ID

        Returns:
            True if removed
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.remove_tag_from_analysis(analysis_id, tag_id)
        except Exception as e:
            logger.error(f"Failed to remove tag from analysis: {e}")
            return False

    def get_tags_for_analysis(self, analysis_id: int) -> List[Dict[str, Any]]:
        """Get all tags for a specific analysis.

        Args:
            analysis_id: Analysis ID

        Returns:
            List of tag dictionaries
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.get_tags_for_analysis(analysis_id)
        except Exception as e:
            logger.error(f"Failed to get tags for analysis #{analysis_id}: {e}")
            return []

    def get_analyses_by_tag(self, tag_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all analyses with a specific tag.

        Args:
            tag_id: Tag ID
            limit: Maximum results

        Returns:
            List of analysis dictionaries
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.get_analyses_by_tag(tag_id, limit)
        except Exception as e:
            logger.error(f"Failed to get analyses by tag #{tag_id}: {e}")
            return []

    def get_tag_counts(self) -> Dict[str, int]:
        """Get usage count for each tag.

        Returns:
            Dict mapping tag name to usage count
        """
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.get_tag_counts()
        except Exception as e:
            logger.error(f"Failed to get tag counts: {e}")
            return {}

    # =========================================================================
    # Project Scanner Methods
    # =========================================================================

    def scan_project_directory(
        self,
        path: str,
        config: ScanConfig = None,
        progress_callback: callable = None
    ) -> ScanResult:
        """
        Scan a project directory for analyzable files.

        Args:
            path: Path to the project root directory
            config: Scan configuration (uses defaults if not provided)
            progress_callback: Optional callback(current, total, message)

        Returns:
            ScanResult with found files and tree structure
        """
        try:
            from src.scanner import ProjectScanner

            scanner = ProjectScanner()
            result = scanner.scan_directory(path, config, progress_callback)
            return result

        except Exception as e:
            logger.error(f"Failed to scan directory {path}: {e}")
            return ScanResult(project_path=path)

    def detect_project_framework(self, path: str) -> ProjectInfo:
        """
        Detect the framework and build tools used in a project.

        Args:
            path: Path to the project root directory

        Returns:
            ProjectInfo with detected framework details
        """
        try:
            from src.scanner import FrameworkDetector

            detector = FrameworkDetector()
            return detector.detect(path)

        except Exception as e:
            logger.error(f"Failed to detect framework in {path}: {e}")
            return ProjectInfo()

    def analyze_project(
        self,
        scan_result: ScanResult,
        target_browsers: Dict[str, str] = None,
        progress_callback: callable = None
    ) -> ProjectAnalysisResult:
        """
        Analyze all files from a project scan.

        Args:
            scan_result: ScanResult from scan_project_directory()
            target_browsers: Target browsers (uses defaults if not provided)
            progress_callback: Optional callback(current, total, file_name)

        Returns:
            ProjectAnalysisResult with aggregate results
        """
        import time
        from datetime import datetime
        import os

        start_time = time.time()
        target_browsers = target_browsers or self.DEFAULT_BROWSERS

        # Get project info
        project_info = self.detect_project_framework(scan_result.project_path)

        result = ProjectAnalysisResult(
            success=True,
            project_path=scan_result.project_path,
            project_name=os.path.basename(scan_result.project_path),
            framework=project_info.framework,
            build_tool=project_info.build_tool,
            html_files=scan_result.html_count,
            css_files=scan_result.css_count,
            js_files=scan_result.js_count,
            total_files=scan_result.total_files,
            scanned_at=datetime.now().isoformat(),
        )

        if scan_result.total_files == 0:
            result.error = "No files to analyze"
            return result

        # Analyze files
        all_files = scan_result.get_all_files()
        file_results = []
        total_score = 0.0
        all_unsupported = []
        all_partial = []
        unique_features = set()

        for i, file_path in enumerate(all_files):
            if progress_callback:
                progress_callback(i + 1, len(all_files), os.path.basename(file_path))

            # Determine file type
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ('.html', '.htm'):
                file_type = 'html'
                analysis_result = self.analyze_files(html_files=[file_path], target_browsers=target_browsers)
            elif ext == '.css':
                file_type = 'css'
                analysis_result = self.analyze_files(css_files=[file_path], target_browsers=target_browsers)
            else:
                file_type = 'javascript'
                analysis_result = self.analyze_files(js_files=[file_path], target_browsers=target_browsers)

            if not analysis_result.success:
                continue

            # Collect file result
            file_result = FileAnalysisResult(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                file_type=file_type,
                score=analysis_result.scores.simple_score if analysis_result.scores else 0.0,
                grade=analysis_result.scores.grade if analysis_result.scores else 'N/A',
                features_count=analysis_result.summary.total_features if analysis_result.summary else 0,
            )

            # Collect issues from browsers
            for browser_name, browser_data in analysis_result.browsers.items():
                file_result.unsupported_features.extend(browser_data.unsupported_features)
                file_result.partial_features.extend(browser_data.partial_features)

            file_result.issues_count = len(set(file_result.unsupported_features)) + len(set(file_result.partial_features))

            file_results.append(file_result)
            total_score += file_result.score

            # Aggregate features
            if analysis_result.detected_features:
                unique_features.update(analysis_result.detected_features.all)
            all_unsupported.extend(file_result.unsupported_features)
            all_partial.extend(file_result.partial_features)

        # Calculate aggregates
        result.file_results = file_results
        result.total_features = sum(fr.features_count for fr in file_results)
        result.unique_features = len(unique_features)

        if file_results:
            result.overall_score = total_score / len(file_results)
            result.overall_grade = self._score_to_grade(result.overall_score)

            # Find worst files
            sorted_by_score = sorted(file_results, key=lambda x: x.score)
            result.worst_files = sorted_by_score[:5]

        # Count unique issues
        result.unsupported_count = len(set(all_unsupported))
        result.partial_count = len(set(all_partial))

        # Top issues (most frequent unsupported features)
        from collections import Counter
        issue_counts = Counter(all_unsupported)
        result.top_issues = [
            {'feature': feat, 'count': count}
            for feat, count in issue_counts.most_common(10)
        ]

        # Timing
        result.analysis_duration_ms = int((time.time() - start_time) * 1000)

        return result

    def _score_to_grade(self, score: float) -> str:
        """Convert a score to a letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


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
