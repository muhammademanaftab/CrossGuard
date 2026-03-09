"""Tests for JUnit XML exporter."""

import xml.etree.ElementTree as ET
import pytest

from src.export.junit_exporter import export_junit


_SAMPLE_REPORT = {
    'success': True,
    'browsers': {
        'chrome': {
            'version': '120',
            'supported': 8,
            'partial': 1,
            'unsupported': 2,
            'unsupported_features': ['css-grid', 'css-subgrid'],
            'partial_features': ['flexbox-gap'],
        },
        'firefox': {
            'version': '121',
            'supported': 10,
            'partial': 0,
            'unsupported': 1,
            'unsupported_features': ['css-subgrid'],
            'partial_features': [],
        },
    },
}


class TestJunitStructure:
    def test_valid_xml_with_browser_suites(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        assert root.tag == 'testsuites'
        assert root.attrib['name'] == 'CrossGuard'
        suites = root.findall('testsuite')
        assert len(suites) == 2
        names = {s.attrib['name'] for s in suites}
        assert 'chrome 120' in names
        assert 'firefox 121' in names


class TestJunitTestcases:
    def test_failure_types_and_counts(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        chrome = [s for s in root.findall('testsuite')
                  if 'chrome' in s.attrib['name']][0]
        assert len(chrome.findall('.//failure[@type="unsupported"]')) == 2
        assert len(chrome.findall('.//failure[@type="partial"]')) == 1
        assert chrome.attrib['failures'] == '2'

    def test_testcase_classname_present(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        for tc in root.findall('.//testcase'):
            assert 'classname' in tc.attrib

    def test_tests_attribute_matches_testcase_count(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        for suite in root.findall('testsuite'):
            assert int(suite.attrib['tests']) == len(suite.findall('testcase'))


class TestJunitFileOutput:
    def test_write_to_file(self, tmp_path):
        out = tmp_path / 'report.xml'
        result = export_junit(_SAMPLE_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()
        root = ET.parse(str(out)).getroot()
        assert root.tag == 'testsuites'

    @pytest.mark.parametrize("bad_input", [{}, None])
    def test_invalid_report_raises(self, bad_input):
        with pytest.raises(ValueError):
            export_junit(bad_input)


class TestJunitEdgeCases:
    def test_no_issues(self):
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

    def test_empty_browsers(self):
        xml_str = export_junit({'browsers': {}})
        root = ET.fromstring(xml_str)
        assert len(root.findall('testsuite')) == 0
