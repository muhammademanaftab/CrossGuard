"""Scoring helpers for browser compatibility."""

from typing import Dict, List


class CompatibilityScorer:
    """Central place for score math. STATUS_SCORES is the single source of truth
    for per-status point contribution; everything else builds on it."""

    # Can I Use status code → points out of 100 a feature contributes for a given browser.
    # Tweak these to change how strictly partial / prefixed / polyfilled features are scored.
    STATUS_SCORES = {
        'y': 100,            # fully supported
        'a': 50, 'x': 50,    # almost-supported / needs vendor prefix (partial)
        'n': 0,              # not supported
        'p': 0, 'd': 0, 'u': 0,  # polyfill-only / disabled by default / unknown
    }

    def score_statuses(self, statuses: List[str]) -> float:
        """Average per-status points across all checked features for one browser."""
        if not statuses:
            return 100.0
        total = sum(self.STATUS_SCORES.get(s, 0) for s in statuses)
        return total / len(statuses)

    def overall_score(self, browser_percentages: Dict[str, float]) -> float:
        if not browser_percentages:
            return 0.0
        return sum(browser_percentages.values()) / len(browser_percentages)

    def grade(self, score: float) -> str:
        if score >= 90:
            return 'A'
        if score >= 80:
            return 'B'
        if score >= 70:
            return 'C'
        if score >= 60:
            return 'D'
        return 'F'

    def risk_level(self, score: float, unsupported_count: int) -> str:
        if not unsupported_count:
            return 'none'
        if score >= 80:
            return 'low'
        if score >= 60:
            return 'medium'
        return 'high'
