"""Generates version ranges like caniuse shows (e.g. '37-143: Supported')."""

import json
from pathlib import Path
from typing import Dict, List


def get_version_ranges(feature_id: str, browser: str) -> List[Dict]:
    """Collapses per-version support entries into contiguous status ranges"""
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
            if version == "TP":  # Safari Technology Preview — sort last
                sort_key = 9999
            elif "-" in version:
                sort_key = float(version.split("-")[0])
            else:
                sort_key = float(version)
            versions.append((sort_key, version, status))
        except ValueError:
            versions.append((9998, version, status))

    versions.sort(key=lambda x: x[0])

    def _flush(status, start, end):
        ranges.append({
            "start": start,
            "end": end,
            "status": status,
            "status_text": _get_status_text(status),
        })

    ranges = []
    current_status = None
    start_version = None
    prev_version = None

    for _, version, status in versions:
        base_status = status.split()[0] if status else 'u'  # caniuse appends notes like "#1"

        if base_status != current_status:
            if current_status is not None:
                _flush(current_status, start_version, prev_version)
            start_version = version
            current_status = base_status
        prev_version = version

    if current_status is not None:
        _flush(current_status, start_version, prev_version)

    return ranges


def _get_status_text(status: str) -> str:
    status_map = {
        'y': 'Supported',
        'n': 'Not Supported',
        'a': 'Supported',  # "almost" maps to Supported to match caniuse site display
        'p': 'Partial Support',
        'x': 'Requires Prefix',
        'u': 'Unknown',
        'd': 'Disabled by Default'
    }
    return status_map.get(status, status)


def get_support_summary(feature_id: str) -> Dict[str, Dict]:
    """Current status + supported-since version + full ranges, per browser"""
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
