"""JUnit XML exporter for Cross Guard analysis reports.

Generates JUnit XML output consumable by Jenkins, GitLab CI,
and other CI systems that read JUnit reports.

Uses only ``xml.etree.ElementTree`` from the standard library.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Optional, Union


def export_junit(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[str, None]:
    """Export an analysis report as JUnit XML.

    Mapping:
      - ``<testsuites name="CrossGuard">`` wrapper.
      - One ``<testsuite>`` per browser.
      - One ``<testcase>`` per feature; ``<failure>`` for unsupported,
        ``type="partial"`` for partial.

    Args:
        report: Analysis result dict (single-file or project).
        output_path: If given, write XML to this file and return the path.
                     Otherwise return the XML string.

    Returns:
        XML string (when *output_path* is None) or the written file path.

    Raises:
        ValueError: If *report* is empty/None.
    """
    if not report:
        raise ValueError("No analysis report to export")

    testsuites = ET.Element('testsuites', name='CrossGuard')

    browsers = report.get('browsers', {})
    for browser_name, browser_data in browsers.items():
        if not isinstance(browser_data, dict):
            continue

        supported = browser_data.get('supported', 0)
        unsupported_list = browser_data.get('unsupported_features', [])
        partial_list = browser_data.get('partial_features', [])
        unsupported_count = len(unsupported_list)
        partial_count_actual = len(partial_list)
        # tests = individual testcases we actually emit
        has_supported_summary = 1 if supported > 0 else 0
        total_tests = unsupported_count + partial_count_actual + has_supported_summary
        failures = unsupported_count
        version = browser_data.get('version', '')

        testsuite = ET.SubElement(testsuites, 'testsuite',
                                  name=f"{browser_name} {version}".strip(),
                                  tests=str(total_tests),
                                  failures=str(failures))

        # Generate testcases for unsupported
        for feat in unsupported_list:
            tc = ET.SubElement(testsuite, 'testcase',
                               classname=f"crossguard.{browser_name}",
                               name=feat)
            failure = ET.SubElement(tc, 'failure',
                                   type='unsupported',
                                   message=f"'{feat}' is not supported in "
                                           f"{browser_name} {version}")
            failure.text = f"Feature '{feat}' is not supported"

        # Generate testcases for partial
        for feat in partial_list:
            tc = ET.SubElement(testsuite, 'testcase',
                               classname=f"crossguard.{browser_name}",
                               name=feat)
            failure = ET.SubElement(tc, 'failure',
                                   type='partial',
                                   message=f"'{feat}' is only partially supported in "
                                           f"{browser_name} {version}")
            failure.text = f"Feature '{feat}' has partial support"

        # Generate a passing testcase as a summary for supported features
        if supported > 0:
            tc = ET.SubElement(testsuite, 'testcase',
                               classname=f"crossguard.{browser_name}",
                               name=f"{supported} features fully supported")

    xml_string = ET.tostring(testsuites, encoding='unicode', xml_declaration=True)

    if output_path is None:
        return xml_string

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    return output_path
