"""Tests for CLI helper functions (_count_issues, _format_ci_output)."""

import json
import xml.etree.ElementTree as ET
import pytest

from src.cli.main import _count_issues, _format_ci_output


class TestCountIssues:
    @pytest.mark.parametrize("report, expected", [
        ({}, (0, 0)),
        ({'browsers': {}}, (0, 0)),
        ({'browsers': {'chrome': {'unsupported': 3, 'partial': 2}}}, (3, 2)),
        ({'browsers': {
            'chrome': {'unsupported': 3, 'partial': 2},
            'firefox': {'unsupported': 1, 'partial': 4},
        }}, (4, 6)),
        ({'browsers': {
            'chrome': {'unsupported': 2, 'partial': 1},
            'invalid': 'not a dict',
        }}, (2, 1)),
        ({'browsers': {'chrome': {'supported': 10}}}, (0, 0)),
        ({'browsers': {'chrome': {'unsupported': 0, 'partial': 0}}}, (0, 0)),
    ])
    def test_count_issues(self, report, expected):
        assert _count_issues(report) == expected


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
        data = json.loads(_format_ci_output(_CI_REPORT, 'sarif'))
        assert data['version'] == '2.1.0'

    def test_junit_returns_valid_xml(self):
        root = ET.fromstring(_format_ci_output(_CI_REPORT, 'junit'))
        assert root.tag == 'testsuites'

    def test_checkstyle_returns_valid_xml(self):
        root = ET.fromstring(_format_ci_output(_CI_REPORT, 'checkstyle'))
        assert root.tag == 'checkstyle'

    def test_csv_returns_header(self):
        assert 'feature_id' in _format_ci_output(_CI_REPORT, 'csv')

    def test_unknown_format_returns_empty(self):
        assert _format_ci_output(_CI_REPORT, 'unknown') == ''
