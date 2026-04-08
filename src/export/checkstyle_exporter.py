"""Checkstyle XML export for SonarQube and similar tools."""

import xml.etree.ElementTree as ET
from typing import Dict, Optional, Union


def export_checkstyle(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[str, None]:
    """Write Checkstyle XML to file, or return XML string if no path given.

    Each unsupported feature becomes an <error severity="error">,
    each partial feature becomes <error severity="warning">.
    """
    if not report:
        raise ValueError("No analysis report to export")

    root = ET.Element('checkstyle', version='1.0.0')

    file_path = report.get('file_path', 'unknown')

    file_elem = ET.SubElement(root, 'file', name=file_path)

    # Build AI suggestion lookup
    ai_map = {}
    for s in report.get('ai_suggestions') or []:
        ai_map[s['feature_id']] = s

    for browser_name, browser_data in report.get('browsers', {}).items():
        if not isinstance(browser_data, dict):
            continue
        version = browser_data.get('version', '')

        for feat in browser_data.get('unsupported_features', []):
            msg = f"'{feat}' is not supported in {browser_name} {version}"
            ai = ai_map.get(feat)
            if ai:
                msg += f" -- Fix: {ai['suggestion']}"
            ET.SubElement(file_elem, 'error',
                          severity='error',
                          message=msg,
                          source=f"crossguard.{browser_name}.unsupported")

        for feat in browser_data.get('partial_features', []):
            msg = f"'{feat}' is only partially supported in {browser_name} {version}"
            ai = ai_map.get(feat)
            if ai:
                msg += f" -- Fix: {ai['suggestion']}"
            ET.SubElement(file_elem, 'error',
                          severity='warning',
                          message=msg,
                          source=f"crossguard.{browser_name}.partial")

    xml_string = ET.tostring(root, encoding='unicode', xml_declaration=True)

    if output_path is None:
        return xml_string

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    return output_path
