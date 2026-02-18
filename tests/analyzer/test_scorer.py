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

    def test_all_supported_is_100(self, scorer):
        """All 'y' statuses produce score 100."""
        assert scorer.calculate_simple_score({'chrome': 'y', 'firefox': 'y', 'safari': 'y'}) == 100.0

    def test_all_unsupported_is_0(self, scorer):
        """All 'n' statuses produce score 0."""
        assert scorer.calculate_simple_score({'chrome': 'n', 'firefox': 'n'}) == 0.0

    def test_mixed_correct_average(self, scorer):
        """y=100 + n=0 => average 50."""
        assert scorer.calculate_simple_score({'chrome': 'y', 'firefox': 'n'}) == 50.0

    def test_empty_returns_0(self, scorer):
        """Empty input returns 0."""
        assert scorer.calculate_simple_score({}) == 0.0

    def test_single_browser(self, scorer):
        """Single browser returns that browser's status score."""
        assert scorer.calculate_simple_score({'chrome': 'x'}) == 70.0

    def test_prefix_and_supported_average(self, scorer):
        """x=70 + y=100 => average 85."""
        assert scorer.calculate_simple_score({'chrome': 'x', 'firefox': 'y'}) == 85.0

    def test_all_almost_supported_is_100(self, scorer):
        """All 'a' statuses produce 100 (treated as full per Can I Use)."""
        assert scorer.calculate_simple_score({'chrome': 'a', 'firefox': 'a'}) == 100.0

    def test_unrecognized_status_treated_as_0(self, scorer):
        """Unrecognized status character maps to 0 via .get() default."""
        assert scorer.calculate_simple_score({'chrome': 'z'}) == 0.0

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

    def test_all_supported_risk_none(self, scorer):
        """All 'y' => risk_level 'none'."""
        result = scorer.calculate_compatibility_index({'chrome': 'y', 'firefox': 'y', 'safari': 'y'})
        assert result['risk_level'] == 'none'
        assert result['score'] == 100.0

    def test_partial_only_risk_low(self, scorer):
        """Only partial support (no unsupported) => risk_level 'low'."""
        result = scorer.calculate_compatibility_index({'chrome': 'y', 'firefox': 'a', 'safari': 'x'})
        assert result['risk_level'] == 'low'

    def test_some_unsupported_risk_medium(self, scorer):
        """< 50% unsupported => risk_level 'medium'."""
        result = scorer.calculate_compatibility_index({'chrome': 'y', 'firefox': 'y', 'ie': 'n'})
        assert result['risk_level'] == 'medium'

    def test_majority_unsupported_risk_high(self, scorer):
        """>= 50% unsupported => risk_level 'high'."""
        result = scorer.calculate_compatibility_index({'chrome': 'n', 'firefox': 'n', 'safari': 'y'})
        assert result['risk_level'] == 'high'

    def test_counts_match_input(self, scorer):
        """Supported, partial, unsupported counts are accurate."""
        result = scorer.calculate_compatibility_index({'chrome': 'y', 'firefox': 'x', 'ie': 'n'})
        assert result['supported_count'] == 1
        assert result['partial_count'] == 1
        assert result['unsupported_count'] == 1
        assert result['total_browsers'] == 3

    def test_grade_assigned(self, scorer):
        """Result includes a valid letter grade."""
        result = scorer.calculate_compatibility_index({'chrome': 'y', 'firefox': 'y'})
        assert result['grade'] in ['A', 'B', 'C', 'D', 'F']

    def test_empty_input_returns_high_risk(self, scorer):
        """Empty status returns zeroed result with risk 'high'."""
        result = scorer.calculate_compatibility_index({})
        assert result['score'] == 0
        assert result['risk_level'] == 'high'
        assert result['grade'] == 'F'

    def test_support_percentage_only_counts_y(self, scorer):
        """support_percentage counts only 'y', not 'a' or partial.

        1 'y' out of 3 browsers = 33.33%.
        """
        result = scorer.calculate_compatibility_index({'chrome': 'y', 'firefox': 'a', 'safari': 'n'})
        assert abs(result['support_percentage'] - 33.33) < 0.1

    def test_all_keys_present(self, scorer):
        """Result dict has all expected keys."""
        result = scorer.calculate_compatibility_index({'chrome': 'y'})
        expected = {'score', 'grade', 'supported_count', 'partial_count',
                    'unsupported_count', 'total_browsers', 'support_percentage', 'risk_level'}
        assert set(result.keys()) == expected


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

    def test_modern_vs_legacy_split(self, scorer):
        """Modern browsers score 100, legacy scores 0."""
        result = scorer.calculate_progressive_score(
            {'chrome': 'y', 'firefox': 'y', 'ie': 'n'},
            {'chrome', 'firefox'},
        )
        assert result['modern'] == 100.0
        assert result['legacy'] == 0.0

    def test_overall_is_average_of_modern_and_legacy(self, scorer):
        """Overall is (modern + legacy) / 2."""
        result = scorer.calculate_progressive_score({'chrome': 'y', 'ie': 'n'}, {'chrome'})
        assert result['overall'] == (result['modern'] + result['legacy']) / 2

    def test_all_modern_legacy_defaults_0(self, scorer):
        """When all browsers are modern, legacy defaults to 0."""
        result = scorer.calculate_progressive_score(
            {'chrome': 'y', 'firefox': 'y'},
            {'chrome', 'firefox'},
        )
        assert result['legacy'] == 0.0

    def test_no_modern_defaults_100(self, scorer):
        """When no browsers are modern, modern score defaults to 100."""
        result = scorer.calculate_progressive_score({'ie': 'n'}, set())
        assert result['modern'] == 100.0

    def test_mixed_modern_scores(self, scorer):
        """Mixed modern support calculates correctly."""
        result = scorer.calculate_progressive_score(
            {'chrome': 'y', 'firefox': 'n', 'ie': 'n'},
            {'chrome', 'firefox'},
        )
        assert result['modern'] == 50.0  # (100 + 0) / 2
        assert result['legacy'] == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: calculate_trend_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestTrendScore:
    """Tests for calculate_trend_score()."""

    def test_improving_trend(self, scorer):
        """Score improving by >10 points => 'improving'."""
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

    def test_declining_trend(self, scorer):
        """Score declining by >10 points => 'declining'."""
        history = {
            '100': {'chrome': 'y', 'firefox': 'y'},
            '120': {'chrome': 'n', 'firefox': 'n'},
        }
        result = scorer.calculate_trend_score(history)
        assert result['trend'] == 'declining'
        assert result['improvement'] == -100.0

    def test_stable_trend(self, scorer):
        """Score change within [-10, +10] => 'stable'."""
        history = {
            '100': {'chrome': 'y', 'firefox': 'y'},
            '120': {'chrome': 'y', 'firefox': 'y'},
        }
        result = scorer.calculate_trend_score(history)
        assert result['trend'] == 'stable'
        assert result['improvement'] == 0.0

    def test_empty_history_unknown(self, scorer):
        """Empty history returns trend 'unknown'."""
        result = scorer.calculate_trend_score({})
        assert result['trend'] == 'unknown'
        assert result['improvement'] == 0

    def test_single_version_stable(self, scorer):
        """Single version returns 'stable' (no comparison possible)."""
        result = scorer.calculate_trend_score({'120': {'chrome': 'y'}})
        assert result['trend'] == 'stable'

    def test_versions_analyzed_count(self, scorer):
        """versions_analyzed matches input size."""
        history = {'100': {'chrome': 'n'}, '110': {'chrome': 'y'}, '120': {'chrome': 'y'}}
        result = scorer.calculate_trend_score(history)
        assert result['versions_analyzed'] == 3

    def test_versions_sorted_before_comparison(self, scorer):
        """Versions are sorted numerically, not by insertion order."""
        history = {
            '120': {'chrome': 'y', 'firefox': 'y'},  # Inserted first but higher
            '100': {'chrome': 'n', 'firefox': 'n'},  # Inserted second but lower
        }
        result = scorer.calculate_trend_score(history)
        assert result['first_score'] == 0.0   # version 100
        assert result['last_score'] == 100.0  # version 120
        assert result['trend'] == 'improving'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: compare_features()
# ═══════════════════════════════════════════════════════════════════════════

class TestCompareFeatures:
    """Tests for compare_features()."""

    def test_best_and_worst_identified(self, scorer):
        """Best features are sorted highest-first, worst lowest-first."""
        scores = {'flexbox': 100, 'dialog': 50, 'css-grid': 80}
        result = scorer.compare_features(scores)
        assert result['best_features'][0] == {'feature': 'flexbox', 'score': 100}
        assert result['worst_features'][0] == {'feature': 'dialog', 'score': 50}

    def test_average_score_correct(self, scorer):
        """Average score is arithmetic mean."""
        result = scorer.compare_features({'a': 100, 'b': 0})
        assert result['average_score'] == 50.0

    def test_empty_input_zeroed(self, scorer):
        """Empty input returns zeroed comparison."""
        result = scorer.compare_features({})
        assert result['best_features'] == []
        assert result['worst_features'] == []
        assert result['average_score'] == 0

    def test_total_features_count(self, scorer):
        """total_features matches input dict size."""
        result = scorer.compare_features({'a': 90, 'b': 80, 'c': 70})
        assert result['total_features'] == 3

    def test_variance_zero_when_equal(self, scorer):
        """Identical scores produce variance 0."""
        result = scorer.compare_features({'a': 50, 'b': 50})
        assert result['score_variance'] == 0.0

    def test_variance_calculation(self, scorer):
        """Variance for [0, 100] is 2500.0."""
        result = scorer.compare_features({'a': 0, 'b': 100})
        # mean=50, variance = ((0-50)^2 + (100-50)^2) / 2 = 2500
        assert result['score_variance'] == 2500.0

    def test_limits_to_five(self, scorer):
        """Best/worst lists capped at 5 items."""
        scores = {f'f{i}': i * 10 for i in range(10)}
        result = scorer.compare_features(scores)
        assert len(result['best_features']) == 5
        assert len(result['worst_features']) == 5


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: calculate_market_share_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestMarketShareScore:
    """Tests for calculate_market_share_score()."""

    def test_high_share_browser_dominates(self, scorer):
        """Browser with 65% share dominates over 2% share.

        (100*65 + 0*2) / 67 = 97.01
        """
        score = scorer.calculate_market_share_score(
            {'chrome': 'y', 'ie': 'n'},
            {'chrome': 65.0, 'ie': 2.0},
        )
        assert abs(score - 97.01) < 0.1

    def test_empty_returns_0(self, scorer):
        """Empty input returns 0."""
        assert scorer.calculate_market_share_score({}, {}) == 0.0

    def test_missing_share_skipped(self, scorer):
        """Browser without market share data is excluded from calculation."""
        score = scorer.calculate_market_share_score(
            {'chrome': 'y', 'unknown_browser': 'n'},
            {'chrome': 65.0},
        )
        assert score == 100.0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 11: calculate_feature_importance_score()
# ═══════════════════════════════════════════════════════════════════════════

class TestFeatureImportanceScore:
    """Tests for calculate_feature_importance_score()."""

    def test_high_importance_unsupported_dominates(self, scorer):
        """High-importance unsupported feature drags score down.

        (0*1.0 + 100*0.1) / 1.1 = 9.09
        """
        features = {
            'critical': {'chrome': 'n'},
            'optional': {'chrome': 'y'},
        }
        weights = {'critical': 1.0, 'optional': 0.1}
        score = scorer.calculate_feature_importance_score(features, weights)
        assert abs(score - 9.09) < 0.1

    def test_empty_returns_0(self, scorer):
        """Empty features returns 0."""
        assert scorer.calculate_feature_importance_score({}, {}) == 0.0

    def test_missing_weight_defaults_to_1(self, scorer):
        """Feature not in weights dict uses default importance 1.0."""
        score = scorer.calculate_feature_importance_score(
            {'a': {'chrome': 'y'}},
            {},  # No weights
        )
        assert score == 100.0

    def test_equal_weights_equals_simple_average(self, scorer):
        """When all features have weight 1.0, result equals simple average."""
        features = {
            'f1': {'chrome': 'y'},   # 100
            'f2': {'chrome': 'n'},   # 0
        }
        weights = {'f1': 1.0, 'f2': 1.0}
        score = scorer.calculate_feature_importance_score(features, weights)
        assert score == 50.0
