"""Blackbox tests for all 6 export formats (JSON, PDF, SARIF, JUnit, Checkstyle, CSV)."""

import csv
import io
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


# --- Cross-format: invalid input ---

@pytest.mark.blackbox
@pytest.mark.parametrize("export_fn", [
    export_json, export_sarif, export_junit, export_checkstyle, export_csv,
])
@pytest.mark.parametrize("bad_input", [{}, None])
def test_invalid_report_raises_value_error(export_fn, bad_input):
    with pytest.raises(ValueError):
        export_fn(bad_input)


@pytest.mark.blackbox
@pytest.mark.parametrize("bad_input", [{}, None])
def test_pdf_invalid_report_raises(bad_input, tmp_path):
    with pytest.raises(ValueError, match="No analysis report"):
        export_pdf(bad_input, str(tmp_path / "report.pdf"))


# --- JSON exporter ---

@pytest.mark.blackbox
class TestJsonExporter:
    def test_returns_enriched_dict(self):
        result = export_json(_FULL_REPORT)
        assert isinstance(result, dict)
        assert result['generated_by'] == 'Cross Guard'
        assert 'generated_at' in result
        assert result['success'] is True
        assert result['scores']['grade'] == 'B'

    def test_writes_valid_json_file(self, tmp_path):
        out = str(tmp_path / "report.json")
        result = export_json(_FULL_REPORT, output_path=out)
        assert result == out
        assert os.path.isfile(out)
        data = json.load(open(out))
        assert data['generated_by'] == 'Cross Guard'
        # Verify pretty-printed (indented)
        text = open(out).read()
        assert '\n' in text and '  ' in text


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

    @pytest.mark.parametrize("label,report_data", [
        ("minimal", {'success': True, 'summary': {}, 'scores': {}, 'browsers': {}, 'recommendations': []}),
        ("no_browsers", {'success': True, 'summary': {'total_features': 3}, 'scores': {'grade': 'A', 'simple_score': 100.0, 'weighted_score': 100.0}, 'browsers': {}, 'recommendations': []}),
        ("many_recs", {'success': True, 'summary': {}, 'scores': {}, 'browsers': {}, 'recommendations': [f"Rec #{i}" for i in range(20)]}),
    ])
    def test_edge_case_reports_produce_valid_pdf(self, label, report_data, tmp_path):
        out = str(tmp_path / f"{label}.pdf")
        export_pdf(report_data, out)
        assert os.path.isfile(out)


# --- SARIF exporter ---

@pytest.mark.blackbox
class TestSarifExporter:
    def test_top_level_structure_and_schema(self):
        sarif = export_sarif(_FULL_REPORT)
        assert sarif['version'] == '2.1.0'
        assert '$schema' in sarif
        assert len(sarif['runs']) == 1

    def test_tool_driver_contains_rules(self):
        sarif = export_sarif(_FULL_REPORT)
        driver = sarif['runs'][0]['tool']['driver']
        assert driver['name'] == 'CrossGuard'
        rule_ids = {r['id'] for r in driver['rules']}
        assert 'css-grid' in rule_ids
        assert 'flexbox-gap' in rule_ids

    def test_results_have_correct_levels_and_locations(self):
        sarif = export_sarif(_FULL_REPORT)
        results = sarif['runs'][0]['results']
        levels = {r['level'] for r in results}
        assert 'error' in levels
        assert 'warning' in levels
        for result in results:
            assert 'ruleId' in result
            assert 'physicalLocation' in result['locations'][0]

    def test_writes_valid_sarif_file(self, tmp_path):
        out = tmp_path / 'report.sarif'
        result = export_sarif(_FULL_REPORT, output_path=str(out))
        assert result == str(out)
        data = json.loads(out.read_text())
        assert data['version'] == '2.1.0'


# --- JUnit exporter ---

@pytest.mark.blackbox
class TestJunitExporter:
    def test_xml_structure_with_browser_suites(self):
        xml_str = export_junit(_FULL_REPORT)
        root = ET.fromstring(xml_str)
        assert root.tag == 'testsuites'
        assert root.attrib['name'] == 'CrossGuard'
        suites = root.findall('testsuite')
        assert len(suites) == 2
        names = {s.attrib['name'] for s in suites}
        assert 'chrome 120' in names
        assert 'firefox 121' in names

    def test_failure_counts_and_test_totals(self):
        xml_str = export_junit(_FULL_REPORT)
        root = ET.fromstring(xml_str)
        chrome = [s for s in root.findall('testsuite') if 'chrome' in s.attrib['name']][0]
        assert len(chrome.findall('.//failure[@type="unsupported"]')) == 2
        assert len(chrome.findall('.//failure[@type="partial"]')) == 1
        assert chrome.attrib['failures'] == '2'
        # tests count matches actual testcase elements
        assert int(chrome.attrib['tests']) == len(chrome.findall('testcase'))

    def test_writes_valid_junit_file(self, tmp_path):
        out = tmp_path / 'report.xml'
        result = export_junit(_FULL_REPORT, output_path=str(out))
        assert result == str(out)
        root = ET.parse(str(out)).getroot()
        assert root.tag == 'testsuites'

    def test_no_issues_zero_failures(self):
        report = {
            'browsers': {
                'chrome': {
                    'version': '120', 'supported': 10, 'partial': 0, 'unsupported': 0,
                    'unsupported_features': [], 'partial_features': [],
                },
            },
        }
        xml_str = export_junit(report)
        root = ET.fromstring(xml_str)
        assert root.find('testsuite').attrib['failures'] == '0'

    def test_empty_browsers_no_suites(self):
        xml_str = export_junit({'browsers': {}})
        root = ET.fromstring(xml_str)
        assert len(root.findall('testsuite')) == 0


# --- Checkstyle exporter ---

@pytest.mark.blackbox
class TestCheckstyleExporter:
    def test_xml_structure_and_severity_levels(self):
        xml_str = export_checkstyle(_FULL_REPORT)
        root = ET.fromstring(xml_str)
        assert root.tag == 'checkstyle'
        files = root.findall('file')
        assert len(files) == 1
        assert files[0].attrib['name'] == 'src/style.css'
        errors = root.findall('.//error[@severity="error"]')
        warnings = root.findall('.//error[@severity="warning"]')
        assert len(errors) >= 2
        assert len(warnings) >= 1
        assert 'crossguard' in errors[0].attrib['source']

    def test_writes_valid_checkstyle_file(self, tmp_path):
        out = tmp_path / 'report.xml'
        result = export_checkstyle(_FULL_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()

    def test_no_issues_no_errors(self):
        report = {
            'file_path': 'app.js',
            'browsers': {
                'chrome': {
                    'version': '120', 'supported': 10, 'partial': 0, 'unsupported': 0,
                    'unsupported_features': [], 'partial_features': [],
                },
            },
        }
        xml_str = export_checkstyle(report)
        root = ET.fromstring(xml_str)
        assert len(root.findall('.//error')) == 0


# --- CSV exporter ---

@pytest.mark.blackbox
class TestCsvExporter:
    def test_header_row_count_and_statuses(self):
        csv_text = export_csv(_FULL_REPORT)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        assert rows[0] == ['feature_id', 'feature_name', 'browser', 'version', 'status', 'file_path']
        # 2 unsupported + 1 partial (chrome) + 1 unsupported (firefox) = 4 data rows
        assert len(rows) == 5
        for row in rows[1:]:
            assert row[4] in ('unsupported', 'partial')
            assert row[5] == 'src/style.css'

    def test_writes_valid_csv_file(self, tmp_path):
        out = tmp_path / 'report.csv'
        result = export_csv(_FULL_REPORT, output_path=str(out))
        assert result == str(out)
        assert 'feature_id' in out.read_text()

    def test_no_issues_header_only(self):
        report = {
            'file_path': 'app.js',
            'browsers': {
                'chrome': {
                    'version': '120',
                    'unsupported_features': [],
                    'partial_features': [],
                },
            },
        }
        csv_text = export_csv(report)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) == 1  # header only
