"""Single backend facade — frontends (GUI and CLI) talk only to this."""

from typing import Optional, Dict, List, Any
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
from src.database.repositories import (
    AnalysisRepository,
    SettingsRepository,
    BookmarksRepository,
    save_analysis_from_result,
)
from src.database.statistics import get_statistics_service

logger = get_logger('api.service')


class AnalyzerService:
    """Single facade that the GUI and CLI talk to. Hides parsers, scorer, database, and AI."""

    DEFAULT_BROWSERS = {
        'chrome': LATEST_VERSIONS['chrome'],
        'firefox': LATEST_VERSIONS['firefox'],
        'safari': LATEST_VERSIONS['safari'],
        'edge': LATEST_VERSIONS['edge']
    }

    def __init__(self, config: Optional[Dict] = None):
        self._analyzer = None
        self._database_updater = None
        self._web_features = None
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

    def _get_web_features(self):
        if self._web_features is None:
            from src.analyzer.web_features import WebFeaturesManager
            self._web_features = WebFeaturesManager()
        return self._web_features

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        if not request.has_files():
            return AnalysisResult(
                success=False,
                error="No files provided for analysis"
            )

        try:
            analyzer = self._get_analyzer()
            target_browsers = request.target_browsers or self.DEFAULT_BROWSERS

            report = analyzer.run_analysis(
                html_files=request.html_files if request.html_files else None,
                css_files=request.css_files if request.css_files else None,
                js_files=request.js_files if request.js_files else None,
                target_browsers=target_browsers
            )

            result = AnalysisResult.from_dict(report)

            # Enrich with Baseline status if web-features data is available
            result.baseline_summary = self._get_baseline_summary(result)

            return result

        except Exception as e:
            return AnalysisResult(
                success=False,
                error=str(e)
            )

    def _get_baseline_summary(self, result: AnalysisResult) -> Optional[Dict]:
        try:
            wf = self._get_web_features()
            if not wf.has_data():
                return None

            feature_ids = []
            if result.detected_features:
                feature_ids = result.detected_features.get('all', [])

            if not feature_ids:
                return None

            return wf.get_baseline_summary(feature_ids)
        except Exception:
            return None

    def analyze_files(
        self,
        html_files: List[str] = None,
        css_files: List[str] = None,
        js_files: List[str] = None,
        target_browsers: Dict[str, str] = None
    ) -> AnalysisResult:
        """Convenience wrapper — avoids building an AnalysisRequest by hand."""
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

            npm_version = info.get('npm_version')

            # Check for npm updates (non-blocking, best-effort)
            npm_latest = None
            update_available = False
            try:
                npm_check = updater.check_npm_update()
                if npm_check.get('success'):
                    npm_latest = npm_check.get('latest_version')
                    update_available = npm_check.get('update_available', False)
            except Exception:
                pass

            return DatabaseInfo(
                features_count=info.get('features_count', 0),
                last_updated=str(last_updated),
                is_git_repo=info.get('is_git_repo', False),
                npm_version=npm_version,
                npm_latest=npm_latest,
                update_available=update_available,
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
        try:
            from src.parsers.custom_rules_loader import reload_custom_rules
            reload_custom_rules()
            self._analyzer = None
        except Exception:
            pass

    def _analysis_repo(self) -> AnalysisRepository:
        return AnalysisRepository()

    def _settings_repo(self) -> SettingsRepository:
        return SettingsRepository()

    def _bookmarks_repo(self) -> BookmarksRepository:
        return BookmarksRepository()

    # -- History ---------------------------------------------------------------

    def save_analysis_to_history(
        self,
        result: AnalysisResult,
        file_name: str = 'analysis',
        file_path: str = '',
        file_type: str = 'mixed'
    ) -> Optional[int]:
        if not result.success:
            logger.warning("Cannot save failed analysis to history")
            return None

        try:
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
            analyses = self._analysis_repo().get_all_analyses(limit=limit, offset=offset)
            return [analysis.to_dict() for analysis in analyses]
        except Exception:
            return []

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        try:
            analysis = self._analysis_repo().get_analysis_by_id(analysis_id, include_features=True)
            if analysis:
                return analysis.to_dict()
            return None
        except Exception:
            return None

    def delete_from_history(self, analysis_id: int) -> bool:
        try:
            return self._analysis_repo().delete_analysis(analysis_id)
        except Exception:
            return False

    def clear_history(self) -> bool:
        try:
            count = self._analysis_repo().clear_all()
            logger.info(f"Cleared {count} analyses from history")
            return True
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False

    def get_history_count(self) -> int:
        try:
            return self._analysis_repo().get_count()
        except Exception:
            return 0

    # -- Statistics ------------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        try:
            return get_statistics_service().get_summary_statistics()
        except Exception as e:
            return {
                'total_analyses': 0,
                'average_score': 0,
                'best_score': 0,
                'worst_score': 0,
                'top_problematic_features': [],
                'most_analyzed_files': [],
                'error': str(e),
            }

    # -- Settings --------------------------------------------------------------

    def get_setting(self, key: str, default: str = '') -> str:
        try:
            return self._settings_repo().get(key, default)
        except Exception:
            return default

    def set_setting(self, key: str, value: str) -> bool:
        try:
            self._settings_repo().set(key, value)
            return True
        except Exception:
            return False

    def get_setting_as_bool(self, key: str, default: bool = False) -> bool:
        try:
            return self._settings_repo().get_as_bool(key, default)
        except Exception:
            return default

    def get_setting_as_list(self, key: str, default: List[str] = None) -> List[str]:
        try:
            return self._settings_repo().get_as_list(key, default)
        except Exception:
            return default or []

    # -- Bookmarks -------------------------------------------------------------

    def add_bookmark(self, analysis_id: int, note: str = '') -> bool:
        try:
            self._bookmarks_repo().add_bookmark(analysis_id, note)
            return True
        except Exception:
            return False

    def remove_bookmark(self, analysis_id: int) -> bool:
        try:
            return self._bookmarks_repo().remove_bookmark(analysis_id)
        except Exception:
            return False

    def is_bookmarked(self, analysis_id: int) -> bool:
        try:
            return self._bookmarks_repo().is_bookmarked(analysis_id)
        except Exception:
            return False

    def toggle_bookmark(self, analysis_id: int, note: str = '') -> bool:
        """Returns True if now bookmarked, False if removed."""
        if self.is_bookmarked(analysis_id):
            self.remove_bookmark(analysis_id)
            return False
        self.add_bookmark(analysis_id, note)
        return True

    def get_all_bookmarks(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            return self._bookmarks_repo().get_all_bookmarks(limit)
        except Exception:
            return []

    # -- Web Features (Baseline) -----------------------------------------------

    def get_baseline_status(self, feature_id: str) -> Optional[Dict]:
        try:
            wf = self._get_web_features()
            info = wf.get_baseline_status(feature_id)
            return info.to_dict() if info else None
        except Exception:
            return None

    # -- Export ----------------------------------------------------------------

    def export_to_json(
        self,
        analysis_id_or_result=None,
        output_path: Optional[str] = None,
    ) -> Any:
        """Returns enriched dict if no output_path given, otherwise writes to file and returns path."""
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

    def export_to_sarif(
        self,
        analysis_id_or_result=None,
        output_path: Optional[str] = None,
    ) -> str:
        """Writes SARIF 2.1.0 if output_path is given; otherwise returns the SARIF JSON as a string."""
        import json
        report = self._resolve_report(analysis_id_or_result)
        from src.export.sarif_exporter import export_sarif
        if output_path:
            export_sarif(report, output_path=output_path)
            return output_path
        return json.dumps(export_sarif(report), indent=2)

    def export_to_junit(
        self,
        analysis_id_or_result=None,
        output_path: Optional[str] = None,
    ) -> str:
        """Writes JUnit XML if output_path is given; otherwise returns the XML as a string."""
        report = self._resolve_report(analysis_id_or_result)
        from src.export.junit_exporter import export_junit
        result = export_junit(report, output_path=output_path)
        return output_path if output_path else (result or '')

    def _resolve_report(self, analysis_id_or_result) -> Dict:
        """Accept int (history ID), dict, or AnalysisResult and normalize to the
        exporter-shaped report dict (summary/scores/browsers/features/...).
        """
        if isinstance(analysis_id_or_result, int):
            record = self.get_analysis_by_id(analysis_id_or_result)
            if record is None:
                raise ValueError(f"Analysis #{analysis_id_or_result} not found")
            return self._db_record_to_report(record)
        if hasattr(analysis_id_or_result, 'to_dict'):
            return analysis_id_or_result.to_dict()
        if isinstance(analysis_id_or_result, dict):
            return analysis_id_or_result
        raise TypeError(f"Expected int, dict, or AnalysisResult, got {type(analysis_id_or_result)}")

    def _db_record_to_report(self, db: Dict) -> Dict:
        """Rebuild the analyzer-shaped report from what the DB stored.

        The DB schema is lossy — we don't persist feature descriptions,
        matched properties, unrecognized patterns, or recommendations. This
        reconstructs enough for the exporters to render a usable report.
        """
        features = db.get('features') or []

        # Group feature IDs by category
        def _ids_for(cat_values):
            return [f['feature_id'] for f in features if f.get('category') in cat_values]

        html_ids = _ids_for(('html',))
        css_ids = _ids_for(('css',))
        js_ids = _ids_for(('js', 'javascript'))
        all_ids = [f['feature_id'] for f in features]

        # Per-browser rollups from browser_results attached to each feature
        browsers_used = db.get('browsers') or {}
        browser_details = {}
        for browser_code, version in browsers_used.items():
            supported = partial = unsupported = unknown = 0
            unsup_list, part_list = [], []
            for f in features:
                for br in f.get('browser_results', []) or []:
                    if br.get('browser') != browser_code:
                        continue
                    status = br.get('support_status', 'u')
                    if status == 'y':
                        supported += 1
                    elif status == 'a':
                        partial += 1
                        part_list.append(f['feature_id'])
                    elif status == 'n':
                        unsupported += 1
                        unsup_list.append(f['feature_id'])
                    else:
                        unknown += 1
                    break
            total = supported + partial + unsupported + unknown
            compat_pct = ((supported + partial * 0.5) / total * 100) if total else 0
            browser_details[browser_code] = {
                'version': version,
                'total_features': total,
                'supported': supported,
                'partial': partial,
                'unsupported': unsupported,
                'unknown': unknown,
                'compatibility_percentage': round(compat_pct, 2),
                'unsupported_features': sorted(unsup_list),
                'partial_features': sorted(part_list),
            }

        # Critical issues = union of unsupported features across browsers
        critical = set()
        for details in browser_details.values():
            critical.update(details['unsupported_features'])

        # Risk level derived from score + critical count
        from src.analyzer.scorer import CompatibilityScorer
        score = float(db.get('overall_score') or 0)
        risk = CompatibilityScorer().risk_level(score, len(critical))

        def _details_for(cat_values):
            return [
                {
                    'feature': f['feature_id'],
                    'description': f.get('feature_name') or '',
                    'matched_properties': [],
                }
                for f in features if f.get('category') in cat_values
            ]

        # Best-effort recommendations from the reconstructed numbers
        partial_count = sum(d['partial'] for d in browser_details.values())
        recommendations = []
        if critical:
            recommendations.append(
                f"{len(critical)} features are not supported in some browsers. "
                "Consider providing fallbacks or polyfills."
            )
        if partial_count:
            recommendations.append(
                f"{partial_count} features have partial support. "
                "Test thoroughly in target browsers."
            )
        if not critical and not partial_count:
            recommendations.append("All features are well-supported across target browsers.")

        return {
            'success': True,
            'timestamp': db.get('analyzed_at') or '',
            'file_name': db.get('file_name', ''),
            'summary': {
                'total_features': db.get('total_features') or len(all_ids),
                'html_features': len(html_ids),
                'css_features': len(css_ids),
                'js_features': len(js_ids),
                'critical_issues': len(critical),
                'overall_grade': db.get('grade') or 'N/A',
                'risk_level': risk,
            },
            'scores': {
                'simple_score': round(score, 2),
                'weighted_score': round(score, 2),
                'compatibility_index': round(score, 2),
                'grade': db.get('grade') or 'N/A',
                'risk_level': risk,
            },
            'browsers': browser_details,
            'features': {
                'html': sorted(html_ids),
                'css': sorted(css_ids),
                'js': sorted(js_ids),
                'all': sorted(all_ids),
            },
            'feature_details': {
                'html': _details_for(('html',)),
                'css': _details_for(('css',)),
                'js': _details_for(('js', 'javascript')),
            },
            'unrecognized': {'html': [], 'css': [], 'js': [], 'total': 0},
            'issues': {'critical': sorted(critical), 'warnings': [], 'errors': []},
            'recommendations': recommendations,
        }

    # -- Feature Utilities -----------------------------------------------------

    def get_feature_display_name(self, feature_id: str) -> str:
        from src.utils.feature_names import get_feature_name
        return get_feature_name(feature_id)

    def get_fix_suggestion(self, feature_id: str) -> Optional[str]:
        from src.utils.feature_names import get_fix_suggestion
        return get_fix_suggestion(feature_id)

    def get_version_ranges(self, feature_id: str, browser: str) -> List[Dict]:
        from src.analyzer.version_ranges import get_version_ranges
        return get_version_ranges(feature_id, browser)

    def get_version_range_summary(self, feature_id: str) -> Dict[str, Dict]:
        """Per-feature support ranges across every browser in the catalog."""
        from src.analyzer.version_ranges import get_support_summary
        return get_support_summary(feature_id)

    def get_browser_display_names(self) -> Dict[str, str]:
        """Maps short codes ('chrome', 'ios_saf') to display labels ('Chrome', 'Safari on iOS')."""
        from src.analyzer.version_ranges import BROWSER_NAMES
        return dict(BROWSER_NAMES)

    def get_feature_catalogs(self) -> Dict[str, Dict]:
        """Pre-grouped built-in feature detection rules for the Custom Rules editor."""
        from src.parsers.css_feature_maps import (
            ALL_CSS_FEATURES,
            CSS_LAYOUT_FEATURES, CSS_TRANSFORM_ANIMATION, CSS_COLOR_BACKGROUND,
            CSS_TYPOGRAPHY, CSS_BOX_MODEL, CSS_BORDER_OUTLINE, CSS_SHADOW_EFFECTS,
            CSS_SELECTORS, CSS_MEDIA_QUERIES, CSS_UNITS, CSS_VARIABLES, CSS_AT_RULES,
            CSS_POSITIONING, CSS_OVERFLOW, CSS_INTERACTION, CSS_MISC, CSS_CONTAINER,
            CSS_SUBGRID, CSS_CASCADE, CSS_NESTING, CSS_ADDITIONAL_1, CSS_ADDITIONAL_2,
            CSS_ADDITIONAL_3,
        )
        from src.parsers.js_feature_maps import (
            ALL_JS_FEATURES,
            JS_SYNTAX_FEATURES, JS_API_FEATURES, JS_ARRAY_METHODS, JS_STRING_METHODS,
            JS_OBJECT_METHODS, JS_STORAGE_APIS, JS_DOM_APIS,
        )
        from src.parsers.html_feature_maps import (
            ALL_HTML_FEATURES,
            HTML_ELEMENTS, HTML_ATTRIBUTES, HTML_INPUT_TYPES, HTML_ATTRIBUTE_VALUES,
        )
        return {
            'css': {
                'all': ALL_CSS_FEATURES,
                'categories': {
                    'Layout': CSS_LAYOUT_FEATURES,
                    'Transforms & Animation': CSS_TRANSFORM_ANIMATION,
                    'Colors & Background': CSS_COLOR_BACKGROUND,
                    'Typography': CSS_TYPOGRAPHY,
                    'Box Model': CSS_BOX_MODEL,
                    'Border & Outline': CSS_BORDER_OUTLINE,
                    'Shadow & Effects': CSS_SHADOW_EFFECTS,
                    'Selectors': CSS_SELECTORS,
                    'Media Queries': CSS_MEDIA_QUERIES,
                    'Units': CSS_UNITS,
                    'Variables': CSS_VARIABLES,
                    'At-Rules': CSS_AT_RULES,
                    'Positioning': CSS_POSITIONING,
                    'Overflow': CSS_OVERFLOW,
                    'Interaction': CSS_INTERACTION,
                    'Container': CSS_CONTAINER,
                    'Subgrid': CSS_SUBGRID,
                    'Cascade': CSS_CASCADE,
                    'Nesting': CSS_NESTING,
                    'Other': {**CSS_MISC, **CSS_ADDITIONAL_1, **CSS_ADDITIONAL_2, **CSS_ADDITIONAL_3},
                },
            },
            'js': {
                'all': ALL_JS_FEATURES,
                'categories': {
                    'Syntax': JS_SYNTAX_FEATURES,
                    'Web APIs': JS_API_FEATURES,
                    'Array Methods': JS_ARRAY_METHODS,
                    'String Methods': JS_STRING_METHODS,
                    'Object Methods': JS_OBJECT_METHODS,
                    'Storage': JS_STORAGE_APIS,
                    'DOM APIs': JS_DOM_APIS,
                },
            },
            'html': {
                'all': ALL_HTML_FEATURES,
                'elements': HTML_ELEMENTS,
                'attributes': HTML_ATTRIBUTES,
                'input_types': HTML_INPUT_TYPES,
                'attribute_values': HTML_ATTRIBUTE_VALUES,
            },
        }

    def get_polyfill_map(self) -> Dict:
        """Raw polyfill-recommendation JSON used by the Rules editor."""
        from src.polyfill.polyfill_loader import load_polyfill_map
        return load_polyfill_map()

    def save_polyfill_map(self, data: Dict) -> bool:
        """Write the polyfill-recommendation JSON. Returns True on success."""
        from src.polyfill.polyfill_loader import save_polyfill_map
        return save_polyfill_map(data)

    def get_ai_fix_suggestions(
        self,
        unsupported_features: List[str],
        partial_features: List[str] = None,
        file_type: str = "css",
        browsers: Dict[str, str] = None,
        api_key: str = None,
        provider: str = "anthropic",
    ) -> List[Any]:
        """Returns [] immediately if no API key is configured — never raises."""
        key = api_key or self.get_setting('ai_api_key', '')
        if not key:
            return []
        try:
            from src.ai import AIFixService
            prov = provider or self.get_setting('ai_provider', 'anthropic')
            model = self.get_setting('ai_model', '')
            max_feat = int(self.get_setting('ai_max_features', '10'))
            priority = self.get_setting('ai_priority', 'unsupported_first')
            service = AIFixService(
                api_key=key, provider=prov,
                model=model or None, max_features=max_feat, priority=priority,
            )
            return service.get_fix_suggestions(
                unsupported_features=set(unsupported_features),
                partial_features=set(partial_features or []),
                file_type=file_type,
                browsers=browsers or self.DEFAULT_BROWSERS,
            )
        except Exception as e:
            logger.error(f"Failed to get AI fix suggestions: {e}")
            return []

    def get_polyfill_recommendations(
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
        except Exception:
            return []

    def categorize_polyfill_recommendations(self, recommendations: List[Any]) -> Dict:
        from src.polyfill import PolyfillService
        return PolyfillService().categorize_recommendations(recommendations)

    def get_polyfill_install_command(self, recommendations: List[Any]) -> str:
        from src.polyfill import PolyfillService
        return PolyfillService().get_aggregate_install_command(recommendations)

    def get_polyfill_imports(self, recommendations: List[Any]) -> List[str]:
        from src.polyfill import PolyfillService
        return PolyfillService().get_aggregate_imports(recommendations)

    def get_polyfill_total_size_kb(self, recommendations: List[Any]) -> float:
        from src.polyfill import PolyfillService
        return PolyfillService().get_total_size_kb(recommendations)

    def generate_polyfills_file(
        self,
        recommendations: List[Any],
        output_path: str,
    ) -> str:
        from src.polyfill import generate_polyfills_file
        return generate_polyfills_file(recommendations, output_path)

    # -- Custom Rules ----------------------------------------------------------

    def get_custom_rules(self) -> Dict:
        from src.parsers.custom_rules_loader import load_raw_custom_rules
        return load_raw_custom_rules()

    def save_custom_rules(self, rules_data: Dict) -> bool:
        """Resets the analyzer after saving so the next analysis picks up the new rules."""
        from src.parsers.custom_rules_loader import save_custom_rules
        result = save_custom_rules(rules_data)
        if result:
            self._analyzer = None
        return result


_service_instance: Optional[AnalyzerService] = None


def get_analyzer_service() -> AnalyzerService:
    global _service_instance
    if _service_instance is None:
        _service_instance = AnalyzerService()
    return _service_instance
