"""PDF export using ReportLab -- professional compatibility report."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
    SimpleDocTemplate, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, String, Wedge, Circle, Rect

# --- Constants ---

COLORS = {
    'primary': '#2563eb',
    'success': '#16a34a',
    'warning': '#d97706',
    'danger': '#dc2626',
    'neutral': '#6b7280',
    'text_dark': '#111827',
    'bg_light': '#f9fafb',
    'bg_white': '#ffffff',
    'header_bg': '#1e3a5f',
}

SP = 10       # Standard spacing
SP_HALF = 5   # Tight spacing

MAX_ROWS = 12  # Table truncation limit

GRADE_INFO = {
    'A+': ('90-100%', 'Excellent. All features well-supported across target browsers.'),
    'A': ('90-100%', 'Excellent. All features well-supported across target browsers.'),
    'A-': ('85-89%', 'Very good. Nearly all features supported with minimal gaps.'),
    'B+': ('82-84%', 'Good. Minor issues in some browsers; most users unaffected.'),
    'B': ('80-84%', 'Good. Minor issues in some browsers; most users unaffected.'),
    'B-': ('77-79%', 'Above average. A few features need fallbacks.'),
    'C+': ('73-76%', 'Fair. Several features need fallbacks for full coverage.'),
    'C': ('70-76%', 'Fair. Several features need fallbacks for full coverage.'),
    'C-': ('67-69%', 'Below average. Notable compatibility gaps.'),
    'D+': ('63-66%', 'Poor. Significant gaps affecting user experience.'),
    'D': ('60-66%', 'Poor. Significant gaps affecting user experience.'),
    'D-': ('57-59%', 'Very poor. Many features broken in multiple browsers.'),
    'F': ('0-59%', 'Critical. Major features broken across browsers.'),
}

TYPE_COLORS = {
    'html': '#e34c26',
    'css': '#2563eb',
    'js': '#ca8a04',
}


def export_pdf(report: Dict, output_path: str) -> str:
    if not report:
        raise ValueError("No analysis report to export")
    _create_pdf(report, output_path)
    return output_path


# --- Helpers ---

def _hex(key):
    return HexColor(COLORS[key]) if key in COLORS else HexColor(key)


def _score_color(score):
    if score >= 90: return HexColor('#16a34a')
    if score >= 75: return HexColor('#059669')
    if score >= 60: return HexColor('#d97706')
    return HexColor('#dc2626')


def _score_bg(score):
    if score >= 90: return HexColor('#f0fdf4')
    if score >= 75: return HexColor('#ecfdf5')
    if score >= 60: return HexColor('#fffbeb')
    return HexColor('#fef2f2')


def _section_header(text):
    return Paragraph(text, ParagraphStyle(
        f'H_{id(text)}', fontName='Helvetica-Bold', fontSize=13,
        textColor=_hex('bg_white'), backColor=_hex('header_bg'),
        borderPadding=(8, 8, 8, 10), spaceBefore=SP, spaceAfter=12,
    ))


def _executive_verdict(score, grade, critical, browsers):
    if score >= 90:
        return f"Your code has excellent cross-browser compatibility (Grade {grade}). All tested features are well-supported."
    if score >= 75:
        if critical > 0:
            return f"Your code has good compatibility (Grade {grade}) with {critical} feature{'s' if critical != 1 else ''} requiring attention in some browsers."
        return f"Your code has good cross-browser compatibility (Grade {grade}). Minor issues may exist but most users are unaffected."
    if score >= 60:
        return f"Your code has fair compatibility (Grade {grade}). {critical} feature{'s' if critical != 1 else ''} unsupported in some target browsers, requiring fallbacks."

    # Find most affected browser
    worst = min(browsers.items(), key=lambda x: x[1].get('compatibility_percentage', 100)) if browsers else None
    worst_name = worst[0].capitalize() if worst else "some browsers"
    return f"Your code has significant compatibility issues (Grade {grade}). {critical} features are broken in {worst_name} and other browsers."


def _build_issue_list(browsers):
    from src.utils.feature_names import get_feature_name, get_fix_suggestion

    unsupported_map = {}
    partial_map = {}
    for name, details in browsers.items():
        for feat in details.get('unsupported_features', []):
            unsupported_map.setdefault(feat, set()).add(name.capitalize())
        for feat in details.get('partial_features', []):
            partial_map.setdefault(feat, set()).add(name.capitalize())

    issues = []
    for feat, bs in unsupported_map.items():
        n = len(bs)
        issues.append({
            'feature': feat,
            'name': get_feature_name(feat) or feat,
            'status': 'Unsupported',
            'severity': 'High' if n >= 3 else 'Med',
            'sev_color': COLORS['danger'] if n >= 3 else '#ea580c',
            'row_bg': '#fef2f2',
            'browsers': ', '.join(sorted(bs)),
            'browser_count': n,
            'fix': get_fix_suggestion(feat) or '-',
        })
    for feat, bs in partial_map.items():
        if feat not in unsupported_map:
            issues.append({
                'feature': feat,
                'name': get_feature_name(feat) or feat,
                'status': 'Partial',
                'severity': 'Low',
                'sev_color': COLORS['warning'],
                'row_bg': '#fffbeb',
                'browsers': ', '.join(sorted(bs)),
                'browser_count': len(bs),
                'fix': get_fix_suggestion(feat) or '-',
            })

    issues.sort(key=lambda x: (0 if x['status'] == 'Unsupported' else 1, -x['browser_count'], x['name']))
    return issues


# --- Page Footer ---

def _draw_page(canvas, doc):
    w, h = letter
    canvas.saveState()
    canvas.setStrokeColor(_hex('neutral'))
    canvas.setLineWidth(0.5)
    canvas.line(0.6 * inch, 0.42 * inch, w - 0.6 * inch, 0.42 * inch)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(_hex('neutral'))
    canvas.drawString(0.6 * inch, 0.26 * inch, "Cross Guard - Browser Compatibility Report")
    canvas.drawRightString(w - 0.6 * inch, 0.26 * inch, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


# --- Section Builders ---

def _build_header(report):
    fname = Path(report.get('file_path', '')).name if report.get('file_path') else ''
    now = datetime.now().strftime('%B %d, %Y at %H:%M')
    n_browsers = len(report.get('browsers', {}))

    banner = Table([[Paragraph(
        "CROSS GUARD<br/>"
        "<font size='10' color='#93c5fd'>Browser Compatibility Report</font>",
        ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=22,
                       textColor=colors.white, alignment=TA_CENTER, leading=28),
    )]], colWidths=[7.3 * inch])
    banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _hex('header_bg')),
        ('TOPPADDING', (0, 0), (0, 0), 14),
        ('BOTTOMPADDING', (0, 0), (0, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    parts = []
    if fname:
        parts.append(f"File: <b>{fname}</b>")
    parts.append(now)
    if n_browsers:
        parts.append(f"{n_browsers} browsers tested")
    meta_text = "&nbsp;&nbsp;|&nbsp;&nbsp;".join(parts)

    meta = Paragraph(meta_text, ParagraphStyle(
        'M', fontName='Helvetica', fontSize=8, textColor=_hex('neutral'), alignment=TA_CENTER))

    return [banner, Spacer(1, SP_HALF), meta, Spacer(1, SP_HALF)]


def _build_executive_summary(report):
    scores = report.get('scores', {})
    summary = report.get('summary', {})
    browsers = report.get('browsers', {})

    score = float(scores.get('weighted_score', 0) or 0)
    grade = str(scores.get('grade', 'N/A') or 'N/A')
    risk = str(scores.get('risk_level', 'none') or 'none')
    critical = summary.get('critical_issues', 0) or 0
    total = summary.get('total_features', 0) or 0
    html_c = summary.get('html_features', 0) or 0
    css_c = summary.get('css_features', 0) or 0
    js_c = summary.get('js_features', 0) or 0

    verdict = _executive_verdict(score, grade, critical, browsers)

    worst_line = ""
    if browsers:
        worst_name, worst_data = min(browsers.items(), key=lambda x: x[1].get('compatibility_percentage', 100))
        worst_pct = worst_data.get('compatibility_percentage', 0)
        if worst_pct < 100:
            worst_line = f"Lowest compatibility: {worst_name.capitalize()} at {worst_pct:.1f}%"

    title_style = ParagraphStyle('EST', fontName='Helvetica-Bold', fontSize=11, textColor=_hex('text_dark'))
    body_style = ParagraphStyle('ESB', fontName='Helvetica', fontSize=10, textColor=_hex('text_dark'), leading=14)
    bullet_style = ParagraphStyle('ESL', fontName='Helvetica', fontSize=9, textColor=_hex('text_dark'),
                                   leading=13, leftIndent=12, bulletIndent=4)

    type_parts = []
    if html_c: type_parts.append(f"{html_c} HTML")
    if css_c: type_parts.append(f"{css_c} CSS")
    if js_c: type_parts.append(f"{js_c} JS")
    type_str = ", ".join(type_parts) if type_parts else ""

    bullets = [f"{total} web features detected ({type_str})" if type_str else f"{total} web features detected"]
    if critical > 0:
        bullets.append(f"{critical} feature{'s' if critical != 1 else ''} unsupported in at least one browser")
    else:
        bullets.append("No unsupported features detected")
    if worst_line:
        bullets.append(worst_line)

    rows = [
        [Paragraph("Executive Summary", title_style)],
        [Paragraph(verdict, body_style)],
    ]
    for b in bullets:
        rows.append([Paragraph(f"\u2022 {b}", bullet_style)])

    risk_colors = {'low': COLORS['success'], 'medium': COLORS['warning'],
                   'high': COLORS['danger'], 'critical': COLORS['danger'], 'none': COLORS['success']}
    rc = risk_colors.get(risk.lower(), COLORS['neutral'])
    rows.append([Paragraph(
        f"<font color='{rc}'><b>{risk.upper()} RISK</b></font>",
        ParagraphStyle('R', fontName='Helvetica-Bold', fontSize=9, textColor=_hex('neutral'))
    )])

    table = Table(rows, colWidths=[7.3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _hex('bg_light')),
        ('BOX', (0, 0), (-1, -1), 0.5, _hex('neutral')),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, -1), (0, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))

    return [table, Spacer(1, SP_HALF)]


def _build_score_section(scores, summary):
    score = float(scores.get('weighted_score', 0) or 0)
    grade = str(scores.get('grade', 'N/A') or 'N/A')
    risk = str(scores.get('risk_level', 'none') or 'none')
    total = summary.get('total_features', 0) or 0
    critical = summary.get('critical_issues', 0) or 0
    sc = _score_color(score)

    d = Drawing(170, 140)
    d.add(Wedge(85, 78, 52, 0, 360, fillColor=_hex('bg_light'), strokeColor=None))
    if score > 0:
        d.add(Wedge(85, 78, 52, 90, 90 - score * 3.6, fillColor=sc, strokeColor=None))
    d.add(Circle(85, 78, 34, fillColor=colors.white, strokeColor=None))
    d.add(String(85, 86, f"{score:.0f}%", fontSize=24, fontName='Helvetica-Bold',
                  fillColor=sc, textAnchor='middle'))
    d.add(String(85, 70, f"Grade {grade}", fontSize=11, fontName='Helvetica-Bold',
                  fillColor=_hex('text_dark'), textAnchor='middle'))

    grade_key = grade if grade in GRADE_INFO else grade[0] if grade and grade[0] in GRADE_INFO else 'F'
    range_str, desc = GRADE_INFO.get(grade_key, ('', ''))
    grade_text = f"<b>Grade {grade}</b> ({range_str}): {desc}" if range_str else f"<b>Grade {grade}</b>"

    grade_card = Table([[Paragraph(grade_text, ParagraphStyle(
        'GE', fontName='Helvetica', fontSize=8, textColor=_hex('text_dark'), leading=11,
    ))]], colWidths=[4.0 * inch])
    grade_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _score_bg(score)),
        ('BOX', (0, 0), (-1, -1), 0.5, _hex('neutral')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    def _stat(label, value, vc=None):
        vc = vc or _hex('text_dark')
        t = Table([
            [Paragraph(str(value), ParagraphStyle('SV', fontName='Helvetica-Bold', fontSize=16,
                                                   textColor=vc, alignment=TA_CENTER))],
            [Paragraph(label, ParagraphStyle('SL', fontName='Helvetica', fontSize=8,
                                              textColor=_hex('neutral'), alignment=TA_CENTER))],
        ], colWidths=[1.3 * inch], rowHeights=[24, 14])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), _hex('bg_light')),
            ('BOX', (0, 0), (-1, -1), 0.5, _hex('neutral')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (0, 0), 6),
            ('BOTTOMPADDING', (0, -1), (0, -1), 4),
        ]))
        return t

    risk_colors = {'low': _hex('success'), 'medium': _hex('warning'),
                   'high': _hex('danger'), 'critical': _hex('danger'), 'none': _hex('success')}
    crit_c = _hex('danger') if critical > 0 else _hex('success')
    risk_c = risk_colors.get(risk.lower(), _hex('neutral'))

    stats_row = Table([
        [_stat("Features", str(total)), _stat("Critical", str(critical), crit_c),
         _stat("Risk", risk.capitalize(), risk_c)],
    ], colWidths=[1.35 * inch, 1.35 * inch, 1.35 * inch])
    stats_row.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    right_col = Table([
        [grade_card],
        [Spacer(1, SP_HALF)],
        [stats_row],
    ], colWidths=[4.2 * inch])
    right_col.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))

    row = Table([[d, right_col]], colWidths=[3.0 * inch, 4.3 * inch])
    row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
    ]))

    return [_section_header("Compatibility Score"), row, Spacer(1, SP_HALF)]


def _build_analysis_scope(report):
    fname = Path(report.get('file_path', '')).name if report.get('file_path') else 'N/A'
    summary = report.get('summary', {})
    browsers = report.get('browsers', {})
    total = summary.get('total_features', 0) or 0
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    html_c = summary.get('html_features', 0) or 0
    css_c = summary.get('css_features', 0) or 0
    js_c = summary.get('js_features', 0) or 0
    types = []
    if html_c: types.append('HTML')
    if css_c: types.append('CSS')
    if js_c: types.append('JavaScript')
    ftype = ', '.join(types) if types else 'Unknown'

    browser_lines = [f"{n.capitalize()} {d.get('version', '')}" for n, d in browsers.items()]
    browser_text = ", ".join(browser_lines) if browser_lines else "N/A"

    lbl = ParagraphStyle('SL', fontName='Helvetica-Bold', fontSize=9, textColor=_hex('text_dark'))
    val = ParagraphStyle('SV', fontName='Helvetica', fontSize=9, textColor=_hex('text_dark'))

    data = [
        [Paragraph("File", lbl), Paragraph(fname, val),
         Paragraph("Target Browsers", lbl), Paragraph(browser_text, val)],
        [Paragraph("File Type", lbl), Paragraph(ftype, val),
         Paragraph("Features Detected", lbl), Paragraph(str(total), val)],
    ]

    table = Table(data, colWidths=[0.9 * inch, 2.7 * inch, 1.2 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _hex('bg_light')),
        ('BOX', (0, 0), (-1, -1), 0.5, _hex('neutral')),
        ('GRID', (0, 0), (-1, -1), 0.5, _hex('neutral')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    return [_section_header("Analysis Scope"), table, Spacer(1, SP_HALF)]


def _build_browser_section(browsers):
    if not browsers:
        return []

    num = len(browsers)
    chart_h = 14 + num * 30
    drawing = Drawing(500, chart_h)

    bar_h = 16
    max_w = 280
    bar_x = 100
    start_y = chart_h - 20

    for i, (name, details) in enumerate(browsers.items()):
        y = start_y - i * 30
        sup = details.get('supported', 0) or 0
        par = details.get('partial', 0) or 0
        uns = details.get('unsupported', 0) or 0
        total = sup + par + uns
        pct = float(details.get('compatibility_percentage', 0) or 0)
        ver = details.get('version', '')

        drawing.add(String(bar_x - 6, y + 3, f"{name.capitalize()} {ver}",
                            fontSize=8, fontName='Helvetica-Bold',
                            fillColor=colors.HexColor(COLORS['text_dark']), textAnchor='end'))

        drawing.add(Rect(bar_x, y, max_w, bar_h,
                          fillColor=colors.HexColor(COLORS['bg_light']),
                          strokeColor=colors.HexColor(COLORS['neutral']), strokeWidth=0.3, rx=3, ry=3))

        if total > 0:
            sw = (sup / total) * max_w
            pw = (par / total) * max_w
            uw = (uns / total) * max_w
            if sw > 0:
                drawing.add(Rect(bar_x, y, sw, bar_h, fillColor=colors.HexColor(COLORS['success']),
                                  strokeColor=None, rx=2, ry=2))
            if pw > 0:
                drawing.add(Rect(bar_x + sw, y, pw, bar_h, fillColor=colors.HexColor(COLORS['warning']),
                                  strokeColor=None))
            if uw > 0:
                drawing.add(Rect(bar_x + sw + pw, y, uw, bar_h, fillColor=colors.HexColor(COLORS['danger']),
                                  strokeColor=None))

        drawing.add(String(bar_x + max_w + 8, y + 3, f"{pct:.1f}%",
                            fontSize=8, fontName='Helvetica-Bold', fillColor=_score_color(pct)))

    lx = bar_x
    for label, color in [("Supported", COLORS['success']), ("Partial", COLORS['warning']),
                          ("Unsupported", COLORS['danger'])]:
        drawing.add(Rect(lx, 1, 8, 8, fillColor=colors.HexColor(color), strokeColor=None, rx=2, ry=2))
        drawing.add(String(lx + 11, 2, label, fontSize=7, fontName='Helvetica',
                            fillColor=colors.HexColor(COLORS['neutral'])))
        lx += 75

    header = ['Browser', 'Version', 'Compat %', 'Supported', 'Partial', 'Unsupported']
    data = [header]
    for name, details in browsers.items():
        pct = float(details.get('compatibility_percentage', 0) or 0)
        data.append([name.capitalize(), str(details.get('version', '')), f"{pct:.1f}%",
                     str(details.get('supported', 0)), str(details.get('partial', 0)),
                     str(details.get('unsupported', 0))])

    table = Table(data, colWidths=[1.3 * inch, 0.7 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch, 1.0 * inch],
                  repeatRows=1)  # Repeat header row on page splits
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), _hex('header_bg')),
        ('TEXTCOLOR', (0, 0), (-1, 0), _hex('bg_white')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), _hex('text_dark')),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, _hex('neutral')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), _hex('bg_light')))
        pct = float(list(browsers.values())[i - 1].get('compatibility_percentage', 0) or 0)
        cmds.append(('TEXTCOLOR', (2, i), (2, i), _score_color(pct)))
        cmds.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
    table.setStyle(TableStyle(cmds))

    return [_section_header("Browser Compatibility"),
            drawing, Spacer(1, SP_HALF), table, Spacer(1, SP)]


def _build_feature_distribution(summary, baseline):
    html_c = summary.get('html_features', 0) or 0
    css_c = summary.get('css_features', 0) or 0
    js_c = summary.get('js_features', 0) or 0
    total = html_c + css_c + js_c
    items = [('HTML', TYPE_COLORS['html'], html_c), ('CSS', TYPE_COLORS['css'], css_c),
             ('JS', TYPE_COLORS['js'], js_c)]
    active = [(l, c, n) for l, c, n in items if n > 0]

    elements = []

    if len(active) <= 1 and total > 0:
        tname = active[0][0] if active else "unknown"
        elements.append(Paragraph(
            f"All {total} detected features are <b>{tname}</b> features.",
            ParagraphStyle('FT', fontName='Helvetica', fontSize=9, textColor=_hex('text_dark'))))
    elif total > 0:
        d = Drawing(260, 60)
        d.add(String(130, 50, "Feature Distribution", fontSize=9, fontName='Helvetica-Bold',
                      fillColor=colors.HexColor(COLORS['text_dark']), textAnchor='middle'))
        bx, bw, bh = 10, 240, 16
        d.add(Rect(bx, 22, bw, bh, fillColor=colors.HexColor(COLORS['bg_light']),
                    strokeColor=colors.HexColor(COLORS['neutral']), rx=3, ry=3))
        x = bx
        for _, color, count in active:
            w = (count / total) * bw
            d.add(Rect(x, 22, w, bh, fillColor=colors.HexColor(color), strokeColor=None, rx=2, ry=2))
            x += w
        lx = 10
        for label, color, count in active:
            d.add(Rect(lx, 4, 8, 8, fillColor=colors.HexColor(color), strokeColor=None, rx=2, ry=2))
            d.add(String(lx + 11, 5, f"{label}: {count}", fontSize=7, fontName='Helvetica',
                          fillColor=colors.HexColor(COLORS['neutral'])))
            lx += 70
        elements.append(d)

    if baseline:
        widely = baseline.get('widely_available', 0) or 0
        newly = baseline.get('newly_available', 0) or 0
        limited = baseline.get('limited', 0) or 0
        unknown = baseline.get('unknown', 0) or 0
        b_total = widely + newly + limited + unknown
        if b_total > 0:
            bd = Drawing(260, 60)
            bd.add(String(130, 50, "Baseline Status", fontSize=9, fontName='Helvetica-Bold',
                           fillColor=colors.HexColor(COLORS['text_dark']), textAnchor='middle'))
            bi = [('Widely', COLORS['success'], widely), ('Newly', COLORS['primary'], newly),
                  ('Limited', COLORS['warning'], limited), ('Unknown', '#9ca3af', unknown)]
            bx, bw, bh = 10, 240, 16
            bd.add(Rect(bx, 22, bw, bh, fillColor=colors.HexColor(COLORS['bg_light']),
                         strokeColor=colors.HexColor(COLORS['neutral']), rx=3, ry=3))
            x = bx
            for _, color, count in bi:
                if count > 0:
                    w = (count / b_total) * bw
                    bd.add(Rect(x, 22, w, bh, fillColor=colors.HexColor(color), strokeColor=None, rx=2, ry=2))
                    x += w
            lx = 10
            for label, color, count in bi:
                if count > 0:
                    bd.add(Rect(lx, 4, 8, 8, fillColor=colors.HexColor(color), strokeColor=None, rx=2, ry=2))
                    bd.add(String(lx + 11, 5, f"{count} {label}", fontSize=7, fontName='Helvetica',
                                   fillColor=colors.HexColor(COLORS['neutral'])))
                    lx += 55
            elements.append(bd)

    if not elements:
        return []

    card_rows = [[e] for e in elements]
    card = Table(card_rows, colWidths=[7.3 * inch])
    card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _hex('bg_light')),
        ('BOX', (0, 0), (-1, -1), 0.5, _hex('neutral')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return [_section_header("Feature Analysis"), card, Spacer(1, SP_HALF)]


def _build_issues_section(browsers):
    issues = _build_issue_list(browsers)
    if not issues:
        return []

    total = len(issues)
    display = issues[:MAX_ROWS]

    cell = ParagraphStyle('IC', fontName='Helvetica', fontSize=8, textColor=_hex('text_dark'), leading=10)
    cell_b = ParagraphStyle('ICB', fontName='Helvetica-Bold', fontSize=8, textColor=_hex('text_dark'), leading=10)
    fix_style = ParagraphStyle('IF', fontName='Helvetica', fontSize=7.5, textColor=_hex('text_dark'), leading=10)

    rows = [['Sev.', 'Feature', 'Status', 'Browsers', 'Suggested Fix']]
    for issue in display:
        rows.append([
            Paragraph(f"<font color='{issue['sev_color']}'><b>{issue['severity']}</b></font>", cell),
            Paragraph(issue['name'], cell_b),
            Paragraph(f"<font color='{issue['sev_color']}'>{issue['status']}</font>", cell),
            Paragraph(issue['browsers'], cell),
            Paragraph(issue['fix'][:120], fix_style),
        ])

    table = Table(rows, colWidths=[0.5 * inch, 1.4 * inch, 0.8 * inch, 1.4 * inch, 3.2 * inch],
                  repeatRows=1)
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), _hex('header_bg')),
        ('TEXTCOLOR', (0, 0), (-1, 0), _hex('bg_white')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, _hex('neutral')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    for i, issue in enumerate(display, 1):
        cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor(issue['row_bg'])))
    table.setStyle(TableStyle(cmds))

    elements = [_section_header("Compatibility Issues"), table]
    if total > MAX_ROWS:
        elements.append(Paragraph(
            f"Showing top {MAX_ROWS} of {total} issues, sorted by impact.",
            ParagraphStyle('N', fontName='Helvetica', fontSize=7, textColor=_hex('neutral'), spaceBefore=3)))
    elements.append(Spacer(1, SP))
    return elements


def _build_browser_details(browsers):
    from src.utils.feature_names import get_feature_name

    has_issues = any(d.get('unsupported_features') or d.get('partial_features') for d in browsers.values())
    if not has_issues:
        return []

    elements = [_section_header("Detailed Browser Analysis")]
    body = ParagraphStyle('BD', fontName='Helvetica', fontSize=8, textColor=_hex('text_dark'), leading=11)

    for name, details in browsers.items():
        unsupported = details.get('unsupported_features', [])
        partial = details.get('partial_features', [])
        if not unsupported and not partial:
            continue

        pct = float(details.get('compatibility_percentage', 0) or 0)
        version = details.get('version', '')
        _, status_hex = ('Good', COLORS['success']) if pct >= 75 else ('Fair', COLORS['warning']) if pct >= 60 else ('Poor', COLORS['danger'])

        rows = [[Paragraph(
            f"<font color='{status_hex}'><b>{name.capitalize()} {version} &mdash; {pct:.1f}% Compatible</b></font>",
            ParagraphStyle('BH', fontName='Helvetica-Bold', fontSize=10, textColor=_hex('text_dark')))]]

        if unsupported:
            names = sorted([get_feature_name(f) or f for f in unsupported])[:MAX_ROWS]
            extra = f" (+{len(unsupported) - MAX_ROWS} more)" if len(unsupported) > MAX_ROWS else ""
            rows.append([Paragraph(
                f"<font color='{COLORS['danger']}'><b>Unsupported ({len(unsupported)}):</b></font> "
                f"{', '.join(names)}{extra}", body)])

        if partial:
            names = sorted([get_feature_name(f) or f for f in partial])[:MAX_ROWS]
            extra = f" (+{len(partial) - MAX_ROWS} more)" if len(partial) > MAX_ROWS else ""
            rows.append([Paragraph(
                f"<font color='{COLORS['warning']}'><b>Partial ({len(partial)}):</b></font> "
                f"{', '.join(names)}{extra}", body)])

        card = Table(rows, colWidths=[7.1 * inch])
        card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), _hex('bg_light')),
            ('BOX', (0, 0), (-1, -1), 0.5, _hex('neutral')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.extend([card, Spacer(1, SP_HALF)])

    elements.append(Spacer(1, SP_HALF))
    return elements


def _build_feature_details(feature_details):
    from src.utils.feature_names import get_feature_name

    if not feature_details:
        return []

    elements = [_section_header("Detected Features")]
    cell = ParagraphStyle('FC', fontName='Helvetica', fontSize=8, textColor=_hex('text_dark'), leading=10)
    cell_b = ParagraphStyle('FB', fontName='Helvetica-Bold', fontSize=8, textColor=_hex('text_dark'), leading=10)

    for ftype in ['html', 'css', 'js']:
        items = feature_details.get(ftype, [])
        if not items:
            continue

        color = TYPE_COLORS.get(ftype, COLORS['primary'])
        label = {'html': 'HTML', 'css': 'CSS', 'js': 'JavaScript'}[ftype]

        elements.append(Paragraph(f"{label} Features ({len(items)})", ParagraphStyle(
            f'FH_{ftype}', fontName='Helvetica-Bold', fontSize=9,
            textColor=colors.HexColor(color), spaceBefore=SP_HALF, spaceAfter=3)))

        rows = [['Feature', 'Description']]
        for item in items[:MAX_ROWS]:
            feat = item.get('feature', '')
            desc = item.get('description', '') or get_feature_name(feat) or ''
            rows.append([Paragraph(feat, cell_b), Paragraph(desc, cell)])

        table = Table(rows, colWidths=[2.5 * inch, 4.8 * inch], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, _hex('neutral')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            *[('BACKGROUND', (0, i), (-1, i), _hex('bg_light')) for i in range(2, len(rows), 2)],
        ]))
        elements.append(table)
        if len(items) > MAX_ROWS:
            elements.append(Paragraph(f"... and {len(items) - MAX_ROWS} more {label.lower()} features",
                                       ParagraphStyle('N', fontName='Helvetica', fontSize=7,
                                                      textColor=_hex('neutral'), spaceBefore=2)))
        elements.append(Spacer(1, SP_HALF))

    return elements


def _build_recommendations(recommendations, report):
    from src.utils.feature_names import get_feature_name, get_fix_suggestion

    if not recommendations:
        return []

    body = ParagraphStyle('RB', fontName='Helvetica', fontSize=9, textColor=_hex('text_dark'), leading=13)
    num = ParagraphStyle('RN', fontName='Helvetica-Bold', fontSize=9, textColor=_hex('primary'))

    recs = list(recommendations)
    issues = _build_issue_list(report.get('browsers', {}))
    for issue in issues[:5]:
        if issue['fix'] != '-':
            recs.append(f"{issue['name']}: {issue['fix']}")

    rows = [[Paragraph(f"{i}.", num), Paragraph(r, body)] for i, r in enumerate(recs[:10], 1)]

    table = Table(rows, colWidths=[0.35 * inch, 6.95 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _hex('bg_light')),
        ('BOX', (0, 0), (-1, -1), 0.5, _hex('neutral')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, _hex('neutral')),
    ]))

    return [_section_header("Recommendations"), table, Spacer(1, SP_HALF)]


def _build_ai_suggestions(ai_suggestions):
    if not ai_suggestions:
        return []

    elements = [_section_header("AI Fix Suggestions")]
    name_s = ParagraphStyle('AN', fontName='Helvetica-Bold', fontSize=10, textColor=_hex('primary'))
    body_s = ParagraphStyle('AB', fontName='Helvetica', fontSize=9, textColor=_hex('text_dark'), leading=12)
    code_s = ParagraphStyle('AC', fontName='Courier', fontSize=8, textColor=_hex('text_dark'),
                             backColor=colors.HexColor('#f3f4f6'), borderPadding=(5, 5, 5, 5), leading=11)
    meta_s = ParagraphStyle('AM', fontName='Helvetica', fontSize=7.5, textColor=_hex('neutral'))

    for s in ai_suggestions[:10]:
        fname = s.get('feature_name', s.get('feature_id', ''))
        suggestion = s.get('suggestion', '')
        code = s.get('code_example', '')
        affected = s.get('browsers_affected', [])

        rows = [[Paragraph(fname, name_s)]]
        if affected:
            bt = ', '.join(affected) if isinstance(affected, list) else str(affected)
            rows.append([Paragraph(f"Affects: {bt}", meta_s)])
        rows.append([Paragraph(suggestion, body_s)])
        if code:
            safe = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            rows.append([Paragraph(safe, code_s)])

        card = Table(rows, colWidths=[7.1 * inch])
        card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), _hex('bg_light')),
            ('BOX', (0, 0), (-1, -1), 0.5, _hex('neutral')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.extend([card, Spacer(1, SP_HALF)])

    return elements


def _build_footer():
    return [
        Spacer(1, SP_HALF),
        HRFlowable(width="100%", thickness=0.5, color=_hex('neutral')),
        Spacer(1, 3),
        Paragraph(f"Generated by Cross Guard &bull; {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                  ParagraphStyle('F', fontName='Helvetica', fontSize=8, textColor=_hex('neutral'),
                                 alignment=TA_CENTER)),
    ]


# --- Orchestrator ---

def _create_pdf(report, file_path):
    doc = SimpleDocTemplate(file_path, pagesize=letter,
                            rightMargin=0.6 * inch, leftMargin=0.6 * inch,
                            topMargin=0.6 * inch, bottomMargin=0.55 * inch)

    story = []
    story.extend(_build_header(report))
    story.extend(_build_executive_summary(report))
    story.extend(_build_score_section(report.get('scores', {}), report.get('summary', {})))
    story.extend(_build_analysis_scope(report))
    story.extend(_build_browser_section(report.get('browsers', {})))
    story.extend(_build_feature_distribution(report.get('summary', {}), report.get('baseline_summary')))
    story.extend(_build_issues_section(report.get('browsers', {})))
    story.extend(_build_browser_details(report.get('browsers', {})))
    story.extend(_build_feature_details(report.get('feature_details', {})))
    story.extend(_build_recommendations(report.get('recommendations', []), report))
    if report.get('ai_suggestions'):
        story.extend(_build_ai_suggestions(report['ai_suggestions']))
    story.extend(_build_footer())

    doc.build(story, onFirstPage=_draw_page, onLaterPages=_draw_page)
