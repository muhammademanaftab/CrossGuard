"""Scoring algorithms for browser compatibility (simple, weighted, market-share, etc.)."""

from typing import Dict


def _score_to_grade(score: float) -> str:
    """Map a 0-100 score to a 13-level letter grade (A+ through F)."""
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


class CompatibilityScorer:
    """Multiple ways to score browser compatibility results."""

    DEFAULT_WEIGHTS = {
        'chrome': 1.0,
        'firefox': 1.0,
        'safari': 1.0,
        'edge': 1.0,
        'ie': 0.5,  # legacy browser, matters less
        'opera': 0.7
    }

    # How much each caniuse status is "worth" out of 100
    STATUS_SCORES = {
        'y': 100, 'a': 100,  # 'a' = almost supported, treated as full
        'x': 70,   # needs vendor prefix
        'p': 50,   # partial
        'd': 30,   # disabled by default
        'n': 0, 'u': 0
    }

    def __init__(self, browser_weights: Dict[str, float] = None):
        self.browser_weights = browser_weights or self.DEFAULT_WEIGHTS.copy()

    def calculate_simple_score(self, support_status: Dict[str, str]) -> float:
        """Plain average across all browsers."""
        if not support_status:
            return 0.0

        total_score = 0
        for status in support_status.values():
            total_score += self.STATUS_SCORES.get(status, 0)

        return total_score / len(support_status)

    def calculate_weighted_score(self, support_status: Dict[str, str]) -> Dict:
        """Score weighted by browser importance."""
        if not support_status:
            return {'total_score': 0.0, 'weighted_score': 0.0, 'breakdown': {}, 'weights': {}}

        breakdown = {}
        for browser, status in support_status.items():
            breakdown[browser] = self.STATUS_SCORES.get(status, 0)

        simple_score = sum(breakdown.values()) / len(breakdown)

        weighted_sum = 0
        weight_sum = 0

        for browser, score in breakdown.items():
            weight = self.browser_weights.get(browser, 1.0)
            weighted_sum += score * weight
            weight_sum += weight

        weighted_score = weighted_sum / weight_sum if weight_sum > 0 else 0

        return {
            'total_score': simple_score,
            'weighted_score': weighted_score,
            'breakdown': breakdown,
            'weights': {b: self.browser_weights.get(b, 1.0) for b in support_status.keys()},
        }

    def calculate_compatibility_index(self, support_status: Dict[str, str]) -> Dict[str, any]:
        """All-in-one index: score, grade, risk level, and counts."""
        if not support_status:
            return {
                'score': 0,
                'grade': 'F',
                'supported_count': 0,
                'partial_count': 0,
                'unsupported_count': 0,
                'total_browsers': 0,
                'support_percentage': 0,
                'risk_level': 'high'
            }

        supported = sum(1 for s in support_status.values() if s == 'y')
        partial = sum(1 for s in support_status.values() if s in ['a', 'x', 'p'])
        unsupported = sum(1 for s in support_status.values() if s in ['n', 'u'])
        total = len(support_status)

        score = self.calculate_simple_score(support_status)
        support_percentage = (supported / total * 100) if total > 0 else 0

        if unsupported == 0 and partial == 0:
            risk_level = 'none'
        elif unsupported == 0:
            risk_level = 'low'
        elif unsupported < total / 2:
            risk_level = 'medium'
        else:
            risk_level = 'high'

        grade = self._score_to_grade(score)

        return {
            'score': round(score, 2),
            'grade': grade,
            'supported_count': supported,
            'partial_count': partial,
            'unsupported_count': unsupported,
            'total_browsers': total,
            'support_percentage': round(support_percentage, 2),
            'risk_level': risk_level
        }

    def _score_to_grade(self, score: float) -> str:
        return _score_to_grade(score)
