"""Converts caniuse JSON data into numerical feature vectors for ML models."""

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

# Higher = more stable spec
STATUS_SCORES = {
    'rec': 4,      # W3C Recommendation
    'pr': 3,       # Proposed Recommendation
    'cr': 3,       # Candidate Recommendation
    'wd': 2,       # Working Draft
    'ls': 2,       # Living Standard
    'other': 1,
    'unoff': 0,    # Unofficial/experimental
}

PRIMARY_BROWSERS = ['chrome', 'firefox', 'safari', 'edge', 'ie', 'opera']

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

FEATURE_NAMES = [
    'usage_perc_y',
    'usage_perc_a',
    'usage_total',
    'status_score',
    'chrome_support',
    'firefox_support',
    'safari_support',
    'edge_support',
    'ie_support',
    'opera_support',
    'avg_browser_support',
    'min_browser_support',
    'max_browser_support',
    'browsers_full_support',
    'browsers_partial_support',
    'browsers_no_support',
    'support_variance',
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
    """Turns raw caniuse JSON into numerical feature vectors for ML."""

    def __init__(self):
        self.feature_names = FEATURE_NAMES
        self.n_features = len(FEATURE_NAMES)

    def extract_features(self, feature_data: Dict[str, Any]) -> np.ndarray:
        """Extract feature vector from a single caniuse entry."""
        features = np.zeros(self.n_features, dtype=np.float32)

        features[0] = self._safe_float(feature_data.get('usage_perc_y', 0))
        features[1] = self._safe_float(feature_data.get('usage_perc_a', 0))
        features[2] = features[0] + features[1]

        status = feature_data.get('status', 'other')
        features[3] = STATUS_SCORES.get(status, STATUS_SCORES['other'])

        stats = feature_data.get('stats', {})
        browser_supports = self._extract_browser_support(stats)

        features[4] = browser_supports.get('chrome', 0)
        features[5] = browser_supports.get('firefox', 0)
        features[6] = browser_supports.get('safari', 0)
        features[7] = browser_supports.get('edge', 0)
        features[8] = browser_supports.get('ie', 0)
        features[9] = browser_supports.get('opera', 0)

        support_values = list(browser_supports.values())
        if support_values:
            features[10] = np.mean(support_values)
            features[11] = np.min(support_values)
            features[12] = np.max(support_values)
            features[13] = sum(1 for v in support_values if v >= 0.9)
            features[14] = sum(1 for v in support_values if 0.5 <= v < 0.9)
            features[15] = sum(1 for v in support_values if v < 0.5)
            features[16] = np.var(support_values) if len(support_values) > 1 else 0

        keywords = feature_data.get('keywords', '')
        features[17] = len(keywords.split(',')) if keywords else 0

        bugs = feature_data.get('bugs', [])
        features[18] = len(bugs) if isinstance(bugs, list) else 0

        links = feature_data.get('links', [])
        features[19] = len(links) if isinstance(links, list) else 0

        notes_by_num = feature_data.get('notes_by_num', {})
        features[20] = len(notes_by_num) if isinstance(notes_by_num, dict) else 0

        features[21] = 1.0 if feature_data.get('parent', '') else 0.0
        features[22] = 1.0 if feature_data.get('ucprefix', False) else 0.0

        description = feature_data.get('description', '')
        features[23] = len(description) / 100.0

        title = feature_data.get('title', '')
        features[24] = len(title) / 10.0

        categories = feature_data.get('categories', [])
        if categories:
            primary_category = categories[0] if isinstance(categories, list) else categories
            features[25] = CATEGORY_ENCODING.get(primary_category, 0)

        return features

    def _extract_browser_support(self, stats: Dict[str, Dict[str, str]]) -> Dict[str, float]:
        """Get support scores (0-1) for each browser's latest version."""
        browser_supports = {}

        for browser in PRIMARY_BROWSERS:
            if browser not in stats:
                browser_supports[browser] = 0.0
                continue

            browser_stats = stats[browser]
            latest_version = LATEST_VERSIONS.get(browser, '')
            support_str = browser_stats.get(latest_version, '')

            if not support_str:
                support_str = self._find_closest_version_support(browser_stats, latest_version)

            browser_supports[browser] = self._parse_support_score(support_str)

        return browser_supports

    def _find_closest_version_support(
        self, browser_stats: Dict[str, str], target_version: str
    ) -> str:
        """Fall back to nearest version when exact match isn't in the data."""
        try:
            target_num = float(target_version)
        except ValueError:
            return ''

        closest_version = None
        min_diff = float('inf')

        for version in browser_stats.keys():
            try:
                version_num = float(version.split('-')[0])  # handle ranges like "15.2-15.3"
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
        """Turn caniuse status string into a 0-1 score. Only the first char matters."""
        if not status:
            return 0.0

        primary = status.strip()[0].lower()

        score_map = {
            'y': 1.0,
            'a': 0.75,
            'x': 0.75,   # prefix required but usable
            'p': 0.5,    # polyfill available
            'd': 0.25,   # disabled by default
            'n': 0.0,
            'u': 0.0,
        }

        return score_map.get(primary, 0.0)

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def get_feature_names(self) -> List[str]:
        return self.feature_names.copy()

    def extract_from_file(self, feature_file: Path) -> Optional[Tuple[str, np.ndarray]]:
        """Load a caniuse JSON file and return (feature_id, vector) or None."""
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
    """Build the full training dataset from all caniuse feature files."""
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
    """Create a feature vector for features NOT in caniuse, using available metadata."""
    extractor = FeatureExtractor()
    features = np.zeros(extractor.n_features, dtype=np.float32)

    # Rough usage estimate based on how many browsers ship it
    estimated_usage = browsers_implementing * 15.0
    features[0] = min(estimated_usage, 50.0)
    features[1] = 5.0
    features[2] = features[0] + features[1]

    features[3] = STATUS_SCORES.get(spec_status, STATUS_SCORES['other'])

    # Assume Chrome/Firefox/Safari implement first
    browser_order = ['chrome', 'firefox', 'safari', 'edge', 'opera', 'ie']
    for i, browser in enumerate(browser_order[:browsers_implementing]):
        features[4 + i] = 1.0 if has_polyfill else 0.75

    support_values = features[4:10]
    features[10] = np.mean(support_values)
    features[11] = np.min(support_values)
    features[12] = np.max(support_values)
    features[13] = sum(1 for v in support_values if v >= 0.9)
    features[14] = sum(1 for v in support_values if 0.5 <= v < 0.9)
    features[15] = sum(1 for v in support_values if v < 0.5)
    features[16] = np.var(support_values)

    complexity_map = {'low': 3, 'medium': 6, 'high': 12}
    features[17] = complexity_map.get(complexity, 6)
    features[18] = 1 if complexity == 'high' else 0
    features[19] = 2
    features[20] = 1 if complexity != 'low' else 0
    features[21] = 0.0
    features[22] = 0.0
    features[23] = description_length / 100.0
    features[24] = 3.0
    features[25] = CATEGORY_ENCODING.get(category, 0)

    return features
