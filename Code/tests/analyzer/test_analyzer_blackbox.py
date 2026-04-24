"""Black-box tests for the analyzer public API -- classification, scoring, version ranges.

Tests CompatibilityAnalyzer.classify_features, CompatibilityScorer, and
version_ranges through their public interfaces with real and mocked data.
"""

import pytest
from unittest.mock import MagicMock

from src.analyzer.compatibility import CompatibilityAnalyzer
from src.analyzer.scorer import CompatibilityScorer
from src.analyzer.version_ranges import (
    get_version_ranges,
    _get_status_text,
)


def _score(analyzer: CompatibilityAnalyzer, features, browsers) -> float:
    """Classify features then score via STATUS_SCORES -- what the pipeline does."""
    classification = analyzer.classify_features(features, browsers)
    scorer = CompatibilityScorer()
    pcts = {
        b: scorer.score_statuses(r['statuses'])
        for b, r in classification.items()
    }
    return scorer.overall_score(pcts), pcts


# ============================================================================
# SECTION 1: classify_features + scorer -- End-to-End Scoring
# ============================================================================

class TestClassifyAndScore:
    """Tests for classify_features(features, target_browsers) + CompatibilityScorer."""

    @pytest.mark.blackbox
    def test_well_supported_high_score(self, analyzer, modern_browsers, well_supported_features):
        overall, _ = _score(analyzer, well_supported_features, modern_browsers)
        assert overall >= 80.0

    @pytest.mark.blackbox
    def test_adding_ie_lowers_score(self, analyzer, well_supported_features):
        modern = {'chrome': '120', 'firefox': '121'}
        with_ie = {'chrome': '120', 'firefox': '121', 'ie': '11'}
        assert _score(analyzer, well_supported_features, with_ie)[0] < \
               _score(analyzer, well_supported_features, modern)[0]


# ============================================================================
# SECTION 7: Mocked Database Unit Tests
# ============================================================================

class TestAnalyzerWithMockedDB:

    def _make_analyzer_with_mock(self, support_map):
        mock_db = MagicMock()
        mock_db.check_support.side_effect = lambda f, b, v: support_map.get((f, b), 'u')
        a = CompatibilityAnalyzer.__new__(CompatibilityAnalyzer)
        a.database = mock_db
        return a

    @pytest.mark.blackbox
    def test_mixed_support_correct_score(self):
        a = self._make_analyzer_with_mock({('flexbox', 'chrome'): 'y', ('flexbox', 'ie'): 'n'})
        overall, pcts = _score(a, {'flexbox'}, {'chrome': '120', 'ie': '11'})
        assert pcts['chrome'] == 100.0
        assert pcts['ie'] == 0.0
        assert overall == 50.0


# ============================================================================
# SECTION 15: Version Ranges
# ============================================================================

class TestGetVersionRanges:

    @pytest.mark.blackbox
    def test_flexbox_chrome_ranges(self):
        ranges = get_version_ranges('flexbox', 'chrome')
        assert len(ranges) > 0
        for r in ranges:
            assert set(r.keys()) == {'start', 'end', 'status', 'status_text'}
        assert ranges[-1]['status'] == 'y'


# ============================================================================
# SECTION 16: Status Text, Format, Summary, Browser Names
# ============================================================================

class TestStatusTextAndFormat:

    @pytest.mark.blackbox
    def test_known_status_code(self):
        assert _get_status_text('y') == 'Supported'


# ============================================================================
# SECTION 17: CompatibilityScorer
# ============================================================================

class TestCompatibilityScorer:

    @pytest.mark.blackbox
    @pytest.mark.parametrize("score,expected", [
        (100, 'A'), (89.9, 'B'), (70, 'C'), (60, 'D'), (59.9, 'F'),
    ])
    def test_grade_boundaries(self, score, expected):
        assert CompatibilityScorer().grade(score) == expected

    @pytest.mark.blackbox
    def test_score_statuses_formula(self):
        s = CompatibilityScorer()
        # 2 fully supported + 1 partial (vendor prefix) → (100*2 + 50*1) / 3 ≈ 83.33
        assert round(s.score_statuses(['y', 'y', 'x']), 2) == 83.33
        # no features → 100 (nothing to complain about)
        assert s.score_statuses([]) == 100.0
        # one unsupported + one unknown → 0
        assert s.score_statuses(['n', 'u']) == 0.0

    @pytest.mark.blackbox
    @pytest.mark.parametrize("score,unsupported,expected", [
        (100, 0, 'none'),     # nothing broken
        (85, 3, 'low'),       # broken but score still high
        (70, 5, 'medium'),    # middle ground
        (40, 10, 'high'),     # lots broken, low score
    ])
    def test_risk_level(self, score, unsupported, expected):
        assert CompatibilityScorer().risk_level(score, unsupported) == expected
