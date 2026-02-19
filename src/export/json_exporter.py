"""JSON export for Cross Guard analysis reports.

Formats an AnalysisResult (or raw dict) into a JSON file or dict.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Union


def export_json(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[Dict, str]:
    """Export an analysis report as JSON.

    Args:
        report: Analysis report dictionary (from AnalysisResult.to_dict()).
        output_path: If provided, write JSON to this file and return the path.
                     If None, return the enriched dict.

    Returns:
        The enriched report dict (when output_path is None),
        or the output file path (when output_path is given).

    Raises:
        ValueError: If report is empty or None.
        IOError: If the file cannot be written.
    """
    if not report:
        raise ValueError("No analysis report to export")

    # Enrich with metadata
    enriched = {
        'generated_by': 'Cross Guard',
        'generated_at': datetime.now().isoformat(),
        **report,
    }

    if output_path is None:
        return enriched

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    return output_path
