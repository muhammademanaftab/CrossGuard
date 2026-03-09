"""Generates version ranges like caniuse shows (e.g. '37-143: Supported')."""

import json
from pathlib import Path
from typing import Dict, List, Tuple


def get_version_ranges(feature_id: str, browser: str) -> List[Dict]:
    """Collapse per-version support data into contiguous status ranges."""
    db_path = Path(__file__).parent.parent.parent / "data" / "caniuse" / "data.json"

    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    feature_data = data.get('data', {}).get(feature_id)
    if not feature_data:
        return []

    browser_stats = feature_data.get('stats', {}).get(browser, {})
    if not browser_stats:
        return []

    versions = []
    for version, status in browser_stats.items():
        try:
            if version == "TP":  # Safari Technology Preview
                sort_key = 9999
            elif "-" in version:
                sort_key = float(version.split("-")[0])
            else:
                sort_key = float(version)
            versions.append((sort_key, version, status))
        except ValueError:
            versions.append((9998, version, status))

    versions.sort(key=lambda x: x[0])

    # Merge consecutive versions with the same status into ranges
    ranges = []
    current_status = None
    start_version = None
    prev_version = None

    for _, version, status in versions:
        base_status = status.split()[0] if status else 'u'  # strip notes like "#1"

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

    if current_status is not None:
        ranges.append({
            "start": start_version,
            "end": prev_version,
            "status": current_status,
            "status_text": _get_status_text(current_status)
        })

    return ranges


def _get_status_text(status: str) -> str:
    status_map = {
        'y': 'Supported',
        'n': 'Not Supported',
        'a': 'Supported',  # "almost" = full per caniuse
        'p': 'Partial Support',
        'x': 'Requires Prefix',
        'u': 'Unknown',
        'd': 'Disabled by Default'
    }
    return status_map.get(status, status)


def get_all_browser_ranges(feature_id: str) -> Dict[str, List[Dict]]:
    """Version ranges for every browser we track."""
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
    """e.g. '4-31: Not Supported | 37-143: Supported'"""
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
    """Per-browser summary: current status, supported-since version, and full ranges."""
    browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera', 'ie']

    result = {}
    for browser in browsers:
        ranges = get_version_ranges(feature_id, browser)
        if ranges:
            current = ranges[-1]

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
