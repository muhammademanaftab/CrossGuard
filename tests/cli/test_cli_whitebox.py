"""Whitebox tests for CLI internals: formatters, context, helpers, gates, generators.

Tests internal functions and classes that are not part of the public CLI
interface.
"""

import pytest

from src.cli.context import CliContext
from src.cli.gates import ThresholdConfig, evaluate_gates
from src.cli.generators import generate_ci_config
from src.cli.formatters import _grade_color


ANSI_ESC = '\x1b['


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


# --- CLI context ---


@pytest.mark.whitebox
class TestCliContext:
    def test_defaults(self):
        ctx = CliContext()
        assert ctx.verbosity == 1
        assert ctx.color is True
        assert ctx.timing is False


# --- Formatters ---


@pytest.mark.whitebox
class TestFormatters:
    def test_grade_color_toggle(self):
        assert ANSI_ESC in _grade_color('A', True)
        assert _grade_color('A', False) == 'A'


# --- Generators ---


@pytest.mark.whitebox
class TestGenerators:
    def test_github_ci_config(self):
        output = generate_ci_config('github')
        assert 'crossguard analyze' in output
        assert 'sarif' in output
