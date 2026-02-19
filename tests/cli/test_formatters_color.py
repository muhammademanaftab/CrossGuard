"""Tests for color support in CLI formatters."""

import pytest

from src.cli.formatters import (
    _grade_color,
    _score_color,
    _status_text,
    _risk_color,
    format_result,
    format_summary,
    format_table,
    format_history,
    format_stats,
    format_project_result,
)


# ── Color helper tests ────────────────────────────────────────────────


class TestGradeColor:
    def test_no_color_returns_plain(self):
        assert _grade_color('A', False) == 'A'

    def test_color_a_green(self):
        result = _grade_color('A', True)
        assert 'A' in result
        # ANSI escape codes present
        assert '\x1b[' in result

    def test_color_f_red(self):
        result = _grade_color('F', True)
        assert '\x1b[' in result

    def test_unknown_grade_no_crash(self):
        result = _grade_color('Z', True)
        assert 'Z' in result


class TestScoreColor:
    def test_no_color(self):
        assert _score_color(95.0, False) == '95.0%'

    def test_high_score_green(self):
        result = _score_color(95.0, True)
        assert '95.0%' in result
        assert '\x1b[' in result

    def test_medium_score_cyan(self):
        result = _score_color(80.0, True)
        assert '80.0%' in result

    def test_low_score_yellow(self):
        result = _score_color(65.0, True)
        assert '65.0%' in result

    def test_very_low_score_red(self):
        result = _score_color(40.0, True)
        assert '40.0%' in result


class TestStatusText:
    def test_no_color(self):
        assert _status_text('unsupported', False) == 'unsupported'

    def test_supported_green(self):
        result = _status_text('supported', True)
        assert '\x1b[' in result

    def test_unsupported_red(self):
        result = _status_text('unsupported', True)
        assert '\x1b[' in result


class TestRiskColor:
    def test_no_color(self):
        assert _risk_color('low', False) == 'low'

    def test_low_green(self):
        result = _risk_color('low', True)
        assert '\x1b[' in result

    def test_critical_bold(self):
        result = _risk_color('critical', True)
        assert '\x1b[' in result


# ── Format function color integration ─────────────────────────────────


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
    def test_table_no_color(self):
        out = format_result(_SAMPLE_RESULT, 'table', color=False)
        assert 'Grade: B' in out
        assert '\x1b[' not in out

    def test_table_with_color(self):
        out = format_result(_SAMPLE_RESULT, 'table', color=True)
        assert '\x1b[' in out

    def test_summary_no_color(self):
        out = format_result(_SAMPLE_RESULT, 'summary', color=False)
        assert '\x1b[' not in out

    def test_summary_with_color(self):
        out = format_result(_SAMPLE_RESULT, 'summary', color=True)
        assert '\x1b[' in out

    def test_json_ignores_color(self):
        out = format_result(_SAMPLE_RESULT, 'json', color=True)
        assert '\x1b[' not in out  # JSON is never colored


class TestFormatHistoryColor:
    def test_no_color(self):
        analyses = [{'id': 1, 'analyzed_at': '2026-01-01', 'file_name': 'test.js',
                     'grade': 'A', 'overall_score': 95.0}]
        out = format_history(analyses, color=False)
        assert '\x1b[' not in out

    def test_with_color(self):
        analyses = [{'id': 1, 'analyzed_at': '2026-01-01', 'file_name': 'test.js',
                     'grade': 'A', 'overall_score': 95.0}]
        out = format_history(analyses, color=True)
        assert '\x1b[' in out


class TestFormatStatsColor:
    def test_no_color(self):
        stats = {'total_analyses': 5, 'average_score': 80, 'best_score': 95, 'worst_score': 60}
        out = format_stats(stats, color=False)
        assert '\x1b[' not in out

    def test_with_color(self):
        stats = {'total_analyses': 5, 'average_score': 80, 'best_score': 95, 'worst_score': 60}
        out = format_stats(stats, color=True)
        assert '\x1b[' in out


class TestFormatProjectColor:
    def test_no_color(self):
        result = {
            'success': True,
            'project_name': 'test',
            'overall_score': 85.0,
            'overall_grade': 'B',
            'total_files': 3,
            'html_files': 1, 'css_files': 1, 'js_files': 1,
            'total_features': 20, 'unique_features': 15,
            'unsupported_count': 2, 'partial_count': 3,
        }
        out = format_project_result(result, color=False)
        assert '\x1b[' not in out
