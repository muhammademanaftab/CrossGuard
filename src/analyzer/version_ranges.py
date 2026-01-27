"""
Version Range Generator for Browser Support.

Generates version ranges like Can I Use displays (e.g., "37-143: Supported").
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


def get_version_ranges(feature_id: str, browser: str) -> List[Dict]:
    """
    Get version ranges for a feature in a specific browser.

    Returns a list of ranges like:
    [
        {"start": "4", "end": "31", "status": "n", "status_text": "Not Supported"},
        {"start": "37", "end": "143", "status": "y", "status_text": "Supported"},
    ]
    """
    # Load Can I Use database
    db_path = Path(__file__).parent.parent.parent / "caniuse" / "data.json"

    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get feature data
    feature_data = data.get('data', {}).get(feature_id)
    if not feature_data:
        return []

    # Get browser stats
    browser_stats = feature_data.get('stats', {}).get(browser, {})
    if not browser_stats:
        return []

    # Sort versions numerically
    versions = []
    for version, status in browser_stats.items():
        try:
            # Handle versions like "4", "4.4", "TP" (Technology Preview)
            if version == "TP":
                sort_key = 9999
            elif "-" in version:
                # Handle ranges like "3.5-3.6"
                sort_key = float(version.split("-")[0])
            else:
                sort_key = float(version)
            versions.append((sort_key, version, status))
        except ValueError:
            versions.append((9998, version, status))

    versions.sort(key=lambda x: x[0])

    # Group into ranges
    ranges = []
    current_status = None
    start_version = None
    prev_version = None

    for _, version, status in versions:
        # Normalize status (remove notes like "#1", "x #2", etc.)
        base_status = status.split()[0] if status else 'u'

        if base_status != current_status:
            if current_status is not None:
                ranges.append({
                    "start": start_version,
                    "end": prev_version,
                    "status": current_status,
                    "status_text": _get_status_text(current_status)
                })
            start_version = version
            current_status = base_status
        prev_version = version

    # Add last range
    if current_status is not None:
        ranges.append({
            "start": start_version,
            "end": prev_version,
            "status": current_status,
            "status_text": _get_status_text(current_status)
        })

    return ranges


def _get_status_text(status: str) -> str:
    """Convert status code to human-readable text."""
    status_map = {
        'y': 'Supported',
        'n': 'Not Supported',
        'a': 'Partial Support',
        'p': 'Polyfill',
        'x': 'Requires Prefix',
        'u': 'Unknown',
        'd': 'Disabled by Default'
    }
    return status_map.get(status, status)


def get_all_browser_ranges(feature_id: str) -> Dict[str, List[Dict]]:
    """
    Get version ranges for all browsers for a feature.

    Returns:
    {
        "chrome": [{"start": "4", "end": "31", "status": "n", ...}, ...],
        "firefox": [...],
        ...
    }
    """
    browsers = [
        'chrome', 'firefox', 'safari', 'edge', 'opera', 'ie',
        'android', 'ios_saf', 'samsung', 'op_mini', 'op_mob'
    ]

    result = {}
    for browser in browsers:
        ranges = get_version_ranges(feature_id, browser)
        if ranges:
            result[browser] = ranges

    return result


def format_ranges_for_display(feature_id: str, browser: str) -> str:
    """
    Format version ranges as a display string.

    Returns something like:
    "4-31: Not Supported | 37-143: Supported"
    """
    ranges = get_version_ranges(feature_id, browser)

    if not ranges:
        return "No data available"

    parts = []
    for r in ranges:
        if r["start"] == r["end"]:
            version_str = r["start"]
        else:
            version_str = f"{r['start']}-{r['end']}"
        parts.append(f"{version_str}: {r['status_text']}")

    return " | ".join(parts)


def get_support_summary(feature_id: str) -> Dict[str, Dict]:
    """
    Get a summary of browser support with version ranges.

    Returns:
    {
        "chrome": {
            "current_status": "y",
            "current_status_text": "Supported",
            "supported_since": "37",
            "ranges": [...]
        },
        ...
    }
    """
    browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera', 'ie']

    result = {}
    for browser in browsers:
        ranges = get_version_ranges(feature_id, browser)
        if ranges:
            # Get current status (last range)
            current = ranges[-1]

            # Find when it became supported
            supported_since = None
            for r in ranges:
                if r["status"] == "y":
                    supported_since = r["start"]
                    break

            result[browser] = {
                "current_status": current["status"],
                "current_status_text": current["status_text"],
                "supported_since": supported_since,
                "ranges": ranges
            }

    return result


# Browser display names
BROWSER_NAMES = {
    'chrome': 'Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'edge': 'Edge',
    'opera': 'Opera',
    'ie': 'Internet Explorer',
    'android': 'Android Browser',
    'ios_saf': 'Safari on iOS',
    'samsung': 'Samsung Internet',
    'op_mini': 'Opera Mini',
    'op_mob': 'Opera Mobile'
}


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("VERSION RANGES DEMO - Dialog Element")
    print("=" * 60)

    feature = "dialog"
    summary = get_support_summary(feature)

    for browser, data in summary.items():
        print(f"\n{BROWSER_NAMES.get(browser, browser)}:")
        print(f"  Current: {data['current_status_text']}")
        if data['supported_since']:
            print(f"  Supported since: v{data['supported_since']}")
        print(f"  Ranges:")
        for r in data['ranges']:
            if r['start'] == r['end']:
                print(f"    {r['start']}: {r['status_text']}")
            else:
                print(f"    {r['start']} - {r['end']}: {r['status_text']}")
