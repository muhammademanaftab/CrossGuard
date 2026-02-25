"""Facade over the backend -- the only thing frontends should talk to."""

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
    """Single entry point for all analysis, history, export, and config operations."""

    DEFAULT_BROWSERS = {
        'chrome': LATEST_VERSIONS['chrome'],
        'firefox': LATEST_VERSIONS['firefox'],
        'safari': LATEST_VERSIONS['safari'],
        'edge': LATEST_VERSIONS['edge']
    }

    def __init__(self, config: Optional[Dict] = None):
        self._analyzer = None
        self._database_updater = None
        self._config = config

    def _get_analyzer(self):
        """Lazy-load to keep imports fast at startup."""
        if self._analyzer is None:
            from src.analyzer.main import CrossGuardAnalyzer
            self._analyzer = CrossGuardAnalyzer()
        return self._analyzer

    def _get_database_updater(self):
        if self._database_updater is None:
            from src.analyzer.database_updater import DatabaseUpdater
            from src.utils.config import CANIUSE_DIR
            self._database_updater = DatabaseUpdater(Path(CANIUSE_DIR))
        return self._database_updater

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Run a compatibility analysis from an AnalysisRequest."""
        if not request.has_files():
            return AnalysisResult(
                success=False,
                error="No files provided for analysis"
            )

        try:
            analyzer = self._get_analyzer()
            target_browsers = request.target_browsers or self.DEFAULT_BROWSERS

            report = analyzer.analyze_project(
                html_files=request.html_files if request.html_files else None,
                css_files=request.css_files if request.css_files else None,
                js_files=request.js_files if request.js_files else None,
                target_browsers=target_browsers
            )

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
        """Shorthand -- pass file lists directly instead of building an AnalysisRequest."""
        request = AnalysisRequest(
            html_files=html_files or [],
            css_files=css_files or [],
            js_files=js_files or [],
            target_browsers=target_browsers or self.DEFAULT_BROWSERS
        )
        return self.analyze(request)

    def get_database_info(self) -> DatabaseInfo:
        try:
            updater = self._get_database_updater()
            info = updater.get_database_info()

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
        try:
            updater = self._get_database_updater()
            result = updater.update_database(progress_callback)

            if result.get('success'):
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
        """Hot-reload the Can I Use data after an update."""
        try:
            from src.analyzer.database import reload_database
            reload_database()
            self._analyzer = None  # force re-init on next analysis
        except Exception:
            pass  # next analysis will pick it up anyway

    def reload_custom_rules(self):
        """Reload custom rules from disk."""
        try:
            from src.parsers.custom_rules_loader import reload_custom_rules
            reload_custom_rules()
            self._analyzer = None
        except Exception:
            pass

    def get_default_browsers(self) -> Dict[str, str]:
        return self.DEFAULT_BROWSERS.copy()

    def get_available_browsers(self) -> List[str]:
        return list(self.DEFAULT_BROWSERS.keys())

    # -- History ---------------------------------------------------------------

    def save_analysis_to_history(
        self,
        result: AnalysisResult,
        file_name: str = 'analysis',
        file_path: str = '',
        file_type: str = 'mixed'
    ) -> Optional[int]:
        """Persist an analysis result to the SQLite history."""
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
        try:
            from src.database.repositories import AnalysisRepository

            repo = AnalysisRepository()
            analyses = repo.get_all_analyses(limit=limit, offset=offset)

            return [analysis.to_dict() for analysis in analyses]

        except Exception as e:
            logger.error(f"Failed to get analysis history: {e}")
            return []

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
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
        try:
            from src.database.repositories import AnalysisRepository

            repo = AnalysisRepository()
            return repo.delete_analysis(analysis_id)

        except Exception as e:
            logger.error(f"Failed to delete analysis #{analysis_id}: {e}")
            return False

    def clear_history(self) -> bool:
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
        try:
            from src.database.repositories import AnalysisRepository

            repo = AnalysisRepository()
            return repo.get_count()

        except Exception as e:
            logger.error(f"Failed to get history count: {e}")
            return 0

    # -- Statistics ------------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """Aggregated stats across all saved analyses."""
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
        try:
            from src.database.statistics import get_statistics_service

            service = get_statistics_service()
            return service.get_score_trend(days)

        except Exception as e:
            logger.error(f"Failed to get score trend: {e}")
            return []

    def get_top_problematic_features(self, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            from src.database.statistics import get_statistics_service

            service = get_statistics_service()
            return service.get_top_problematic_features(limit)

        except Exception as e:
            logger.error(f"Failed to get problematic features: {e}")
            return []

    # -- Settings --------------------------------------------------------------

    def get_setting(self, key: str, default: str = '') -> str:
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            return repo.get(key, default)
        except Exception as e:
            logger.error(f"Failed to get setting '{key}': {e}")
            return default

    def set_setting(self, key: str, value: str) -> bool:
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            repo.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Failed to set setting '{key}': {e}")
            return False

    def get_all_settings(self) -> Dict[str, str]:
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            return repo.get_all()
        except Exception as e:
            logger.error(f"Failed to get all settings: {e}")
            return {}

    def get_setting_as_bool(self, key: str, default: bool = False) -> bool:
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            return repo.get_as_bool(key, default)
        except Exception:
            return default

    def get_setting_as_list(self, key: str, default: List[str] = None) -> List[str]:
        try:
            from src.database.repositories import SettingsRepository
            repo = SettingsRepository()
            return repo.get_as_list(key, default)
        except Exception:
            return default or []

    # -- Bookmarks -------------------------------------------------------------

    def add_bookmark(self, analysis_id: int, note: str = '') -> bool:
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            repo.add_bookmark(analysis_id, note)
            return True
        except Exception as e:
            logger.error(f"Failed to add bookmark for analysis #{analysis_id}: {e}")
            return False

    def remove_bookmark(self, analysis_id: int) -> bool:
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.remove_bookmark(analysis_id)
        except Exception as e:
            logger.error(f"Failed to remove bookmark from analysis #{analysis_id}: {e}")
            return False

    def is_bookmarked(self, analysis_id: int) -> bool:
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.is_bookmarked(analysis_id)
        except Exception:
            return False

    def toggle_bookmark(self, analysis_id: int, note: str = '') -> bool:
        """Returns True if now bookmarked, False if removed."""
        if self.is_bookmarked(analysis_id):
            self.remove_bookmark(analysis_id)
            return False
        else:
            self.add_bookmark(analysis_id, note)
            return True

    def get_all_bookmarks(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.get_all_bookmarks(limit)
        except Exception as e:
            logger.error(f"Failed to get bookmarks: {e}")
            return []

    def update_bookmark_note(self, analysis_id: int, note: str) -> bool:
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.update_note(analysis_id, note)
        except Exception as e:
            logger.error(f"Failed to update bookmark note: {e}")
            return False

    def get_bookmarks_count(self) -> int:
        try:
            from src.database.repositories import BookmarksRepository
            repo = BookmarksRepository()
            return repo.get_count()
        except Exception:
            return 0

    # -- Tags ------------------------------------------------------------------

    def create_tag(self, name: str, color: str = '#58a6ff') -> Optional[int]:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.create_tag(name, color)
        except Exception as e:
            logger.error(f"Failed to create tag '{name}': {e}")
            return None

    def get_all_tags(self) -> List[Dict[str, Any]]:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.get_all_tags()
        except Exception as e:
            logger.error(f"Failed to get tags: {e}")
            return []

    def delete_tag(self, tag_id: int) -> bool:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.delete_tag(tag_id)
        except Exception as e:
            logger.error(f"Failed to delete tag #{tag_id}: {e}")
            return False

    def update_tag(self, tag_id: int, name: str = None, color: str = None) -> bool:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.update_tag(tag_id, name, color)
        except Exception as e:
            logger.error(f"Failed to update tag #{tag_id}: {e}")
            return False

    def add_tag_to_analysis(self, analysis_id: int, tag_id: int) -> bool:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.add_tag_to_analysis(analysis_id, tag_id)
        except Exception as e:
            logger.error(f"Failed to add tag to analysis: {e}")
            return False

    def remove_tag_from_analysis(self, analysis_id: int, tag_id: int) -> bool:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.remove_tag_from_analysis(analysis_id, tag_id)
        except Exception as e:
            logger.error(f"Failed to remove tag from analysis: {e}")
            return False

    def get_tags_for_analysis(self, analysis_id: int) -> List[Dict[str, Any]]:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.get_tags_for_analysis(analysis_id)
        except Exception as e:
            logger.error(f"Failed to get tags for analysis #{analysis_id}: {e}")
            return []

    def get_analyses_by_tag(self, tag_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.get_analyses_by_tag(tag_id, limit)
        except Exception as e:
            logger.error(f"Failed to get analyses by tag #{tag_id}: {e}")
            return []

    def get_tag_counts(self) -> Dict[str, int]:
        try:
            from src.database.repositories import TagsRepository
            repo = TagsRepository()
            return repo.get_tag_counts()
        except Exception as e:
            logger.error(f"Failed to get tag counts: {e}")
            return {}

    # -- Configuration ---------------------------------------------------------

    def load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load and merge config from file, CLI overrides, and defaults."""
        from src.config import load_config
        mgr = load_config(config_path=config_path, overrides=self._config)
        self._config = mgr.to_dict()
        if 'browsers' in self._config:
            self.DEFAULT_BROWSERS.update(self._config['browsers'])
        return self._config

    # -- Export ----------------------------------------------------------------

    def export_to_json(
        self,
        analysis_id_or_result=None,
        output_path: Optional[str] = None,
    ) -> Any:
        """Export as JSON. Returns enriched dict if no output_path, else the file path."""
        report = self._resolve_report(analysis_id_or_result)
        from src.export.json_exporter import export_json
        return export_json(report, output_path=output_path)

    def export_to_pdf(
        self,
        analysis_id_or_result=None,
        output_path: str = '',
    ) -> str:
        report = self._resolve_report(analysis_id_or_result)
        from src.export.pdf_exporter import export_pdf
        return export_pdf(report, output_path)

    def _resolve_report(self, analysis_id_or_result) -> Dict:
        """Accept int (history ID), dict, or AnalysisResult and normalize to dict."""
        if isinstance(analysis_id_or_result, int):
            record = self.get_analysis_by_id(analysis_id_or_result)
            if record is None:
                raise ValueError(f"Analysis #{analysis_id_or_result} not found")
            return record
        if hasattr(analysis_id_or_result, 'to_dict'):
            return analysis_id_or_result.to_dict()
        if isinstance(analysis_id_or_result, dict):
            return analysis_id_or_result
        raise TypeError(f"Expected int, dict, or AnalysisResult, got {type(analysis_id_or_result)}")

    # -- Feature Utilities -----------------------------------------------------

    def get_feature_display_name(self, feature_id: str) -> str:
        from src.utils.feature_names import get_feature_name
        return get_feature_name(feature_id)

    def get_fix_suggestion(self, feature_id: str) -> Optional[str]:
        from src.utils.feature_names import get_fix_suggestion
        return get_fix_suggestion(feature_id)

    def get_polyfill_suggestions(
        self,
        unsupported_features: List[str],
        partial_features: List[str] = None,
        browsers: Dict[str, str] = None,
    ) -> List[Any]:
        try:
            from src.polyfill import PolyfillService
            service = PolyfillService()
            return service.get_recommendations(
                unsupported_features=set(unsupported_features),
                partial_features=set(partial_features or []),
                browsers=browsers or self.DEFAULT_BROWSERS,
            )
        except Exception as e:
            logger.error(f"Failed to get polyfill suggestions: {e}")
            return []

    def generate_polyfills_file(
        self,
        recommendations: List[Any],
        output_path: str,
    ) -> str:
        from src.polyfill import generate_polyfills_file
        return generate_polyfills_file(recommendations, output_path)

    def classify_file(self, file_path: str) -> Optional[str]:
        """Map a file extension to 'html', 'css', 'js', or None."""
        import os
        ext = os.path.splitext(file_path)[1].lower()
        ext_map = {
            '.html': 'html', '.htm': 'html',
            '.css': 'css',
            '.js': 'js', '.mjs': 'js', '.jsx': 'js',
            '.ts': 'js', '.tsx': 'js',
        }
        return ext_map.get(ext)

    def is_ml_enabled(self) -> bool:
        from src.utils.config import ML_ENABLED
        return ML_ENABLED

    # -- Custom Rules ----------------------------------------------------------

    def get_custom_rules(self) -> Dict:
        from src.parsers.custom_rules_loader import load_raw_custom_rules
        return load_raw_custom_rules()

    def save_custom_rules(self, rules_data: Dict) -> bool:
        """Save rules to disk and reset the analyzer so they take effect."""
        from src.parsers.custom_rules_loader import save_custom_rules
        result = save_custom_rules(rules_data)
        if result:
            self._analyzer = None
        return result

    def is_user_rule(
        self, category: str, feature_id: str, subtype: Optional[str] = None
    ) -> bool:
        """Check if a rule was user-added (vs built-in)."""
        from src.parsers.custom_rules_loader import is_user_rule
        return is_user_rule(category, feature_id, subtype)

    # -- Project Scanner -------------------------------------------------------

    def scan_project_directory(
        self,
        path: str,
        config: ScanConfig = None,
        progress_callback: callable = None
    ) -> ScanResult:
        """Find all analyzable files in a directory tree."""
        try:
            from src.scanner import ProjectScanner

            scanner = ProjectScanner()
            result = scanner.scan_directory(path, config, progress_callback)
            return result

        except Exception as e:
            logger.error(f"Failed to scan directory {path}: {e}")
            return ScanResult(project_path=path)

    def detect_project_framework(self, path: str) -> ProjectInfo:
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
        """Analyze every file from a scan and aggregate the results."""
        import time
        from datetime import datetime
        import os

        start_time = time.time()
        target_browsers = target_browsers or self.DEFAULT_BROWSERS

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

        all_files = scan_result.get_all_files()
        file_results = []
        total_score = 0.0
        all_unsupported = []
        all_partial = []
        unique_features = set()

        for i, file_path in enumerate(all_files):
            if progress_callback:
                progress_callback(i + 1, len(all_files), os.path.basename(file_path))

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

            file_result = FileAnalysisResult(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                file_type=file_type,
                score=analysis_result.scores.simple_score if analysis_result.scores else 0.0,
                grade=analysis_result.scores.grade if analysis_result.scores else 'N/A',
                features_count=analysis_result.summary.total_features if analysis_result.summary else 0,
            )

            for browser_name, browser_data in analysis_result.browsers.items():
                file_result.unsupported_features.extend(browser_data.unsupported_features)
                file_result.partial_features.extend(browser_data.partial_features)

            file_result.issues_count = len(set(file_result.unsupported_features)) + len(set(file_result.partial_features))

            file_results.append(file_result)
            total_score += file_result.score

            if analysis_result.detected_features:
                unique_features.update(analysis_result.detected_features.all)
            all_unsupported.extend(file_result.unsupported_features)
            all_partial.extend(file_result.partial_features)

        result.file_results = file_results
        result.total_features = sum(fr.features_count for fr in file_results)
        result.unique_features = len(unique_features)

        if file_results:
            result.overall_score = total_score / len(file_results)
            result.overall_grade = self._score_to_grade(result.overall_score)
            sorted_by_score = sorted(file_results, key=lambda x: x.score)
            result.worst_files = sorted_by_score[:5]

        result.unsupported_count = len(set(all_unsupported))
        result.partial_count = len(set(all_partial))

        from collections import Counter
        issue_counts = Counter(all_unsupported)
        result.top_issues = [
            {'feature': feat, 'count': count}
            for feat, count in issue_counts.most_common(10)
        ]

        result.analysis_duration_ms = int((time.time() - start_time) * 1000)

        return result

    def _score_to_grade(self, score: float) -> str:
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


_service_instance: Optional[AnalyzerService] = None


def get_analyzer_service() -> AnalyzerService:
    """Return the shared singleton instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = AnalyzerService()
    return _service_instance
