"""CSV exporter for Cross Guard analysis reports.

Outputs a flat table of feature/browser/status rows suitable for
spreadsheets, data pipelines, or quick ``grep``/``awk`` processing.

Uses only ``csv`` and ``io`` from the standard library.
"""

import csv
import io
from typing import Dict, Optional, Union


_COLUMNS = ['feature_id', 'feature_name', 'browser', 'version', 'status', 'file_path']


def export_csv(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[str, None]:
    """Export an analysis report as CSV.

    Columns: feature_id, feature_name, browser, version, status, file_path

    Args:
        report: Analysis result dict (single-file or project).
        output_path: If given, write CSV to this file and return the path.
                     Otherwise return the CSV string.

    Returns:
        CSV string (when *output_path* is None) or the written file path.

    Raises:
        ValueError: If *report* is empty/None.
    """
    if not report:
        raise ValueError("No analysis report to export")

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_COLUMNS)

    file_path = report.get('file_path', report.get('project_path', 'unknown'))

    for browser_name, browser_data in report.get('browsers', {}).items():
        if not isinstance(browser_data, dict):
            continue
        version = browser_data.get('version', '')

        for feat in browser_data.get('unsupported_features', []):
            writer.writerow([
                feat.lower().replace(' ', '-'),
                feat,
                browser_name,
                version,
                'unsupported',
                file_path,
            ])

        for feat in browser_data.get('partial_features', []):
            writer.writerow([
                feat.lower().replace(' ', '-'),
                feat,
                browser_name,
                version,
                'partial',
                file_path,
            ])

    csv_text = buf.getvalue()

    if output_path is None:
        return csv_text

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(csv_text)
    return output_path
