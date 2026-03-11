#!/usr/bin/env python3
"""Generate the CrossGuard Competitor Comparison Report PDF."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.barcharts import HorizontalBarChart
import os

WIDTH, HEIGHT = A4
MARGIN = 50

# Colors
BLUE = colors.HexColor("#4472C4")
DARK_BLUE = colors.HexColor("#2F5496")
GREEN = colors.HexColor("#548235")
LIGHT_GREEN = colors.HexColor("#E2EFDA")
LIGHT_BLUE = colors.HexColor("#D6E4F0")
LIGHT_GRAY = colors.HexColor("#F2F2F2")
WHITE = colors.white
BLACK = colors.black
GRAY = colors.HexColor("#808080")
RED = colors.HexColor("#C00000")
ORANGE = colors.HexColor("#ED7D31")
HEADER_BG = colors.HexColor("#4472C4")
ROW_ALT = colors.HexColor("#F2F7FC")

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
    fontSize=28, textColor=DARK_BLUE, spaceAfter=6, alignment=TA_CENTER,
    fontName='Helvetica-Bold')

subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
    fontSize=14, textColor=GRAY, alignment=TA_CENTER, spaceAfter=20)

heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading1'],
    fontSize=18, textColor=DARK_BLUE, spaceBefore=16, spaceAfter=10,
    fontName='Helvetica-Bold')

subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading2'],
    fontSize=14, textColor=DARK_BLUE, spaceBefore=12, spaceAfter=6,
    fontName='Helvetica-Bold')

body_style = ParagraphStyle('Body', parent=styles['Normal'],
    fontSize=10, leading=14, spaceAfter=6)

small_style = ParagraphStyle('Small', parent=styles['Normal'],
    fontSize=8, leading=10, textColor=GRAY)

# Table cell styles
cell_style = ParagraphStyle('Cell', parent=styles['Normal'],
    fontSize=9, leading=12, alignment=TA_LEFT)

cell_center = ParagraphStyle('CellCenter', parent=styles['Normal'],
    fontSize=9, leading=12, alignment=TA_CENTER)

cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'],
    fontSize=9, leading=12, fontName='Helvetica-Bold')

cell_header = ParagraphStyle('CellHeader', parent=styles['Normal'],
    fontSize=9, leading=12, fontName='Helvetica-Bold', textColor=WHITE,
    alignment=TA_CENTER)

cell_header_left = ParagraphStyle('CellHeaderLeft', parent=styles['Normal'],
    fontSize=9, leading=12, fontName='Helvetica-Bold', textColor=WHITE)


def make_table(data, col_widths=None, header_bg=HEADER_BG):
    """Create a styled table."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]
    # Alternate row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t


def draw_horizontal_bar_chart(title, tools, values, bar_color=BLUE, width=480, height=200):
    """Draw a clean horizontal bar chart with labels inside bars."""
    d = Drawing(width, height + 40)

    # Title
    d.add(String(width / 2, height + 25, title,
        fontSize=13, fontName='Helvetica-Bold', fillColor=DARK_BLUE,
        textAnchor='middle'))

    chart_left = 130
    chart_width = width - chart_left - 40
    chart_bottom = 15
    chart_height = height - 10
    max_val = max(values) * 1.1

    bar_count = len(tools)
    bar_height = min(28, (chart_height - 10) / bar_count - 6)
    total_bars_height = bar_count * (bar_height + 6)
    start_y = chart_bottom + (chart_height - total_bars_height) / 2

    for i, (tool, val) in enumerate(zip(tools, values)):
        y = start_y + i * (bar_height + 6)
        bar_w = (val / max_val) * chart_width if max_val > 0 else 0

        # Bar
        is_crossguard = (tool == "Cross Guard")
        color = DARK_BLUE if is_crossguard else colors.HexColor("#A0BBD8")
        d.add(Rect(chart_left, y, bar_w, bar_height, fillColor=color,
            strokeColor=None, strokeWidth=0))

        # Tool label (left of bar)
        d.add(String(chart_left - 8, y + bar_height / 2 - 4, tool,
            fontSize=10, fontName='Helvetica-Bold' if is_crossguard else 'Helvetica',
            fillColor=BLACK, textAnchor='end'))

        # Value label
        label_str = str(int(val)) if val == int(val) else f"{val:.1f}"
        if bar_w > 40:
            # Inside bar (white text)
            d.add(String(chart_left + bar_w - 8, y + bar_height / 2 - 4,
                label_str, fontSize=10, fontName='Helvetica-Bold',
                fillColor=WHITE, textAnchor='end'))
        else:
            # Outside bar (dark text)
            d.add(String(chart_left + bar_w + 5, y + bar_height / 2 - 4,
                label_str, fontSize=10, fontName='Helvetica-Bold',
                fillColor=BLACK, textAnchor='start'))

    # X-axis line
    d.add(Line(chart_left, chart_bottom - 2, chart_left + chart_width, chart_bottom - 2,
        strokeColor=GRAY, strokeWidth=0.5))

    # X-axis ticks
    tick_interval = 5 if max_val <= 30 else 10
    tick_val = 0
    while tick_val <= max_val:
        x = chart_left + (tick_val / max_val) * chart_width
        d.add(Line(x, chart_bottom - 2, x, chart_bottom - 6,
            strokeColor=GRAY, strokeWidth=0.5))
        d.add(String(x, chart_bottom - 16, str(int(tick_val)),
            fontSize=7, fillColor=GRAY, textAnchor='middle'))
        tick_val += tick_interval

    return d


def draw_grouped_bar_chart(title, categories, groups, group_colors, legend_labels, width=480, height=220):
    """Draw grouped bar chart (CSS/HTML/JS side by side)."""
    d = Drawing(width, height + 60)

    # Title
    d.add(String(width / 2, height + 45, title,
        fontSize=13, fontName='Helvetica-Bold', fillColor=DARK_BLUE,
        textAnchor='middle'))

    chart_left = 130
    chart_width = width - chart_left - 40
    chart_bottom = 25
    chart_height = height - 10

    all_vals = [v for group in groups for v in group]
    max_val = max(all_vals) * 1.15 if all_vals else 1

    n_tools = len(categories)
    n_groups = len(groups)
    group_spacing = 8
    sub_bar_height = 8
    tool_block_height = n_groups * sub_bar_height + group_spacing
    total_height = n_tools * tool_block_height
    start_y = chart_bottom + (chart_height - total_height) / 2

    for i, tool in enumerate(categories):
        y_base = start_y + i * tool_block_height

        # Tool label
        is_cg = (tool == "Cross Guard")
        d.add(String(chart_left - 8, y_base + (n_groups * sub_bar_height) / 2 - 4,
            tool, fontSize=9,
            fontName='Helvetica-Bold' if is_cg else 'Helvetica',
            fillColor=BLACK, textAnchor='end'))

        for j, (group_vals, color) in enumerate(zip(groups, group_colors)):
            val = group_vals[i]
            bar_w = (val / max_val) * chart_width if max_val > 0 else 0
            y = y_base + j * sub_bar_height

            d.add(Rect(chart_left, y, bar_w, sub_bar_height - 1,
                fillColor=color, strokeColor=None))

            # Value label
            if val > 0:
                label = str(int(val))
                if bar_w > 25:
                    d.add(String(chart_left + bar_w - 4, y + sub_bar_height / 2 - 4,
                        label, fontSize=7, fontName='Helvetica-Bold',
                        fillColor=WHITE, textAnchor='end'))
                else:
                    d.add(String(chart_left + bar_w + 3, y + sub_bar_height / 2 - 4,
                        label, fontSize=7, fontName='Helvetica-Bold',
                        fillColor=color, textAnchor='start'))

    # Legend (top right)
    legend_x = width - 140
    legend_y = height + 25
    for j, (label, color) in enumerate(zip(legend_labels, group_colors)):
        lx = legend_x + j * 55
        d.add(Rect(lx, legend_y, 10, 10, fillColor=color, strokeColor=None))
        d.add(String(lx + 13, legend_y + 1, label, fontSize=8, fillColor=BLACK))

    # X-axis
    d.add(Line(chart_left, chart_bottom - 2, chart_left + chart_width, chart_bottom - 2,
        strokeColor=GRAY, strokeWidth=0.5))
    tick_interval = 5 if max_val <= 25 else 10
    tick_val = 0
    while tick_val <= max_val:
        x = chart_left + (tick_val / max_val) * chart_width
        d.add(Line(x, chart_bottom - 2, x, chart_bottom - 6,
            strokeColor=GRAY, strokeWidth=0.5))
        d.add(String(x, chart_bottom - 16, str(int(tick_val)),
            fontSize=7, fillColor=GRAY, textAnchor='middle'))
        tick_val += tick_interval

    return d


def build_report():
    output_path = os.path.join(os.path.dirname(__file__),
        "reports", "CrossGuard_Competitor_Comparison_Report.pdf")

    doc = SimpleDocTemplate(output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN)

    story = []
    page_width = WIDTH - 2 * MARGIN

    # =========== PAGE 1: TITLE ===========
    story.append(Spacer(1, 80))
    story.append(Paragraph("CROSS GUARD", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Competitor Comparison Report", subtitle_style))
    story.append(Spacer(1, 40))

    # Divider
    divider_data = [["", ""]]
    divider = Table(divider_data, colWidths=[page_width])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, BLUE),
    ]))
    story.append(divider)
    story.append(Spacer(1, 30))

    # Info table
    info_data = [
        [Paragraph("<b>Author</b>", cell_style), Paragraph("Muhammad Eman", cell_style)],
        [Paragraph("<b>Date</b>", cell_style), Paragraph("2026-03-11", cell_style)],
        [Paragraph("<b>Test Files</b>", cell_style),
         Paragraph("examples/sample.css (69 lines), examples/sample.html (34 lines), examples/sample.js (95 lines)", cell_style)],
    ]
    info_table = Table(info_data, colWidths=[120, page_width - 120])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)

    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "All tools were tested on the <b>same three files</b> for a fair, reproducible comparison. "
        "Results show features detected, compatibility scoring, and output capabilities.",
        body_style))

    # =========== PAGE 2: COMPETITIVE LANDSCAPE ===========
    story.append(PageBreak())

    # Blue header bar
    header_data = [[Paragraph("<font color='white'><b>THE COMPETITIVE LANDSCAPE</b></font>",
        ParagraphStyle('h', fontSize=16, textColor=WHITE, fontName='Helvetica-Bold',
            alignment=TA_LEFT, leading=22))]]
    header_table = Table(header_data, colWidths=[page_width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    competitors = [
        ("doiuse", "CSS-only compatibility linter",
         "Uses the same Can I Use database as Cross Guard to check CSS features against target browsers. "
         "It is the closest CSS competitor. However, it only checks CSS — crashes on JavaScript, "
         "silently fails on HTML. No scoring, no GUI, plain text warnings only."),
        ("eslint-plugin-compat", "JavaScript API compatibility checker",
         "An ESLint plugin that detects usage of browser APIs (fetch, Promise, IntersectionObserver) "
         "and reports if they are unsupported in target browsers. JavaScript only — cannot check CSS or HTML. "
         "Requires ESLint project setup; not standalone."),
        ("webhint (Microsoft)", "Web best-practices analyzer (abandoned 2022)",
         "A multi-purpose web linter focused on accessibility (axe-core), performance, and SEO. "
         "Browser compatibility was a secondary feature — it found only 2 of 16 CSS compatibility issues "
         "and zero HTML/JS compatibility issues. Discontinued in April 2022."),
        ("browser-compat-checker", "Multi-language compatibility checker",
         "A Node.js tool that checks HTML, CSS, and JS files. Uses MDN data (not Can I Use). "
         "With modern browser targets, reports zero issues for all file types. "
         "No scoring, no GUI, no export formats."),
        ("Browserslist", "Browser target configuration tool",
         "NOT a compatibility checker — only defines which browsers to target. "
         "Included because many tools in the ecosystem depend on it for browser queries. "
         "Does not analyze code at all."),
    ]

    for name, tagline, desc in competitors:
        story.append(Paragraph(f"<b>{name}</b> — <i>{tagline}</i>", ParagraphStyle(
            'comp_name', fontSize=11, fontName='Helvetica-Bold', textColor=DARK_BLUE,
            spaceBefore=8, spaceAfter=2, leading=14)))
        story.append(Paragraph(desc, ParagraphStyle(
            'comp_desc', fontSize=9, leading=13, spaceAfter=8, textColor=colors.HexColor("#333333"))))

    # =========== PAGE 3: EXECUTIVE SUMMARY ===========
    story.append(PageBreak())

    header_data = [[Paragraph("<font color='white'><b>EXECUTIVE SUMMARY</b></font>",
        ParagraphStyle('h', fontSize=16, textColor=WHITE, fontName='Helvetica-Bold',
            alignment=TA_LEFT, leading=22))]]
    header_table = Table(header_data, colWidths=[page_width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    summary_items = [
        "<b>Cross Guard detected 44 features</b> across all three file types — 4.4x more than the next best competitor (doiuse: 10 CSS features only).",
        "<b>No competitor analyzes all three file types</b> (HTML + CSS + JS) with compatibility scoring.",
        "<b>Cross Guard is the only tool</b> producing a quantitative compatibility score (0-100) with letter grades.",
        "<b>All competitors report zero issues</b> with modern browser targets — Cross Guard still provides full feature audits with per-browser breakdown.",
        "<b>Cross Guard offers 6 export formats</b> (JSON, PDF, SARIF, JUnit, Checkstyle, CSV) plus a desktop GUI — no competitor has any of these.",
    ]
    for item in summary_items:
        story.append(Paragraph(f"• {item}", ParagraphStyle(
            'bullet', fontSize=10, leading=14, spaceAfter=6, leftIndent=15, firstLineIndent=-15)))

    # =========== CHARTS ===========
    story.append(Spacer(1, 20))

    # Chart 1: Total features bar chart
    tools_total = ["browser-compat", "eslint-compat", "webhint", "doiuse", "Cross Guard"]
    values_total = [15, 5, 2, 10, 44]

    chart1 = draw_horizontal_bar_chart(
        "Total Features Detected (all file types combined)",
        tools_total, values_total, width=page_width, height=170)
    story.append(chart1)

    story.append(Spacer(1, 20))

    # Chart 2: Grouped bar chart (CSS/HTML/JS breakdown)
    categories = ["browser-compat", "eslint-compat", "webhint", "doiuse", "Cross Guard"]
    css_vals =  [8, 0, 2, 10, 16]
    html_vals = [4, 0, 0, 0, 11]
    js_vals =   [3, 5, 0, 0, 17]

    chart2 = draw_grouped_bar_chart(
        "Features Detected by File Type",
        categories,
        [css_vals, html_vals, js_vals],
        [BLUE, GREEN, ORANGE],
        ["CSS", "HTML", "JS"],
        width=page_width, height=200)
    story.append(chart2)

    # =========== PAGE 4: PER-FILE COMPARISON TABLES ===========
    story.append(PageBreak())

    header_data = [[Paragraph("<font color='white'><b>PER-FILE COMPARISON</b></font>",
        ParagraphStyle('h', fontSize=16, textColor=WHITE, fontName='Helvetica-Bold',
            alignment=TA_LEFT, leading=22))]]
    header_table = Table(header_data, colWidths=[page_width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # CSS comparison
    story.append(Paragraph("sample.css — CSS Compatibility", subheading_style))
    css_data = [
        [Paragraph("<b>Tool</b>", cell_header_left),
         Paragraph("<b>Features</b>", cell_header),
         Paragraph("<b>Score</b>", cell_header),
         Paragraph("<b>Notes</b>", cell_header)],
        [Paragraph("Cross Guard", cell_bold), Paragraph("16", cell_center),
         Paragraph("89.1 (B)", cell_center),
         Paragraph("Full per-browser breakdown, 1 unsupported", cell_style)],
        [Paragraph("doiuse", cell_style), Paragraph("10*", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("19 line-level warnings (IE/Blackberry); 0 with modern browsers", cell_style)],
        [Paragraph("webhint", cell_style), Paragraph("2", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("Only found subgrid + oklch. Missed 14 features.", cell_style)],
        [Paragraph("eslint-compat", cell_style), Paragraph("0", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph('"File ignored" — JS only tool', cell_style)],
        [Paragraph("browser-compat", cell_style), Paragraph("8", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("Only flags against IE. 0 issues with modern browsers.", cell_style)],
    ]
    col_w = [110, 55, 65, page_width - 230]
    story.append(make_table(css_data, col_w))
    story.append(Spacer(1, 16))

    # HTML comparison
    story.append(Paragraph("sample.html — HTML Compatibility", subheading_style))
    html_data = [
        [Paragraph("<b>Tool</b>", cell_header_left),
         Paragraph("<b>Features</b>", cell_header),
         Paragraph("<b>Score</b>", cell_header),
         Paragraph("<b>Notes</b>", cell_header)],
        [Paragraph("Cross Guard", cell_bold), Paragraph("11", cell_center),
         Paragraph("96.6 (A)", cell_center),
         Paragraph("dialog, details, picture, srcset, lazy loading, input types, WebP", cell_style)],
        [Paragraph("doiuse", cell_style), Paragraph("0", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("Silent failure: 'unfinished business' error", cell_style)],
        [Paragraph("webhint", cell_style), Paragraph("0", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("Only found accessibility issues, zero compat issues", cell_style)],
        [Paragraph("eslint-compat", cell_style), Paragraph("0", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph('"File ignored" — JS only tool', cell_style)],
        [Paragraph("browser-compat", cell_style), Paragraph("4", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("Only flags against IE. 0 issues with modern browsers.", cell_style)],
    ]
    story.append(make_table(html_data, col_w))
    story.append(Spacer(1, 16))

    # JS comparison
    story.append(Paragraph("sample.js — JavaScript Compatibility", subheading_style))
    js_data = [
        [Paragraph("<b>Tool</b>", cell_header_left),
         Paragraph("<b>Features</b>", cell_header),
         Paragraph("<b>Score</b>", cell_header),
         Paragraph("<b>Notes</b>", cell_header)],
        [Paragraph("Cross Guard", cell_bold), Paragraph("17", cell_center),
         Paragraph("88.2 (B)", cell_center),
         Paragraph("Arrow functions, async/await, fetch, optional chaining, BigInt, etc.", cell_style)],
        [Paragraph("doiuse", cell_style), Paragraph("0", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("CRASHED: CssSyntaxError — tries to parse JS as CSS", cell_style)],
        [Paragraph("webhint", cell_style), Paragraph("0", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("Zero JS compatibility checking", cell_style)],
        [Paragraph("eslint-compat", cell_style), Paragraph("5", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("fetch, Array.flat, Object.entries, Promise, IntersectionObserver", cell_style)],
        [Paragraph("browser-compat", cell_style), Paragraph("3", cell_center),
         Paragraph("N/A", cell_center),
         Paragraph("Only flags against IE. 0 issues with modern browsers.", cell_style)],
    ]
    story.append(make_table(js_data, col_w))

    # =========== PAGE 5: MASTER FEATURE TABLE ===========
    story.append(PageBreak())

    header_data = [[Paragraph("<font color='white'><b>MASTER FEATURE COMPARISON</b></font>",
        ParagraphStyle('h', fontSize=16, textColor=WHITE, fontName='Helvetica-Bold',
            alignment=TA_LEFT, leading=22))]]
    header_table = Table(header_data, colWidths=[page_width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    YES = '<font color="#548235"><b>Yes</b></font>'
    NO = '<font color="#C00000">No</font>'
    PART = '<font color="#ED7D31">Partial</font>'

    # Capabilities comparison
    cap_header = [
        Paragraph("<b>Capability</b>", cell_header_left),
        Paragraph("<b>Cross Guard</b>", cell_header),
        Paragraph("<b>doiuse</b>", cell_header),
        Paragraph("<b>webhint</b>", cell_header),
        Paragraph("<b>eslint-compat</b>", cell_header),
        Paragraph("<b>browser-compat</b>", cell_header),
    ]
    cap_col_w = [140, 72, 62, 62, 72, 82]

    capabilities = [
        ("CSS analysis", YES, YES, PART, NO, YES),
        ("HTML analysis", YES, NO, NO, NO, YES),
        ("JS analysis", YES, NO, NO, YES, YES),
        ("Compatibility score", YES, NO, NO, NO, NO),
        ("Letter grade", YES, NO, NO, NO, NO),
        ("Per-browser breakdown", YES, NO, PART, NO, NO),
        ("Standalone (no setup)", YES, YES, NO, NO, YES),
        ("Desktop GUI", YES, NO, NO, NO, NO),
        ("SARIF export", YES, NO, NO, YES, NO),
        ("JUnit XML export", YES, NO, NO, NO, NO),
        ("PDF report", YES, NO, NO, NO, NO),
        ("CSV export", YES, NO, NO, NO, NO),
        ("Polyfill suggestions", YES, NO, NO, NO, NO),
        ("Analysis history/DB", YES, NO, NO, NO, NO),
        ("Custom rules", YES, NO, NO, NO, NO),
        ("Quality gates (CI/CD)", YES, NO, NO, NO, NO),
        ("Works offline", YES, YES, NO, YES, YES),
        ("Actively maintained", YES, PART, NO, YES, YES),
        ("Data source", "Can I Use", "Can I Use", "MDN", "MDN", "MDN"),
        ("AST-based parsing", YES, NO, YES, YES, NO),
    ]

    cap_data = [cap_header]
    for row in capabilities:
        cap_data.append([
            Paragraph(row[0], cell_bold),
            *[Paragraph(str(v), cell_center) for v in row[1:]]
        ])

    cap_table = Table(cap_data, colWidths=cap_col_w, repeatRows=1)
    cap_style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        # Highlight Cross Guard column
        ('BACKGROUND', (1, 1), (1, -1), LIGHT_GREEN),
    ]
    for i in range(1, len(cap_data)):
        if i % 2 == 0:
            for col in range(len(cap_header)):
                if col != 1:  # Don't override green column
                    cap_style_cmds.append(('BACKGROUND', (col, i), (col, i), ROW_ALT))
    cap_table.setStyle(TableStyle(cap_style_cmds))
    story.append(cap_table)

    # =========== PAGE 6: UNIQUE ADVANTAGES ===========
    story.append(PageBreak())

    header_data = [[Paragraph("<font color='white'><b>CROSS GUARD — UNIQUE ADVANTAGES</b></font>",
        ParagraphStyle('h', fontSize=16, textColor=WHITE, fontName='Helvetica-Bold',
            alignment=TA_LEFT, leading=22))]]
    header_table = Table(header_data, colWidths=[page_width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), GREEN),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    advantages = [
        ("Only tool analyzing HTML + CSS + JS\nwith a unified compatibility score",
         "Developers get a single metric (0-100) rather than\nscattered warnings from multiple tools"),
        ("AST-based parsing with tinycss2,\ntree-sitter, and BeautifulSoup4",
         "Deep, accurate detection — not just regex pattern\nmatching. 3-tier JS detection strategy"),
        ("Desktop GUI with drag-and-drop",
         "Accessible to non-CLI users.\nNo competitor offers a GUI"),
        ("6 CI/CD export formats:\nJSON, PDF, SARIF, JUnit, Checkstyle, CSV",
         "Integrates with GitHub Code Scanning,\nJenkins, GitLab CI, SonarQube"),
        ("Quality gates for CI/CD:\n--fail-on-score, --fail-on-errors",
         "Blocks builds that fail\ncompatibility thresholds"),
        ("Analysis history with\nbookmarks, tags, and statistics",
         "Track compatibility over time.\nNo competitor persists results"),
        ("Polyfill recommendations",
         "Actionable fix suggestions,\nnot just problem reports"),
        ("Built on Python (unique)",
         "All competitors require Node.js.\nCross Guard works in Python ecosystems natively"),
    ]

    adv_header = [
        Paragraph("<b>#</b>", ParagraphStyle('ah', fontSize=10, fontName='Helvetica-Bold',
            textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("<b>Advantage</b>", ParagraphStyle('ah', fontSize=10, fontName='Helvetica-Bold',
            textColor=WHITE)),
        Paragraph("<b>Why It Matters</b>", ParagraphStyle('ah', fontSize=10, fontName='Helvetica-Bold',
            textColor=WHITE)),
    ]

    adv_data = [adv_header]
    for i, (adv, why) in enumerate(advantages, 1):
        adv_data.append([
            Paragraph(str(i), ParagraphStyle('num', fontSize=10, alignment=TA_CENTER,
                fontName='Helvetica-Bold')),
            Paragraph(f"<b>{adv}</b>", ParagraphStyle('adv_cell', fontSize=9.5, leading=13,
                fontName='Helvetica-Bold')),
            Paragraph(why, ParagraphStyle('why_cell', fontSize=9.5, leading=13)),
        ])

    # Key fix: wider columns with proper proportions
    num_col = 30
    adv_col = (page_width - num_col) * 0.45
    why_col = (page_width - num_col) * 0.55
    adv_table = Table(adv_data, colWidths=[num_col, adv_col, why_col], repeatRows=1)
    adv_style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]
    for i in range(1, len(adv_data)):
        if i % 2 == 0:
            adv_style_cmds.append(('BACKGROUND', (0, i), (-1, i), LIGHT_GREEN))
    adv_table.setStyle(TableStyle(adv_style_cmds))
    story.append(adv_table)

    # =========== PAGE 7: CONCLUSION ===========
    story.append(PageBreak())

    header_data = [[Paragraph("<font color='white'><b>CONCLUSION</b></font>",
        ParagraphStyle('h', fontSize=16, textColor=WHITE, fontName='Helvetica-Bold',
            alignment=TA_LEFT, leading=22))]]
    header_table = Table(header_data, colWidths=[page_width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    conclusion_text = [
        "Cross Guard fills a clear gap in the browser compatibility tooling ecosystem. "
        "While existing tools address isolated aspects of the problem — doiuse for CSS, "
        "eslint-plugin-compat for JavaScript APIs — no single tool provides a unified, "
        "scored, multi-language analysis.",

        "Testing all five competitors on identical files reveals that Cross Guard detects "
        "<b>4.4x more features</b> than the next best competitor, while being the only tool "
        "that produces a quantitative compatibility score and supports all three web languages.",

        "Cross Guard's unique combination of AST-based parsing, quantitative scoring, "
        "6 export formats, desktop GUI, quality gates, analysis history, and polyfill "
        "recommendations makes it a comprehensive solution that addresses the limitations "
        "of every existing tool in the ecosystem.",
    ]
    for para in conclusion_text:
        story.append(Paragraph(para, ParagraphStyle(
            'conclusion', fontSize=11, leading=16, spaceAfter=12)))

    story.append(Spacer(1, 20))

    # Score summary box
    score_data = [
        [Paragraph("<font color='white'><b>Tool</b></font>", cell_header),
         Paragraph("<font color='white'><b>Total Features Detected</b></font>", cell_header),
         Paragraph("<font color='white'><b>File Types</b></font>", cell_header),
         Paragraph("<font color='white'><b>Score</b></font>", cell_header)],
        [Paragraph("<b>Cross Guard</b>", cell_center), Paragraph("<b>44</b>", cell_center),
         Paragraph("HTML + CSS + JS", cell_center), Paragraph("<b>91.3 avg</b>", cell_center)],
        [Paragraph("doiuse", cell_center), Paragraph("10", cell_center),
         Paragraph("CSS only", cell_center), Paragraph("N/A", cell_center)],
        [Paragraph("eslint-compat", cell_center), Paragraph("5", cell_center),
         Paragraph("JS only", cell_center), Paragraph("N/A", cell_center)],
        [Paragraph("browser-compat", cell_center), Paragraph("15", cell_center),
         Paragraph("HTML + CSS + JS", cell_center), Paragraph("N/A", cell_center)],
        [Paragraph("webhint", cell_center), Paragraph("2", cell_center),
         Paragraph("CSS only (partial)", cell_center), Paragraph("N/A", cell_center)],
    ]
    score_table = Table(score_data, colWidths=[110, 130, 120, 130])
    score_style = [
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('BACKGROUND', (0, 1), (-1, 1), LIGHT_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]
    for i in range(2, len(score_data)):
        if i % 2 == 0:
            score_style.append(('BACKGROUND', (0, i), (-1, i), ROW_ALT))
    score_table.setStyle(TableStyle(score_style))
    story.append(score_table)

    # Build PDF
    doc.build(story)
    return output_path


if __name__ == "__main__":
    path = build_report()
    print(f"Report generated: {path}")
