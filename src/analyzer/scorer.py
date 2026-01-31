"""Scoring Algorithms for Compatibility Analysis.

This module provides various scoring algorithms and metrics for
evaluating browser compatibility.
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class WeightedScore:
    """Weighted compatibility score with breakdown."""
    total_score: float  # 0-100
    weighted_score: float  # 0-100 with browser weights
    breakdown: Dict[str, float]  # Per-browser scores
    weights: Dict[str, float]  # Browser weights used


class CompatibilityScorer:
    """Advanced scoring algorithms for compatibility analysis."""
    
    # Default browser weights (can be customized)
    DEFAULT_WEIGHTS = {
        'chrome': 1.0,
        'firefox': 1.0,
        'safari': 1.0,
        'edge': 1.0,
        'ie': 0.5,  # Lower weight for older browsers
        'opera': 0.7
    }
    
    # Support status score values
    STATUS_SCORES = {
        'y': 100,  # Fully supported
        'a': 100,  # Almost supported (treated as full per Can I Use website)
        'x': 70,   # Requires prefix
        'p': 50,   # Partial support
        'd': 30,   # Disabled by default
        'n': 0,    # Not supported
        'u': 0     # Unknown
    }
    
    def __init__(self, browser_weights: Dict[str, float] = None):
        """Initialize scorer with optional custom browser weights.
        
        Args:
            browser_weights: Optional dict of browser weights (0-1)
        """
        self.browser_weights = browser_weights or self.DEFAULT_WEIGHTS.copy()
    
    def calculate_simple_score(self, support_status: Dict[str, str]) -> float:
        """Calculate simple average compatibility score.
        
        Args:
            support_status: Dict mapping browsers to support status
            
        Returns:
            Score from 0-100
        """
        if not support_status:
            return 0.0
        
        total_score = 0
        for status in support_status.values():
            total_score += self.STATUS_SCORES.get(status, 0)
        
        return total_score / len(support_status)
    
    def calculate_weighted_score(self, support_status: Dict[str, str]) -> WeightedScore:
        """Calculate weighted compatibility score based on browser importance.
        
        Args:
            support_status: Dict mapping browsers to support status
            
        Returns:
            WeightedScore object with detailed breakdown
        """
        if not support_status:
            return WeightedScore(0.0, 0.0, {}, {})
        
        # Calculate per-browser scores
        breakdown = {}
        for browser, status in support_status.items():
            breakdown[browser] = self.STATUS_SCORES.get(status, 0)
        
        # Calculate simple average
        simple_score = sum(breakdown.values()) / len(breakdown)
        
        # Calculate weighted score
        weighted_sum = 0
        weight_sum = 0
        
        for browser, score in breakdown.items():
            weight = self.browser_weights.get(browser, 1.0)
            weighted_sum += score * weight
            weight_sum += weight
        
        weighted_score = weighted_sum / weight_sum if weight_sum > 0 else 0
        
        return WeightedScore(
            total_score=simple_score,
            weighted_score=weighted_score,
            breakdown=breakdown,
            weights={b: self.browser_weights.get(b, 1.0) for b in support_status.keys()}
        )
    
    def calculate_market_share_score(self, support_status: Dict[str, str],
                                    market_shares: Dict[str, float]) -> float:
        """Calculate score weighted by browser market share.
        
        Args:
            support_status: Dict mapping browsers to support status
            market_shares: Dict mapping browsers to market share (0-100)
            
        Returns:
            Market-share weighted score (0-100)
        """
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
        """Calculate separate scores for modern vs legacy browsers.
        
        Args:
            support_status: Dict mapping browsers to support status
            modern_browsers: Set of browsers considered "modern"
            
        Returns:
            Dict with 'modern' and 'legacy' scores
        """
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
        """Calculate score considering feature importance.
        
        Args:
            features: Dict mapping feature IDs to support status dicts
            importance_weights: Dict mapping feature IDs to importance (0-1)
            
        Returns:
            Importance-weighted score (0-100)
        """
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
        """Calculate comprehensive compatibility index with multiple metrics.
        
        Args:
            support_status: Dict mapping browsers to support status
            
        Returns:
            Dict with various compatibility metrics
        """
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
        
        # Count support levels
        supported = sum(1 for s in support_status.values() if s == 'y')
        partial = sum(1 for s in support_status.values() if s in ['a', 'x', 'p'])
        unsupported = sum(1 for s in support_status.values() if s in ['n', 'u'])
        total = len(support_status)
        
        # Calculate score
        score = self.calculate_simple_score(support_status)
        
        # Calculate support percentage (only fully supported)
        support_percentage = (supported / total * 100) if total > 0 else 0
        
        # Determine risk level
        if unsupported == 0 and partial == 0:
            risk_level = 'none'
        elif unsupported == 0:
            risk_level = 'low'
        elif unsupported < total / 2:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # Assign grade
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
        """Compare multiple features and identify problematic ones.
        
        Args:
            feature_scores: Dict mapping feature IDs to scores
            
        Returns:
            Dict with comparison analysis
        """
        if not feature_scores:
            return {
                'best_features': [],
                'worst_features': [],
                'average_score': 0,
                'score_variance': 0
            }
        
        # Sort features by score
        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate statistics
        scores = list(feature_scores.values())
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        
        # Identify best and worst
        best_features = sorted_features[:5]  # Top 5
        worst_features = sorted_features[-5:]  # Bottom 5
        worst_features.reverse()  # Worst first
        
        return {
            'best_features': [{'feature': f, 'score': s} for f, s in best_features],
            'worst_features': [{'feature': f, 'score': s} for f, s in worst_features],
            'average_score': round(avg_score, 2),
            'score_variance': round(variance, 2),
            'total_features': len(feature_scores)
        }
    
    def calculate_trend_score(self, support_history: Dict[str, Dict[str, str]]) -> Dict[str, float]:
        """Calculate compatibility trend over browser versions.
        
        Args:
            support_history: Dict mapping version numbers to support status dicts
            
        Returns:
            Dict with trend analysis
        """
        if not support_history:
            return {'trend': 'unknown', 'improvement': 0}
        
        # Sort versions
        versions = sorted(support_history.keys())
        
        if len(versions) < 2:
            return {'trend': 'stable', 'improvement': 0}
        
        # Calculate scores for each version
        scores = []
        for version in versions:
            score = self.calculate_simple_score(support_history[version])
            scores.append(score)
        
        # Calculate trend
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
        """Convert numeric score to letter grade.
        
        Args:
            score: Score (0-100)
            
        Returns:
            Letter grade
        """
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def set_browser_weight(self, browser: str, weight: float):
        """Set custom weight for a browser.
        
        Args:
            browser: Browser name
            weight: Weight value (0-1, where 1 is most important)
        """
        if 0 <= weight <= 1:
            self.browser_weights[browser] = weight
        else:
            raise ValueError("Weight must be between 0 and 1")
    
    def get_browser_weights(self) -> Dict[str, float]:
        """Get current browser weights.
        
        Returns:
            Dict of browser weights
        """
        return self.browser_weights.copy()
