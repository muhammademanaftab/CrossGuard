"""Tests for quality gate evaluation."""

import pytest

from src.cli.gates import ThresholdConfig, GateResult, evaluate_gates


class TestThresholdConfigDefaults:
    def test_all_none_by_default(self):
        config = ThresholdConfig()
        assert config.min_score is None
        assert config.max_errors is None
        assert config.max_warnings is None


class TestEvaluateGatesScoreThreshold:
    def test_score_above_threshold_passes(self):
        config = ThresholdConfig(min_score=80.0)
        result = evaluate_gates(90.0, 0, 0, config)
        assert result.passed is True
        assert len(result.failures) == 0

    def test_score_at_threshold_passes(self):
        config = ThresholdConfig(min_score=80.0)
        result = evaluate_gates(80.0, 0, 0, config)
        assert result.passed is True

    def test_score_below_threshold_fails(self):
        config = ThresholdConfig(min_score=80.0)
        result = evaluate_gates(75.0, 0, 0, config)
        assert result.passed is False
        assert len(result.failures) == 1
        assert '75.0%' in result.failures[0]
        assert '80.0%' in result.failures[0]


class TestEvaluateGatesErrorThreshold:
    def test_errors_within_threshold_passes(self):
        config = ThresholdConfig(max_errors=5)
        result = evaluate_gates(100.0, 3, 0, config)
        assert result.passed is True

    def test_errors_at_threshold_passes(self):
        config = ThresholdConfig(max_errors=5)
        result = evaluate_gates(100.0, 5, 0, config)
        assert result.passed is True

    def test_errors_exceed_threshold_fails(self):
        config = ThresholdConfig(max_errors=5)
        result = evaluate_gates(100.0, 10, 0, config)
        assert result.passed is False
        assert '10' in result.failures[0]


class TestEvaluateGatesWarningThreshold:
    def test_warnings_within_threshold_passes(self):
        config = ThresholdConfig(max_warnings=10)
        result = evaluate_gates(100.0, 0, 5, config)
        assert result.passed is True

    def test_warnings_exceed_threshold_fails(self):
        config = ThresholdConfig(max_warnings=3)
        result = evaluate_gates(100.0, 0, 5, config)
        assert result.passed is False
        assert '5' in result.failures[0]


class TestEvaluateGatesMultiple:
    def test_all_gates_pass(self):
        config = ThresholdConfig(min_score=70, max_errors=5, max_warnings=10)
        result = evaluate_gates(80.0, 3, 5, config)
        assert result.passed is True

    def test_all_gates_fail(self):
        config = ThresholdConfig(min_score=90, max_errors=2, max_warnings=3)
        result = evaluate_gates(50.0, 10, 15, config)
        assert result.passed is False
        assert len(result.failures) == 3

    def test_score_fails_errors_pass(self):
        config = ThresholdConfig(min_score=90, max_errors=10)
        result = evaluate_gates(80.0, 5, 0, config)
        assert result.passed is False
        assert len(result.failures) == 1


class TestEvaluateGatesNoThresholds:
    def test_no_thresholds_always_passes(self):
        config = ThresholdConfig()
        result = evaluate_gates(0.0, 1000, 1000, config)
        assert result.passed is True
        assert len(result.failures) == 0


class TestEvaluateGatesEdgeCases:
    def test_zero_score_with_zero_threshold(self):
        config = ThresholdConfig(min_score=0.0)
        result = evaluate_gates(0.0, 0, 0, config)
        assert result.passed is True

    def test_negative_score_fails(self):
        config = ThresholdConfig(min_score=0.0)
        result = evaluate_gates(-1.0, 0, 0, config)
        assert result.passed is False
