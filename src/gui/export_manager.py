"""
Export Manager for Cross Guard
Handles PDF and JSON export functionality using tkinter dialogs.
"""

from tkinter import filedialog
from typing import Dict

from .widgets.messagebox import show_info, show_warning, show_error


class ExportManager:
    """Manages export functionality for analysis reports."""

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

        # Ask user where to save
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
        """Export analysis report as PDF file.

        Args:
            report: Analysis report dictionary
        """
        if not report:
            show_warning(self.parent, "No Report", "No analysis report to export.")
            return

        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            title="Save Report as PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
            initialfile="compatibility_report.pdf",
        )

        if file_path:
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.units import inch

                # Create PDF
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()

                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#2196F3'),
                    spaceAfter=30
                )
                story.append(Paragraph("Cross Guard Compatibility Report", title_style))
                story.append(Spacer(1, 0.2*inch))

                # Summary
                summary = report.get('summary', {})
                scores = report.get('scores', {})

                story.append(Paragraph("<b>Summary</b>", styles['Heading2']))
                summary_data = [
                    ['Total Features:', str(summary.get('total_features', 0))],
                    ['HTML Features:', str(summary.get('html_features', 0))],
                    ['CSS Features:', str(summary.get('css_features', 0))],
                    ['JS Features:', str(summary.get('js_features', 0))],
                    ['Critical Issues:', str(summary.get('critical_issues', 0))],
                ]
                summary_table = Table(summary_data, colWidths=[2*inch, 1*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(summary_table)
                story.append(Spacer(1, 0.3*inch))

                # Compatibility Score
                story.append(Paragraph("<b>Compatibility Score</b>", styles['Heading2']))
                score_data = [
                    ['Grade:', scores.get('grade', 'N/A')],
                    ['Risk Level:', scores.get('risk_level', 'N/A')],
                    ['Simple Score:', f"{scores.get('simple_score', 0):.1f}%"],
                    ['Weighted Score:', f"{scores.get('weighted_score', 0):.1f}%"],
                ]
                score_table = Table(score_data, colWidths=[2*inch, 1*inch])
                score_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(score_table)
                story.append(Spacer(1, 0.3*inch))

                # Browser Compatibility
                story.append(Paragraph("<b>Browser Compatibility</b>", styles['Heading2']))
                browsers = report.get('browsers', {})

                for browser_name, details in browsers.items():
                    browser_title = f"{browser_name.upper()} {details.get('version', '')}"
                    story.append(Paragraph(f"<b>{browser_title}</b>", styles['Heading3']))

                    browser_data = [
                        ['Compatibility:', f"{details.get('compatibility_percentage', 0):.1f}%"],
                        ['Supported:', str(details.get('supported', 0))],
                        ['Partial:', str(details.get('partial', 0))],
                        ['Unsupported:', str(details.get('unsupported', 0))],
                    ]

                    if details.get('unsupported_features'):
                        browser_data.append(['Not Supported:', ', '.join(details['unsupported_features'][:3])])
                    if details.get('partial_features'):
                        browser_data.append(['Partial Support:', ', '.join(details['partial_features'][:3])])

                    browser_table = Table(browser_data, colWidths=[2*inch, 4*inch])
                    browser_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(browser_table)
                    story.append(Spacer(1, 0.2*inch))

                # Recommendations
                recommendations = report.get('recommendations', [])
                if recommendations:
                    story.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
                    for i, rec in enumerate(recommendations, 1):
                        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))

                # Build PDF
                doc.build(story)

                show_info(
                    self.parent,
                    "Export Successful",
                    f"PDF report saved to:\n{file_path}"
                )

            except ImportError:
                show_error(
                    self.parent,
                    "Missing Library",
                    "ReportLab library is required for PDF export.\n\n"
                    "Install it with: pip install reportlab"
                )
            except Exception as e:
                show_error(
                    self.parent,
                    "Export Failed",
                    f"Failed to create PDF:\n{str(e)}"
                )
