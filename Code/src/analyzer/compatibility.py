"""Checks detected features against target browsers and classifies issues by severity."""

from collections import Counter
from typing import Dict, List, Set

from .database import get_database

# plain strings instead of an enum to keep the serialized report format stable
SEVERITY_CRITICAL = "critical"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"
SEVERITY_INFO = "info"


class CompatibilityAnalyzer:

    def __init__(self):
        self.database = get_database()

    def analyze(self, features: Set[str], target_browsers: Dict[str, str]) -> Dict:
        issues = []
        browser_scores = {}

        for browser, version in target_browsers.items():
            score = self._analyze_browser(features, browser, version, issues)
            browser_scores[browser] = score

        overall_score = self._calculate_overall_score(browser_scores)

        severity_counts = Counter(issue['severity'] for issue in issues)

        return {
            'overall_score': overall_score,
            'browser_scores': browser_scores,
            'issues': issues,
            'features_analyzed': len(features),
            'critical_issues': severity_counts[SEVERITY_CRITICAL],
            'high_issues': severity_counts[SEVERITY_HIGH],
            'medium_issues': severity_counts[SEVERITY_MEDIUM],
            'low_issues': severity_counts[SEVERITY_LOW],
        }

    def _analyze_browser(self, features: Set[str], browser: str,
                        version: str, issues: List[Dict]) -> Dict:
        supported = 0
        partial = 0
        unsupported = 0

        for feature_id in features:
            status = self.database.check_support(feature_id, browser, version)

            if status in ['y', 'a']:  # 'a' = almost; caniuse treats it as full support
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

        return {
            'browser': browser,
            'version': version,
            'score': score,
            'supported_count': supported,
            'partial_count': partial,
            'unsupported_count': unsupported,
            'total_features': total,
        }

    def _calculate_overall_score(self, browser_scores: Dict[str, Dict]) -> float:
        if not browser_scores:
            return 0.0

        total_score = sum(bs['score'] for bs in browser_scores.values())
        return total_score / len(browser_scores)

    def _calculate_severity(self, support_status: Dict[str, str],
                           total_browsers: int) -> str:
        unsupported_count = sum(1 for status in support_status.values()
                               if status in ['n', 'u'])
        partial_count = sum(1 for status in support_status.values()
                           if status in ['a', 'x', 'p'])

        if unsupported_count == total_browsers:
            return SEVERITY_CRITICAL
        if unsupported_count >= total_browsers / 2:
            return SEVERITY_HIGH
        if unsupported_count > 0 or partial_count > 0:
            return SEVERITY_MEDIUM
        return SEVERITY_LOW

    def _extreme_browser(self, browser_scores: Dict[str, Dict], fn) -> str:
        if not browser_scores:
            return "None"
        b = fn(browser_scores.values(), key=lambda x: x['score'])
        return f"{b['browser']} ({b['score']:.1f}%)"
