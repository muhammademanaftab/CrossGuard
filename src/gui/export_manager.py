"""
Export Manager for Cross Guard
Professional PDF and JSON export with beautiful charts and modern design.
"""

import io
import os
from datetime import datetime
from tkinter import filedialog
from typing import Dict, List, Tuple

from .widgets.messagebox import show_info, show_warning, show_error


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
}


class ExportManager:
    """Manages export functionality for analysis reports with professional design."""

    def __init__(self, parent):
        """Initialize export manager.

        Args:
            parent: Parent widget for dialogs
        """
        self.parent = parent

    def export_json(self, report: Dict) -> None:
        """Export analysis report as JSON file.

        Args:
            report: Analysis report dictionary
        """
        if not report:
            show_warning(self.parent, "No Report", "No analysis report to export.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Report as JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialfile="compatibility_report.json",
        )

        if file_path:
            try:
                import json
                with open(file_path, 'w') as f:
                    json.dump(report, f, indent=2)

                show_info(
                    self.parent,
                    "Export Successful",
                    f"Report saved to:\n{file_path}"
                )
            except Exception as e:
                show_error(
                    self.parent,
                    "Export Failed",
                    f"Failed to save JSON file:\n{str(e)}"
                )

    def export_pdf(self, report: Dict) -> None:
        """Export analysis report as a beautifully designed PDF.

        Args:
            report: Analysis report dictionary
        """
        if not report:
            show_warning(self.parent, "No Report", "No analysis report to export.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Report as PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
            initialfile="compatibility_report.pdf",
        )

        if file_path:
            try:
                self._create_professional_pdf(report, file_path)
                show_info(
                    self.parent,
                    "Export Successful",
                    f"PDF report saved to:\n{file_path}"
                )
            except ImportError as e:
                show_error(
                    self.parent,
                    "Missing Library",
                    f"Required libraries for PDF export:\n\n"
                    f"pip install reportlab matplotlib\n\n"
                    f"Error: {str(e)}"
                )
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"PDF Export Error:\n{error_details}")  # Log to console
                # Show last few lines of traceback in dialog
                lines = error_details.strip().split('\n')
                short_trace = '\n'.join(lines[-4:]) if len(lines) > 4 else error_details
                show_error(
                    self.parent,
                    "Export Failed",
                    f"Failed to create PDF:\n{short_trace}"
                )

    def _create_professional_pdf(self, report: Dict, file_path: str):
        """Create a professionally designed PDF report."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            Image, PageBreak, HRFlowable
        )
        from reportlab.lib.units import inch, cm
        from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Wedge, Line
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics import renderPDF

        # Extract data
        summary = report.get('summary', {})
        scores = report.get('scores', {})
        browsers = report.get('browsers', {})
        recommendations = report.get('recommendations', [])

        # Create document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Custom styles
        styles = getSampleStyleSheet()

        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#58a6ff'),
            spaceAfter=5,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Subtitle style
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#8b949e'),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        # Section header style
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#f0f6fc'),
            spaceBefore=20,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#21262d'),
            borderPadding=(10, 10, 10, 10),
            leftIndent=-10,
            rightIndent=-10
        )

        # Body text style
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#c9d1d9'),
            spaceBefore=5,
            spaceAfter=5
        )

        story = []

        try:
            # ===== HEADER SECTION =====
            story.append(self._create_header_section(title_style, subtitle_style))
            story.append(Spacer(1, 0.3*inch))
        except Exception as e:
            print(f"PDF Error in HEADER SECTION: {e}")
            raise

        try:
            # ===== SCORE OVERVIEW =====
            story.append(Paragraph("COMPATIBILITY SCORE", section_style))
            story.append(Spacer(1, 0.2*inch))

            # Score card with gauge
            score_drawing = self._create_score_gauge(
                scores.get('weighted_score', 0) or 0,
                scores.get('grade', 'N/A') or 'N/A',
                scores.get('risk_level', 'unknown') or 'unknown'
            )
            story.append(score_drawing)
            story.append(Spacer(1, 0.3*inch))

            # Score details table
            story.append(self._create_score_table(scores))
            story.append(Spacer(1, 0.4*inch))
        except Exception as e:
            print(f"PDF Error in SCORE OVERVIEW: {e}")
            raise

        try:
            # ===== FEATURE SUMMARY =====
            story.append(Paragraph("FEATURE ANALYSIS", section_style))
            story.append(Spacer(1, 0.2*inch))

            # Feature distribution pie chart
            feature_chart = self._create_feature_pie_chart(summary)
            story.append(feature_chart)
            story.append(Spacer(1, 0.2*inch))

            # Summary stats table
            story.append(self._create_summary_table(summary))
            story.append(Spacer(1, 0.4*inch))
        except Exception as e:
            print(f"PDF Error in FEATURE SUMMARY: {e}")
            raise

        try:
            # ===== BROWSER COMPATIBILITY =====
            story.append(Paragraph("BROWSER COMPATIBILITY", section_style))
            story.append(Spacer(1, 0.2*inch))

            # Browser comparison bar chart
            if browsers:
                browser_chart = self._create_browser_bar_chart(browsers)
                story.append(browser_chart)
                story.append(Spacer(1, 0.3*inch))

                # Browser details table
                story.append(self._create_browser_table(browsers))
            story.append(Spacer(1, 0.4*inch))
        except Exception as e:
            print(f"PDF Error in BROWSER COMPATIBILITY: {e}")
            raise

        try:
            # ===== ISSUES BY BROWSER =====
            if browsers:
                story.append(PageBreak())
                story.append(Paragraph("DETAILED BROWSER ANALYSIS", section_style))
                story.append(Spacer(1, 0.2*inch))

                for browser_name, details in browsers.items():
                    story.append(self._create_browser_detail_section(browser_name, details, styles))
                    story.append(Spacer(1, 0.3*inch))
        except Exception as e:
            print(f"PDF Error in BROWSER DETAILS: {e}")
            raise

        try:
            # ===== RECOMMENDATIONS =====
            if recommendations:
                story.append(Paragraph("RECOMMENDATIONS", section_style))
                story.append(Spacer(1, 0.2*inch))
                story.append(self._create_recommendations_section(recommendations, body_style))
        except Exception as e:
            print(f"PDF Error in RECOMMENDATIONS: {e}")
            raise

        # ===== FOOTER =====
        story.append(Spacer(1, 0.5*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#30363d')))
        story.append(Spacer(1, 0.1*inch))

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6e7681'),
            alignment=TA_CENTER
        )
        story.append(Paragraph(
            f"Generated by Cross Guard • {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            footer_style
        ))

        # Build PDF
        try:
            doc.build(story)
        except Exception as e:
            print(f"PDF Error during doc.build: {e}")
            print(f"Story has {len(story)} elements")
            raise

    def _create_header_section(self, title_style, subtitle_style):
        """Create the report header section."""
        from reportlab.platypus import Paragraph, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        # Create header table with logo and title
        header_data = [[
            Paragraph("◇ CROSS GUARD", title_style),
        ], [
            Paragraph("Browser Compatibility Analysis Report", subtitle_style),
        ], [
            Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", subtitle_style),
        ]]

        header_table = Table(header_data, colWidths=[6.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        return header_table

    def _create_score_gauge(self, score: float, grade: str, risk_level: str):
        """Create a score card visualization (no arcs to avoid bezierArc issues)."""
        from reportlab.graphics.shapes import Drawing, Circle, String, Rect
        from reportlab.lib import colors

        # Ensure valid values
        score = float(score or 0)
        grade = str(grade or 'N/A')
        risk_level = str(risk_level or 'unknown')

        drawing = Drawing(400, 150)

        # Determine color based on score
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

        # Background card
        drawing.add(Rect(50, 20, 300, 110, fillColor=colors.HexColor('#161b22'),
                        strokeColor=colors.HexColor('#30363d'), strokeWidth=1, rx=8, ry=8))

        # Score display (large)
        drawing.add(String(200, 95, f"{score:.0f}%",
                          fontSize=42, fontName='Helvetica-Bold',
                          fillColor=score_color, textAnchor='middle'))

        # Grade badge
        drawing.add(Rect(160, 55, 80, 28, fillColor=score_color, strokeColor=None, rx=4, ry=4))
        drawing.add(String(200, 63, f"Grade {grade}",
                          fontSize=14, fontName='Helvetica-Bold',
                          fillColor=colors.white, textAnchor='middle'))

        # Risk level
        risk_colors = {
            'low': colors.HexColor('#3fb950'),
            'medium': colors.HexColor('#d29922'),
            'high': colors.HexColor('#f85149'),
        }
        risk_color = risk_colors.get(risk_level.lower(), colors.HexColor('#8b949e'))

        drawing.add(String(200, 35, f"{risk_level.upper()} RISK",
                          fontSize=11, fontName='Helvetica-Bold',
                          fillColor=risk_color, textAnchor='middle'))

        # Progress bar at bottom
        bar_width = 260
        bar_height = 8
        bar_x = 70
        bar_y = 25

        # Background bar
        drawing.add(Rect(bar_x, bar_y, bar_width, bar_height,
                        fillColor=colors.HexColor('#21262d'), strokeColor=None, rx=4, ry=4))

        # Filled bar
        if score > 0:
            filled_width = (score / 100) * bar_width
            drawing.add(Rect(bar_x, bar_y, filled_width, bar_height,
                            fillColor=score_color, strokeColor=None, rx=4, ry=4))

        return drawing

    def _create_score_table(self, scores: Dict):
        """Create a styled score details table."""
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

        table = Table(data, colWidths=[2.5*inch, 2*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#58a6ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#161b22')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#c9d1d9')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),

            # Alternating rows
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#21262d')),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#21262d')),

            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#30363d')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#30363d')),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))

        return table

    def _create_feature_pie_chart(self, summary: Dict):
        """Create a horizontal bar chart showing feature distribution by type."""
        from reportlab.graphics.shapes import Drawing, String, Rect
        from reportlab.lib import colors

        html_count = summary.get('html_features', 0) or 0
        css_count = summary.get('css_features', 0) or 0
        js_count = summary.get('js_features', 0) or 0
        total = html_count + css_count + js_count

        drawing = Drawing(450, 140)

        # Title
        drawing.add(String(225, 125, "Feature Distribution",
                          fontSize=12, fontName='Helvetica-Bold',
                          fillColor=colors.HexColor('#f0f6fc'), textAnchor='middle'))

        if total == 0:
            drawing.add(String(225, 60, "No features detected",
                              fontSize=14, fillColor=colors.HexColor('#8b949e'),
                              textAnchor='middle'))
            return drawing

        all_items = [
            ('HTML', '#e34c26', html_count),
            ('CSS', '#264de4', css_count),
            ('JavaScript', '#f7df1e', js_count),
        ]

        bar_height = 24
        max_width = 250
        start_x = 100
        start_y = 95

        for i, (label, color, count) in enumerate(all_items):
            y = start_y - (i * 35)
            pct = (count / total * 100) if total > 0 else 0

            # Label
            drawing.add(String(start_x - 10, y + 6, label,
                              fontSize=11, fontName='Helvetica-Bold',
                              fillColor=colors.HexColor('#c9d1d9'), textAnchor='end'))

            # Background bar
            drawing.add(Rect(start_x, y, max_width, bar_height,
                            fillColor=colors.HexColor('#21262d'), strokeColor=None, rx=4, ry=4))

            # Filled bar
            if count > 0:
                bar_width = (pct / 100) * max_width
                drawing.add(Rect(start_x, y, bar_width, bar_height,
                                fillColor=colors.HexColor(color), strokeColor=None, rx=4, ry=4))

            # Count and percentage
            drawing.add(String(start_x + max_width + 15, y + 6, f"{count} ({pct:.0f}%)",
                              fontSize=10, fontName='Helvetica',
                              fillColor=colors.HexColor('#8b949e')))

        return drawing

    def _create_summary_table(self, summary: Dict):
        """Create a styled summary statistics table."""
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

        table = Table(data, colWidths=[1.8*inch, 1*inch, 3*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#58a6ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#161b22')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#c9d1d9')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),

            # Alternating
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#21262d')),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#21262d')),

            # Critical row highlight
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#4a1e1c')),
            ('TEXTCOLOR', (0, 5), (-1, 5), colors.HexColor('#f85149')),

            # Borders & padding
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#30363d')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))

        return table

    def _create_browser_bar_chart(self, browsers: Dict):
        """Create a horizontal bar chart comparing browser compatibility."""
        from reportlab.graphics.shapes import Drawing, String, Rect, Line
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        if not browsers:
            drawing = Drawing(500, 100)
            drawing.add(String(250, 50, "No browser data available",
                              fontSize=14, fillColor=colors.HexColor('#8b949e'),
                              textAnchor='middle'))
            return drawing

        num_browsers = len(browsers)
        drawing = Drawing(500, 40 + num_browsers * 50)

        # Title
        drawing.add(String(250, 30 + num_browsers * 50, "Browser Compatibility Comparison",
                          fontSize=12, fontName='Helvetica-Bold',
                          fillColor=colors.HexColor('#f0f6fc'), textAnchor='middle'))

        bar_height = 25
        max_width = 300
        start_x = 120
        start_y = num_browsers * 50

        for i, (browser_name, details) in enumerate(browsers.items()):
            y = start_y - (i * 50)
            pct = float(details.get('compatibility_percentage', 0) or 0)

            # Browser label
            drawing.add(String(start_x - 10, y + 8, browser_name.capitalize(),
                              fontSize=11, fontName='Helvetica-Bold',
                              fillColor=colors.HexColor('#c9d1d9'), textAnchor='end'))

            # Background bar
            drawing.add(Rect(start_x, y, max_width, bar_height,
                            fillColor=colors.HexColor('#21262d'), strokeColor=None, rx=4, ry=4))

            # Determine color
            if pct >= 90:
                bar_color = colors.HexColor('#3fb950')
            elif pct >= 75:
                bar_color = colors.HexColor('#56d364')
            elif pct >= 60:
                bar_color = colors.HexColor('#d29922')
            else:
                bar_color = colors.HexColor('#f85149')

            # Filled bar
            if pct > 0:
                bar_width = (pct / 100) * max_width
                drawing.add(Rect(start_x, y, bar_width, bar_height,
                                fillColor=bar_color, strokeColor=None, rx=4, ry=4))

            # Percentage label
            drawing.add(String(start_x + max_width + 15, y + 8, f"{pct:.1f}%",
                              fontSize=11, fontName='Helvetica-Bold',
                              fillColor=bar_color))

        return drawing

    def _create_browser_table(self, browsers: Dict):
        """Create a detailed browser comparison table."""
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        # Header
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

        table = Table(data, colWidths=[1.2*inch, 0.8*inch, 1.1*inch, 0.9*inch, 0.8*inch, 1*inch])

        style_commands = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#58a6ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#161b22')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#c9d1d9')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),

            # Borders & padding
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#30363d')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]

        # Color code compatibility column
        for i, (browser_name, details) in enumerate(browsers.items(), 1):
            pct = float(details.get('compatibility_percentage', 0) or 0)
            if pct >= 90:
                style_commands.append(('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#3fb950')))
            elif pct >= 75:
                style_commands.append(('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#56d364')))
            elif pct >= 60:
                style_commands.append(('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#d29922')))
            else:
                style_commands.append(('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#f85149')))

        table.setStyle(TableStyle(style_commands))
        return table

    def _create_browser_detail_section(self, browser_name: str, details: Dict, styles):
        """Create a detailed section for a single browser."""
        from reportlab.platypus import Table, TableStyle, Paragraph
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.lib.styles import ParagraphStyle

        browser_style = ParagraphStyle(
            'BrowserHeader',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#58a6ff'),
            spaceBefore=10,
            spaceAfter=5
        )

        pct = float(details.get('compatibility_percentage', 0) or 0)
        version = details.get('version', '') or ''

        # Determine status color
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

        # Browser header with status
        header_text = f"{browser_name.capitalize()} {version} - {pct:.1f}% Compatible ({status_text})"

        data = [[Paragraph(f"<font color='{status_color}'>{header_text}</font>", browser_style)]]

        # Unsupported features
        unsupported = details.get('unsupported_features', [])
        if unsupported:
            features_text = ', '.join(unsupported[:10])
            if len(unsupported) > 10:
                features_text += f'... (+{len(unsupported) - 10} more)'
            data.append([Paragraph(f"<b>Unsupported ({len(unsupported)}):</b> <font color='#f85149'>{features_text}</font>", styles['Normal'])])

        # Partial features
        partial = details.get('partial_features', [])
        if partial:
            features_text = ', '.join(partial[:10])
            if len(partial) > 10:
                features_text += f'... (+{len(partial) - 10} more)'
            data.append([Paragraph(f"<b>Partial ({len(partial)}):</b> <font color='#d29922'>{features_text}</font>", styles['Normal'])])

        table = Table(data, colWidths=[6.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#161b22')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#30363d')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))

        return table

    def _create_recommendations_section(self, recommendations: List[str], body_style):
        """Create a styled recommendations section."""
        from reportlab.platypus import Table, TableStyle, Paragraph
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.lib.styles import ParagraphStyle

        rec_style = ParagraphStyle(
            'Recommendation',
            parent=body_style,
            fontSize=10,
            textColor=colors.HexColor('#c9d1d9'),
            leftIndent=20,
            bulletIndent=10,
        )

        data = []
        for i, rec in enumerate(recommendations, 1):
            # Create a row with number and recommendation
            data.append([
                Paragraph(f"<font color='#58a6ff'><b>{i}.</b></font>", body_style),
                Paragraph(rec, rec_style)
            ])

        table = Table(data, colWidths=[0.4*inch, 6*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#161b22')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#30363d')),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#21262d')),
        ]))

        return table
