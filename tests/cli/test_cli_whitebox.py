"""Whitebox tests for CLI internals: formatters, context, helpers, gates, generators.

Tests internal functions and classes that are not part of the public CLI
interface. These verify formatting logic, quality gate evaluation,
CI config generation, and context/verbosity resolution.
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
from src.cli.main import _count_issues, _format_ci_output, _write_secondary_outputs


ANSI_ESC = '\x1b['


# --- Quality gate evaluation ---


@pytest.mark.whitebox
class TestEvaluateGates:
    @pytest.mark.parametrize("score, threshold, should_pass", [
        (90.0, 80.0, True),
        (80.0, 80.0, True),
        (75.0, 80.0, False),
    ])
    def test_score_gate(self, score, threshold, should_pass):
        config = ThresholdConfig(min_score=threshold)
        result = evaluate_gates(score, 0, 0, config)
        assert result.passed is should_pass

    @pytest.mark.parametrize("count, threshold, should_pass", [
        (3, 5, True),
        (10, 5, False),
    ])
    def test_error_gate(self, count, threshold, should_pass):
        config = ThresholdConfig(max_errors=threshold)
        result = evaluate_gates(100.0, count, 0, config)
        assert result.passed is should_pass

    def test_warning_gate(self):
        config = ThresholdConfig(max_warnings=3)
        assert evaluate_gates(100.0, 0, 5, config).passed is False
        assert evaluate_gates(100.0, 0, 2, config).passed is True

    def test_all_gates_fail_reports_all_failures(self):
        config = ThresholdConfig(min_score=90, max_errors=2, max_warnings=3)
        result = evaluate_gates(50.0, 10, 15, config)
        assert result.passed is False
        assert len(result.failures) == 3

    def test_no_thresholds_always_passes(self):
        config = ThresholdConfig()
        result = evaluate_gates(0.0, 1000, 1000, config)
        assert result.passed is True
        assert len(result.failures) == 0


# --- CLI context ---


@pytest.mark.whitebox
class TestCliContext:
    def test_defaults(self):
        ctx = CliContext()
        assert ctx.verbosity == 1
        assert ctx.color is True
        assert ctx.timing is False

    @pytest.mark.parametrize("kwargs, expected", [
        ({}, 1),
        ({'quiet': True}, 0),
        ({'debug': True}, 3),
    ])
    def test_verbosity_levels(self, kwargs, expected):
        assert CliContext.resolve_verbosity(**kwargs) == expected

    @pytest.mark.parametrize("kwargs, env_vars, expected", [
        ({'no_color_flag': True}, {}, False),
        ({}, {'NO_COLOR': '1'}, False),
    ])
    def test_color_detection(self, kwargs, env_vars, expected):
        with patch.dict(os.environ, env_vars, clear=False):
            assert CliContext.detect_color(**kwargs) is expected


# --- Helpers ---


@pytest.mark.whitebox
class TestCountIssues:
    @pytest.mark.parametrize("report, expected", [
        ({}, (0, 0)),
        ({'browsers': {'chrome': {'unsupported': 3, 'partial': 2}}}, (3, 2)),
        ({'browsers': {
            'chrome': {'unsupported': 3, 'partial': 2},
            'firefox': {'unsupported': 1, 'partial': 4},
        }}, (4, 6)),
    ])
    def test_count_issues(self, report, expected):
        assert _count_issues(report) == expected


@pytest.mark.whitebox
class TestFormatCiOutput:
    def test_sarif_returns_valid_json(self):
        data = json.loads(_format_ci_output(_ci_report(), 'sarif'))
        assert data['version'] == '2.1.0'

    def test_junit_returns_valid_xml(self):
        root = ET.fromstring(_format_ci_output(_ci_report(), 'junit'))
        assert root.tag == 'testsuites'

    def test_csv_returns_header(self):
        assert 'feature_id' in _format_ci_output(_ci_report(), 'csv')

    def test_unknown_format_returns_empty(self):
        assert _format_ci_output(_ci_report(), 'unknown') == ''


# --- Multi-output writer ---


@pytest.mark.whitebox
class TestWriteSecondaryOutputs:
    def test_sarif_output(self, tmp_path):
        out = str(tmp_path / 'report.sarif')
        _write_secondary_outputs(_sample_report(), sarif=out)
        assert os.path.exists(out)
        data = json.loads(open(out).read())
        assert data['version'] == '2.1.0'

    def test_none_paths_ignored(self):
        _write_secondary_outputs(_sample_report(), sarif=None, junit=None, json=None)


# --- Formatters ---


@pytest.mark.whitebox
class TestFormatters:
    def test_grade_color_toggle(self):
        assert ANSI_ESC in _grade_color('A', True)
        assert _grade_color('A', False) == 'A'

    def test_score_color_toggle(self):
        assert ANSI_ESC in _score_color(95.0, True)
        assert _score_color(95.0, False) == '95.0%'

    def test_status_text_toggle(self):
        assert ANSI_ESC in _status_text('unsupported', True)
        assert _status_text('unsupported', False) == 'unsupported'

    def test_format_result_color_toggle(self):
        result_data = _format_result_sample()
        assert ANSI_ESC in format_result(result_data, 'table', color=True)
        assert ANSI_ESC not in format_result(result_data, 'table', color=False)

    def test_json_format_ignores_color(self):
        out = format_result(_format_result_sample(), 'json', color=True)
        assert ANSI_ESC not in out

    def test_history_color_toggle(self):
        analyses = [{'id': 1, 'analyzed_at': '2026-01-01', 'file_name': 'test.js',
                     'grade': 'A', 'overall_score': 95.0}]
        assert ANSI_ESC in format_history(analyses, color=True)
        assert ANSI_ESC not in format_history(analyses, color=False)

    def test_stats_color_toggle(self):
        stats = {'total_analyses': 5, 'average_score': 80, 'best_score': 95, 'worst_score': 60}
        assert ANSI_ESC in format_stats(stats, color=True)
        assert ANSI_ESC not in format_stats(stats, color=False)


# --- Generators ---


@pytest.mark.whitebox
class TestGenerators:
    def test_github_ci_config(self):
        output = generate_ci_config('github')
        assert 'crossguard analyze' in output
        assert 'sarif' in output

    def test_gitlab_ci_config(self):
        output = generate_ci_config('gitlab')
        assert 'crossguard analyze' in output
        assert 'junit' in output

    def test_unsupported_provider_raises(self):
        with pytest.raises(ValueError, match="Unsupported CI provider"):
            generate_ci_config('jenkins')

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


def _sample_report():
    return {
        'success': True,
        'file_path': 'test.js',
        'browsers': {
            'chrome': {
                'version': '120', 'supported': 8, 'partial': 1,
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
