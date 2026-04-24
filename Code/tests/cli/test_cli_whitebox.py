"""Whitebox tests for CLI internals: gate evaluation and CI config generators.

Tests internal functions that are not part of the public CLI interface.
"""

import pytest

from src.cli.gates import ThresholdConfig, evaluate_gates
from src.cli.generators import generate_ci_config


# --- Quality gate evaluation ---


@pytest.mark.whitebox
class TestEvaluateGates:
    @pytest.mark.parametrize("score, threshold, should_pass", [
        (90.0, 80.0, True),
    ])
    def test_score_gate(self, score, threshold, should_pass):
        config = ThresholdConfig(min_score=threshold)
        result = evaluate_gates(score, 0, 0, config)
        assert result.passed is should_pass


# --- Generators ---


@pytest.mark.whitebox
class TestGenerators:
    def test_github_ci_config(self):
        output = generate_ci_config('github')
        assert 'crossguard analyze' in output
        assert 'sarif' in output
