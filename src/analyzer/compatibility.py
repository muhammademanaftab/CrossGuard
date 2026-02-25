"""Checks detected features against target browsers and classifies issues by severity."""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from .database import get_database
from ..utils.config import SUPPORT_STATUS, SEVERITY_LEVELS


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class CompatibilityIssue:
    feature_id: str
    feature_name: str
    severity: Severity
    browsers_affected: List[str]
    support_status: Dict[str, str]
    description: str
    category: str
    workaround: Optional[str] = None


@dataclass
class BrowserScore:
    browser: str
    version: str
    score: float  # 0-100
    supported_count: int
    partial_count: int
    unsupported_count: int
    total_features: int


@dataclass
class CompatibilityReport:
    overall_score: float  # 0-100
    browser_scores: Dict[str, BrowserScore]
    issues: List[CompatibilityIssue]
    features_analyzed: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int


class CompatibilityAnalyzer:
    """Checks features against the caniuse DB and produces scored reports."""

    def __init__(self):
        self.database = get_database()
    
    def analyze(self, features: Set[str], target_browsers: Dict[str, str]) -> CompatibilityReport:
        """Run a full compatibility check and return a scored report."""
        issues = []
        browser_scores = {}

        for browser, version in target_browsers.items():
            score = self._analyze_browser(features, browser, version, issues)
            browser_scores[browser] = score

        overall_score = self._calculate_overall_score(browser_scores)

        critical_count = sum(1 for issue in issues if issue.severity == Severity.CRITICAL)
        high_count = sum(1 for issue in issues if issue.severity == Severity.HIGH)
        medium_count = sum(1 for issue in issues if issue.severity == Severity.MEDIUM)
        low_count = sum(1 for issue in issues if issue.severity == Severity.LOW)
        
        return CompatibilityReport(
            overall_score=overall_score,
            browser_scores=browser_scores,
            issues=issues,
            features_analyzed=len(features),
            critical_issues=critical_count,
            high_issues=high_count,
            medium_issues=medium_count,
            low_issues=low_count
        )
    
    def _analyze_browser(self, features: Set[str], browser: str,
                        version: str, issues: List[CompatibilityIssue]) -> BrowserScore:
        """Score one browser and collect any issues into the shared list."""
        supported = 0
        partial = 0
        unsupported = 0
        
        for feature_id in features:
            status = self.database.check_support(feature_id, browser, version)

            if status in ['y', 'a']:  # 'a' = almost supported, counts as full
                supported += 1
            elif status in ['x', 'p']:
                partial += 1
            elif status in ['n', 'u']:
                unsupported += 1
        
        total = len(features)
        if total == 0:
            score = 100.0
        else:
            score = ((supported * 100) + (partial * 50)) / total
        
        return BrowserScore(
            browser=browser,
            version=version,
            score=score,
            supported_count=supported,
            partial_count=partial,
            unsupported_count=unsupported,
            total_features=total
        )
    
    def _calculate_overall_score(self, browser_scores: Dict[str, BrowserScore]) -> float:
        """Average of all per-browser scores."""
        if not browser_scores:
            return 0.0
        
        total_score = sum(score.score for score in browser_scores.values())
        return total_score / len(browser_scores)
    
    def analyze_feature(self, feature_id: str,
                       target_browsers: Dict[str, str]) -> CompatibilityIssue:
        """Check one feature across all browsers and return its issue."""
        support_status = {}
        browsers_affected = []
        
        for browser, version in target_browsers.items():
            status = self.database.check_support(feature_id, browser, version)
            support_status[browser] = status
            
            if status in ['n', 'u']:
                browsers_affected.append(browser)
        
        severity = self._calculate_severity(support_status, len(target_browsers))

        feature_info = self.database.get_feature_info(feature_id)
        feature_name = feature_info['title'] if feature_info else feature_id
        description = feature_info['description'] if feature_info else "No description"
        category = feature_info['categories'][0] if feature_info and feature_info['categories'] else "Unknown"
        
        return CompatibilityIssue(
            feature_id=feature_id,
            feature_name=feature_name,
            severity=severity,
            browsers_affected=browsers_affected,
            support_status=support_status,
            description=description,
            category=category
        )
    
    def _calculate_severity(self, support_status: Dict[str, str],
                           total_browsers: int) -> Severity:
        """More unsupported browsers = higher severity."""
        unsupported_count = sum(1 for status in support_status.values() 
                               if status in ['n', 'u'])
        partial_count = sum(1 for status in support_status.values() 
                           if status in ['a', 'x', 'p'])
        
        if unsupported_count == total_browsers:
            return Severity.CRITICAL
        if unsupported_count >= total_browsers / 2:
            return Severity.HIGH
        if unsupported_count > 0 or partial_count > 0:
            return Severity.MEDIUM
        return Severity.LOW
    
    def get_detailed_issues(self, features: Set[str],
                           target_browsers: Dict[str, str]) -> List[CompatibilityIssue]:
        """Return only medium+ issues, sorted critical-first."""
        issues = []

        for feature_id in features:
            issue = self.analyze_feature(feature_id, target_browsers)
            if issue.severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM]:
                issues.append(issue)

        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4
        }
        
        issues.sort(key=lambda x: severity_order[x.severity])
        
        return issues
    
    def get_browser_comparison(self, features: Set[str],
                              target_browsers: Dict[str, str]) -> Dict[str, Dict]:
        """Feature support matrix: browser -> feature -> status."""
        comparison = {}
        
        for browser, version in target_browsers.items():
            browser_data = {
                'version': version,
                'features': {}
            }
            
            for feature_id in features:
                status = self.database.check_support(feature_id, browser, version)
                feature_info = self.database.get_feature_info(feature_id)
                
                browser_data['features'][feature_id] = {
                    'status': status,
                    'status_text': SUPPORT_STATUS.get(status, 'Unknown'),
                    'name': feature_info['title'] if feature_info else feature_id
                }
            
            comparison[browser] = browser_data
        
        return comparison
    
    def suggest_workarounds(self, issue: CompatibilityIssue) -> List[str]:
        """Suggest polyfills, prefixes, or notes from the DB for an issue."""
        workarounds = []

        if 'p' in issue.support_status.values():
            workarounds.append("Polyfill available - consider using a polyfill library")
        
        if 'x' in issue.support_status.values():
            workarounds.append("Vendor prefix required - use autoprefixer or add prefixes manually")
        
        feature = self.database.get_feature(issue.feature_id)
        if feature and 'notes' in feature:
            workarounds.append(f"Note: {feature['notes']}")
        
        return workarounds
    
    def get_summary_statistics(self, report: CompatibilityReport) -> Dict:
        """Distill a report into a flat summary dict."""
        return {
            'overall_score': round(report.overall_score, 2),
            'grade': self._score_to_grade(report.overall_score),
            'features_analyzed': report.features_analyzed,
            'total_issues': len(report.issues),
            'critical_issues': report.critical_issues,
            'high_issues': report.high_issues,
            'medium_issues': report.medium_issues,
            'low_issues': report.low_issues,
            'browsers_tested': len(report.browser_scores),
            'best_browser': self._get_best_browser(report.browser_scores),
            'worst_browser': self._get_worst_browser(report.browser_scores)
        }
    
    def _score_to_grade(self, score: float) -> str:
        if score >= 97:
            return 'A+'
        elif score >= 93:
            return 'A'
        elif score >= 90:
            return 'A-'
        elif score >= 87:
            return 'B+'
        elif score >= 83:
            return 'B'
        elif score >= 80:
            return 'B-'
        elif score >= 77:
            return 'C+'
        elif score >= 73:
            return 'C'
        elif score >= 70:
            return 'C-'
        elif score >= 67:
            return 'D+'
        elif score >= 63:
            return 'D'
        elif score >= 60:
            return 'D-'
        else:
            return 'F'
    
    def _get_best_browser(self, browser_scores: Dict[str, BrowserScore]) -> str:
        if not browser_scores:
            return "None"
        
        best = max(browser_scores.values(), key=lambda x: x.score)
        return f"{best.browser} ({best.score:.1f}%)"
    
    def _get_worst_browser(self, browser_scores: Dict[str, BrowserScore]) -> str:
        if not browser_scores:
            return "None"
        
        worst = min(browser_scores.values(), key=lambda x: x.score)
        return f"{worst.browser} ({worst.score:.1f}%)"
