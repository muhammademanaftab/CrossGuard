"""Output formatters for Cross Guard CLI.

Formats analysis results for terminal output in table, JSON, or summary mode.
All public format functions accept an optional ``color`` flag (default False)
for backward compatibility.
"""

import json
from typing import Any, Dict, List

import click


# ── Color helpers ─────────────────────────────────────────────────────


def _grade_color(grade: str, color: bool) -> str:
    """Return the grade string, optionally wrapped in ANSI color."""
    if not color:
        return grade
    mapping = {
        'A': 'green', 'A+': 'green', 'A-': 'green',
        'B': 'cyan', 'B+': 'cyan', 'B-': 'cyan',
        'C': 'yellow', 'C+': 'yellow', 'C-': 'yellow',
        'D': 'red', 'D+': 'red', 'D-': 'red',
        'F': 'red',
    }
    return click.style(grade, fg=mapping.get(grade, None), bold=True)


def _score_color(score: float, color: bool) -> str:
    """Return the score as a string, optionally colored."""
    text = f"{score:.1f}%"
    if not color:
        return text
    if score >= 90:
        return click.style(text, fg='green')
    if score >= 75:
        return click.style(text, fg='cyan')
    if score >= 60:
        return click.style(text, fg='yellow')
    return click.style(text, fg='red')


def _status_text(status: str, color: bool) -> str:
    """Color a support status label."""
    if not color:
        return status
    mapping = {
        'supported': 'green',
        'partial': 'yellow',
        'unsupported': 'red',
        'unknown': None,
    }
    return click.style(status, fg=mapping.get(status.lower(), None))


def _risk_color(risk: str, color: bool) -> str:
    """Color a risk-level label."""
    if not color:
        return risk
    mapping = {
        'low': 'green',
        'medium': 'yellow',
        'high': 'red',
        'critical': 'red',
    }
    return click.style(risk, fg=mapping.get(risk.lower(), None), bold=risk.lower() == 'critical')


# ── Public format functions ───────────────────────────────────────────


def format_result(result: Dict, fmt: str = 'table', *, color: bool = False) -> str:
    """Format an analysis result for terminal output.

    Args:
        result: Analysis result dict (from AnalysisResult.to_dict()).
        fmt: Output format — 'table', 'json', or 'summary'.
        color: Emit ANSI color codes.

    Returns:
        Formatted string.
    """
    if fmt == 'json':
        return format_json(result)
    elif fmt == 'summary':
        return format_summary(result, color=color)
    return format_table(result, color=color)


def format_json(result: Dict) -> str:
    """Format result as pretty-printed JSON."""
    return json.dumps(result, indent=2, ensure_ascii=False)


def format_summary(result: Dict, *, color: bool = False) -> str:
    """Format result as a compact one-line summary."""
    if not result.get('success'):
        return f"Error: {result.get('error', 'Unknown error')}"

    scores = result.get('scores', {})
    summary = result.get('summary', {})

    grade = scores.get('grade', 'N/A')
    score = scores.get('simple_score', 0)
    total = summary.get('total_features', 0)
    critical = summary.get('critical_issues', 0)

    return (
        f"Grade: {_grade_color(grade, color)}  "
        f"Score: {_score_color(score, color)}  "
        f"Features: {total}  Issues: {critical}"
    )


def format_table(result: Dict, *, color: bool = False) -> str:
    """Format result as a readable terminal table."""
    if not result.get('success'):
        return f"Error: {result.get('error', 'Unknown error')}"

    lines: List[str] = []

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
    lines.append(
        f"  Grade: {_grade_color(grade, color)}    "
        f"Score: {_score_color(simple, color)}    "
        f"Weighted: {_score_color(weighted, color)}    "
        f"Risk: {_risk_color(risk, color)}"
    )

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
                f"{_score_color(pct, color):>7} "
                f"{data.get('supported', 0):>5} "
                f"{data.get('partial', 0):>8} "
                f"{data.get('unsupported', 0):>5}"
            )

        # Issues
        for name, data in browsers.items():
            unsupported = data.get('unsupported_features', [])
            if unsupported:
                lines.append("")
                label = _status_text('unsupported', color)
                lines.append(f"  {name.capitalize()} — {label} ({len(unsupported)}):")
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


def format_history(analyses: List[Dict], *, color: bool = False) -> str:
    """Format analysis history as a table."""
    if not analyses:
        return "No analysis history found."

    lines: List[str] = []
    lines.append(f"{'ID':>5}  {'Date':<20} {'File':<30} {'Grade':>5} {'Score':>7}")
    lines.append("-" * 72)

    for a in analyses:
        grade = a.get('grade', 'N/A')
        score = a.get('overall_score', 0)
        lines.append(
            f"{a.get('id', '?'):>5}  "
            f"{a.get('analyzed_at', ''):<20.20} "
            f"{a.get('file_name', ''):<30.30} "
            f"{_grade_color(grade, color):>5} "
            f"{_score_color(score, color):>6}"
        )

    return "\n".join(lines)


def format_stats(stats: Dict, *, color: bool = False) -> str:
    """Format statistics as a readable table."""
    lines: List[str] = []
    lines.append("Cross Guard Statistics")
    lines.append("=" * 40)
    lines.append(f"  Total Analyses: {stats.get('total_analyses', 0)}")
    lines.append(f"  Average Score:  {_score_color(stats.get('average_score', 0), color)}")
    lines.append(f"  Best Score:     {_score_color(stats.get('best_score', 0), color)}")
    lines.append(f"  Worst Score:    {_score_color(stats.get('worst_score', 0), color)}")

    top_issues = stats.get('top_problematic_features', [])
    if top_issues:
        lines.append("")
        lines.append("  Most Problematic Features:")
        for item in top_issues[:5]:
            lines.append(f"    - {item.get('feature_name', item.get('feature_id', '?'))}"
                         f" ({item.get('count', 0)} occurrences)")

    return "\n".join(lines)


def format_project_result(result: Dict, *, color: bool = False) -> str:
    """Format a project analysis result."""
    if not result.get('success'):
        return f"Error: {result.get('error', 'Unknown error')}"

    lines: List[str] = []
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"  Project: {result.get('project_name', 'Unknown')}")
    lines.append("=" * 60)

    score = result.get('overall_score', 0)
    grade = result.get('overall_grade', 'N/A')
    lines.append(
        f"  Score: {_score_color(score, color)}  "
        f"Grade: {_grade_color(grade, color)}"
    )
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
            w_score = f.get('score', 0)
            w_grade = f.get('grade', '?')
            lines.append(
                f"    {f.get('file_name', '?')} — "
                f"{_score_color(w_score, color)} ({_grade_color(w_grade, color)})"
            )

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
