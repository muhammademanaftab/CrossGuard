"""Entry point that combines parsers, compatibility checking, and scoring."""

from typing import Dict, List, Set, Optional
from pathlib import Path
from datetime import datetime

from ..parsers.html_parser import HTMLParser
from ..parsers.js_parser import JavaScriptParser
from ..parsers.css_parser import CSSParser
from .compatibility import CompatibilityAnalyzer
from .scorer import CompatibilityScorer
from .web_features import WebFeaturesManager
from ..utils.config import get_logger, LATEST_VERSIONS

# Maps web-features baseline status codes to display labels used in reports.
_BASELINE_LABELS = {'high': 'Widely', 'low': 'Newly', 'limited': 'Limited'}

logger = get_logger('analyzer.main')


class CrossGuardAnalyzer:

    def __init__(self):
        self.html_parser = HTMLParser()
        self.js_parser = JavaScriptParser()
        self.css_parser = CSSParser()
        self.compatibility_analyzer = CompatibilityAnalyzer()
        self.scorer = CompatibilityScorer()
        self.web_features = WebFeaturesManager()
        self._reset_state()

    def _annotate_baseline(self, detail_lists):
        """Attach a 'baseline' label to each feature_details entry. Falls back to 'Unknown'."""
        has_data = self.web_features.has_data()
        for entries in detail_lists:
            for entry in entries:
                if not has_data:
                    entry['baseline'] = 'Unknown'
                    continue
                info = self.web_features.get_baseline_status(entry.get('feature', ''))
                entry['baseline'] = _BASELINE_LABELS.get(info.status, 'Unknown') if info else 'Unknown'

    def run_analysis(
        self,
        html_files: Optional[List[str]] = None,
        css_files: Optional[List[str]] = None,
        js_files: Optional[List[str]] = None,
        target_browsers: Optional[Dict[str, str]] = None
    ) -> Dict:
        self._reset_state()

        if target_browsers is None:
            target_browsers = self._get_default_browsers()

        validation_result = self._validate_inputs(html_files, css_files, js_files)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': validation_result['error'],
                'timestamp': datetime.now().isoformat()
            }

        logger.info("Analyzing project files...")
        self._parse_html_files(html_files or [])
        self._parse_css_files(css_files or [])
        self._parse_js_files(js_files or [])

        self.all_features = self.html_features | self.js_features | self.css_features

        logger.info("Checking browser compatibility...")
        compatibility_results = self._check_compatibility(target_browsers)

        logger.info("Calculating compatibility scores...")
        scores = self._calculate_scores(compatibility_results, target_browsers)

        report = self._generate_report(
            compatibility_results,
            scores,
            target_browsers
        )

        return report

    def _reset_state(self):
        self.html_features = set()
        self.js_features = set()
        self.css_features = set()
        self.all_features = set()
        self.errors = []
        self.warnings = []
        self.unrecognized_html = set()
        self.unrecognized_css = set()
        self.unrecognized_js = set()
        # which source properties/APIs matched which caniuse feature ID
        self.css_feature_details = []
        self.js_feature_details = []
        self.html_feature_details = []

    def _validate_inputs(
        self,
        html_files: Optional[List[str]],
        css_files: Optional[List[str]],
        js_files: Optional[List[str]]
    ) -> Dict:
        if not any([html_files, css_files, js_files]):
            return {
                'valid': False,
                'error': 'No files provided. Please provide at least one HTML, CSS, or JS file.'
            }

        all_files = (html_files or []) + (css_files or []) + (js_files or [])
        for filepath in all_files:
            if not Path(filepath).exists():
                return {
                    'valid': False,
                    'error': f'File not found: {filepath}'
                }

        return {'valid': True}

    def _parse_files(self, label: str, files: List[str], parser,
                     feature_set: set, unrecognized_set: set, details_list: list):
        for filepath in files:
            try:
                features = parser.parse_file(filepath)
                feature_set.update(features)
                unrecognized_set.update(parser.unrecognized_patterns)
                details_list.extend(parser.feature_details)
                logger.info(f"Parsed {label}: {Path(filepath).name} ({len(features)} features)")
            except Exception as e:
                error_msg = f"Error parsing {label} file {filepath}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)

    def _parse_html_files(self, html_files: List[str]):
        self._parse_files('HTML', html_files, self.html_parser,
                          self.html_features, self.unrecognized_html, self.html_feature_details)

    def _parse_css_files(self, css_files: List[str]):
        self._parse_files('CSS', css_files, self.css_parser,
                          self.css_features, self.unrecognized_css, self.css_feature_details)

    def _parse_js_files(self, js_files: List[str]):
        self._parse_files('JS', js_files, self.js_parser,
                          self.js_features, self.unrecognized_js, self.js_feature_details)

    def _check_compatibility(self, target_browsers: Dict[str, str]) -> Dict:
        return self.compatibility_analyzer.classify_features(self.all_features, target_browsers)

    def _calculate_scores(
        self,
        compatibility_results: Dict,
        target_browsers: Dict[str, str]
    ) -> Dict:
        browser_percentages = {
            browser: self.scorer.score_statuses(results['statuses'])
            for browser, results in compatibility_results.items()
        }

        overall_score = self.scorer.overall_score(browser_percentages)
        grade = self.scorer.grade(overall_score)

        unsupported_count = sum(
            len(results['unsupported'])
            for results in compatibility_results.values()
        )
        risk_level = self.scorer.risk_level(overall_score, unsupported_count)

        return {
            'simple_score': overall_score,  # kept for API compat
            'weighted_score': overall_score,
            'compatibility_index': {
                'score': overall_score,
                'grade': grade,
                'risk_level': risk_level
            },
            'grade': grade,
            'risk_level': risk_level
        }

    def _generate_report(
        self,
        compatibility_results: Dict,
        scores: Dict,
        target_browsers: Dict[str, str]
    ) -> Dict:
        total_features = len(self.all_features)
        html_count = len(self.html_features)
        css_count = len(self.css_features)
        js_count = len(self.js_features)

        # union of unsupported features across all browsers (shown as critical issues)
        critical_issues = set()
        for browser, results in compatibility_results.items():
            critical_issues.update(results['unsupported'])

        browser_details = {}
        for browser, results in compatibility_results.items():
            total = len(self.all_features)
            supported = len(results['supported'])
            partial = len(results['partial'])
            unsupported = len(results['unsupported'])

            compatibility_pct = 0
            if total:
                compatibility_pct = ((supported + partial * 0.5) / total) * 100

            browser_details[browser] = {
                'version': target_browsers[browser],
                'total_features': total,
                'supported': supported,
                'partial': partial,
                'unsupported': unsupported,
                'unknown': len(results['unknown']),
                'compatibility_percentage': round(compatibility_pct, 2),
                'supported_features': results['supported'],
                'partial_features': results['partial'],
                'unsupported_features': results['unsupported'],
                'unknown_features': results['unknown'],
            }

        recommendations = self._generate_recommendations(
            critical_issues,
            compatibility_results,
            target_browsers
        )

        self._annotate_baseline([
            self.css_feature_details,
            self.js_feature_details,
            self.html_feature_details,
        ])

        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_features': total_features,
                'html_features': html_count,
                'css_features': css_count,
                'js_features': js_count,
                'critical_issues': len(critical_issues),
                'overall_grade': scores['grade'],
                'risk_level': scores['risk_level']
            },
            'scores': {
                'simple_score': round(scores['simple_score'], 2),
                'weighted_score': round(scores['weighted_score'], 2),
                'compatibility_index': round(scores['compatibility_index']['score'], 2),
                'grade': scores['grade'],
                'risk_level': scores['risk_level']
            },
            'browsers': browser_details,
            'features': {
                'html': sorted(self.html_features),
                'css': sorted(self.css_features),
                'js': sorted(self.js_features),
                'all': sorted(self.all_features)
            },
            'feature_details': {
                'css': self.css_feature_details,
                'js': self.js_feature_details,
                'html': self.html_feature_details,
            },
            'unrecognized': {
                'html': sorted(self.unrecognized_html),
                'css': sorted(self.unrecognized_css),
                'js': sorted(self.unrecognized_js),
                'total': len(self.unrecognized_html) + len(self.unrecognized_css) + len(self.unrecognized_js)
            },
            'issues': {
                'critical': sorted(critical_issues),
                'warnings': self.warnings,
                'errors': self.errors
            },
            'recommendations': recommendations
        }

    def _generate_recommendations(
        self,
        critical_issues: Set[str],
        compatibility_results: Dict,
        target_browsers: Dict[str, str]
    ) -> List[str]:
        recommendations = []

        if critical_issues:
            recommendations.append(
                f"{len(critical_issues)} features are not supported in some browsers. "
                "Consider providing fallbacks or polyfills."
            )

        partial_count = sum(
            len(results['partial'])
            for results in compatibility_results.values()
        )
        if partial_count:
            recommendations.append(
                f"{partial_count} features have partial support. "
                "Test thoroughly in target browsers."
            )

        unknown_features = set()
        for results in compatibility_results.values():
            unknown_features.update(results['unknown'])

        if unknown_features:
            num_browsers = len(target_browsers)
            num_features = len(unknown_features)

            feature_text = "feature" if num_features == 1 else "features"

            recommendations.append(
                f"{num_features} {feature_text} not found in database across {num_browsers} browsers. "
                "These may be universally supported or custom features."
            )

        for browser, results in compatibility_results.items():
            unsupported = len(results['unsupported'])
            if unsupported > 5:
                recommendations.append(
                    f"{browser.capitalize()}: {unsupported} unsupported features detected. "
                    "Consider testing and providing alternatives."
                )

        if not critical_issues and not partial_count:
            recommendations.append(
                "All features are well-supported across target browsers."
            )

        return recommendations

    def _get_default_browsers(self) -> Dict[str, str]:
        return {
            'chrome': LATEST_VERSIONS['chrome'],
            'firefox': LATEST_VERSIONS['firefox'],
            'safari': LATEST_VERSIONS['safari'],
            'edge': LATEST_VERSIONS['edge']
        }
