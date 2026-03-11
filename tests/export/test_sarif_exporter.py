"""Tests for SARIF 2.1.0 exporter."""

import json
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

class TestSarifSchema:
    def test_top_level_structure(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        assert sarif['version'] == '2.1.0'
        assert '$schema' in sarif
        assert len(sarif['runs']) == 1

    def test_tool_driver_and_rules(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        driver = sarif['runs'][0]['tool']['driver']
        assert driver['name'] == 'CrossGuard'
        rule_ids = {r['id'] for r in driver['rules']}
        assert 'css-grid' in rule_ids
        assert 'flexbox-gap' in rule_ids


class TestSarifResults:
    def test_error_and_warning_levels(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        results = sarif['runs'][0]['results']
        errors = [r for r in results if r['level'] == 'error']
        warnings = [r for r in results if r['level'] == 'warning']
        assert len(errors) >= 1
        assert len(warnings) >= 1

    def test_result_has_location_and_rule_id(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        for result in sarif['runs'][0]['results']:
            assert 'ruleId' in result
            assert 'locations' in result
            assert 'physicalLocation' in result['locations'][0]


class TestSarifProperties:
    def test_score_in_properties(self):
        sarif = export_sarif(_SAMPLE_REPORT)
        assert sarif['runs'][0]['properties']['score'] == 78.5

class TestSarifFileOutput:
    def test_write_to_file(self, tmp_path):
        out = tmp_path / 'report.sarif'
        result = export_sarif(_SAMPLE_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()
        data = json.loads(out.read_text())
        assert data['version'] == '2.1.0'

    @pytest.mark.parametrize("bad_input", [{}, None])
    def test_invalid_report_raises(self, bad_input):
        with pytest.raises(ValueError):
            export_sarif(bad_input)


