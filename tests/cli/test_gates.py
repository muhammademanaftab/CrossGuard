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
    @pytest.mark.parametrize("score, threshold, should_pass", [
        (90.0, 80.0, True),    # above
        (80.0, 80.0, True),    # at
        (75.0, 80.0, False),   # below
        (0.0, 0.0, True),      # zero edge
        (-1.0, 0.0, False),    # negative edge
    ])
    def test_score_gate(self, score, threshold, should_pass):
        config = ThresholdConfig(min_score=threshold)
        result = evaluate_gates(score, 0, 0, config)
        assert result.passed is should_pass
        if not should_pass:
            assert len(result.failures) == 1


class TestEvaluateGatesErrorThreshold:
    @pytest.mark.parametrize("errors, threshold, should_pass", [
        (3, 5, True),    # within
        (5, 5, True),    # at
        (10, 5, False),  # exceed
    ])
    def test_error_gate(self, errors, threshold, should_pass):
        config = ThresholdConfig(max_errors=threshold)
        result = evaluate_gates(100.0, errors, 0, config)
        assert result.passed is should_pass


class TestEvaluateGatesWarningThreshold:
    @pytest.mark.parametrize("warnings, threshold, should_pass", [
        (5, 10, True),    # within
        (5, 3, False),    # exceed
    ])
    def test_warning_gate(self, warnings, threshold, should_pass):
        config = ThresholdConfig(max_warnings=threshold)
        result = evaluate_gates(100.0, 0, warnings, config)
        assert result.passed is should_pass


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

    def test_no_thresholds_always_passes(self):
        config = ThresholdConfig()
        result = evaluate_gates(0.0, 1000, 1000, config)
        assert result.passed is True
        assert len(result.failures) == 0
