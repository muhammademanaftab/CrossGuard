"""Output formatters for Cross Guard CLI.

Formats analysis results for terminal output in table, JSON, or summary mode.
"""

import json
import sys
from typing import Any, Dict, List


def format_result(result: Dict, fmt: str = 'table') -> str:
    """Format an analysis result for terminal output.

    Args:
        result: Analysis result dict (from AnalysisResult.to_dict()).
        fmt: Output format — 'table', 'json', or 'summary'.

    Returns:
        Formatted string.
    """
    if fmt == 'json':
        return format_json(result)
    elif fmt == 'summary':
        return format_summary(result)
    return format_table(result)


def format_json(result: Dict) -> str:
    """Format result as pretty-printed JSON."""
    return json.dumps(result, indent=2, ensure_ascii=False)


def format_summary(result: Dict) -> str:
    """Format result as a compact one-line summary."""
    if not result.get('success'):
        return f"Error: {result.get('error', 'Unknown error')}"

    scores = result.get('scores', {})
    summary = result.get('summary', {})

    grade = scores.get('grade', 'N/A')
    score = scores.get('simple_score', 0)
    total = summary.get('total_features', 0)
    critical = summary.get('critical_issues', 0)

    return f"Grade: {grade}  Score: {score:.0f}%  Features: {total}  Issues: {critical}"


def format_table(result: Dict) -> str:
    """Format result as a readable terminal table."""
    if not result.get('success'):
        return f"Error: {result.get('error', 'Unknown error')}"

    lines = []

    # Header
    lines.append("")
    lines.append("=" * 60)
    lines.append("  CROSS GUARD — Browser Compatibility Report")
    lines.append("=" * 60)

    # Scores
    scores = result.get('scores', {})
    grade = scores.get('grade', 'N/A')
    simple = scores.get('simple_score', 0)
    weighted = scores.get('weighted_score', 0)
    risk = scores.get('risk_level', 'unknown')

    lines.append("")
    lines.append(f"  Grade: {grade}    Score: {simple:.1f}%    "
                 f"Weighted: {weighted:.1f}%    Risk: {risk}")

    # Feature summary
    summary = result.get('summary', {})
    lines.append("")
    lines.append("  Features Detected:")
    lines.append(f"    Total: {summary.get('total_features', 0)}")
    lines.append(f"    HTML:  {summary.get('html_features', 0)}")
    lines.append(f"    CSS:   {summary.get('css_features', 0)}")
    lines.append(f"    JS:    {summary.get('js_features', 0)}")
    lines.append(f"    Critical Issues: {summary.get('critical_issues', 0)}")

    # Browser table
    browsers = result.get('browsers', {})
    if browsers:
        lines.append("")
        lines.append("  Browser Compatibility:")
        lines.append(f"  {'Browser':<12} {'Version':>8} {'Compat':>8} "
                     f"{'OK':>5} {'Partial':>8} {'Fail':>5}")
        lines.append("  " + "-" * 52)

        for name, data in browsers.items():
            pct = data.get('compatibility_percentage', 0)
            lines.append(
                f"  {name.capitalize():<12} {data.get('version', ''):>8} "
                f"{pct:>7.1f}% "
                f"{data.get('supported', 0):>5} "
                f"{data.get('partial', 0):>8} "
                f"{data.get('unsupported', 0):>5}"
            )

        # Issues
        for name, data in browsers.items():
            unsupported = data.get('unsupported_features', [])
            if unsupported:
                lines.append("")
                lines.append(f"  {name.capitalize()} — unsupported ({len(unsupported)}):")
                for feat in unsupported[:10]:
                    lines.append(f"    - {feat}")
                if len(unsupported) > 10:
                    lines.append(f"    ... and {len(unsupported) - 10} more")

    # Recommendations
    recs = result.get('recommendations', [])
    if recs:
        lines.append("")
        lines.append("  Recommendations:")
        for i, rec in enumerate(recs[:5], 1):
            lines.append(f"    {i}. {rec}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_history(analyses: List[Dict]) -> str:
    """Format analysis history as a table."""
    if not analyses:
        return "No analysis history found."

    lines = []
    lines.append(f"{'ID':>5}  {'Date':<20} {'File':<30} {'Grade':>5} {'Score':>7}")
    lines.append("-" * 72)

    for a in analyses:
        lines.append(
            f"{a.get('id', '?'):>5}  "
            f"{a.get('analyzed_at', ''):<20.20} "
            f"{a.get('file_name', ''):<30.30} "
            f"{a.get('grade', 'N/A'):>5} "
            f"{a.get('overall_score', 0):>6.1f}%"
        )

    return "\n".join(lines)


def format_stats(stats: Dict) -> str:
    """Format statistics as a readable table."""
    lines = []
    lines.append("Cross Guard Statistics")
    lines.append("=" * 40)
    lines.append(f"  Total Analyses: {stats.get('total_analyses', 0)}")
    lines.append(f"  Average Score:  {stats.get('average_score', 0):.1f}%")
    lines.append(f"  Best Score:     {stats.get('best_score', 0):.1f}%")
    lines.append(f"  Worst Score:    {stats.get('worst_score', 0):.1f}%")

    top_issues = stats.get('top_problematic_features', [])
    if top_issues:
        lines.append("")
        lines.append("  Most Problematic Features:")
        for item in top_issues[:5]:
            lines.append(f"    - {item.get('feature_name', item.get('feature_id', '?'))}"
                         f" ({item.get('count', 0)} occurrences)")

    return "\n".join(lines)


def format_project_result(result: Dict) -> str:
    """Format a project analysis result."""
    if not result.get('success'):
        return f"Error: {result.get('error', 'Unknown error')}"

    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"  Project: {result.get('project_name', 'Unknown')}")
    lines.append("=" * 60)

    lines.append(f"  Score: {result.get('overall_score', 0):.1f}%  "
                 f"Grade: {result.get('overall_grade', 'N/A')}")
    lines.append(f"  Files: {result.get('total_files', 0)} "
                 f"(HTML: {result.get('html_files', 0)}, "
                 f"CSS: {result.get('css_files', 0)}, "
                 f"JS: {result.get('js_files', 0)})")
    lines.append(f"  Features: {result.get('total_features', 0)} total, "
                 f"{result.get('unique_features', 0)} unique")
    lines.append(f"  Issues: {result.get('unsupported_count', 0)} unsupported, "
                 f"{result.get('partial_count', 0)} partial")

    worst = result.get('worst_files', [])
    if worst:
        lines.append("")
        lines.append("  Worst Files:")
        for f in worst[:5]:
            lines.append(f"    {f.get('file_name', '?')} — "
                         f"{f.get('score', 0):.0f}% ({f.get('grade', '?')})")

    top_issues = result.get('top_issues', [])
    if top_issues:
        lines.append("")
        lines.append("  Top Issues:")
        for item in top_issues[:5]:
            lines.append(f"    - {item.get('feature', '?')} "
                         f"(in {item.get('count', 0)} files)")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)
