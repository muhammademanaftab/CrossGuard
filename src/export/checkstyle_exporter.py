"""Checkstyle XML exporter for Cross Guard analysis reports.

Generates Checkstyle-format XML consumable by SonarQube and similar tools.

Uses only ``xml.etree.ElementTree`` from the standard library.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Optional, Union


def export_checkstyle(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[str, None]:
    """Export an analysis report as Checkstyle XML.

    Mapping:
      - ``<checkstyle>`` root.
      - One ``<file>`` per source file (or one for single-file reports).
      - ``<error>`` elements for unsupported/partial features.

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

    root = ET.Element('checkstyle', version='1.0.0')

    file_path = report.get('file_path', report.get('project_path', 'unknown'))

    file_elem = ET.SubElement(root, 'file', name=file_path)

    for browser_name, browser_data in report.get('browsers', {}).items():
        if not isinstance(browser_data, dict):
            continue
        version = browser_data.get('version', '')

        for feat in browser_data.get('unsupported_features', []):
            ET.SubElement(file_elem, 'error',
                          severity='error',
                          message=f"'{feat}' is not supported in {browser_name} {version}",
                          source=f"crossguard.{browser_name}.unsupported")

        for feat in browser_data.get('partial_features', []):
            ET.SubElement(file_elem, 'error',
                          severity='warning',
                          message=f"'{feat}' is only partially supported in {browser_name} {version}",
                          source=f"crossguard.{browser_name}.partial")

    xml_string = ET.tostring(root, encoding='unicode', xml_declaration=True)

    if output_path is None:
        return xml_string

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    return output_path
