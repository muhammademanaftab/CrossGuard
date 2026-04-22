"""CSV export -- flat rows of feature/browser/status for easy processing."""

import csv
import io
from typing import Dict, Optional, Union


_COLUMNS = ['feature_id', 'feature_name', 'browser', 'version', 'status', 'file_path',
            'ai_suggestion', 'ai_code_example']


def export_csv(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[str, None]:
    """Write CSV to file, or return CSV string if no path given."""
    if not report:
        raise ValueError("No analysis report to export")

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_COLUMNS)

    file_path = report.get('file_path', 'unknown')

    # Build AI suggestion lookup
    ai_map = {}
    for s in report.get('ai_suggestions') or []:
        ai_map[s['feature_id']] = s

    for browser_name, browser_data in report.get('browsers', {}).items():
        if not isinstance(browser_data, dict):
            continue
        version = browser_data.get('version', '')

        for feat in browser_data.get('unsupported_features', []):
            ai = ai_map.get(feat, {})
            writer.writerow([
                feat.lower().replace(' ', '-'),
                feat,
                browser_name,
                version,
                'unsupported',
                file_path,
                ai.get('suggestion', ''),
                ai.get('code_example', ''),
            ])

        for feat in browser_data.get('partial_features', []):
            ai = ai_map.get(feat, {})
            writer.writerow([
                feat.lower().replace(' ', '-'),
                feat,
                browser_name,
                version,
                'partial',
                file_path,
                ai.get('suggestion', ''),
                ai.get('code_example', ''),
            ])

    csv_text = buf.getvalue()

    if output_path is None:
        return csv_text

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(csv_text)
    return output_path
