"""Writes the analysis report to a JSON file. Used for piping into other tools or scripts."""

import json
from datetime import datetime
from typing import Dict, Optional, Union


def export_json(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[Dict, str]:
    """Write report as JSON to file, or return enriched dict if no path given."""
    if not report:
        raise ValueError("No analysis report to export")

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
