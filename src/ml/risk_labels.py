"""Risk Label Generator for ML-based Compatibility Risk Prediction.

This module computes binary risk labels (HIGH/LOW) from Can I Use data.
No manual labeling is required - labels are automatically derived from
usage percentages, browser support, and specification status.

Risk Classification:
- HIGH RISK (1): Feature has compatibility concerns
- LOW RISK (0): Feature is widely supported and stable
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import IntEnum
import numpy as np

from ..utils.config import (
    CANIUSE_FEATURES_PATH,
    LATEST_VERSIONS,
    get_logger,
)

logger = get_logger('ml.risk_labels')


class RiskLevel(IntEnum):
    """Binary risk classification levels."""
    LOW = 0
    HIGH = 1


@dataclass
class RiskFactors:
    """Detailed breakdown of risk contributing factors.

    Attributes:
        low_usage: True if global usage < threshold
        poor_chrome_support: True if Chrome doesn't fully support
        poor_firefox_support: True if Firefox doesn't fully support
        poor_safari_support: True if Safari doesn't fully support
        poor_edge_support: True if Edge doesn't fully support
        unstable_spec: True if spec is WD or unofficial
        many_bugs: True if feature has many known bugs
        high_variance: True if browser support is inconsistent
    """
    low_usage: bool = False
    poor_chrome_support: bool = False
    poor_firefox_support: bool = False
    poor_safari_support: bool = False
    poor_edge_support: bool = False
    unstable_spec: bool = False
    many_bugs: bool = False
    high_variance: bool = False

    def to_reasons(self) -> List[str]:
        """Convert factors to human-readable risk reasons.

        Returns:
            List of risk reason strings
        """
        reasons = []
        if self.low_usage:
            reasons.append("Low global browser usage (<90%)")
        if self.poor_chrome_support:
            reasons.append("Chrome doesn't fully support")
        if self.poor_firefox_support:
            reasons.append("Firefox doesn't fully support")
        if self.poor_safari_support:
            reasons.append("Safari doesn't fully support")
        if self.poor_edge_support:
            reasons.append("Edge doesn't fully support")
        if self.unstable_spec:
            reasons.append("Specification is still in draft/unofficial status")
        if self.many_bugs:
            reasons.append("Many known browser bugs")
        if self.high_variance:
            reasons.append("Inconsistent support across browsers")
        return reasons

    def risk_count(self) -> int:
        """Count number of active risk factors.

        Returns:
            Number of True risk factors
        """
        return sum([
            self.low_usage,
            self.poor_chrome_support,
            self.poor_firefox_support,
            self.poor_safari_support,
            self.poor_edge_support,
            self.unstable_spec,
            self.many_bugs,
            self.high_variance,
        ])


# Risk thresholds (configurable for experiments)
THRESHOLDS = {
    'usage_perc_y_min': 90.0,      # Minimum % for low risk
    'usage_perc_combined_min': 95.0,  # Combined y+a minimum
    'browser_support_min': 0.9,    # Minimum browser support score
    'bug_count_max': 3,            # Maximum bugs for low risk
    'support_variance_max': 0.1,   # Maximum variance for low risk
}

# Unstable specification statuses
UNSTABLE_STATUSES = {'wd', 'unoff', 'other'}


class RiskLabeler:
    """Generates binary risk labels from caniuse feature data.

    Labels are computed automatically based on:
    1. Usage percentage (< 90% = high risk)
    2. Major browser support (Chrome/Firefox/Safari/Edge)
    3. Specification status (WD/unofficial = high risk)
    4. Bug count and support variance
    """

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """Initialize the risk labeler.

        Args:
            thresholds: Optional custom threshold overrides
        """
        self.thresholds = {**THRESHOLDS, **(thresholds or {})}

    def compute_label(self, feature_data: Dict[str, Any]) -> Tuple[int, RiskFactors]:
        """Compute binary risk label for a single feature.

        Args:
            feature_data: Dictionary containing caniuse feature data

        Returns:
            Tuple of (label, risk_factors) where:
            - label is 0 (LOW) or 1 (HIGH)
            - risk_factors contains detailed breakdown
        """
        factors = RiskFactors()

        # Factor 1: Low usage
        usage_y = self._safe_float(feature_data.get('usage_perc_y', 0))
        usage_a = self._safe_float(feature_data.get('usage_perc_a', 0))
        usage_total = usage_y + usage_a

        if usage_y < self.thresholds['usage_perc_y_min']:
            factors.low_usage = True

        # Factor 2: Browser support
        stats = feature_data.get('stats', {})
        browser_supports = self._get_browser_supports(stats)

        min_support = self.thresholds['browser_support_min']

        if browser_supports.get('chrome', 0) < min_support:
            factors.poor_chrome_support = True
        if browser_supports.get('firefox', 0) < min_support:
            factors.poor_firefox_support = True
        if browser_supports.get('safari', 0) < min_support:
            factors.poor_safari_support = True
        if browser_supports.get('edge', 0) < min_support:
            factors.poor_edge_support = True

        # Factor 3: Unstable specification
        status = feature_data.get('status', 'other')
        if status in UNSTABLE_STATUSES:
            factors.unstable_spec = True

        # Factor 4: Many bugs
        bugs = feature_data.get('bugs', [])
        bug_count = len(bugs) if isinstance(bugs, list) else 0
        if bug_count > self.thresholds['bug_count_max']:
            factors.many_bugs = True

        # Factor 5: High variance in support
        support_values = list(browser_supports.values())
        if len(support_values) > 1:
            variance = np.var(support_values)
            if variance > self.thresholds['support_variance_max']:
                factors.high_variance = True

        # Determine final label
        # HIGH RISK if ANY of the major factors are true
        major_factors = [
            factors.low_usage,
            factors.poor_chrome_support,
            factors.poor_firefox_support,
            factors.poor_safari_support,
            factors.poor_edge_support,
            factors.unstable_spec,
        ]

        if any(major_factors):
            label = RiskLevel.HIGH
        else:
            label = RiskLevel.LOW

        return int(label), factors

    def _get_browser_supports(self, stats: Dict[str, Dict[str, str]]) -> Dict[str, float]:
        """Get support scores for major browsers.

        Args:
            stats: Browser stats from caniuse data

        Returns:
            Dict mapping browser names to support scores (0.0 - 1.0)
        """
        supports = {}

        for browser in ['chrome', 'firefox', 'safari', 'edge']:
            if browser not in stats:
                supports[browser] = 0.0
                continue

            browser_stats = stats[browser]
            latest_version = LATEST_VERSIONS.get(browser, '')

            # Find support for latest version
            support_str = browser_stats.get(latest_version, '')

            if not support_str:
                support_str = self._find_closest_version(browser_stats, latest_version)

            supports[browser] = self._parse_support(support_str)

        return supports

    def _find_closest_version(self, browser_stats: Dict[str, str], target: str) -> str:
        """Find closest version support status.

        Args:
            browser_stats: Version -> status mapping
            target: Target version string

        Returns:
            Support status string
        """
        try:
            target_num = float(target)
        except ValueError:
            return ''

        closest = None
        min_diff = float('inf')

        for version in browser_stats.keys():
            try:
                version_num = float(version.split('-')[0])
                diff = abs(version_num - target_num)
                if diff < min_diff:
                    min_diff = diff
                    closest = version
            except ValueError:
                continue

        return browser_stats.get(closest, '') if closest else ''

    def _parse_support(self, status: str) -> float:
        """Parse support status to numerical score.

        Args:
            status: Raw status string

        Returns:
            Support score (0.0 - 1.0)
        """
        if not status:
            return 0.0

        primary = status.strip()[0].lower()

        scores = {
            'y': 1.0,
            'a': 0.75,
            'x': 0.75,
            'p': 0.5,
            'd': 0.25,
            'n': 0.0,
            'u': 0.0,
        }

        return scores.get(primary, 0.0)

    def _safe_float(self, value: Any) -> float:
        """Safely convert to float.

        Args:
            value: Value to convert

        Returns:
            Float value or 0.0
        """
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0


def compute_risk_label(feature_data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Convenience function to compute risk label.

    Args:
        feature_data: Caniuse feature data dictionary

    Returns:
        Tuple of (label, reasons) where label is 0 or 1
    """
    labeler = RiskLabeler()
    label, factors = labeler.compute_label(feature_data)
    return label, factors.to_reasons()


def generate_all_labels(
    features_path: Optional[Path] = None,
    return_factors: bool = False,
) -> Tuple[np.ndarray, List[str], Optional[List[RiskFactors]]]:
    """Generate risk labels for all caniuse features.

    This is the main entry point for creating the training label set.

    Args:
        features_path: Path to features-json directory
        return_factors: If True, also return RiskFactors for each

    Returns:
        Tuple of:
        - Label array of shape (n_samples,) with 0/1 values
        - List of feature IDs in same order
        - Optional list of RiskFactors (if return_factors=True)
    """
    if features_path is None:
        features_path = Path(CANIUSE_FEATURES_PATH)

    labeler = RiskLabeler()
    feature_files = list(features_path.glob('*.json'))

    logger.info(f"Generating labels for {len(feature_files)} features...")

    labels = []
    feature_ids = []
    factors_list = [] if return_factors else None

    for feature_file in feature_files:
        try:
            with open(feature_file, 'r', encoding='utf-8') as f:
                feature_data = json.load(f)

            feature_id = feature_file.stem
            label, factors = labeler.compute_label(feature_data)

            labels.append(label)
            feature_ids.append(feature_id)

            if return_factors:
                factors_list.append(factors)

        except Exception as e:
            logger.warning(f"Skipping {feature_file.name}: {e}")
            continue

    y = np.array(labels, dtype=np.int32)

    # Log class distribution
    high_risk = np.sum(y == 1)
    low_risk = np.sum(y == 0)
    logger.info(f"Labels generated: {high_risk} HIGH RISK, {low_risk} LOW RISK")
    logger.info(f"Class balance: {high_risk / len(y) * 100:.1f}% HIGH RISK")

    return y, feature_ids, factors_list


def get_label_statistics(
    features_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Get detailed statistics about label distribution.

    Args:
        features_path: Path to features-json directory

    Returns:
        Dict containing label statistics
    """
    y, feature_ids, factors = generate_all_labels(features_path, return_factors=True)

    # Count factor contributions
    factor_counts = {
        'low_usage': 0,
        'poor_chrome_support': 0,
        'poor_firefox_support': 0,
        'poor_safari_support': 0,
        'poor_edge_support': 0,
        'unstable_spec': 0,
        'many_bugs': 0,
        'high_variance': 0,
    }

    for f in factors:
        if f.low_usage:
            factor_counts['low_usage'] += 1
        if f.poor_chrome_support:
            factor_counts['poor_chrome_support'] += 1
        if f.poor_firefox_support:
            factor_counts['poor_firefox_support'] += 1
        if f.poor_safari_support:
            factor_counts['poor_safari_support'] += 1
        if f.poor_edge_support:
            factor_counts['poor_edge_support'] += 1
        if f.unstable_spec:
            factor_counts['unstable_spec'] += 1
        if f.many_bugs:
            factor_counts['many_bugs'] += 1
        if f.high_variance:
            factor_counts['high_variance'] += 1

    return {
        'total_features': len(y),
        'high_risk_count': int(np.sum(y == 1)),
        'low_risk_count': int(np.sum(y == 0)),
        'high_risk_percentage': float(np.mean(y == 1) * 100),
        'factor_counts': factor_counts,
        'avg_risk_factors_per_high_risk': np.mean([
            f.risk_count() for f, l in zip(factors, y) if l == 1
        ]) if np.sum(y == 1) > 0 else 0,
    }
