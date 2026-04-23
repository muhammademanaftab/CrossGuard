"""Buckets detected features into supported / partial / unsupported / unknown per target browser,
and returns the raw Can I Use status codes so the scorer can weight each one via STATUS_SCORES."""

from typing import Dict, Set

from .database import get_database


class CompatibilityAnalyzer:
    """Per-browser feature classification. Scoring lives in CompatibilityScorer."""

    def __init__(self):
        self.database = get_database()

    def classify_features(
        self,
        features: Set[str],
        target_browsers: Dict[str, str],
    ) -> Dict[str, Dict]:
        """Returns {browser: {supported, partial, unsupported, unknown, statuses}}:
        the first four are feature-id lists for the UI, 'statuses' is the raw
        Can I Use code ('y'/'a'/'x'/'n'/'p'/'d'/'u') for every feature, in order."""
        results: Dict[str, Dict] = {}
        for browser, version in target_browsers.items():
            bucket = {
                'supported': [],
                'partial': [],
                'unsupported': [],
                'unknown': [],
                'statuses': [],
            }
            for feature_id in features:
                status = self.database.check_support(feature_id, browser, version)
                bucket['statuses'].append(status)
                if status == 'y':
                    bucket['supported'].append(feature_id)
                elif status in ('a', 'x'):
                    bucket['partial'].append(feature_id)
                elif status == 'n':
                    bucket['unsupported'].append(feature_id)
                else:
                    bucket['unknown'].append(feature_id)
            results[browser] = bucket
        return results
