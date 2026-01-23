"""
Cross Guard Main Window
Main GUI window with file selection interface for browser compatibility analysis.
CustomTkinter implementation with simple page navigation.
"""

from pathlib import Path
from typing import Dict, List, Optional

import customtkinter as ctk
from PIL import Image

# API Layer imports - Frontend only depends on API, not backend directly
from src.api import get_analyzer_service, AnalysisResult

from .theme import COLORS, SPACING, get_score_color
from .file_selector import FileSelectorGroup
from .export_manager import ExportManager
from .widgets.score_card import ScoreCard
from .widgets.browser_card import BrowserCard
from .widgets.charts import CompatibilityBarChart
from .widgets.messagebox import (
    show_info, show_warning, show_error, ask_question, ProgressDialog
)
from .widgets.rules_manager import show_rules_manager


class MainWindow(ctk.CTkFrame):
    """Main application window content for Cross Guard."""

    def __init__(self, master):
        """Initialize the main window."""
        super().__init__(master, fg_color=COLORS['bg_dark'])

        self.master = master
        self.current_report = None
        self.export_manager = ExportManager(master)
        self._analyzer_service = get_analyzer_service()
        self._current_page = None

        # Build the upload page directly (simplest approach)
        self._build_upload_page()

    def _build_upload_page(self):
        """Build the upload page UI directly in this frame."""
        # Clear any existing content
        for widget in self.winfo_children():
            widget.destroy()

        self._current_page = 'upload'

        # Scrollable content area
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_dark'],
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['primary'],
        )
        self.content.pack(fill="both", expand=True, padx=30, pady=30)

        # Header section
        self._create_header()

        # File selection sections
        self._create_file_selectors()

        # Action buttons
        self._create_action_buttons()

    def _create_header(self):
        """Create the header section."""
        header_frame = ctk.CTkFrame(
            self.content,
            fg_color=COLORS['bg_medium'],
            corner_radius=10,
        )
        header_frame.pack(fill="x", pady=(0, 20))

        # Inner container
        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=20, pady=20)

        # Left side - Logo and title
        title_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        title_frame.pack(side="left")

        # Try to load logo
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            try:
                logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(80, 80),
                )
                logo_label = ctk.CTkLabel(title_frame, image=logo_image, text="")
                logo_label.pack(side="left", padx=(0, 15))
            except Exception:
                pass

        # Title
        title_label = ctk.CTkLabel(
            title_frame,
            text="Browser Compatibility Checker",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title_label.pack(side="left")

        # Buttons frame (right side)
        buttons_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        buttons_frame.pack(side="right")

        # Custom Rules button
        rules_btn = ctk.CTkButton(
            buttons_frame,
            text="⚙ Custom Rules",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140,
            height=40,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            command=self._open_rules_manager,
        )
        rules_btn.pack(side="left", padx=(0, 10))

        # Update Database button
        update_btn = ctk.CTkButton(
            buttons_frame,
            text="Update Database",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=160,
            height=40,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            command=self._update_database,
        )
        update_btn.pack(side="left")

    def _create_file_selectors(self):
        """Create the file selection sections."""
        # HTML Files
        self.html_selector = FileSelectorGroup(
            self.content,
            "HTML Files",
            "Add HTML files to analyze",
            "html",
            on_files_changed=self._update_status,
        )
        self.html_selector.pack(fill="x", pady=(0, 15))

        # CSS Files
        self.css_selector = FileSelectorGroup(
            self.content,
            "CSS Files",
            "Add CSS files to analyze",
            "css",
            on_files_changed=self._update_status,
        )
        self.css_selector.pack(fill="x", pady=(0, 15))

        # JavaScript Files
        self.js_selector = FileSelectorGroup(
            self.content,
            "JavaScript Files",
            "Add JavaScript files to analyze",
            "javascript",
            on_files_changed=self._update_status,
        )
        self.js_selector.pack(fill="x", pady=(0, 15))

    def _create_action_buttons(self):
        """Create the action buttons."""
        # Spacer
        spacer = ctk.CTkFrame(self.content, fg_color="transparent", height=20)
        spacer.pack(fill="x")

        # Button container
        button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        # Clear button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear All Files",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140,
            height=45,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_muted'],
            command=self._clear_all_files,
        )
        clear_btn.pack(side="left")

        # Analyze button
        analyze_btn = ctk.CTkButton(
            button_frame,
            text="Analyze Compatibility",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=45,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            command=self._analyze_files,
        )
        analyze_btn.pack(side="right")

    def _build_results_page(self, report: Dict):
        """Build the results page UI."""
        # Clear any existing content
        for widget in self.winfo_children():
            widget.destroy()

        self._current_page = 'results'
        self.current_report = report

        # Top bar with back and export buttons
        top_bar = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'], corner_radius=8)
        top_bar.pack(fill="x", padx=30, pady=(30, 20))

        bar_inner = ctk.CTkFrame(top_bar, fg_color="transparent")
        bar_inner.pack(fill="x", padx=15, pady=10)

        # Back button
        back_btn = ctk.CTkButton(
            bar_inner,
            text="← Back to Upload",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=45,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            command=self._build_upload_page,
        )
        back_btn.pack(side="left")

        # Export buttons
        export_frame = ctk.CTkFrame(bar_inner, fg_color="transparent")
        export_frame.pack(side="right")

        ctk.CTkLabel(
            export_frame,
            text="Export:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_muted'],
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            export_frame,
            text="PDF",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            height=45,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            command=lambda: self.export_manager.export_pdf(self.current_report),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            export_frame,
            text="JSON",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            height=45,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            command=lambda: self.export_manager.export_json(self.current_report),
        ).pack(side="left")

        # Scrollable results area
        results_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_dark'],
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['primary'],
        )
        results_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Results title
        ctk.CTkLabel(
            results_scroll,
            text="Analysis Complete!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 20))

        # Add result sections
        self._add_summary_section(results_scroll, report.get('summary', {}))
        self._add_score_section(results_scroll, report.get('scores', {}))
        self._add_chart_section(results_scroll, report.get('browsers', {}))
        self._add_browser_section(results_scroll, report.get('browsers', {}))
        self._add_recommendations_section(results_scroll, report.get('recommendations', []))

    def _add_summary_section(self, parent, summary: Dict):
        """Add summary section to results."""
        section = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8)
        section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            section, text="Summary",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", padx=15, pady=(12, 8))

        stats_frame = ctk.CTkFrame(section, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=(0, 12))

        stats = [
            f"Total Features: {summary.get('total_features', 0)}",
            f"HTML: {summary.get('html_features', 0)} | CSS: {summary.get('css_features', 0)} | JS: {summary.get('js_features', 0)}",
            f"Critical Issues: {summary.get('critical_issues', 0)}",
        ]
        for text in stats:
            ctk.CTkLabel(
                stats_frame, text=text,
                font=ctk.CTkFont(size=13),
                text_color=COLORS['text_secondary'],
            ).pack(anchor="w", pady=2)

    def _add_score_section(self, parent, scores: Dict):
        """Add score section to results."""
        section = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8)
        section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            section, text="Compatibility Score",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", padx=15, pady=(12, 8))

        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 12))

        # Score card
        weighted_score = scores.get('weighted_score', 0)
        grade = scores.get('grade', 'N/A')

        score_card = ScoreCard(content, weighted_score, grade, "Weighted Score")
        score_card.pack(side="left", padx=(0, 20))
        score_card.set_score(weighted_score, grade, animate=True)

        # Details
        details = ctk.CTkFrame(content, fg_color="transparent")
        details.pack(side="left", fill="y")

        ctk.CTkLabel(
            details,
            text=f"Risk Level: {scores.get('risk_level', 'N/A').upper()}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(
            details,
            text=f"Simple Score: {scores.get('simple_score', 0):.1f}%",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w")

    def _add_chart_section(self, parent, browsers: Dict):
        """Add chart section to results."""
        if not browsers:
            return

        section = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8)
        section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            section, text="Browser Comparison",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", padx=15, pady=(12, 8))

        chart_data = {
            name: {
                'supported': d.get('supported', 0),
                'partial': d.get('partial', 0),
                'unsupported': d.get('unsupported', 0),
                'compatibility_percentage': d.get('compatibility_percentage', 0)
            }
            for name, d in browsers.items()
        }

        chart = CompatibilityBarChart(section)
        chart.pack(fill="x", padx=15, pady=(0, 12))
        chart.set_data(chart_data)

    def _add_browser_section(self, parent, browsers: Dict):
        """Add browser details section to results."""
        section = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8)
        section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            section, text="Browser Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", padx=15, pady=(12, 8))

        cards_frame = ctk.CTkFrame(section, fg_color="transparent")
        cards_frame.pack(fill="x", padx=15, pady=(0, 12))

        for browser_name, details in browsers.items():
            card = BrowserCard(
                cards_frame,
                browser_name=browser_name,
                version=details.get('version', ''),
                supported=details.get('supported', 0),
                partial=details.get('partial', 0),
                unsupported=details.get('unsupported', 0),
                compatibility_pct=details.get('compatibility_percentage', 0),
                unsupported_features=details.get('unsupported_features', []),
                partial_features=details.get('partial_features', []),
            )
            card.pack(fill="x", pady=(0, 10))

    def _add_recommendations_section(self, parent, recommendations: List[str]):
        """Add recommendations section to results."""
        section = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8)
        section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            section, text="Recommendations",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", padx=15, pady=(12, 8))

        recs_frame = ctk.CTkFrame(section, fg_color="transparent")
        recs_frame.pack(fill="x", padx=15, pady=(0, 12))

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_frame = ctk.CTkFrame(recs_frame, fg_color=COLORS['bg_light'], corner_radius=5)
                rec_frame.pack(fill="x", pady=(0, 6))
                ctk.CTkLabel(
                    rec_frame,
                    text=f"{i}. {rec}",
                    font=ctk.CTkFont(size=13),
                    text_color=COLORS['text_secondary'],
                    wraplength=600,
                    justify="left",
                ).pack(anchor="w", padx=10, pady=8)
        else:
            ctk.CTkLabel(
                recs_frame,
                text="No issues found! Your code is well-supported.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS['success'],
            ).pack(anchor="w")

    def _clear_all_files(self):
        """Clear all selected files."""
        self.html_selector.clear_files()
        self.css_selector.clear_files()
        self.js_selector.clear_files()
        self._update_status()

    def _update_status(self):
        """Update window title with file count."""
        total = (len(self.html_selector.get_files()) +
                 len(self.css_selector.get_files()) +
                 len(self.js_selector.get_files()))

        if total > 0:
            self.master.title(f"Cross Guard - {total} file(s) selected")
        else:
            self.master.title("Cross Guard - Browser Compatibility Checker")

    def _analyze_files(self):
        """Analyze selected files."""
        html_files = self.html_selector.get_files()
        css_files = self.css_selector.get_files()
        js_files = self.js_selector.get_files()

        if not html_files and not css_files and not js_files:
            show_warning(self.master, "No Files", "Please select at least one file.")
            return

        file_count = len(html_files) + len(css_files) + len(js_files)
        if ask_question(self.master, "Confirm", f"Analyze {file_count} file(s)?"):
            self._run_analysis(html_files, css_files, js_files)

    def _run_analysis(self, html_files, css_files, js_files):
        """Run the analysis."""
        try:
            progress = ProgressDialog(self.master, "Analyzing", "Starting...")
            progress.set_progress(10)
            self.master.update()

            progress.set_progress(30, "Analyzing files...")
            result = self._analyzer_service.analyze_files(
                html_files=html_files if html_files else None,
                css_files=css_files if css_files else None,
                js_files=js_files if js_files else None,
            )

            progress.set_progress(100)
            progress.close()

            if result.success:
                report = result.to_dict()
                self._build_results_page(report)
            else:
                show_error(self.master, "Failed", f"{result.error or 'Unknown error'}")

        except Exception as e:
            show_error(self.master, "Error", str(e))
            import traceback
            traceback.print_exc()

    def _update_database(self):
        """Update the Can I Use database."""
        try:
            db_info = self._analyzer_service.get_database_info()

            msg = f"Features: {db_info.features_count}\n"
            msg += f"Last updated: {db_info.last_updated}\n\n"
            msg += "Update now?"

            if not ask_question(self.master, "Update Database", msg):
                return

            progress = ProgressDialog(self.master, "Updating", "...")
            progress.set_progress(0)

            def update_progress(message: str, percentage: int):
                progress.set_progress(percentage, message)
                self.master.update()

            result = self._analyzer_service.update_database(update_progress)

            progress.set_progress(100)
            progress.close()

            if result.success:
                show_info(self.master, "Done", result.message or 'Updated!')
            else:
                show_error(self.master, "Failed", result.message or 'Error')

        except Exception as e:
            show_error(self.master, "Error", str(e))

    def _open_rules_manager(self):
        """Open the custom rules manager dialog."""
        def on_rules_changed():
            # Reload custom rules when they change
            from src.parsers.custom_rules_loader import reload_custom_rules
            reload_custom_rules()
        
        show_rules_manager(self.master, on_rules_changed)
