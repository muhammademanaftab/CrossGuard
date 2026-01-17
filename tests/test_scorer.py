"""
Test suite for CompatibilityScorer.
Tests scoring algorithms and metrics.
"""

import pytest
from src.analyzer.scorer import CompatibilityScorer, WeightedScore


class TestScorerBasic:
    """Basic tests for CompatibilityScorer."""

    def test_scorer_initialization(self, scorer):
        """Test scorer initializes correctly."""
        assert scorer is not None
        assert hasattr(scorer, 'calculate_simple_score')
        assert hasattr(scorer, 'calculate_weighted_score')

    def test_scorer_has_default_weights(self, scorer):
        """Test scorer has default browser weights."""
        weights = scorer.get_browser_weights()
        assert 'chrome' in weights
        assert 'firefox' in weights
        assert 'safari' in weights

    def test_scorer_status_scores(self, scorer):
        """Test scorer has status score mappings."""
        assert scorer.STATUS_SCORES['y'] == 100
        assert scorer.STATUS_SCORES['n'] == 0


class TestSimpleScore:
    """Test simple score calculation."""

    def test_simple_score_all_supported(self, scorer):
        """Test simple score when all supported."""
        support_status = {'chrome': 'y', 'firefox': 'y', 'safari': 'y', 'edge': 'y'}
        score = scorer.calculate_simple_score(support_status)
        assert score == 100.0

    def test_simple_score_all_unsupported(self, scorer):
        """Test simple score when none supported."""
        support_status = {'chrome': 'n', 'firefox': 'n', 'safari': 'n', 'edge': 'n'}
        score = scorer.calculate_simple_score(support_status)
        assert score == 0.0

    def test_simple_score_mixed_support(self, scorer):
        """Test simple score with mixed support."""
        support_status = {'chrome': 'y', 'firefox': 'y', 'safari': 'n', 'edge': 'n'}
        score = scorer.calculate_simple_score(support_status)
        assert score == 50.0

    def test_simple_score_partial_support(self, scorer):
        """Test simple score with partial support."""
        support_status = {'chrome': 'y', 'firefox': 'a', 'safari': 'y', 'edge': 'y'}
        score = scorer.calculate_simple_score(support_status)
        expected = (100 + 50 + 100 + 100) / 4
        assert score == expected

    def test_simple_score_empty(self, scorer):
        """Test simple score with empty input."""
        score = scorer.calculate_simple_score({})
        assert score == 0.0


class TestWeightedScore:
    """Test weighted score calculation."""

    def test_weighted_score_returns_object(self, scorer):
        """Test weighted score returns WeightedScore object."""
        support_status = {'chrome': 'y', 'firefox': 'y'}
        result = scorer.calculate_weighted_score(support_status)
        assert isinstance(result, WeightedScore)

    def test_weighted_score_has_breakdown(self, scorer):
        """Test weighted score has breakdown."""
        support_status = {'chrome': 'y', 'firefox': 'n'}
        result = scorer.calculate_weighted_score(support_status)
        assert 'chrome' in result.breakdown
        assert 'firefox' in result.breakdown

    def test_weighted_score_has_weights(self, scorer):
        """Test weighted score includes weights used."""
        support_status = {'chrome': 'y', 'firefox': 'y'}
        result = scorer.calculate_weighted_score(support_status)
        assert 'chrome' in result.weights
        assert 'firefox' in result.weights

    def test_weighted_score_empty(self, scorer):
        """Test weighted score with empty input."""
        result = scorer.calculate_weighted_score({})
        assert result.weighted_score == 0.0


class TestCompatibilityIndex:
    """Test compatibility index calculation."""

    def test_compatibility_index_structure(self, scorer):
        """Test compatibility index has expected fields."""
        support_status = {'chrome': 'y', 'firefox': 'y'}
        index = scorer.calculate_compatibility_index(support_status)

        assert 'score' in index
        assert 'grade' in index
        assert 'supported_count' in index
        assert 'partial_count' in index
        assert 'unsupported_count' in index
        assert 'risk_level' in index

    def test_compatibility_index_counts(self, scorer):
        """Test compatibility index counts correctly."""
        support_status = {'chrome': 'y', 'firefox': 'a', 'safari': 'n', 'edge': 'y'}
        index = scorer.calculate_compatibility_index(support_status)

        assert index['supported_count'] == 2
        assert index['partial_count'] == 1
        assert index['unsupported_count'] == 1
        assert index['total_browsers'] == 4

    def test_compatibility_index_risk_none(self, scorer):
        """Test risk level none when all supported."""
        support_status = {'chrome': 'y', 'firefox': 'y', 'safari': 'y'}
        index = scorer.calculate_compatibility_index(support_status)
        assert index['risk_level'] == 'none'

    def test_compatibility_index_risk_high(self, scorer):
        """Test risk level high when mostly unsupported."""
        support_status = {'chrome': 'n', 'firefox': 'n', 'safari': 'n', 'edge': 'y'}
        index = scorer.calculate_compatibility_index(support_status)
        assert index['risk_level'] == 'high'


class TestGrading:
    """Test score to grade conversion."""

    def test_grade_a(self, scorer):
        """Test A grade for high scores."""
        grade = scorer._score_to_grade(95)
        assert grade == 'A'

    def test_grade_b(self, scorer):
        """Test B grade."""
        grade = scorer._score_to_grade(85)
        assert grade == 'B'

    def test_grade_c(self, scorer):
        """Test C grade."""
        grade = scorer._score_to_grade(75)
        assert grade == 'C'

    def test_grade_d(self, scorer):
        """Test D grade."""
        grade = scorer._score_to_grade(65)
        assert grade == 'D'

    def test_grade_f(self, scorer):
        """Test F grade for low scores."""
        grade = scorer._score_to_grade(50)
        assert grade == 'F'


class TestBrowserWeights:
    """Test browser weight management."""

    def test_set_browser_weight(self, scorer):
        """Test setting custom browser weight."""
        scorer.set_browser_weight('chrome', 0.8)
        weights = scorer.get_browser_weights()
        assert weights['chrome'] == 0.8

    def test_set_browser_weight_invalid(self, scorer):
        """Test setting invalid weight raises error."""
        with pytest.raises(ValueError):
            scorer.set_browser_weight('chrome', 1.5)

    def test_set_browser_weight_negative(self, scorer):
        """Test setting negative weight raises error."""
        with pytest.raises(ValueError):
            scorer.set_browser_weight('chrome', -0.1)


class TestProgressiveScore:
    """Test progressive scoring (modern vs legacy)."""

    def test_progressive_score_structure(self, scorer):
        """Test progressive score has expected fields."""
        support_status = {'chrome': 'y', 'firefox': 'y', 'ie': 'n'}
        modern_browsers = {'chrome', 'firefox'}
        result = scorer.calculate_progressive_score(support_status, modern_browsers)

        assert 'modern' in result
        assert 'legacy' in result
        assert 'overall' in result

    def test_progressive_score_modern_only(self, scorer):
        """Test progressive score with modern browsers."""
        support_status = {'chrome': 'y', 'firefox': 'y'}
        modern_browsers = {'chrome', 'firefox'}
        result = scorer.calculate_progressive_score(support_status, modern_browsers)

        assert result['modern'] == 100.0


class TestFeatureComparison:
    """Test feature comparison functionality."""

    def test_compare_features_structure(self, scorer):
        """Test feature comparison has expected fields."""
        feature_scores = {'flexbox': 100, 'css-grid': 90, 'container-queries': 50}
        result = scorer.compare_features(feature_scores)

        assert 'best_features' in result
        assert 'worst_features' in result
        assert 'average_score' in result

    def test_compare_features_sorting(self, scorer):
        """Test features are sorted by score."""
        feature_scores = {'a': 100, 'b': 50, 'c': 75}
        result = scorer.compare_features(feature_scores)

        best = result['best_features']
        assert best[0]['score'] >= best[-1]['score']

    def test_compare_features_empty(self, scorer):
        """Test comparing empty features."""
        result = scorer.compare_features({})
        assert result['average_score'] == 0


class TestTrendScore:
    """Test trend score calculation."""

    def test_trend_score_improving(self, scorer):
        """Test detecting improving trend."""
        support_history = {
            '100': {'chrome': 'n', 'firefox': 'n'},
            '110': {'chrome': 'a', 'firefox': 'a'},
            '120': {'chrome': 'y', 'firefox': 'y'}
        }
        result = scorer.calculate_trend_score(support_history)
        assert result['trend'] == 'improving'

    def test_trend_score_stable(self, scorer):
        """Test detecting stable trend."""
        support_history = {
            '100': {'chrome': 'y', 'firefox': 'y'},
            '110': {'chrome': 'y', 'firefox': 'y'},
            '120': {'chrome': 'y', 'firefox': 'y'}
        }
        result = scorer.calculate_trend_score(support_history)
        assert result['trend'] == 'stable'

    def test_trend_score_empty(self, scorer):
        """Test trend score with empty history."""
        result = scorer.calculate_trend_score({})
        assert result['trend'] == 'unknown'
