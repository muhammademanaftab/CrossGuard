"""Tests for color support in CLI formatters."""

import pytest

from src.cli.formatters import (
    _grade_color,
    _score_color,
    _status_text,
    _risk_color,
    format_result,
    format_history,
    format_stats,
)


ANSI_ESC = '\x1b['


# --- Color helper tests (parametrized) ---


class TestColorHelpers:
    @pytest.mark.parametrize("grade", ['A', 'B', 'C', 'F', 'Z'])
    def test_grade_color_with_color(self, grade):
        result = _grade_color(grade, True)
        assert grade in result
        assert ANSI_ESC in result

    @pytest.mark.parametrize("grade", ['A', 'F'])
    def test_grade_color_no_color(self, grade):
        assert _grade_color(grade, False) == grade

    @pytest.mark.parametrize("score, expected_str", [
        (95.0, '95.0%'),
        (80.0, '80.0%'),
        (65.0, '65.0%'),
        (40.0, '40.0%'),
    ])
    def test_score_color_with_color(self, score, expected_str):
        result = _score_color(score, True)
        assert expected_str in result
        assert ANSI_ESC in result

    def test_score_color_no_color(self):
        assert _score_color(95.0, False) == '95.0%'

    @pytest.mark.parametrize("status", ['supported', 'unsupported', 'partial'])
    def test_status_text_with_color(self, status):
        result = _status_text(status, True)
        assert ANSI_ESC in result

    def test_status_text_no_color(self):
        assert _status_text('unsupported', False) == 'unsupported'

    @pytest.mark.parametrize("risk", ['low', 'medium', 'high', 'critical'])
    def test_risk_color_with_color(self, risk):
        result = _risk_color(risk, True)
        assert ANSI_ESC in result

    def test_risk_color_no_color(self):
        assert _risk_color('low', False) == 'low'


# --- Format function color integration ---


_SAMPLE_RESULT = {
    'success': True,
    'scores': {
        'grade': 'B',
        'simple_score': 78.5,
        'weighted_score': 80.0,
        'risk_level': 'medium',
    },
    'summary': {
        'total_features': 10,
        'html_features': 3,
        'css_features': 4,
        'js_features': 3,
        'critical_issues': 1,
    },
    'browsers': {
        'chrome': {
            'version': '120',
            'supported': 8,
            'partial': 1,
            'unsupported': 1,
            'compatibility_percentage': 80.0,
            'unsupported_features': ['css-grid'],
            'partial_features': ['flexbox'],
        }
    },
    'recommendations': ['Use autoprefixer'],
}


class TestFormatResultColor:
    @pytest.mark.parametrize("fmt", ['table', 'summary'])
    def test_format_with_color_has_ansi(self, fmt):
        out = format_result(_SAMPLE_RESULT, fmt, color=True)
        assert ANSI_ESC in out

    @pytest.mark.parametrize("fmt", ['table', 'summary'])
    def test_format_no_color_clean(self, fmt):
        out = format_result(_SAMPLE_RESULT, fmt, color=False)
        assert ANSI_ESC not in out

    def test_json_ignores_color(self):
        out = format_result(_SAMPLE_RESULT, 'json', color=True)
        assert ANSI_ESC not in out


class TestFormatCollectionColor:
    def test_history_color_toggle(self):
        analyses = [{'id': 1, 'analyzed_at': '2026-01-01', 'file_name': 'test.js',
                     'grade': 'A', 'overall_score': 95.0}]
        assert ANSI_ESC in format_history(analyses, color=True)
        assert ANSI_ESC not in format_history(analyses, color=False)

    def test_stats_color_toggle(self):
        stats = {'total_analyses': 5, 'average_score': 80, 'best_score': 95, 'worst_score': 60}
        assert ANSI_ESC in format_stats(stats, color=True)
        assert ANSI_ESC not in format_stats(stats, color=False)

