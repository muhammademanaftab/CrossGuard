"""Tests for CompatibilityScorer — scoring algorithms and metrics.

Validates simple, weighted, progressive, trend, and comparison scoring
plus the 5-level grading scale (A/B/C/D/F).
"""

import pytest

from src.analyzer.scorer import CompatibilityScorer, WeightedScore


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: STATUS_SCORES Constants
# ═══════════════════════════════════════════════════════════════════════════

class TestStatusScores:
    """Verify the score values for each support status character."""

    @pytest.mark.parametrize("status,expected", [
        ('y', 100), ('a', 100), ('x', 70),
        ('p', 50), ('d', 30), ('n', 0), ('u', 0),
    ])
    def test_status_score_values(self, scorer, status, expected):
        """Each status char maps to its defined score value."""
        assert scorer.STATUS_SCORES[status] == expected

    def test_all_statuses_present(self, scorer):
        """All 7 status codes are defined in STATUS_SCORES."""
        assert set(scorer.STATUS_SCORES.keys()) == {'y', 'a', 'x', 'p', 'd', 'n', 'u'}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: DEFAULT_WEIGHTS
# ═══════════════════════════════════════════════════════════════════════════

class TestDefaultWeights:
    """Verify the default browser weights."""

    @pytest.mark.parametrize("browser,expected", [
        ('chrome', 1.0), ('firefox', 1.0), ('safari', 1.0),
        ('edge', 1.0), ('ie', 0.5), ('opera', 0.7),
    ])
    def test_default_weight_values(self, scorer, browser, expected):
        """Default weight for each browser is correct."""
        assert scorer.browser_weights[browser] == expected

    def test_custom_weights_override_defaults(self, scorer_custom):
        """Custom weights replace defaults entirely."""
        s = scorer_custom({'chrome': 0.9, 'firefox': 0.8})
        assert s.browser_weights == {'chrome': 0.9, 'firefox': 0.8}
        assert 'ie' not in s.browser_weights

    def test_set_browser_weight(self, scorer):
        """set_browser_weight() updates a single browser."""
        scorer.set_browser_weight('chrome', 0.5)
        assert scorer.browser_weights['chrome'] == 0.5

    def test_set_browser_weight_too_high(self, scorer):
        """set_browser_weight() rejects weight > 1."""
        with pytest.raises(ValueError):
            scorer.set_browser_weight('chrome', 1.5)

    def test_set_browser_weight_negative(self, scorer):
        """set_browser_weight() rejects negative weight."""
        with pytest.raises(ValueError):
            scorer.set_browser_weight('chrome', -0.1)

    def test_set_browser_weight_boundary_0(self, scorer):
        """Weight of exactly 0 is accepted."""
        scorer.set_browser_weight('ie', 0.0)
        assert scorer.browser_weights['ie'] == 0.0

    def test_set_browser_weight_boundary_1(self, scorer):
        """Weight of exactly 1 is accepted."""
        scorer.set_browser_weight('ie', 1.0)
        assert scorer.browser_weights['ie'] == 1.0

    def test_get_browser_weights_returns_copy(self, scorer):
        """get_browser_weights() returns a copy, not a reference."""
        weights = scorer.get_browser_weights()
        weights['chrome'] = 0.0
        assert scorer.browser_weights['chrome'] == 1.0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: calculate_simple_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestSimpleScore:
    """Tests for calculate_simple_score()."""

    @pytest.mark.parametrize("status,expected", [
        ({'chrome': 'y', 'firefox': 'y', 'safari': 'y'}, 100.0),
        ({'chrome': 'n', 'firefox': 'n'}, 0.0),
        ({'chrome': 'y', 'firefox': 'n'}, 50.0),
        ({}, 0.0),
        ({'chrome': 'x'}, 70.0),
        ({'chrome': 'x', 'firefox': 'y'}, 85.0),
        ({'chrome': 'a', 'firefox': 'a'}, 100.0),
        ({'chrome': 'z'}, 0.0),
    ])
    def test_simple_score_calculation(self, scorer, status, expected):
        assert scorer.calculate_simple_score(status) == expected

    def test_all_statuses_combined(self, scorer):
        """Score for all 7 status types averaged correctly."""
        status = {'b1': 'y', 'b2': 'a', 'b3': 'x', 'b4': 'p', 'b5': 'd', 'b6': 'n', 'b7': 'u'}
        expected = (100 + 100 + 70 + 50 + 30 + 0 + 0) / 7
        assert abs(scorer.calculate_simple_score(status) - expected) < 0.01


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: calculate_weighted_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestWeightedScore:
    """Tests for calculate_weighted_score()."""

    def test_returns_weighted_score_object(self, scorer):
        """Returns a WeightedScore dataclass."""
        result = scorer.calculate_weighted_score({'chrome': 'y'})
        assert isinstance(result, WeightedScore)

    def test_all_supported_weighted_100(self, scorer):
        """All supported => weighted score 100."""
        result = scorer.calculate_weighted_score({'chrome': 'y', 'firefox': 'y'})
        assert result.weighted_score == 100.0

    def test_ie_weight_calculation(self, scorer):
        """IE's weight (0.5) produces correct weighted score.

        chrome y=100 weight=1.0, ie n=0 weight=0.5
        weighted = (100*1.0 + 0*0.5) / (1.0+0.5) = 66.67
        """
        result = scorer.calculate_weighted_score({'chrome': 'y', 'ie': 'n'})
        assert abs(result.weighted_score - 66.67) < 0.1

    def test_weighted_differs_from_simple_with_ie(self, scorer):
        """Weighted and simple scores diverge when browser weights differ."""
        result = scorer.calculate_weighted_score({'chrome': 'y', 'ie': 'n'})
        assert result.total_score == 50.0              # Simple average
        assert result.weighted_score > result.total_score  # Weighted favors chrome

    def test_breakdown_dict_has_correct_scores(self, scorer):
        """Breakdown maps each browser to its status score."""
        result = scorer.calculate_weighted_score({'chrome': 'y', 'firefox': 'n'})
        assert result.breakdown == {'chrome': 100, 'firefox': 0}

    def test_weights_dict_matches_config(self, scorer):
        """Weights dict reflects the configured browser weights."""
        result = scorer.calculate_weighted_score({'chrome': 'y', 'ie': 'n'})
        assert result.weights == {'chrome': 1.0, 'ie': 0.5}

    def test_empty_returns_zeroed(self, scorer):
        """Empty input returns all-zero WeightedScore."""
        result = scorer.calculate_weighted_score({})
        assert result.total_score == 0.0
        assert result.weighted_score == 0.0
        assert result.breakdown == {}

    def test_custom_weights_change_outcome(self, scorer_custom):
        """Custom weights produce different weighted score.

        chrome y=100 weight=0.1, firefox n=0 weight=1.0
        weighted = (100*0.1 + 0*1.0) / (0.1+1.0) = 9.09
        """
        s = scorer_custom({'chrome': 0.1, 'firefox': 1.0})
        result = s.calculate_weighted_score({'chrome': 'y', 'firefox': 'n'})
        assert abs(result.weighted_score - 9.09) < 0.1

    def test_unknown_browser_gets_default_weight_1(self, scorer):
        """Browser not in weights dict gets default weight 1.0."""
        result = scorer.calculate_weighted_score({'brand_new_browser': 'y'})
        assert result.weights['brand_new_browser'] == 1.0
        assert result.weighted_score == 100.0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: calculate_compatibility_index()
# ═══════════════════════════════════════════════════════════════════════════

class TestCompatibilityIndex:
    """Tests for calculate_compatibility_index()."""

    @pytest.mark.parametrize("status,expected_risk", [
        ({'chrome': 'y', 'firefox': 'y', 'safari': 'y'}, 'none'),
        ({'chrome': 'y', 'firefox': 'a', 'safari': 'x'}, 'low'),
        ({'chrome': 'y', 'firefox': 'y', 'ie': 'n'}, 'medium'),
        ({'chrome': 'n', 'firefox': 'n', 'safari': 'y'}, 'high'),
        ({}, 'high'),
    ])
    def test_risk_level(self, scorer, status, expected_risk):
        result = scorer.calculate_compatibility_index(status)
        assert result['risk_level'] == expected_risk

    def test_counts_match_input(self, scorer):
        result = scorer.calculate_compatibility_index({'chrome': 'y', 'firefox': 'x', 'ie': 'n'})
        assert result['supported_count'] == 1
        assert result['partial_count'] == 1
        assert result['unsupported_count'] == 1
        assert result['total_browsers'] == 3

    def test_all_keys_present(self, scorer):
        result = scorer.calculate_compatibility_index({'chrome': 'y'})
        expected = {'score', 'grade', 'supported_count', 'partial_count',
                    'unsupported_count', 'total_browsers', 'support_percentage', 'risk_level'}
        assert set(result.keys()) == expected

    def test_support_percentage_only_counts_y(self, scorer):
        result = scorer.calculate_compatibility_index({'chrome': 'y', 'firefox': 'a', 'safari': 'n'})
        assert abs(result['support_percentage'] - 33.33) < 0.1


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: _score_to_grade() — 5-level grading
# ═══════════════════════════════════════════════════════════════════════════

class TestScorerGrade:
    """Tests for the scorer's 5-level grading scale."""

    @pytest.mark.parametrize("score,expected", [
        (100, 'A'), (95, 'A'), (90, 'A'),
        (89.99, 'B'), (80, 'B'),
        (79.99, 'C'), (70, 'C'),
        (69.99, 'D'), (60, 'D'),
        (59.99, 'F'), (0, 'F'),
    ])
    def test_grade_boundaries(self, scorer, score, expected):
        """Grade boundaries: 90+=A, 80+=B, 70+=C, 60+=D, <60=F."""
        assert scorer._score_to_grade(score) == expected


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: calculate_progressive_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestProgressiveScore:
    """Tests for calculate_progressive_score()."""

    @pytest.mark.parametrize("status,modern_set,expected_modern,expected_legacy", [
        ({'chrome': 'y', 'firefox': 'y', 'ie': 'n'}, {'chrome', 'firefox'}, 100.0, 0.0),
        ({'chrome': 'y', 'firefox': 'y'}, {'chrome', 'firefox'}, 100.0, 0.0),
        ({'ie': 'n'}, set(), 100.0, 0.0),
        ({'chrome': 'y', 'firefox': 'n', 'ie': 'n'}, {'chrome', 'firefox'}, 50.0, 0.0),
    ])
    def test_modern_vs_legacy_split(self, scorer, status, modern_set, expected_modern, expected_legacy):
        result = scorer.calculate_progressive_score(status, modern_set)
        assert result['modern'] == expected_modern
        assert result['legacy'] == expected_legacy

    def test_overall_is_average_of_modern_and_legacy(self, scorer):
        result = scorer.calculate_progressive_score({'chrome': 'y', 'ie': 'n'}, {'chrome'})
        assert result['overall'] == (result['modern'] + result['legacy']) / 2


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: calculate_trend_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestTrendScore:
    """Tests for calculate_trend_score()."""

    def test_improving_trend(self, scorer):
        history = {
            '100': {'chrome': 'n', 'firefox': 'n'},
            '110': {'chrome': 'y', 'firefox': 'n'},
            '120': {'chrome': 'y', 'firefox': 'y'},
        }
        result = scorer.calculate_trend_score(history)
        assert result['trend'] == 'improving'
        assert result['improvement'] == 100.0
        assert result['first_score'] == 0.0
        assert result['last_score'] == 100.0
        assert result['versions_analyzed'] == 3

    def test_declining_trend(self, scorer):
        history = {
            '100': {'chrome': 'y', 'firefox': 'y'},
            '120': {'chrome': 'n', 'firefox': 'n'},
        }
        result = scorer.calculate_trend_score(history)
        assert result['trend'] == 'declining'
        assert result['improvement'] == -100.0

    @pytest.mark.parametrize("history,expected_trend", [
        ({'100': {'chrome': 'y', 'firefox': 'y'}, '120': {'chrome': 'y', 'firefox': 'y'}}, 'stable'),
        ({'120': {'chrome': 'y'}}, 'stable'),
        ({}, 'unknown'),
    ])
    def test_edge_case_trends(self, scorer, history, expected_trend):
        result = scorer.calculate_trend_score(history)
        assert result['trend'] == expected_trend

    def test_versions_sorted_before_comparison(self, scorer):
        """Versions are sorted numerically, not by insertion order."""
        history = {
            '120': {'chrome': 'y', 'firefox': 'y'},
            '100': {'chrome': 'n', 'firefox': 'n'},
        }
        result = scorer.calculate_trend_score(history)
        assert result['first_score'] == 0.0
        assert result['last_score'] == 100.0
        assert result['trend'] == 'improving'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: compare_features()
# ═══════════════════════════════════════════════════════════════════════════

class TestCompareFeatures:
    """Tests for compare_features()."""

    def test_best_and_worst_identified(self, scorer):
        scores = {'flexbox': 100, 'dialog': 50, 'css-grid': 80}
        result = scorer.compare_features(scores)
        assert result['best_features'][0] == {'feature': 'flexbox', 'score': 100}
        assert result['worst_features'][0] == {'feature': 'dialog', 'score': 50}

    def test_empty_input_zeroed(self, scorer):
        result = scorer.compare_features({})
        assert result['best_features'] == []
        assert result['worst_features'] == []
        assert result['average_score'] == 0

    @pytest.mark.parametrize("scores,expected_avg,expected_var", [
        ({'a': 100, 'b': 0}, 50.0, 2500.0),
        ({'a': 50, 'b': 50}, 50.0, 0.0),
    ])
    def test_average_and_variance(self, scorer, scores, expected_avg, expected_var):
        result = scorer.compare_features(scores)
        assert result['average_score'] == expected_avg
        assert result['score_variance'] == expected_var

    def test_limits_to_five(self, scorer):
        scores = {f'f{i}': i * 10 for i in range(10)}
        result = scorer.compare_features(scores)
        assert len(result['best_features']) == 5
        assert len(result['worst_features']) == 5
        assert result['total_features'] == 10


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: calculate_market_share_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestMarketShareScore:
    """Tests for calculate_market_share_score()."""

    @pytest.mark.parametrize("status,shares,expected", [
        ({'chrome': 'y', 'ie': 'n'}, {'chrome': 65.0, 'ie': 2.0}, 97.01),
        ({}, {}, 0.0),
        ({'chrome': 'y', 'unknown_browser': 'n'}, {'chrome': 65.0}, 100.0),
    ])
    def test_market_share_score(self, scorer, status, shares, expected):
        score = scorer.calculate_market_share_score(status, shares)
        assert abs(score - expected) < 0.1


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 11: calculate_feature_importance_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestFeatureImportanceScore:
    """Tests for calculate_feature_importance_score()."""

    @pytest.mark.parametrize("features,weights,expected", [
        ({'critical': {'chrome': 'n'}, 'optional': {'chrome': 'y'}}, {'critical': 1.0, 'optional': 0.1}, 9.09),
        ({}, {}, 0.0),
        ({'a': {'chrome': 'y'}}, {}, 100.0),
        ({'f1': {'chrome': 'y'}, 'f2': {'chrome': 'n'}}, {'f1': 1.0, 'f2': 1.0}, 50.0),
    ])
    def test_feature_importance_score(self, scorer, features, weights, expected):
        score = scorer.calculate_feature_importance_score(features, weights)
        assert abs(score - expected) < 0.1
