"""SARIF 2.1.0 export for GitHub Code Scanning, VS Code SARIF Viewer, etc."""

import json
from typing import Dict, List, Optional, Union


_SARIF_VERSION = "2.1.0"
_SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json"


def export_sarif(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[Dict, str]:
    """Write SARIF 2.1.0 to file, or return dict if no path given. Handles both single-file and project reports."""
    if not report:
        raise ValueError("No analysis report to export")

    results, rules = _single_file_results(report)

    # Stash scores in SARIF properties so CI tools can read them
    properties: Dict = {}
    scores = report.get('scores', {})
    if scores:
        properties['score'] = scores.get('simple_score', 0)
        properties['grade'] = scores.get('grade', 'N/A')
    baseline = report.get('baseline_summary')
    if baseline:
        properties['baseline'] = baseline

    sarif: Dict = {
        "$schema": _SARIF_SCHEMA,
        "version": _SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "CrossGuard",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/user/crossguard",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
                "properties": properties,
            }
        ],
    }

    if output_path is None:
        return sarif

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sarif, f, indent=2, ensure_ascii=False)
    return output_path


def _single_file_results(report: Dict):
    rules: Dict[str, Dict] = {}
    results: List[Dict] = []

    file_path = report.get('file_path', 'unknown')

    for browser_name, browser_data in report.get('browsers', {}).items():
        version = browser_data.get('version', '')

        for feat in browser_data.get('unsupported_features', []):
            rule_id = _to_rule_id(feat)
            _ensure_rule(rules, rule_id, feat)
            results.append(_make_result(
                rule_id=rule_id,
                message=f"'{feat}' is not supported in {browser_name} {version}",
                level="error",
                file_path=file_path,
            ))

        for feat in browser_data.get('partial_features', []):
            rule_id = _to_rule_id(feat)
            _ensure_rule(rules, rule_id, feat)
            results.append(_make_result(
                rule_id=rule_id,
                message=f"'{feat}' is only partially supported in {browser_name} {version}",
                level="warning",
                file_path=file_path,
            ))

    return results, rules


def _to_rule_id(feature_name: str) -> str:
    """Turn a feature name into a valid SARIF rule ID (lowercase, dashes)."""
    return feature_name.lower().replace(' ', '-').replace('/', '-')


def _ensure_rule(rules: Dict[str, Dict], rule_id: str, feature_name: str):
    """Register a SARIF rule if we haven't seen this feature yet."""
    if rule_id not in rules:
        rules[rule_id] = {
            "id": rule_id,
            "shortDescription": {"text": f"Browser compatibility: {feature_name}"},
            "helpUri": f"https://caniuse.com/?search={feature_name}",
        }


def _make_result(
    rule_id: str,
    message: str,
    level: str,
    file_path: str,
) -> Dict:
    # SARIF requires physicalLocation even without line numbers
    return {
        "ruleId": rule_id,
        "level": level,
        "message": {"text": message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": file_path},
                }
            }
        ],
    }
