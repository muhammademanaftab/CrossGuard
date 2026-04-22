"""Main analyzer - combines all parsers and checks browser compatibility."""

from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
from datetime import datetime

from ..parsers.html_parser import HTMLParser
from ..parsers.js_parser import JavaScriptParser
from ..parsers.css_parser import CSSParser
from .database import get_database
from .compatibility import CompatibilityAnalyzer
from .scorer import CompatibilityScorer
from ..utils.config import get_logger, LATEST_VERSIONS

logger = get_logger('analyzer.main')


class CrossGuardAnalyzer:
    """Orchestrates parsing, compatibility checking, and scoring for web files."""

    def __init__(self):
        self.html_parser = HTMLParser()
        self.js_parser = JavaScriptParser()
        self.css_parser = CSSParser()
        self.database = get_database()
        self.compatibility_analyzer = CompatibilityAnalyzer()
        self.scorer = CompatibilityScorer()

        self.html_features = set()
        self.js_features = set()
        self.css_features = set()
        self.all_features = set()
        self.errors = []
        self.warnings = []
        self.unrecognized_html = set()
        self.unrecognized_css = set()
        self.unrecognized_js = set()
        # Tracks which properties/APIs matched which caniuse feature
        self.css_feature_details = []
        self.js_feature_details = []
        self.html_feature_details = []

    def run_analysis(
        self,
        html_files: Optional[List[str]] = None,
        css_files: Optional[List[str]] = None,
        js_files: Optional[List[str]] = None,
        target_browsers: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Analyze a web project and return a full compatibility report."""
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

    def analyze_single_file(
        self,
        filepath: str,
        file_type: str,
        target_browsers: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Analyze one file ('html', 'css', or 'js') and return a compatibility report."""
        self._reset_state()

        if target_browsers is None:
            target_browsers = self._get_default_browsers()

        if file_type.lower() == 'html':
            self._parse_html_files([filepath])
        elif file_type.lower() == 'css':
            self._parse_css_files([filepath])
        elif file_type.lower() in ['js', 'javascript']:
            self._parse_js_files([filepath])
        else:
            return {
                'success': False,
                'error': f"Unknown file type: {file_type}. Use 'html', 'css', or 'js'."
            }

        self.all_features = self.html_features | self.js_features | self.css_features

        compatibility_results = self._check_compatibility(target_browsers)
        scores = self._calculate_scores(compatibility_results, target_browsers)

        return self._generate_report(compatibility_results, scores, target_browsers)

    def _reset_state(self):
        """Clear all state for a fresh analysis run."""
        self.html_features = set()
        self.js_features = set()
        self.css_features = set()
        self.all_features = set()
        self.errors = []
        self.warnings = []
        self.unrecognized_html = set()
        self.unrecognized_css = set()
        self.unrecognized_js = set()
        self.css_feature_details = []
        self.js_feature_details = []
        self.html_feature_details = []

    def _validate_inputs(
        self,
        html_files: Optional[List[str]],
        css_files: Optional[List[str]],
        js_files: Optional[List[str]]
    ) -> Dict:
        """Check that we got at least one file and all paths exist."""
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

    def _parse_html_files(self, html_files: List[str]):
        for filepath in html_files:
            try:
                features = self.html_parser.parse_file(filepath)
                self.html_features.update(features)
                self.unrecognized_html.update(self.html_parser.unrecognized_patterns)
                self.html_feature_details.extend(self.html_parser.feature_details)
                logger.info(f"Parsed HTML: {Path(filepath).name} ({len(features)} features)")
            except Exception as e:
                error_msg = f"Error parsing HTML file {filepath}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)

    def _parse_css_files(self, css_files: List[str]):
        for filepath in css_files:
            try:
                features = self.css_parser.parse_file(filepath)
                self.css_features.update(features)
                self.unrecognized_css.update(self.css_parser.unrecognized_patterns)
                self.css_feature_details.extend(self.css_parser.feature_details)
                logger.info(f"Parsed CSS: {Path(filepath).name} ({len(features)} features)")
            except Exception as e:
                error_msg = f"Error parsing CSS file {filepath}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)

    def _parse_js_files(self, js_files: List[str]):
        for filepath in js_files:
            try:
                features = self.js_parser.parse_file(filepath)
                self.js_features.update(features)
                self.unrecognized_js.update(self.js_parser.unrecognized_patterns)
                self.js_feature_details.extend(self.js_parser.feature_details)
                logger.info(f"Parsed JS: {Path(filepath).name} ({len(features)} features)")
            except Exception as e:
                error_msg = f"Error parsing JS file {filepath}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)

    def _check_compatibility(self, target_browsers: Dict[str, str]) -> Dict:
        """Look up each feature in the caniuse DB for every target browser."""
        results = {}

        for browser, version in target_browsers.items():
            browser_results = {
                'supported': [],
                'partial': [],
                'unsupported': [],
                'unknown': []
            }

            for feature in self.all_features:
                try:
                    support_status = self.database.check_support(feature, browser, version)

                    if support_status == 'y':
                        browser_results['supported'].append(feature)
                    elif support_status in ['a', 'x']:
                        browser_results['partial'].append(feature)
                    elif support_status == 'n':
                        browser_results['unsupported'].append(feature)
                    else:
                        browser_results['unknown'].append(feature)

                except Exception as e:
                    browser_results['unknown'].append(feature)
                    if feature not in [w.split(':')[0] for w in self.warnings]:
                        self.warnings.append(f"{feature}: Not found in database")

            results[browser] = browser_results

        return results

    def _calculate_scores(
        self,
        compatibility_results: Dict,
        target_browsers: Dict[str, str]
    ) -> Dict:
        """Compute per-browser percentages and an overall weighted score."""
        total_features = len(self.all_features)

        browser_percentages = {}
        for browser, results in compatibility_results.items():
            if total_features == 0:
                browser_percentages[browser] = 100.0
                continue

            supported = len(results['supported'])
            partial = len(results['partial'])

            # supported=100%, partial=50%, unsupported=0%
            compatibility_pct = ((supported * 100) + (partial * 50)) / total_features
            browser_percentages[browser] = compatibility_pct

        # Average across all browsers
        if browser_percentages:
            weighted_score = sum(browser_percentages.values()) / len(browser_percentages)
        else:
            weighted_score = 0.0

        if weighted_score >= 90:
            grade = 'A'
        elif weighted_score >= 80:
            grade = 'B'
        elif weighted_score >= 70:
            grade = 'C'
        elif weighted_score >= 60:
            grade = 'D'
        else:
            grade = 'F'

        unsupported_count = sum(
            len(results['unsupported'])
            for results in compatibility_results.values()
        )
        if unsupported_count == 0:
            risk_level = 'none'
        elif weighted_score >= 80:
            risk_level = 'low'
        elif weighted_score >= 60:
            risk_level = 'medium'
        else:
            risk_level = 'high'

        return {
            'simple_score': weighted_score,  # Same as weighted for consistency
            'weighted_score': weighted_score,
            'compatibility_index': {
                'score': weighted_score,
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
        """Build the final report dict with scores, browser details, and recommendations."""
        total_features = len(self.all_features)
        html_count = len(self.html_features)
        css_count = len(self.css_features)
        js_count = len(self.js_features)

        # Features unsupported in at least one browser
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
            if total > 0:
                compatibility_pct = ((supported + partial * 0.5) / total) * 100

            browser_details[browser] = {
                'version': target_browsers[browser],
                'total_features': total,
                'supported': supported,
                'partial': partial,
                'unsupported': unsupported,
                'unknown': len(results['unknown']),
                'compatibility_percentage': round(compatibility_pct, 2),
                'unsupported_features': results['unsupported'],
                'partial_features': results['partial']
            }

        recommendations = self._generate_recommendations(
            critical_issues,
            compatibility_results,
            target_browsers
        )

        report = {
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
                'html': sorted(list(self.html_features)),
                'css': sorted(list(self.css_features)),
                'js': sorted(list(self.js_features)),
                'all': sorted(list(self.all_features))
            },
            'feature_details': {
                'css': self.css_feature_details,
                'js': self.js_feature_details,
                'html': self.html_feature_details,
            },
            'unrecognized': {
                'html': sorted(list(self.unrecognized_html)),
                'css': sorted(list(self.unrecognized_css)),
                'js': sorted(list(self.unrecognized_js)),
                'total': len(self.unrecognized_html) + len(self.unrecognized_css) + len(self.unrecognized_js)
            },
            'issues': {
                'critical': sorted(list(critical_issues)),
                'warnings': self.warnings,
                'errors': self.errors
            },
            'recommendations': recommendations
        }

        return report

    def _generate_recommendations(
        self,
        critical_issues: Set[str],
        compatibility_results: Dict,
        target_browsers: Dict[str, str]
    ) -> List[str]:
        """Generate human-friendly suggestions based on what we found."""
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
        if partial_count > 0:
            recommendations.append(
                f"{partial_count} features have partial support. "
                "Test thoroughly in target browsers."
            )

        # Dedupe unknowns across browsers
        unknown_features = set()
        for results in compatibility_results.values():
            unknown_features.update(results['unknown'])

        if unknown_features:
            num_browsers = len(target_browsers)
            num_features = len(unknown_features)

            if num_features == 1:
                feature_text = "feature"
            else:
                feature_text = "features"

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

        if not critical_issues and partial_count == 0:
            recommendations.append(
                "All features are well-supported across target browsers."
            )

        return recommendations

    def _get_default_browsers(self) -> Dict[str, str]:
        """Latest versions of the four major browsers."""
        return {
            'chrome': LATEST_VERSIONS['chrome'],
            'firefox': LATEST_VERSIONS['firefox'],
            'safari': LATEST_VERSIONS['safari'],
            'edge': LATEST_VERSIONS['edge']
        }


def run_analysis(
    html_files: Optional[List[str]] = None,
    css_files: Optional[List[str]] = None,
    js_files: Optional[List[str]] = None,
    target_browsers: Optional[Dict[str, str]] = None
) -> Dict:
    """Shortcut to create an analyzer and run it."""
    analyzer = CrossGuardAnalyzer()
    return analyzer.run_analysis(html_files, css_files, js_files, target_browsers)
