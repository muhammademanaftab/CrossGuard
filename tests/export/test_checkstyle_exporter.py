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
    def test_valid_xml_structure(self):
        xml_str = export_checkstyle(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        assert root.tag == 'checkstyle'
        files = root.findall('file')
        assert len(files) == 1
        assert files[0].attrib['name'] == 'src/style.css'

    def test_error_and_warning_elements(self):
        xml_str = export_checkstyle(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        errors = root.findall('.//error[@severity="error"]')
        assert len(errors) == 2
        warnings = root.findall('.//error[@severity="warning"]')
        assert len(warnings) == 1
        # Verify source attribute
        assert 'crossguard' in errors[0].attrib['source']


class TestCheckstyleFileOutput:
    def test_write_to_file(self, tmp_path):
        out = tmp_path / 'report.xml'
        result = export_checkstyle(_SAMPLE_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()

    @pytest.mark.parametrize("bad_input", [{}, None])
    def test_invalid_report_raises(self, bad_input):
        with pytest.raises(ValueError):
            export_checkstyle(bad_input)


class TestCheckstyleEdgeCases:
    def test_no_issues(self):
        report = {
            'file_path': 'app.js',
            'browsers': {
                'chrome': {
                    'version': '120',
                    'supported': 10, 'partial': 0, 'unsupported': 0,
                    'unsupported_features': [], 'partial_features': [],
                }
            }
        }
        xml_str = export_checkstyle(report)
        root = ET.fromstring(xml_str)
        assert len(root.findall('.//error')) == 0

