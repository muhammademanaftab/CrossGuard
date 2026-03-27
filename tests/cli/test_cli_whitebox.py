"""Whitebox tests for CLI internals: formatters, context, helpers, gates, generators.

Tests internal functions and classes that are not part of the public CLI
interface.
"""

import json
import os
import xml.etree.ElementTree as ET
import pytest
from unittest.mock import patch

from src.cli.context import CliContext
from src.cli.gates import ThresholdConfig, evaluate_gates
from src.cli.generators import generate_ci_config, generate_hooks_config
from src.cli.formatters import (
    _grade_color, _score_color, _status_text,
    format_result, format_history, format_stats,
)
from src.cli.main import _count_issues, _format_ci_output


ANSI_ESC = '\x1b['


# --- Quality gate evaluation ---


@pytest.mark.whitebox
class TestEvaluateGates:
    @pytest.mark.parametrize("score, threshold, should_pass", [
        (90.0, 80.0, True),
        (75.0, 80.0, False),
    ])
    def test_score_gate(self, score, threshold, should_pass):
        config = ThresholdConfig(min_score=threshold)
        result = evaluate_gates(score, 0, 0, config)
        assert result.passed is should_pass

    def test_no_thresholds_always_passes(self):
        config = ThresholdConfig()
        result = evaluate_gates(0.0, 1000, 1000, config)
        assert result.passed is True


# --- CLI context ---


@pytest.mark.whitebox
class TestCliContext:
    def test_defaults(self):
        ctx = CliContext()
        assert ctx.verbosity == 1
        assert ctx.color is True
        assert ctx.timing is False

    def test_no_color_flag(self):
        assert CliContext.detect_color(no_color_flag=True) is False


# --- Helpers ---


@pytest.mark.whitebox
class TestCountIssues:
    def test_count_issues(self):
        report = {'browsers': {
            'chrome': {'unsupported': 3, 'partial': 2},
            'firefox': {'unsupported': 1, 'partial': 4},
        }}
        assert _count_issues(report) == (4, 6)


@pytest.mark.whitebox
class TestFormatCiOutput:
    def test_sarif_returns_valid_json(self):
        data = json.loads(_format_ci_output(_ci_report(), 'sarif'))
        assert data['version'] == '2.1.0'



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

    def test_pre_commit_hook(self):
        output = generate_hooks_config('pre-commit')
        assert 'crossguard' in output.lower()


# --- Shared test data ---


def _ci_report():
    return {
        'success': True,
        'file_path': 'test.js',
        'browsers': {
            'chrome': {
                'version': '120', 'supported': 5, 'partial': 1,
                'unsupported': 1, 'unsupported_features': ['css-grid'],
                'partial_features': ['flexbox'],
            },
        },
        'scores': {'grade': 'B', 'simple_score': 80.0},
    }


def _format_result_sample():
    return {
        'success': True,
        'scores': {
            'grade': 'B', 'simple_score': 78.5,
            'weighted_score': 80.0, 'risk_level': 'medium',
        },
        'summary': {
            'total_features': 10, 'html_features': 3,
            'css_features': 4, 'js_features': 3, 'critical_issues': 1,
        },
        'browsers': {
            'chrome': {
                'version': '120', 'supported': 8, 'partial': 1,
                'unsupported': 1, 'compatibility_percentage': 80.0,
                'unsupported_features': ['css-grid'],
                'partial_features': ['flexbox'],
            }
        },
        'recommendations': ['Use autoprefixer'],
    }
