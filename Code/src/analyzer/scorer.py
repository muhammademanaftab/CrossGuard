"""Scoring helpers for browser compatibility."""

from typing import Dict


class CompatibilityScorer:

    STATUS_SCORES = {
        'y': 100, 'a': 100,  # 'a' = almost; treated as full to match caniuse UX
        'x': 70,   # needs vendor prefix
        'p': 50,   # partial
        'd': 30,   # disabled by default
        'n': 0, 'u': 0
    }

    def calculate_simple_score(self, support_status: Dict[str, str]) -> float:
        if not support_status:
            return 0.0

        total_score = sum(self.STATUS_SCORES.get(s, 0) for s in support_status.values())
        return total_score / len(support_status)
