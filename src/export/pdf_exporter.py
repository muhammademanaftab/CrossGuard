"""PDF export for Cross Guard analysis reports.

Creates a professionally designed PDF report using ReportLab.
All rendering logic lives here, independent of any GUI framework.
"""

from datetime import datetime
from typing import Dict, List

# Color scheme matching the app theme
COLORS = {
    'primary': '#58a6ff',
    'primary_dark': '#1a3a5c',
    'bg_dark': '#0d1117',
    'bg_medium': '#161b22',
    'bg_light': '#21262d',
    'text_primary': '#f0f6fc',
    'text_secondary': '#8b949e',
    'success': '#3fb950',
    'warning': '#d29922',
    'danger': '#f85149',
    'html_color': '#e34c26',
    'css_color': '#264de4',
    'js_color': '#f7df1e',
    'border': '#30363d',
    'text_body': '#c9d1d9',
    'footer': '#6e7681',
    'critical_bg': '#4a1e1c',
}


def export_pdf(report: Dict, output_path: str) -> str:
    """Export an analysis report as a professionally designed PDF.

    Args:
        report: Analysis report dictionary (from AnalysisResult.to_dict()).
        output_path: Path where the PDF will be written.

    Returns:
        The output file path.

    Raises:
        ValueError: If report is empty or None.
        ImportError: If reportlab is not installed.
    """
    if not report:
        raise ValueError("No analysis report to export")

    _create_professional_pdf(report, output_path)
    return output_path


# ── Internal PDF builder ──────────────────────────────────────────────


def _create_professional_pdf(report: Dict, file_path: str):
    """Create a professionally designed PDF report."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable,
    )
    from reportlab.lib.units import inch

    # Extract data
    summary = report.get('summary', {})
    scores = report.get('scores', {})
    browsers = report.get('browsers', {})
    recommendations = report.get('recommendations', [])

    # Create document
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Custom styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor(COLORS['primary']),
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor(COLORS['text_secondary']),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(COLORS['text_primary']),
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor(COLORS['bg_light']),
        borderPadding=(10, 10, 10, 10),
        leftIndent=-10,
        rightIndent=-10,
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor(COLORS['text_body']),
        spaceBefore=5,
        spaceAfter=5,
    )

    story = []

    # ── Header ────────────────────────────────────────────────────────
    story.append(_create_header_section(title_style, subtitle_style))
    story.append(Spacer(1, 0.3 * inch))

    # ── Score overview ────────────────────────────────────────────────
    story.append(Paragraph("COMPATIBILITY SCORE", section_style))
    story.append(Spacer(1, 0.2 * inch))

    score_drawing = _create_score_gauge(
        scores.get('weighted_score', 0) or 0,
        scores.get('grade', 'N/A') or 'N/A',
        scores.get('risk_level', 'unknown') or 'unknown',
    )
    story.append(score_drawing)
    story.append(Spacer(1, 0.3 * inch))
    story.append(_create_score_table(scores))
    story.append(Spacer(1, 0.4 * inch))

    # ── Feature summary ──────────────────────────────────────────────
    story.append(Paragraph("FEATURE ANALYSIS", section_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(_create_feature_pie_chart(summary))
    story.append(Spacer(1, 0.2 * inch))
    story.append(_create_summary_table(summary))
    story.append(Spacer(1, 0.4 * inch))

    # ── Browser compatibility ────────────────────────────────────────
    story.append(Paragraph("BROWSER COMPATIBILITY", section_style))
    story.append(Spacer(1, 0.2 * inch))
    if browsers:
        story.append(_create_browser_bar_chart(browsers))
        story.append(Spacer(1, 0.3 * inch))
        story.append(_create_browser_table(browsers))
    story.append(Spacer(1, 0.4 * inch))

    # ── Detailed browser analysis ────────────────────────────────────
    if browsers:
        story.append(PageBreak())
        story.append(Paragraph("DETAILED BROWSER ANALYSIS", section_style))
        story.append(Spacer(1, 0.2 * inch))
        for browser_name, details in browsers.items():
            story.append(_create_browser_detail_section(browser_name, details, styles))
            story.append(Spacer(1, 0.3 * inch))

    # ── Recommendations ──────────────────────────────────────────────
    if recommendations:
        story.append(Paragraph("RECOMMENDATIONS", section_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(_create_recommendations_section(recommendations, body_style))

    # ── Footer ────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(COLORS['border'])))
    story.append(Spacer(1, 0.1 * inch))

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor(COLORS['footer']),
        alignment=TA_CENTER,
    )
    story.append(Paragraph(
        f"Generated by Cross Guard \u2022 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        footer_style,
    ))

    doc.build(story)


# ── Section builders ─────────────────────────────────────────────────


def _create_header_section(title_style, subtitle_style):
    from reportlab.platypus import Paragraph, Table, TableStyle
    from reportlab.lib.units import inch

    header_data = [
        [Paragraph("\u25C7 CROSS GUARD", title_style)],
        [Paragraph("Browser Compatibility Analysis Report", subtitle_style)],
        [Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", subtitle_style)],
    ]
    header_table = Table(header_data, colWidths=[6.5 * inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return header_table


def _create_score_gauge(score: float, grade: str, risk_level: str):
    from reportlab.graphics.shapes import Drawing, Circle, String, Rect
    from reportlab.lib import colors

    score = float(score or 0)
    grade = str(grade or 'N/A')
    risk_level = str(risk_level or 'unknown')

    drawing = Drawing(400, 150)

    if score >= 90:
        score_color = colors.HexColor('#3fb950')
    elif score >= 75:
        score_color = colors.HexColor('#56d364')
    elif score >= 60:
        score_color = colors.HexColor('#d29922')
    elif score >= 40:
        score_color = colors.HexColor('#f0883e')
    else:
        score_color = colors.HexColor('#f85149')

    drawing.add(Rect(50, 20, 300, 110,
                     fillColor=colors.HexColor(COLORS['bg_medium']),
                     strokeColor=colors.HexColor(COLORS['border']),
                     strokeWidth=1, rx=8, ry=8))

    drawing.add(String(200, 95, f"{score:.0f}%",
                       fontSize=42, fontName='Helvetica-Bold',
                       fillColor=score_color, textAnchor='middle'))

    drawing.add(Rect(160, 55, 80, 28,
                     fillColor=score_color, strokeColor=None, rx=4, ry=4))
    drawing.add(String(200, 63, f"Grade {grade}",
                       fontSize=14, fontName='Helvetica-Bold',
                       fillColor=colors.white, textAnchor='middle'))

    risk_colors = {
        'low': colors.HexColor('#3fb950'),
        'medium': colors.HexColor('#d29922'),
        'high': colors.HexColor('#f85149'),
    }
    risk_color = risk_colors.get(risk_level.lower(), colors.HexColor(COLORS['text_secondary']))

    drawing.add(String(200, 35, f"{risk_level.upper()} RISK",
                       fontSize=11, fontName='Helvetica-Bold',
                       fillColor=risk_color, textAnchor='middle'))

    bar_width = 260
    bar_height = 8
    bar_x = 70
    bar_y = 25

    drawing.add(Rect(bar_x, bar_y, bar_width, bar_height,
                     fillColor=colors.HexColor(COLORS['bg_light']),
                     strokeColor=None, rx=4, ry=4))
    if score > 0:
        filled_width = (score / 100) * bar_width
        drawing.add(Rect(bar_x, bar_y, filled_width, bar_height,
                         fillColor=score_color, strokeColor=None, rx=4, ry=4))

    return drawing


def _create_score_table(scores: Dict):
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    simple_score = float(scores.get('simple_score', 0) or 0)
    weighted_score = float(scores.get('weighted_score', 0) or 0)
    grade = scores.get('grade', 'N/A') or 'N/A'
    risk_level = (scores.get('risk_level', 'N/A') or 'N/A').capitalize()

    data = [
        ['Metric', 'Value'],
        ['Simple Score', f"{simple_score:.1f}%"],
        ['Weighted Score', f"{weighted_score:.1f}%"],
        ['Grade', grade],
        ['Risk Level', risk_level],
    ]

    table = Table(data, colWidths=[2.5 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS['bg_medium'])),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLORS['text_body'])),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor(COLORS['bg_light'])),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor(COLORS['bg_light'])),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['border'])),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(COLORS['border'])),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    return table


def _create_feature_pie_chart(summary: Dict):
    from reportlab.graphics.shapes import Drawing, String, Rect
    from reportlab.lib import colors

    html_count = summary.get('html_features', 0) or 0
    css_count = summary.get('css_features', 0) or 0
    js_count = summary.get('js_features', 0) or 0
    total = html_count + css_count + js_count

    drawing = Drawing(450, 140)
    drawing.add(String(225, 125, "Feature Distribution",
                       fontSize=12, fontName='Helvetica-Bold',
                       fillColor=colors.HexColor(COLORS['text_primary']),
                       textAnchor='middle'))

    if total == 0:
        drawing.add(String(225, 60, "No features detected",
                           fontSize=14, fillColor=colors.HexColor(COLORS['text_secondary']),
                           textAnchor='middle'))
        return drawing

    all_items = [
        ('HTML', COLORS['html_color'], html_count),
        ('CSS', COLORS['css_color'], css_count),
        ('JavaScript', COLORS['js_color'], js_count),
    ]

    bar_height = 24
    max_width = 250
    start_x = 100
    start_y = 95

    for i, (label, color, count) in enumerate(all_items):
        y = start_y - (i * 35)
        pct = (count / total * 100) if total > 0 else 0

        drawing.add(String(start_x - 10, y + 6, label,
                           fontSize=11, fontName='Helvetica-Bold',
                           fillColor=colors.HexColor(COLORS['text_body']),
                           textAnchor='end'))
        drawing.add(Rect(start_x, y, max_width, bar_height,
                         fillColor=colors.HexColor(COLORS['bg_light']),
                         strokeColor=None, rx=4, ry=4))
        if count > 0:
            bar_w = (pct / 100) * max_width
            drawing.add(Rect(start_x, y, bar_w, bar_height,
                             fillColor=colors.HexColor(color),
                             strokeColor=None, rx=4, ry=4))
        drawing.add(String(start_x + max_width + 15, y + 6,
                           f"{count} ({pct:.0f}%)",
                           fontSize=10, fontName='Helvetica',
                           fillColor=colors.HexColor(COLORS['text_secondary'])))

    return drawing


def _create_summary_table(summary: Dict):
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    data = [
        ['Category', 'Count', 'Details'],
        ['Total Features', str(summary.get('total_features', 0) or 0), 'All detected features'],
        ['HTML Features', str(summary.get('html_features', 0) or 0), 'Elements, attributes, input types'],
        ['CSS Features', str(summary.get('css_features', 0) or 0), 'Properties, selectors, at-rules'],
        ['JS Features', str(summary.get('js_features', 0) or 0), 'APIs, methods, syntax'],
        ['Critical Issues', str(summary.get('critical_issues', 0) or 0), 'Features with < 50% support'],
    ]

    table = Table(data, colWidths=[1.8 * inch, 1 * inch, 3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS['bg_medium'])),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLORS['text_body'])),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor(COLORS['bg_light'])),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor(COLORS['bg_light'])),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor(COLORS['critical_bg'])),
        ('TEXTCOLOR', (0, 5), (-1, 5), colors.HexColor(COLORS['danger'])),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['border'])),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return table


def _create_browser_bar_chart(browsers: Dict):
    from reportlab.graphics.shapes import Drawing, String, Rect
    from reportlab.lib import colors

    if not browsers:
        drawing = Drawing(500, 100)
        drawing.add(String(250, 50, "No browser data available",
                           fontSize=14, fillColor=colors.HexColor(COLORS['text_secondary']),
                           textAnchor='middle'))
        return drawing

    num_browsers = len(browsers)
    drawing = Drawing(500, 40 + num_browsers * 50)

    drawing.add(String(250, 30 + num_browsers * 50,
                       "Browser Compatibility Comparison",
                       fontSize=12, fontName='Helvetica-Bold',
                       fillColor=colors.HexColor(COLORS['text_primary']),
                       textAnchor='middle'))

    bar_height = 25
    max_width = 300
    start_x = 120
    start_y = num_browsers * 50

    for i, (browser_name, details) in enumerate(browsers.items()):
        y = start_y - (i * 50)
        pct = float(details.get('compatibility_percentage', 0) or 0)

        drawing.add(String(start_x - 10, y + 8, browser_name.capitalize(),
                           fontSize=11, fontName='Helvetica-Bold',
                           fillColor=colors.HexColor(COLORS['text_body']),
                           textAnchor='end'))
        drawing.add(Rect(start_x, y, max_width, bar_height,
                         fillColor=colors.HexColor(COLORS['bg_light']),
                         strokeColor=None, rx=4, ry=4))

        if pct >= 90:
            bar_color = colors.HexColor('#3fb950')
        elif pct >= 75:
            bar_color = colors.HexColor('#56d364')
        elif pct >= 60:
            bar_color = colors.HexColor('#d29922')
        else:
            bar_color = colors.HexColor('#f85149')

        if pct > 0:
            bar_w = (pct / 100) * max_width
            drawing.add(Rect(start_x, y, bar_w, bar_height,
                             fillColor=bar_color, strokeColor=None, rx=4, ry=4))
        drawing.add(String(start_x + max_width + 15, y + 8, f"{pct:.1f}%",
                           fontSize=11, fontName='Helvetica-Bold',
                           fillColor=bar_color))

    return drawing


def _create_browser_table(browsers: Dict):
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    data = [['Browser', 'Version', 'Compatibility', 'Supported', 'Partial', 'Unsupported']]

    for browser_name, details in browsers.items():
        pct = float(details.get('compatibility_percentage', 0) or 0)
        data.append([
            browser_name.capitalize(),
            str(details.get('version', '')),
            f"{pct:.1f}%",
            str(details.get('supported', 0) or 0),
            str(details.get('partial', 0) or 0),
            str(details.get('unsupported', 0) or 0),
        ])

    table = Table(data, colWidths=[1.2 * inch, 0.8 * inch, 1.1 * inch,
                                   0.9 * inch, 0.8 * inch, 1 * inch])

    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS['bg_medium'])),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(COLORS['text_body'])),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['border'])),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]

    for i, (browser_name, details) in enumerate(browsers.items(), 1):
        pct = float(details.get('compatibility_percentage', 0) or 0)
        if pct >= 90:
            c = '#3fb950'
        elif pct >= 75:
            c = '#56d364'
        elif pct >= 60:
            c = '#d29922'
        else:
            c = '#f85149'
        style_commands.append(('TEXTCOLOR', (2, i), (2, i), colors.HexColor(c)))

    table.setStyle(TableStyle(style_commands))
    return table


def _create_browser_detail_section(browser_name: str, details: Dict, styles):
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.styles import ParagraphStyle

    browser_style = ParagraphStyle(
        'BrowserHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor(COLORS['primary']),
        spaceBefore=10,
        spaceAfter=5,
    )

    pct = float(details.get('compatibility_percentage', 0) or 0)
    version = details.get('version', '') or ''

    if pct >= 90:
        status_color = '#3fb950'
        status_text = 'Excellent'
    elif pct >= 75:
        status_color = '#56d364'
        status_text = 'Good'
    elif pct >= 60:
        status_color = '#d29922'
        status_text = 'Fair'
    else:
        status_color = '#f85149'
        status_text = 'Poor'

    header_text = f"{browser_name.capitalize()} {version} - {pct:.1f}% Compatible ({status_text})"
    data = [[Paragraph(f"<font color='{status_color}'>{header_text}</font>", browser_style)]]

    unsupported = details.get('unsupported_features', [])
    if unsupported:
        features_text = ', '.join(unsupported[:10])
        if len(unsupported) > 10:
            features_text += f'... (+{len(unsupported) - 10} more)'
        data.append([Paragraph(
            f"<b>Unsupported ({len(unsupported)}):</b> "
            f"<font color='#f85149'>{features_text}</font>",
            styles['Normal'],
        )])

    partial = details.get('partial_features', [])
    if partial:
        features_text = ', '.join(partial[:10])
        if len(partial) > 10:
            features_text += f'... (+{len(partial) - 10} more)'
        data.append([Paragraph(
            f"<b>Partial ({len(partial)}):</b> "
            f"<font color='#d29922'>{features_text}</font>",
            styles['Normal'],
        )])

    table = Table(data, colWidths=[6.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLORS['bg_medium'])),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(COLORS['border'])),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    return table


def _create_recommendations_section(recommendations: List[str], body_style):
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.styles import ParagraphStyle

    rec_style = ParagraphStyle(
        'Recommendation',
        parent=body_style,
        fontSize=10,
        textColor=colors.HexColor(COLORS['text_body']),
        leftIndent=20,
        bulletIndent=10,
    )

    data = []
    for i, rec in enumerate(recommendations, 1):
        data.append([
            Paragraph(f"<font color='{COLORS['primary']}'><b>{i}.</b></font>", body_style),
            Paragraph(rec, rec_style),
        ])

    table = Table(data, colWidths=[0.4 * inch, 6 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLORS['bg_medium'])),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(COLORS['border'])),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor(COLORS['bg_light'])),
    ]))
    return table
