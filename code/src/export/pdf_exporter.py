"""Minimal PDF report via ReportLab — default font, aligned flowables, no custom styling.

Public API (unchanged): export_pdf(report, output_path) -> str
"""

from typing import Dict, List
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


_CENTERED_CELL = ParagraphStyle(
    "CenteredCell",
    parent=getSampleStyleSheet()["Normal"],
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=11,
    spaceBefore=0,
    spaceAfter=0,
)

_FEATURE_CELL = ParagraphStyle(
    "FeatureCell",
    parent=getSampleStyleSheet()["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=12,
    spaceBefore=0,
    spaceAfter=0,
)


def export_pdf(report: Dict, output_path: str) -> str:
    if not report:
        raise ValueError("No analysis report to export")

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story: List = []

    story.append(Paragraph("Browser Compatibility Report", styles["Title"]))
    story.append(Spacer(1, 12))

    scores = report.get("scores") or {}
    summary = report.get("summary") or {}
    story.append(Paragraph(
        f"Overall score: <b>{scores.get('weighted_score', 0)}</b> "
        f"(Grade {scores.get('grade', 'N/A')}, "
        f"risk: {scores.get('risk_level', 'n/a')})",
        styles["Normal"],
    ))
    story.append(Paragraph(
        f"Features detected: {summary.get('total_features', 0)} "
        f"(HTML {summary.get('html_features', 0)}, "
        f"CSS {summary.get('css_features', 0)}, "
        f"JS {summary.get('js_features', 0)}). "
        f"Critical issues: {summary.get('critical_issues', 0)}.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 18))

    # Browser table
    browsers = report.get("browsers") or {}
    story.append(Paragraph("Browser compatibility", styles["Heading2"]))
    rows = [["Browser", "Version", "Compat %", "Supported", "Partial", "Unsupported"]]
    for name, info in browsers.items():
        if not isinstance(info, dict):
            continue
        rows.append([
            name.capitalize(),
            info.get("version", ""),
            f"{info.get('compatibility_percentage', 0)}%",
            info.get("supported", 0),
            info.get("partial", 0),
            info.get("unsupported", 0),
        ])
    t = Table(rows, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 18))

    # Key compatibility issues
    issues = _build_key_issues(browsers, report.get("feature_details") or {})
    if issues:
        story.append(Paragraph("Key compatibility issues", styles["Heading2"]))
        for line in issues:
            story.append(Paragraph(f"- {line}", styles["Normal"]))
        story.append(Spacer(1, 18))

    # Baseline counts
    baseline = report.get("baseline_summary")
    if isinstance(baseline, dict):
        story.append(Paragraph("Baseline availability", styles["Heading2"]))
        for label, key in [
            ("Widely available", "widely_available"),
            ("Newly available", "newly_available"),
            ("Limited", "limited"),
            ("Unknown", "unknown"),
        ]:
            story.append(Paragraph(f"{label}: {baseline.get(key, 0)}", styles["Normal"]))
        story.append(Spacer(1, 18))

    # Recommendations
    recs = report.get("recommendations") or []
    if recs:
        story.append(Paragraph("Recommendations", styles["Heading2"]))
        for i, r in enumerate(recs, 1):
            story.append(Paragraph(f"{i}. {r}", styles["Normal"]))
        story.append(Spacer(1, 18))

    # Feature inventory — shows per-browser support indicators (coloured like the GUI dashboard)
    fd = report.get("feature_details") or {}
    if isinstance(fd, list):
        fd = {"css": fd, "html": [], "js": []}
    if any(fd.get(k) for k in ("css", "html", "js")):
        status_map = _build_feature_status_map(browsers)
        browser_cols = _browser_columns(browsers)
        max_label_len = max((len(lbl) for _, lbl in browser_cols), default=1)
        browser_col_w = max(28, 10 * max_label_len + 14)
        legend_text = " · ".join(f"{lbl} = {name}" for name, lbl in browser_cols)
        story.append(PageBreak())
        story.append(Paragraph("Feature inventory", styles["Heading2"]))
        for label, key in [("CSS", "css"), ("HTML", "html"), ("JavaScript", "js")]:
            entries = fd.get(key) or []
            if not entries:
                continue
            # Dedupe by feature ID — feature_details contains one entry per
            # detection, so a feature used in multiple files would otherwise
            # appear in the inventory multiple times. The GUI counts unique
            # features only, so the PDF should match.
            seen_ids = set()
            unique_entries = []
            for e in entries:
                fid = e.get("feature", "")
                if fid and fid not in seen_ids:
                    seen_ids.add(fid)
                    unique_entries.append(e)
            entries = unique_entries
            if not entries:
                continue
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"{label} ({len(entries)})", styles["Heading3"]))
            header = ["Feature"] + [ltr for _, ltr in browser_cols] + ["Baseline"]
            inv = [header]
            for e in entries:
                fid = e.get("feature", "")
                display = e.get("description") or fid
                row = [Paragraph(escape(display), _FEATURE_CELL)]
                feat_statuses = status_map.get(fid, {})
                for browser_name, ltr in browser_cols:
                    row.append(_support_cell(ltr, feat_statuses.get(browser_name)))
                row.append(e.get("baseline", "") or "Unknown")
                inv.append(row)
            col_widths = [200] + [browser_col_w] * len(browser_cols) + [80]
            it = Table(inv, hAlign="LEFT", colWidths=col_widths)
            it.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (-2, -1), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(it)
            story.append(Paragraph(
                f'<font color="#666666" size="8">{escape(legend_text)}</font>',
                styles["Normal"],
            ))

    # AI fix suggestions (only when present)
    ai = report.get("ai_suggestions") or []
    if ai:
        story.append(PageBreak())
        story.append(Paragraph("AI fix suggestions", styles["Heading2"]))
        for s in ai:
            story.append(Spacer(1, 6))
            name = s.get("feature_name") or s.get("feature_id") or ""
            story.append(Paragraph(f"<b>{name}</b>", styles["Normal"]))
            if s.get("browsers_affected"):
                story.append(Paragraph(
                    f"Affects: {', '.join(s['browsers_affected'])}", styles["Normal"]
                ))
            if s.get("suggestion"):
                story.append(Paragraph(s["suggestion"], styles["Normal"]))
            if s.get("code_example"):
                story.append(Paragraph(escape(s["code_example"]), styles["Code"]))

    doc.build(story)
    return output_path


_BROWSER_ORDER = ["safari", "firefox", "chrome", "edge"]
_STATUS_COLOR = {
    "supported": "#27ae60",
    "partial": "#e67e22",
    "unsupported": "#c0392b",
    "unknown": "#888888",
}


def _browser_columns(browsers: Dict):
    """Return [(browser_name, short_label), ...] ordered Safari/Firefox/Chrome/Edge first.

    Labels start as single letters; if any two browsers would collide, the label
    length grows uniformly until every label is unique (e.g. safari+samsung -> Sa/Sm).
    Falls back to the full key if no prefix disambiguates them.
    """
    present = [b for b in _BROWSER_ORDER if b in browsers]
    extras = [b for b in browsers if b not in _BROWSER_ORDER]
    names = present + extras
    labels = [n[:1].upper() for n in names]
    for length in range(2, 10):
        if len(set(labels)) == len(labels):
            break
        labels = [n[:length].upper() for n in names]
    if len(set(labels)) != len(labels):
        labels = [n.upper() for n in names]
    return list(zip(names, labels))


def _build_feature_status_map(browsers: Dict) -> Dict[str, Dict[str, str]]:
    status: Dict[str, Dict[str, str]] = {}
    for name, info in browsers.items():
        if not isinstance(info, dict):
            continue
        for feat in info.get("unsupported_features") or []:
            status.setdefault(feat, {})[name] = "unsupported"
        for feat in info.get("partial_features") or []:
            status.setdefault(feat, {})[name] = "partial"
    return status


def _support_cell(letter: str, status):
    # Default to "supported" when the browser is present but the feature isn't flagged
    # as unsupported/partial — mirrors the GUI dashboard.
    color = _STATUS_COLOR.get(status or "supported", _STATUS_COLOR["supported"])
    return Paragraph(
        f'<font color="{color}">{letter}</font>',
        _CENTERED_CELL,
    )


def _build_key_issues(browsers: Dict, feature_details) -> List[str]:
    descriptions: Dict[str, str] = {}
    if isinstance(feature_details, dict):
        for entries in feature_details.values():
            if isinstance(entries, list):
                for e in entries:
                    fid, desc = e.get("feature"), e.get("description")
                    if fid and desc and fid not in descriptions:
                        descriptions[fid] = desc

    issue_map: Dict[str, List[str]] = {}
    for name, info in browsers.items():
        if not isinstance(info, dict):
            continue
        for feat in info.get("unsupported_features") or []:
            issue_map.setdefault(feat, []).append(name.capitalize())

    total = len(browsers)
    out: List[str] = []
    for feat, where in issue_map.items():
        desc = descriptions.get(feat, feat)
        if len(where) == total and total > 0:
            out.append(f"{desc} ({feat}): unsupported across all browsers")
        else:
            out.append(f"{desc} ({feat}): unsupported in {', '.join(where)}")
    return out
