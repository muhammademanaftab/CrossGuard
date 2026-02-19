"""Tests for CLI helper functions (_count_issues, _format_ci_output)."""

import json
import xml.etree.ElementTree as ET
import pytest

from src.cli.main import _count_issues, _format_ci_output


class TestCountIssues:
    def test_empty_report(self):
        assert _count_issues({}) == (0, 0)

    def test_empty_browsers(self):
        assert _count_issues({'browsers': {}}) == (0, 0)

    def test_single_browser(self):
        report = {
            'browsers': {
                'chrome': {'unsupported': 3, 'partial': 2},
            }
        }
        assert _count_issues(report) == (3, 2)

    def test_multiple_browsers_aggregated(self):
        report = {
            'browsers': {
                'chrome': {'unsupported': 3, 'partial': 2},
                'firefox': {'unsupported': 1, 'partial': 4},
            }
        }
        assert _count_issues(report) == (4, 6)

    def test_non_dict_browser_value_skipped(self):
        report = {
            'browsers': {
                'chrome': {'unsupported': 2, 'partial': 1},
                'invalid': 'not a dict',
            }
        }
        assert _count_issues(report) == (2, 1)

    def test_missing_keys_default_to_zero(self):
        report = {
            'browsers': {
                'chrome': {'supported': 10},
            }
        }
        assert _count_issues(report) == (0, 0)

    def test_zero_issues(self):
        report = {
            'browsers': {
                'chrome': {'unsupported': 0, 'partial': 0},
            }
        }
        assert _count_issues(report) == (0, 0)


_CI_REPORT = {
    'success': True,
    'file_path': 'test.js',
    'browsers': {
        'chrome': {
            'version': '120',
            'supported': 5,
            'partial': 1,
            'unsupported': 1,
            'unsupported_features': ['css-grid'],
            'partial_features': ['flexbox'],
        },
    },
    'scores': {'grade': 'B', 'simple_score': 80.0},
}


class TestFormatCiOutput:
    def test_sarif_returns_valid_json(self):
        result = _format_ci_output(_CI_REPORT, 'sarif')
        data = json.loads(result)
        assert data['version'] == '2.1.0'

    def test_junit_returns_valid_xml(self):
        result = _format_ci_output(_CI_REPORT, 'junit')
        root = ET.fromstring(result)
        assert root.tag == 'testsuites'

    def test_checkstyle_returns_valid_xml(self):
        result = _format_ci_output(_CI_REPORT, 'checkstyle')
        root = ET.fromstring(result)
        assert root.tag == 'checkstyle'

    def test_csv_returns_header(self):
        result = _format_ci_output(_CI_REPORT, 'csv')
        assert 'feature_id' in result

    def test_unknown_format_returns_empty(self):
        result = _format_ci_output(_CI_REPORT, 'unknown')
        assert result == ''
