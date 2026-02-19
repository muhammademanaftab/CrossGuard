"""SARIF 2.1.0 exporter for Cross Guard analysis reports.

Generates Static Analysis Results Interchange Format output consumable
by GitHub Code Scanning, VS Code SARIF Viewer, and other SARIF tools.

Uses only ``json`` from the standard library — zero extra dependencies.
"""

import json
from typing import Dict, List, Optional, Union


_SARIF_VERSION = "2.1.0"
_SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json"


def export_sarif(
    report: Dict,
    output_path: Optional[str] = None,
) -> Union[Dict, str]:
    """Export an analysis report in SARIF 2.1.0 format.

    Args:
        report: Analysis result dict (single-file ``AnalysisResult.to_dict()``
                or project ``ProjectAnalysisResult.to_dict()``).
        output_path: If given, write JSON to this file and return the path.
                     Otherwise return the SARIF dict.

    Returns:
        SARIF dict (when *output_path* is None) or the written file path.

    Raises:
        ValueError: If *report* is empty/None.
    """
    if not report:
        raise ValueError("No analysis report to export")

    # Detect project-level vs single-file
    if 'file_results' in report:
        results, rules = _project_results(report)
    else:
        results, rules = _single_file_results(report)

    # Build properties from scores
    properties: Dict = {}
    scores = report.get('scores', {})
    if scores:
        properties['score'] = scores.get('simple_score', 0)
        properties['grade'] = scores.get('grade', 'N/A')
    if report.get('overall_score') is not None:
        properties['score'] = report['overall_score']
        properties['grade'] = report.get('overall_grade', 'N/A')

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


# ── Internal helpers ──────────────────────────────────────────────────


def _single_file_results(report: Dict):
    """Extract SARIF results from a single-file analysis."""
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


def _project_results(report: Dict):
    """Extract SARIF results from a project-level analysis."""
    rules: Dict[str, Dict] = {}
    results: List[Dict] = []

    for browser_name, browser_data in report.get('browsers', {}).items():
        if not isinstance(browser_data, dict):
            continue
        version = browser_data.get('version', '')

        for feat in browser_data.get('unsupported_features', []):
            rule_id = _to_rule_id(feat)
            _ensure_rule(rules, rule_id, feat)
            results.append(_make_result(
                rule_id=rule_id,
                message=f"'{feat}' is not supported in {browser_name} {version}",
                level="error",
                file_path=report.get('project_path', 'unknown'),
            ))

        for feat in browser_data.get('partial_features', []):
            rule_id = _to_rule_id(feat)
            _ensure_rule(rules, rule_id, feat)
            results.append(_make_result(
                rule_id=rule_id,
                message=f"'{feat}' is only partially supported in {browser_name} {version}",
                level="warning",
                file_path=report.get('project_path', 'unknown'),
            ))

    return results, rules


def _to_rule_id(feature_name: str) -> str:
    """Normalise a feature name into a SARIF rule ID."""
    return feature_name.lower().replace(' ', '-').replace('/', '-')


def _ensure_rule(rules: Dict[str, Dict], rule_id: str, feature_name: str):
    """Add a rule entry if not already present."""
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
    """Create a single SARIF result object."""
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
