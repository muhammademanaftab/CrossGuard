"""
Export Manager for Cross Guard GUI.

Thin GUI shell that delegates to src.export for actual report generation.
Only handles file dialogs, progress indication, and error toasts.
"""

import traceback
from tkinter import filedialog
from typing import Dict

from .widgets.messagebox import show_info, show_warning, show_error


class ExportManager:
    """GUI wrapper for export functionality — file dialogs + error handling."""

    def __init__(self, parent):
        """Initialize export manager.

        Args:
            parent: Parent widget for dialogs
        """
        self.parent = parent

    def export_json(self, report: Dict) -> None:
        """Export analysis report as JSON file via file dialog.

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
                from src.export import export_json as do_export_json
                do_export_json(report, output_path=file_path)

                show_info(
                    self.parent,
                    "Export Successful",
                    f"Report saved to:\n{file_path}",
                )
            except Exception as e:
                show_error(
                    self.parent,
                    "Export Failed",
                    f"Failed to save JSON file:\n{str(e)}",
                )

    def export_pdf(self, report: Dict) -> None:
        """Export analysis report as PDF via file dialog.

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
                from src.export import export_pdf as do_export_pdf
                do_export_pdf(report, output_path=file_path)

                show_info(
                    self.parent,
                    "Export Successful",
                    f"PDF report saved to:\n{file_path}",
                )
            except ImportError as e:
                show_error(
                    self.parent,
                    "Missing Library",
                    f"Required libraries for PDF export:\n\n"
                    f"pip install reportlab matplotlib\n\n"
                    f"Error: {str(e)}",
                )
            except Exception as e:
                error_details = traceback.format_exc()
                print(f"PDF Export Error:\n{error_details}")
                lines = error_details.strip().split('\n')
                short_trace = '\n'.join(lines[-4:]) if len(lines) > 4 else error_details
                show_error(
                    self.parent,
                    "Export Failed",
                    f"Failed to create PDF:\n{short_trace}",
                )
