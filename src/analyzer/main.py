"""
Cross Guard Main Analyzer
Combines HTML, CSS, and JavaScript parsers to analyze complete web projects
for cross-browser compatibility.
"""

from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

from ..parsers.html_parser import HTMLParser
from ..parsers.js_parser import JavaScriptParser
from ..parsers.css_parser import CSSParser
from .database import get_database
from .compatibility import CompatibilityAnalyzer
from .scorer import CompatibilityScorer
from ..utils.config import get_logger, LATEST_VERSIONS

# Module logger
logger = get_logger('analyzer.main')


class CrossGuardAnalyzer:
    """Main analyzer that combines all parsers and generates compatibility reports."""
    
    def __init__(self):
        """Initialize the Cross Guard analyzer."""
        self.html_parser = HTMLParser()
        self.js_parser = JavaScriptParser()
        self.css_parser = CSSParser()
        self.database = get_database()
        self.compatibility_analyzer = CompatibilityAnalyzer()
        self.scorer = CompatibilityScorer()
        
        # Analysis results
        self.html_features = set()
        self.js_features = set()
        self.css_features = set()
        self.all_features = set()
        self.errors = []
        self.warnings = []
        
    def analyze_project(
        self,
        html_files: Optional[List[str]] = None,
        css_files: Optional[List[str]] = None,
        js_files: Optional[List[str]] = None,
        target_browsers: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Analyze a complete web project for compatibility.
        
        Args:
            html_files: List of HTML file paths
            css_files: List of CSS file paths
            js_files: List of JavaScript file paths
            target_browsers: Dict of browser names and versions
                           e.g., {'chrome': '144', 'firefox': '146'}
        
        Returns:
            Comprehensive analysis report with compatibility scores and details
        """
        # Reset state
        self._reset_state()
        
        # Set default target browsers if not provided
        if target_browsers is None:
            target_browsers = self._get_default_browsers()
        
        # Validate inputs
        validation_result = self._validate_inputs(html_files, css_files, js_files)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': validation_result['error'],
                'timestamp': datetime.now().isoformat()
            }
        
        # Parse all files
        logger.info("Analyzing project files...")
        self._parse_html_files(html_files or [])
        self._parse_css_files(css_files or [])
        self._parse_js_files(js_files or [])

        # Combine all features
        self.all_features = self.html_features | self.js_features | self.css_features

        # Check compatibility
        logger.info("Checking browser compatibility...")
        compatibility_results = self._check_compatibility(target_browsers)

        # Calculate scores
        logger.info("Calculating compatibility scores...")
        scores = self._calculate_scores(compatibility_results, target_browsers)
        
        # Generate detailed report
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
        """Analyze a single file for compatibility.
        
        Args:
            filepath: Path to the file
            file_type: Type of file ('html', 'css', or 'js')
            target_browsers: Dict of browser names and versions
        
        Returns:
            Analysis report for the single file
        """
        self._reset_state()
        
        if target_browsers is None:
            target_browsers = self._get_default_browsers()
        
        # Parse based on file type
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
        
        # Check compatibility
        compatibility_results = self._check_compatibility(target_browsers)
        scores = self._calculate_scores(compatibility_results, target_browsers)
        
        return self._generate_report(compatibility_results, scores, target_browsers)
    
    def _reset_state(self):
        """Reset analyzer state for new analysis."""
        self.html_features = set()
        self.js_features = set()
        self.css_features = set()
        self.all_features = set()
        self.errors = []
        self.warnings = []
    
    def _validate_inputs(
        self,
        html_files: Optional[List[str]],
        css_files: Optional[List[str]],
        js_files: Optional[List[str]]
    ) -> Dict:
        """Validate input files.
        
        Returns:
            Dict with 'valid' boolean and optional 'error' message
        """
        # Check if at least one file is provided
        if not any([html_files, css_files, js_files]):
            return {
                'valid': False,
                'error': 'No files provided. Please provide at least one HTML, CSS, or JS file.'
            }
        
        # Check if files exist
        all_files = (html_files or []) + (css_files or []) + (js_files or [])
        for filepath in all_files:
            if not Path(filepath).exists():
                return {
                    'valid': False,
                    'error': f'File not found: {filepath}'
                }
        
        return {'valid': True}
    
    def _parse_html_files(self, html_files: List[str]):
        """Parse all HTML files and collect features."""
        for filepath in html_files:
            try:
                features = self.html_parser.parse_file(filepath)
                self.html_features.update(features)
                logger.info(f"Parsed HTML: {Path(filepath).name} ({len(features)} features)")
            except Exception as e:
                error_msg = f"Error parsing HTML file {filepath}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)

    def _parse_css_files(self, css_files: List[str]):
        """Parse all CSS files and collect features."""
        for filepath in css_files:
            try:
                features = self.css_parser.parse_file(filepath)
                self.css_features.update(features)
                logger.info(f"Parsed CSS: {Path(filepath).name} ({len(features)} features)")
            except Exception as e:
                error_msg = f"Error parsing CSS file {filepath}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)

    def _parse_js_files(self, js_files: List[str]):
        """Parse all JavaScript files and collect features."""
        for filepath in js_files:
            try:
                features = self.js_parser.parse_file(filepath)
                self.js_features.update(features)
                logger.info(f"Parsed JS: {Path(filepath).name} ({len(features)} features)")
            except Exception as e:
                error_msg = f"Error parsing JS file {filepath}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
    
    def _check_compatibility(self, target_browsers: Dict[str, str]) -> Dict:
        """Check compatibility for all detected features.
        
        Returns:
            Dict with compatibility results for each browser
        """
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
                    # Feature not found in database or other error
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
        """Calculate compatibility scores.
        
        Returns:
            Dict with various scoring metrics
        """
        # Prepare support status for scorer
        support_status = {}
        for browser, results in compatibility_results.items():
            total = len(self.all_features)
            if total == 0:
                support_status[browser] = 'y'
                continue
            
            supported = len(results['supported'])
            partial = len(results['partial'])
            unsupported = len(results['unsupported'])
            
            # Determine overall status
            if unsupported == 0 and partial == 0:
                support_status[browser] = 'y'
            elif unsupported > total * 0.2:  # More than 20% unsupported
                support_status[browser] = 'n'
            else:
                support_status[browser] = 'a'
        
        # Calculate scores
        simple_score = self.scorer.calculate_simple_score(support_status)
        weighted_score_obj = self.scorer.calculate_weighted_score(support_status)
        compatibility_index = self.scorer.calculate_compatibility_index(support_status)
        
        # Extract weighted score value
        weighted_score = weighted_score_obj.weighted_score if hasattr(weighted_score_obj, 'weighted_score') else weighted_score_obj
        
        return {
            'simple_score': simple_score,
            'weighted_score': weighted_score,
            'compatibility_index': compatibility_index,
            'grade': compatibility_index['grade'],
            'risk_level': compatibility_index['risk_level']
        }
    
    def _generate_report(
        self,
        compatibility_results: Dict,
        scores: Dict,
        target_browsers: Dict[str, str]
    ) -> Dict:
        """Generate comprehensive analysis report.
        
        Returns:
            Complete analysis report
        """
        # Calculate statistics
        total_features = len(self.all_features)
        html_count = len(self.html_features)
        css_count = len(self.css_features)
        js_count = len(self.js_features)
        
        # Find critical issues (unsupported in any browser)
        critical_issues = set()
        for browser, results in compatibility_results.items():
            critical_issues.update(results['unsupported'])
        
        # Browser-specific details
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
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            critical_issues,
            compatibility_results,
            target_browsers
        )
        
        # Build final report
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
        """Generate recommendations based on analysis results.
        
        Args:
            critical_issues: Set of critical issue feature IDs
            compatibility_results: Browser compatibility results
            target_browsers: Dict of target browsers and versions
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check for critical issues
        if critical_issues:
            recommendations.append(
                f"⚠️  {len(critical_issues)} features are not supported in some browsers. "
                "Consider providing fallbacks or polyfills."
            )
        
        # Check for partial support
        partial_count = sum(
            len(results['partial']) 
            for results in compatibility_results.values()
        )
        if partial_count > 0:
            recommendations.append(
                f"ℹ️  {partial_count} features have partial support. "
                "Test thoroughly in target browsers."
            )
        
        # Check for unknown features
        # Get unique unknown features across all browsers
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
                f"ℹ️  {num_features} {feature_text} not found in database across {num_browsers} browsers. "
                "These may be universally supported or custom features."
            )
        
        # Browser-specific recommendations
        for browser, results in compatibility_results.items():
            unsupported = len(results['unsupported'])
            if unsupported > 5:
                recommendations.append(
                    f"⚠️  {browser.capitalize()}: {unsupported} unsupported features detected. "
                    "Consider testing and providing alternatives."
                )
        
        # If everything is good
        if not critical_issues and partial_count == 0:
            recommendations.append(
                "✅ Excellent! All features are well-supported across target browsers."
            )
        
        return recommendations
    
    def _get_default_browsers(self) -> Dict[str, str]:
        """Get default target browsers.
        
        Returns:
            Dict of default browsers and their latest versions
        """
        return {
            'chrome': LATEST_VERSIONS['chrome'],
            'firefox': LATEST_VERSIONS['firefox'],
            'safari': LATEST_VERSIONS['safari'],
            'edge': LATEST_VERSIONS['edge']
        }
    
    def export_report(self, report: Dict, output_file: str, format: str = 'json'):
        """Export report to file.
        
        Args:
            report: Analysis report
            output_file: Output file path
            format: Export format ('json', 'html', or 'txt')
        """
        output_path = Path(output_file)
        
        try:
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                logger.info(f"Report exported to {output_path}")

            elif format == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(self._format_text_report(report))
                logger.info(f"Report exported to {output_path}")

            elif format == 'html':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(self._format_html_report(report))
                logger.info(f"Report exported to {output_path}")

            else:
                logger.warning(f"Unknown export format: {format}")

        except Exception as e:
            logger.error(f"Error exporting report: {e}")
    
    def _format_text_report(self, report: Dict) -> str:
        """Format report as plain text."""
        lines = []
        lines.append("=" * 70)
        lines.append("  CROSS GUARD COMPATIBILITY REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary
        summary = report['summary']
        lines.append("SUMMARY:")
        lines.append(f"  Total Features: {summary['total_features']}")
        lines.append(f"  HTML: {summary['html_features']}, CSS: {summary['css_features']}, JS: {summary['js_features']}")
        lines.append(f"  Overall Grade: {summary['overall_grade']}")
        lines.append(f"  Risk Level: {summary['risk_level']}")
        lines.append("")
        
        # Browser details
        lines.append("BROWSER COMPATIBILITY:")
        for browser, details in report['browsers'].items():
            lines.append(f"  {browser.capitalize()} {details['version']}:")
            lines.append(f"    Compatibility: {details['compatibility_percentage']}%")
            lines.append(f"    Supported: {details['supported']}, Partial: {details['partial']}, Unsupported: {details['unsupported']}")
        lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS:")
        for rec in report['recommendations']:
            lines.append(f"  {rec}")
        lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_html_report(self, report: Dict) -> str:
        """Format report as HTML."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Cross Guard Compatibility Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .browser {{ margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; }}
        .grade {{ font-size: 24px; font-weight: bold; }}
        .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Cross Guard Compatibility Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Features: {report['summary']['total_features']}</p>
        <p>Grade: <span class="grade">{report['summary']['overall_grade']}</span></p>
        <p>Risk Level: {report['summary']['risk_level']}</p>
    </div>
    <h2>Browser Compatibility</h2>
"""
        
        for browser, details in report['browsers'].items():
            html += f"""
    <div class="browser">
        <h3>{browser.capitalize()} {details['version']}</h3>
        <p>Compatibility: {details['compatibility_percentage']}%</p>
        <p>Supported: {details['supported']}, Partial: {details['partial']}, Unsupported: {details['unsupported']}</p>
    </div>
"""
        
        html += """
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
"""
        
        for rec in report['recommendations']:
            html += f"            <li>{rec}</li>\n"
        
        html += """
        </ul>
    </div>
</body>
</html>
"""
        
        return html


def analyze_project(
    html_files: Optional[List[str]] = None,
    css_files: Optional[List[str]] = None,
    js_files: Optional[List[str]] = None,
    target_browsers: Optional[Dict[str, str]] = None
) -> Dict:
    """Convenience function to analyze a project.
    
    Args:
        html_files: List of HTML file paths
        css_files: List of CSS file paths
        js_files: List of JavaScript file paths
        target_browsers: Dict of browser names and versions
    
    Returns:
        Analysis report
    """
    analyzer = CrossGuardAnalyzer()
    return analyzer.analyze_project(html_files, css_files, js_files, target_browsers)
