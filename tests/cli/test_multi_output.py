"""Tests for multiple simultaneous output support."""

import json
import os
import xml.etree.ElementTree as ET
import pytest
from click.testing import CliRunner

from src.cli.main import _write_secondary_outputs


_SAMPLE_REPORT = {
    'success': True,
    'file_path': 'test.js',
    'browsers': {
        'chrome': {
            'version': '120',
            'supported': 8,
            'partial': 1,
            'unsupported': 1,
            'unsupported_features': ['css-grid'],
            'partial_features': ['flexbox'],
        },
    },
    'scores': {'grade': 'B', 'simple_score': 80.0},
}


class TestWriteSecondaryOutputs:
    def test_sarif_output(self, tmp_path):
        out = str(tmp_path / 'report.sarif')
        _write_secondary_outputs(_SAMPLE_REPORT, sarif=out)
        assert os.path.exists(out)
        data = json.loads(open(out).read())
        assert data['version'] == '2.1.0'

    def test_junit_output(self, tmp_path):
        out = str(tmp_path / 'report.xml')
        _write_secondary_outputs(_SAMPLE_REPORT, junit=out)
        assert os.path.exists(out)
        root = ET.parse(out).getroot()
        assert root.tag == 'testsuites'

    def test_json_output(self, tmp_path):
        out = str(tmp_path / 'report.json')
        _write_secondary_outputs(_SAMPLE_REPORT, json=out)
        assert os.path.exists(out)
        data = json.loads(open(out).read())
        assert 'generated_by' in data

    def test_checkstyle_output(self, tmp_path):
        out = str(tmp_path / 'report.xml')
        _write_secondary_outputs(_SAMPLE_REPORT, checkstyle=out)
        assert os.path.exists(out)
        root = ET.parse(out).getroot()
        assert root.tag == 'checkstyle'

    def test_csv_output(self, tmp_path):
        out = str(tmp_path / 'report.csv')
        _write_secondary_outputs(_SAMPLE_REPORT, csv=out)
        assert os.path.exists(out)
        content = open(out).read()
        assert 'feature_id' in content

    def test_none_paths_ignored(self, tmp_path):
        # Should not crash when all paths are None
        _write_secondary_outputs(_SAMPLE_REPORT, sarif=None, junit=None, json=None)

    def test_multiple_outputs(self, tmp_path):
        sarif_out = str(tmp_path / 'r.sarif')
        junit_out = str(tmp_path / 'r.xml')
        _write_secondary_outputs(
            _SAMPLE_REPORT,
            sarif=sarif_out,
            junit=junit_out,
        )
        assert os.path.exists(sarif_out)
        assert os.path.exists(junit_out)
