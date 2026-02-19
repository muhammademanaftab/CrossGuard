"""Tests for Checkstyle XML exporter."""

import xml.etree.ElementTree as ET
import pytest

from src.export.checkstyle_exporter import export_checkstyle


_SAMPLE_REPORT = {
    'success': True,
    'file_path': 'src/style.css',
    'browsers': {
        'chrome': {
            'version': '120',
            'supported': 8,
            'partial': 1,
            'unsupported': 2,
            'unsupported_features': ['css-grid', 'css-subgrid'],
            'partial_features': ['flexbox-gap'],
        },
    },
}


class TestCheckstyleStructure:
    def test_valid_xml(self):
        xml_str = export_checkstyle(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        assert root.tag == 'checkstyle'

    def test_file_element(self):
        xml_str = export_checkstyle(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        files = root.findall('file')
        assert len(files) == 1
        assert files[0].attrib['name'] == 'src/style.css'

    def test_error_elements(self):
        xml_str = export_checkstyle(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        errors = root.findall('.//error[@severity="error"]')
        assert len(errors) == 2

    def test_warning_elements(self):
        xml_str = export_checkstyle(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        warnings = root.findall('.//error[@severity="warning"]')
        assert len(warnings) == 1

    def test_error_source_attribute(self):
        xml_str = export_checkstyle(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        error = root.find('.//error[@severity="error"]')
        assert 'source' in error.attrib
        assert 'crossguard' in error.attrib['source']


class TestCheckstyleFileOutput:
    def test_write_to_file(self, tmp_path):
        out = tmp_path / 'report.xml'
        result = export_checkstyle(_SAMPLE_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()

    def test_empty_report_raises(self):
        with pytest.raises(ValueError):
            export_checkstyle({})

    def test_none_report_raises(self):
        with pytest.raises(ValueError):
            export_checkstyle(None)


class TestCheckstyleEdgeCases:
    def test_no_issues(self):
        report = {
            'file_path': 'app.js',
            'browsers': {
                'chrome': {
                    'version': '120',
                    'supported': 10,
                    'partial': 0,
                    'unsupported': 0,
                    'unsupported_features': [],
                    'partial_features': [],
                }
            }
        }
        xml_str = export_checkstyle(report)
        root = ET.fromstring(xml_str)
        errors = root.findall('.//error')
        assert len(errors) == 0

    def test_project_path_fallback(self):
        report = {
            'project_path': 'src/',
            'browsers': {
                'chrome': {
                    'version': '120',
                    'unsupported_features': ['css-grid'],
                    'partial_features': [],
                }
            }
        }
        xml_str = export_checkstyle(report)
        root = ET.fromstring(xml_str)
        file_elem = root.find('file')
        assert file_elem.attrib['name'] == 'src/'
