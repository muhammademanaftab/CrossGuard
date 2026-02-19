"""Tests for SARIF 2.1.0 exporter."""

import json
import os
import pytest

from src.export.sarif_exporter import export_sarif


_SAMPLE_REPORT = {
    'success': True,
    'scores': {'grade': 'B', 'simple_score': 78.5},
    'browsers': {
        'chrome': {
            'version': '120',
            'supported': 8,
            'partial': 1,
            'unsupported': 1,
            'compatibility_percentage': 80.0,
            'unsupported_features': ['css-grid'],
            'partial_features': ['flexbox-gap'],
        },
        'firefox': {
            'version': '121',
            'supported': 9,
            'partial': 0,
            'unsupported': 1,
            'compatibility_percentage': 90.0,
            'unsupported_features': ['css-grid'],
            'partial_features': [],
        },
    },
    'file_path': 'src/style.css',
}

_PROJECT_REPORT = {
    'success': True,
    'overall_score': 75.0,
    'overall_grade': 'C',
    'project_path': 'src/',
    'file_results': [{'file_path': 'src/a.css'}],
    'browsers': {
        'chrome': {
            'version': '120',
            'supported': 5,
            'partial': 2,
            'unsupported': 3,
            'unsupported_features': ['css-grid', 'css-subgrid'],
            'partial_features': ['flexbox-gap', 'backdrop-filter'],
        },
    },
}


class TestSarifSchema:
    def test_top_level_structure(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        assert sarif['version'] == '2.1.0'
        assert '$schema' in sarif
        assert 'runs' in sarif
        assert len(sarif['runs']) == 1

    def test_tool_driver(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        driver = sarif['runs'][0]['tool']['driver']
        assert driver['name'] == 'CrossGuard'
        assert 'rules' in driver

    def test_rules_populated(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        rules = sarif['runs'][0]['tool']['driver']['rules']
        rule_ids = {r['id'] for r in rules}
        assert 'css-grid' in rule_ids
        assert 'flexbox-gap' in rule_ids


class TestSarifResults:
    def test_unsupported_is_error(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        results = sarif['runs'][0]['results']
        errors = [r for r in results if r['level'] == 'error']
        assert len(errors) >= 1

    def test_partial_is_warning(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        results = sarif['runs'][0]['results']
        warnings = [r for r in results if r['level'] == 'warning']
        assert len(warnings) >= 1

    def test_result_has_location(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        for result in sarif['runs'][0]['results']:
            assert 'locations' in result
            loc = result['locations'][0]
            assert 'physicalLocation' in loc

    def test_result_has_rule_id(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        for result in sarif['runs'][0]['results']:
            assert 'ruleId' in result


class TestSarifProperties:
    def test_score_in_properties(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        props = sarif['runs'][0]['properties']
        assert props['score'] == 78.5

    def test_project_score_in_properties(self):
        sarif = export_sarif(_PROJECT_REPORT)
        props = sarif['runs'][0]['properties']
        assert props['score'] == 75.0
        assert props['grade'] == 'C'


class TestSarifFileOutput:
    def test_write_to_file(self, tmp_path):
        out = tmp_path / 'report.sarif'
        result = export_sarif(_SAMPLE_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()
        data = json.loads(out.read_text())
        assert data['version'] == '2.1.0'

    def test_empty_report_raises(self):
        with pytest.raises(ValueError):
            export_sarif({})

    def test_none_report_raises(self):
        with pytest.raises(ValueError):
            export_sarif(None)


class TestSarifProjectResults:
    def test_project_results_extracted(self):
        sarif = export_sarif(_PROJECT_REPORT)
        results = sarif['runs'][0]['results']
        assert len(results) > 0

    def test_project_unsupported_features(self):
        sarif = export_sarif(_PROJECT_REPORT)
        results = sarif['runs'][0]['results']
        errors = [r for r in results if r['level'] == 'error']
        assert len(errors) == 2  # css-grid + css-subgrid

    def test_project_partial_features(self):
        sarif = export_sarif(_PROJECT_REPORT)
        results = sarif['runs'][0]['results']
        warnings = [r for r in results if r['level'] == 'warning']
        assert len(warnings) == 2  # flexbox-gap + backdrop-filter
