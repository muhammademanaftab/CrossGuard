"""Feature Extractor for ML-based Compatibility Risk Prediction.

This module extracts 25+ features from Can I Use database entries for use
in machine learning models. Features are designed to capture patterns that
predict browser compatibility risk.

Feature Groups:
- Group A: Usage Metrics (usage_perc_y, usage_perc_a, usage_total)
- Group B: Specification Status (status_score)
- Group C: Browser Support (computed from stats)
- Group D: Complexity Indicators (keywords, bugs, notes, parent)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from ..utils.config import (
    CANIUSE_FEATURES_PATH,
    LATEST_VERSIONS,
    get_logger,
)

logger = get_logger('ml.feature_extractor')

# Specification status scores (higher = more stable)
STATUS_SCORES = {
    'rec': 4,      # W3C Recommendation - fully stable
    'pr': 3,       # Proposed Recommendation
    'cr': 3,       # Candidate Recommendation
    'wd': 2,       # Working Draft
    'ls': 2,       # Living Standard
    'other': 1,    # Other/unknown status
    'unoff': 0,    # Unofficial/experimental
}

# Major browsers to track (desktop focus for primary analysis)
PRIMARY_BROWSERS = ['chrome', 'firefox', 'safari', 'edge', 'ie', 'opera']

# Category encoding for feature extraction
CATEGORY_ENCODING = {
    'CSS': 1,
    'CSS3': 1,
    'HTML5': 2,
    'JS': 3,
    'JS API': 3,
    'Canvas': 4,
    'SVG': 5,
    'DOM': 6,
    'Security': 7,
    'Other': 0,
}

# Feature names in order for ML arrays
FEATURE_NAMES = [
    # Group A: Usage Metrics
    'usage_perc_y',
    'usage_perc_a',
    'usage_total',

    # Group B: Specification Status
    'status_score',

    # Group C: Browser Support (6 browsers)
    'chrome_support',
    'firefox_support',
    'safari_support',
    'edge_support',
    'ie_support',
    'opera_support',

    # Group C: Aggregated Browser Metrics
    'avg_browser_support',
    'min_browser_support',
    'max_browser_support',
    'browsers_full_support',
    'browsers_partial_support',
    'browsers_no_support',
    'support_variance',

    # Group D: Complexity Indicators
    'keyword_count',
    'bug_count',
    'link_count',
    'notes_count',
    'has_parent',
    'has_prefix',
    'description_length',
    'title_length',
    'category_encoded',
]


class FeatureExtractor:
    """Extracts ML features from Can I Use feature data.

    This class transforms raw caniuse feature JSON into numerical features
    suitable for machine learning models.
    """

    def __init__(self):
        """Initialize the feature extractor."""
        self.feature_names = FEATURE_NAMES
        self.n_features = len(FEATURE_NAMES)

    def extract_features(self, feature_data: Dict[str, Any]) -> np.ndarray:
        """Extract ML features from a single caniuse feature entry.

        Args:
            feature_data: Dictionary containing caniuse feature data
                         (loaded from features-json/*.json)

        Returns:
            numpy array of shape (n_features,) with extracted features
        """
        features = np.zeros(self.n_features, dtype=np.float32)

        # Group A: Usage Metrics
        features[0] = self._safe_float(feature_data.get('usage_perc_y', 0))
        features[1] = self._safe_float(feature_data.get('usage_perc_a', 0))
        features[2] = features[0] + features[1]  # usage_total

        # Group B: Specification Status
        status = feature_data.get('status', 'other')
        features[3] = STATUS_SCORES.get(status, STATUS_SCORES['other'])

        # Group C: Browser Support
        stats = feature_data.get('stats', {})
        browser_supports = self._extract_browser_support(stats)

        features[4] = browser_supports.get('chrome', 0)
        features[5] = browser_supports.get('firefox', 0)
        features[6] = browser_supports.get('safari', 0)
        features[7] = browser_supports.get('edge', 0)
        features[8] = browser_supports.get('ie', 0)
        features[9] = browser_supports.get('opera', 0)

        # Aggregated browser metrics
        support_values = list(browser_supports.values())
        if support_values:
            features[10] = np.mean(support_values)  # avg_browser_support
            features[11] = np.min(support_values)   # min_browser_support
            features[12] = np.max(support_values)   # max_browser_support
            features[13] = sum(1 for v in support_values if v >= 0.9)  # browsers_full_support
            features[14] = sum(1 for v in support_values if 0.5 <= v < 0.9)  # browsers_partial_support
            features[15] = sum(1 for v in support_values if v < 0.5)  # browsers_no_support
            features[16] = np.var(support_values) if len(support_values) > 1 else 0  # support_variance

        # Group D: Complexity Indicators
        keywords = feature_data.get('keywords', '')
        features[17] = len(keywords.split(',')) if keywords else 0  # keyword_count

        bugs = feature_data.get('bugs', [])
        features[18] = len(bugs) if isinstance(bugs, list) else 0  # bug_count

        links = feature_data.get('links', [])
        features[19] = len(links) if isinstance(links, list) else 0  # link_count

        notes_by_num = feature_data.get('notes_by_num', {})
        features[20] = len(notes_by_num) if isinstance(notes_by_num, dict) else 0  # notes_count

        features[21] = 1.0 if feature_data.get('parent', '') else 0.0  # has_parent
        features[22] = 1.0 if feature_data.get('ucprefix', False) else 0.0  # has_prefix

        description = feature_data.get('description', '')
        features[23] = len(description) / 100.0  # description_length (normalized)

        title = feature_data.get('title', '')
        features[24] = len(title) / 10.0  # title_length (normalized)

        # Category encoding
        categories = feature_data.get('categories', [])
        if categories:
            primary_category = categories[0] if isinstance(categories, list) else categories
            features[25] = CATEGORY_ENCODING.get(primary_category, 0)

        return features

    def _extract_browser_support(self, stats: Dict[str, Dict[str, str]]) -> Dict[str, float]:
        """Extract browser support scores from stats dictionary.

        Support is calculated based on latest version status:
        - 'y' (full support) = 1.0
        - 'a' (partial) = 0.75
        - 'x' (prefix) = 0.75
        - 'p' (polyfill) = 0.5
        - 'd' (disabled) = 0.25
        - 'n' (no support) = 0.0
        - 'u' (unknown) = 0.0

        Args:
            stats: Browser stats from caniuse feature data

        Returns:
            Dict mapping browser names to support scores (0.0 - 1.0)
        """
        browser_supports = {}

        for browser in PRIMARY_BROWSERS:
            if browser not in stats:
                browser_supports[browser] = 0.0
                continue

            browser_stats = stats[browser]
            latest_version = LATEST_VERSIONS.get(browser, '')

            # Find support for latest version
            support_str = browser_stats.get(latest_version, '')

            # If exact version not found, find closest
            if not support_str:
                support_str = self._find_closest_version_support(browser_stats, latest_version)

            browser_supports[browser] = self._parse_support_score(support_str)

        return browser_supports

    def _find_closest_version_support(
        self, browser_stats: Dict[str, str], target_version: str
    ) -> str:
        """Find support status for closest available version.

        Args:
            browser_stats: Version -> status mapping
            target_version: Target version string

        Returns:
            Support status string for closest version
        """
        try:
            target_num = float(target_version)
        except ValueError:
            return ''

        closest_version = None
        min_diff = float('inf')

        for version in browser_stats.keys():
            try:
                # Handle version ranges like "15.2-15.3"
                version_num = float(version.split('-')[0])
                diff = abs(version_num - target_num)

                if diff < min_diff:
                    min_diff = diff
                    closest_version = version
            except ValueError:
                continue

        if closest_version:
            return browser_stats[closest_version]

        return ''

    def _parse_support_score(self, status: str) -> float:
        """Convert support status string to numerical score.

        Can I Use uses compound statuses like 'a x #2' meaning:
        - a: partial support
        - x: requires prefix
        - #2: see note 2

        Args:
            status: Raw status string from database

        Returns:
            Support score between 0.0 and 1.0
        """
        if not status:
            return 0.0

        # Take first character as primary status
        primary = status.strip()[0].lower()

        score_map = {
            'y': 1.0,    # Full support
            'a': 0.75,   # Partial support
            'x': 0.75,   # Requires prefix (still usable)
            'p': 0.5,    # Polyfill available
            'd': 0.25,   # Disabled by default
            'n': 0.0,    # No support
            'u': 0.0,    # Unknown
        }

        return score_map.get(primary, 0.0)

    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float.

        Args:
            value: Value to convert

        Returns:
            Float value, or 0.0 if conversion fails
        """
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def get_feature_names(self) -> List[str]:
        """Get ordered list of feature names.

        Returns:
            List of feature names in same order as feature vectors
        """
        return self.feature_names.copy()

    def extract_from_file(self, feature_file: Path) -> Optional[Tuple[str, np.ndarray]]:
        """Extract features from a caniuse feature JSON file.

        Args:
            feature_file: Path to feature JSON file

        Returns:
            Tuple of (feature_id, feature_vector) or None if failed
        """
        try:
            with open(feature_file, 'r', encoding='utf-8') as f:
                feature_data = json.load(f)

            feature_id = feature_file.stem
            features = self.extract_features(feature_data)

            return (feature_id, features)

        except Exception as e:
            logger.warning(f"Failed to extract features from {feature_file}: {e}")
            return None


def extract_all_features(
    features_path: Optional[Path] = None,
    return_metadata: bool = False
) -> Tuple[np.ndarray, List[str], Optional[List[Dict]]]:
    """Extract features from all caniuse feature files.

    This is the main entry point for building the training dataset.

    Args:
        features_path: Path to features-json directory (uses default if None)
        return_metadata: If True, also return raw feature metadata

    Returns:
        Tuple of:
        - Feature matrix of shape (n_samples, n_features)
        - List of feature IDs in same order as rows
        - Optional list of raw metadata dicts (if return_metadata=True)
    """
    if features_path is None:
        features_path = Path(CANIUSE_FEATURES_PATH)

    extractor = FeatureExtractor()
    feature_files = list(features_path.glob('*.json'))

    logger.info(f"Extracting features from {len(feature_files)} files...")

    features_list = []
    feature_ids = []
    metadata_list = [] if return_metadata else None

    for feature_file in feature_files:
        try:
            with open(feature_file, 'r', encoding='utf-8') as f:
                feature_data = json.load(f)

            feature_id = feature_file.stem
            features = extractor.extract_features(feature_data)

            features_list.append(features)
            feature_ids.append(feature_id)

            if return_metadata:
                metadata_list.append(feature_data)

        except Exception as e:
            logger.warning(f"Skipping {feature_file.name}: {e}")
            continue

    logger.info(f"Successfully extracted features from {len(feature_ids)} features")

    X = np.array(features_list, dtype=np.float32)

    return X, feature_ids, metadata_list


def extract_features_for_unknown(
    spec_status: str = 'wd',
    category: str = 'CSS',
    browsers_implementing: int = 1,
    has_polyfill: bool = False,
    complexity: str = 'medium',
    description_length: int = 100,
) -> np.ndarray:
    """Extract features for an unknown/new feature.

    This function creates a feature vector for features NOT in the
    Can I Use database based on available metadata.

    Args:
        spec_status: Specification status ('rec', 'cr', 'wd', 'unoff')
        category: Feature category ('CSS', 'JS', 'HTML5')
        browsers_implementing: Number of browsers implementing
        has_polyfill: Whether a polyfill is available
        complexity: Complexity level ('low', 'medium', 'high')
        description_length: Approximate description length

    Returns:
        Feature vector compatible with trained models
    """
    extractor = FeatureExtractor()
    features = np.zeros(extractor.n_features, dtype=np.float32)

    # Estimate usage based on browsers implementing
    estimated_usage = browsers_implementing * 15.0  # Rough estimate
    features[0] = min(estimated_usage, 50.0)  # usage_perc_y (conservative)
    features[1] = 5.0  # usage_perc_a (small partial)
    features[2] = features[0] + features[1]

    # Specification status
    features[3] = STATUS_SCORES.get(spec_status, STATUS_SCORES['other'])

    # Browser support (estimate based on browsers_implementing)
    # Assume Chrome/Firefox/Safari are first to implement
    browser_order = ['chrome', 'firefox', 'safari', 'edge', 'opera', 'ie']
    for i, browser in enumerate(browser_order[:browsers_implementing]):
        features[4 + i] = 1.0 if has_polyfill else 0.75

    # Aggregated metrics
    support_values = features[4:10]
    features[10] = np.mean(support_values)  # avg
    features[11] = np.min(support_values)   # min
    features[12] = np.max(support_values)   # max
    features[13] = sum(1 for v in support_values if v >= 0.9)  # full
    features[14] = sum(1 for v in support_values if 0.5 <= v < 0.9)  # partial
    features[15] = sum(1 for v in support_values if v < 0.5)  # none
    features[16] = np.var(support_values)  # variance

    # Complexity indicators
    complexity_map = {'low': 3, 'medium': 6, 'high': 12}
    features[17] = complexity_map.get(complexity, 6)  # keyword_count estimate
    features[18] = 1 if complexity == 'high' else 0  # bug_count estimate
    features[19] = 2  # link_count (typical)
    features[20] = 1 if complexity != 'low' else 0  # notes_count
    features[21] = 0.0  # has_parent
    features[22] = 0.0  # has_prefix
    features[23] = description_length / 100.0  # description_length
    features[24] = 3.0  # title_length (typical)
    features[25] = CATEGORY_ENCODING.get(category, 0)

    return features
