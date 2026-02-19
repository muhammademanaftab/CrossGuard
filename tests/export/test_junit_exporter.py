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
    def test_valid_xml(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        assert root.tag == 'testsuites'
        assert root.attrib['name'] == 'CrossGuard'

    def test_one_testsuite_per_browser(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        suites = root.findall('testsuite')
        assert len(suites) == 2

    def test_testsuite_names(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        names = {s.attrib['name'] for s in root.findall('testsuite')}
        assert 'chrome 120' in names
        assert 'firefox 121' in names


class TestJunitTestcases:
    def test_unsupported_has_failure(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        chrome = [s for s in root.findall('testsuite')
                  if 'chrome' in s.attrib['name']][0]
        failures = chrome.findall('.//failure[@type="unsupported"]')
        assert len(failures) == 2

    def test_partial_has_failure_type(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        chrome = [s for s in root.findall('testsuite')
                  if 'chrome' in s.attrib['name']][0]
        partials = chrome.findall('.//failure[@type="partial"]')
        assert len(partials) == 1

    def test_testcase_classname(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        cases = root.findall('.//testcase')
        for tc in cases:
            assert 'classname' in tc.attrib

    def test_failure_counts_match(self):
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        chrome = [s for s in root.findall('testsuite')
                  if 'chrome' in s.attrib['name']][0]
        assert chrome.attrib['failures'] == '2'

    def test_tests_attribute_matches_testcase_count(self):
        """tests attribute must equal actual number of testcase elements."""
        xml_str = export_junit(_SAMPLE_REPORT)
        root = ET.fromstring(xml_str)
        for suite in root.findall('testsuite'):
            tests_attr = int(suite.attrib['tests'])
            actual_cases = len(suite.findall('testcase'))
            assert tests_attr == actual_cases, (
                f"Suite '{suite.attrib['name']}': tests={tests_attr} "
                f"but has {actual_cases} testcase elements"
            )


class TestJunitFileOutput:
    def test_write_to_file(self, tmp_path):
        out = tmp_path / 'report.xml'
        result = export_junit(_SAMPLE_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()
        root = ET.parse(str(out)).getroot()
        assert root.tag == 'testsuites'

    def test_empty_report_raises(self):
        with pytest.raises(ValueError):
            export_junit({})

    def test_none_report_raises(self):
        with pytest.raises(ValueError):
            export_junit(None)


class TestJunitEdgeCases:
    def test_no_issues(self):
        report = {
            'browsers': {
                'chrome': {
                    'version': '120',
                    'supported': 10,
                    'partial': 0,
                    'unsupported': 0,
                    'unsupported_features': [],
                    'partial_features': [],
                },
            },
        }
        xml_str = export_junit(report)
        root = ET.fromstring(xml_str)
        suite = root.find('testsuite')
        assert suite.attrib['failures'] == '0'

    def test_empty_browsers(self):
        report = {'browsers': {}}
        xml_str = export_junit(report)
        root = ET.fromstring(xml_str)
        assert len(root.findall('testsuite')) == 0
