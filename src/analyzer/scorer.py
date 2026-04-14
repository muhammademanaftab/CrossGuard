"""Scoring algorithms for browser compatibility (simple, weighted, market-share, etc.)."""

from typing import Dict, Set


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

    def calculate_market_share_score(self, support_status: Dict[str, str],
                                    market_shares: Dict[str, float]) -> float:
        """Score weighted by real-world browser market share."""
        if not support_status or not market_shares:
            return 0.0

        weighted_sum = 0
        total_share = 0

        for browser, status in support_status.items():
            if browser in market_shares:
                score = self.STATUS_SCORES.get(status, 0)
                share = market_shares[browser]
                weighted_sum += score * share
                total_share += share

        return weighted_sum / total_share if total_share > 0 else 0

    def calculate_progressive_score(self, support_status: Dict[str, str],
                                   modern_browsers: Set[str]) -> Dict[str, float]:
        """Split score into modern vs legacy browser buckets."""
        modern_statuses = {}
        legacy_statuses = {}

        for browser, status in support_status.items():
            if browser in modern_browsers:
                modern_statuses[browser] = status
            else:
                legacy_statuses[browser] = status

        modern_score = self.calculate_simple_score(modern_statuses) if modern_statuses else 100.0
        legacy_score = self.calculate_simple_score(legacy_statuses) if legacy_statuses else 0.0

        return {
            'modern': modern_score,
            'legacy': legacy_score,
            'overall': (modern_score + legacy_score) / 2
        }

    def calculate_feature_importance_score(self, features: Dict[str, Dict[str, str]],
                                          importance_weights: Dict[str, float]) -> float:
        """Score weighted by how important each feature is to the project."""
        if not features:
            return 0.0

        weighted_sum = 0
        weight_sum = 0

        for feature_id, support_status in features.items():
            feature_score = self.calculate_simple_score(support_status)
            importance = importance_weights.get(feature_id, 1.0)

            weighted_sum += feature_score * importance
            weight_sum += importance

        return weighted_sum / weight_sum if weight_sum > 0 else 0

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

    def compare_features(self, feature_scores: Dict[str, float]) -> Dict[str, any]:
        """Find the best and worst features by score."""
        if not feature_scores:
            return {
                'best_features': [],
                'worst_features': [],
                'average_score': 0,
                'score_variance': 0
            }

        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)

        scores = list(feature_scores.values())
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)

        best_features = sorted_features[:5]
        worst_features = sorted_features[-5:]
        worst_features.reverse()

        return {
            'best_features': [{'feature': f, 'score': s} for f, s in best_features],
            'worst_features': [{'feature': f, 'score': s} for f, s in worst_features],
            'average_score': round(avg_score, 2),
            'score_variance': round(variance, 2),
            'total_features': len(feature_scores)
        }

    def calculate_trend_score(self, support_history: Dict[str, Dict[str, str]]) -> Dict[str, float]:
        """Is compatibility improving, declining, or stable across versions?"""
        if not support_history:
            return {'trend': 'unknown', 'improvement': 0}

        versions = sorted(support_history.keys())

        if len(versions) < 2:
            return {'trend': 'stable', 'improvement': 0}

        scores = []
        for version in versions:
            score = self.calculate_simple_score(support_history[version])
            scores.append(score)

        first_score = scores[0]
        last_score = scores[-1]
        improvement = last_score - first_score

        if improvement > 10:
            trend = 'improving'
        elif improvement < -10:
            trend = 'declining'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'improvement': round(improvement, 2),
            'first_score': round(first_score, 2),
            'last_score': round(last_score, 2),
            'versions_analyzed': len(versions)
        }

    def _score_to_grade(self, score: float) -> str:
        return _score_to_grade(score)

    def set_browser_weight(self, browser: str, weight: float):
        if 0 <= weight <= 1:
            self.browser_weights[browser] = weight
        else:
            raise ValueError("Weight must be between 0 and 1")

    def get_browser_weights(self) -> Dict[str, float]:
        return self.browser_weights.copy()
