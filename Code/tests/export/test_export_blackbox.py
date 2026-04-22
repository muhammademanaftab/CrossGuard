"""Blackbox tests for all 6 export formats (JSON, PDF, SARIF, JUnit, Checkstyle, CSV)."""

import json
import os
import xml.etree.ElementTree as ET

import pytest

from src.export.json_exporter import export_json
from src.export.pdf_exporter import export_pdf
from src.export.sarif_exporter import export_sarif
from src.export.junit_exporter import export_junit
from src.export.checkstyle_exporter import export_checkstyle
from src.export.csv_exporter import export_csv


# --- Shared fixtures ---

_FULL_REPORT = {
    'success': True,
    'file_path': 'src/style.css',
    'summary': {
        'total_features': 5, 'html_features': 1,
        'css_features': 2, 'js_features': 2, 'critical_issues': 1,
    },
    'scores': {
        'grade': 'B', 'risk_level': 'medium',
        'simple_score': 78.5, 'weighted_score': 80.0,
    },
    'browsers': {
        'chrome': {
            'version': '120', 'supported': 8, 'partial': 1, 'unsupported': 2,
            'compatibility_percentage': 80.0,
            'unsupported_features': ['css-grid', 'css-subgrid'],
            'partial_features': ['flexbox-gap'],
        },
        'firefox': {
            'version': '121', 'supported': 10, 'partial': 0, 'unsupported': 1,
            'compatibility_percentage': 90.0,
            'unsupported_features': ['css-subgrid'],
            'partial_features': [],
        },
    },
    'recommendations': ['Consider polyfills for dialog element'],
}


# --- JSON exporter ---

@pytest.mark.blackbox
class TestJsonExporter:
    def test_returns_enriched_dict(self):
        result = export_json(_FULL_REPORT)
        assert isinstance(result, dict)
        assert result['generated_by'] == 'Cross Guard'
        assert 'generated_at' in result
        assert result['scores']['grade'] == 'B'

    def test_writes_valid_json_file(self, tmp_path):
        out = str(tmp_path / "report.json")
        result = export_json(_FULL_REPORT, output_path=out)
        assert result == out
        assert os.path.isfile(out)
        data = json.load(open(out))
        assert data['generated_by'] == 'Cross Guard'


# --- PDF exporter ---

@pytest.mark.blackbox
class TestPdfExporter:
    def test_creates_valid_pdf(self, tmp_path):
        out = str(tmp_path / "report.pdf")
        result = export_pdf(_FULL_REPORT, out)
        assert result == out
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 1000
        with open(out, 'rb') as f:
            assert f.read(5) == b'%PDF-'


# --- SARIF exporter ---

@pytest.mark.blackbox
class TestSarifExporter:
    def test_writes_valid_sarif_file(self, tmp_path):
        out = tmp_path / 'report.sarif'
        result = export_sarif(_FULL_REPORT, output_path=str(out))
        assert result == str(out)
        data = json.loads(out.read_text())
        assert data['version'] == '2.1.0'


# --- JUnit exporter ---

@pytest.mark.blackbox
class TestJunitExporter:
    def test_writes_valid_junit_file(self, tmp_path):
        out = tmp_path / 'report.xml'
        result = export_junit(_FULL_REPORT, output_path=str(out))
        assert result == str(out)
        root = ET.parse(str(out)).getroot()
        assert root.tag == 'testsuites'


# --- Checkstyle exporter ---

@pytest.mark.blackbox
class TestCheckstyleExporter:
    def test_writes_valid_checkstyle_file(self, tmp_path):
        out = tmp_path / 'report.xml'
        result = export_checkstyle(_FULL_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()


# --- CSV exporter ---

@pytest.mark.blackbox
class TestCsvExporter:
    def test_writes_valid_csv_file(self, tmp_path):
        out = tmp_path / 'report.csv'
        result = export_csv(_FULL_REPORT, output_path=str(out))
        assert result == str(out)
        assert 'feature_id' in out.read_text()
