"""Checks detected features against target browsers and classifies issues by severity."""

from typing import Dict, List, Set

from .database import get_database
from .scorer import _score_to_grade

# Severity constants (plain strings instead of enum)
SEVERITY_CRITICAL = "critical"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"
SEVERITY_INFO = "info"


class CompatibilityAnalyzer:
    """Checks features against the caniuse DB and produces scored reports."""

    def __init__(self):
        self.database = get_database()

    def analyze(self, features: Set[str], target_browsers: Dict[str, str]) -> Dict:
        """Run a full compatibility check and return a scored report."""
        issues = []
        browser_scores = {}

        for browser, version in target_browsers.items():
            score = self._analyze_browser(features, browser, version, issues)
            browser_scores[browser] = score

        overall_score = self._calculate_overall_score(browser_scores)

        critical_count = sum(1 for issue in issues if issue['severity'] == SEVERITY_CRITICAL)
        high_count = sum(1 for issue in issues if issue['severity'] == SEVERITY_HIGH)
        medium_count = sum(1 for issue in issues if issue['severity'] == SEVERITY_MEDIUM)
        low_count = sum(1 for issue in issues if issue['severity'] == SEVERITY_LOW)

        return {
            'overall_score': overall_score,
            'browser_scores': browser_scores,
            'issues': issues,
            'features_analyzed': len(features),
            'critical_issues': critical_count,
            'high_issues': high_count,
            'medium_issues': medium_count,
            'low_issues': low_count,
        }

    def _analyze_browser(self, features: Set[str], browser: str,
                        version: str, issues: List[Dict]) -> Dict:
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
        """Average of all per-browser scores."""
        if not browser_scores:
            return 0.0

        total_score = sum(bs['score'] for bs in browser_scores.values())
        return total_score / len(browser_scores)

    def _calculate_severity(self, support_status: Dict[str, str],
                           total_browsers: int) -> str:
        """More unsupported browsers = higher severity."""
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

    def _score_to_grade(self, score: float) -> str:
        return _score_to_grade(score)

    def _get_best_browser(self, browser_scores: Dict[str, Dict]) -> str:
        if not browser_scores:
            return "None"

        best = max(browser_scores.values(), key=lambda x: x['score'])
        return f"{best['browser']} ({best['score']:.1f}%)"

    def _get_worst_browser(self, browser_scores: Dict[str, Dict]) -> str:
        if not browser_scores:
            return "None"

        worst = min(browser_scores.values(), key=lambda x: x['score'])
        return f"{worst['browser']} ({worst['score']:.1f}%)"
