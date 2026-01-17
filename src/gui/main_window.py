"""
Cross Guard Main Window
Main GUI window with file selection interface for browser compatibility analysis.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QProgressDialog,
    QStackedWidget, QScrollArea, QMessageBox, QGroupBox, QSizePolicy,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt6.QtGui import QFont, QPixmap, QIcon
from typing import Dict, List
from pathlib import Path

# API Layer imports - Frontend only depends on API, not backend directly
from src.api import get_analyzer_service, AnalysisResult

from .file_selector import FileSelectorGroup
from .export_manager import ExportManager
from .styles import get_main_stylesheet
from .widgets.score_card import ScoreCard
from .widgets.browser_card import BrowserCard
from .widgets.charts import CompatibilityBarChart


class MainWindow(QMainWindow):
    """Main application window for Cross Guard."""

    def __init__(self):
        super().__init__()
        self.current_report = None
        self.export_manager = ExportManager(self)
        # Use API service layer instead of direct backend access
        self._analyzer_service = get_analyzer_service()

        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Cross Guard - Browser Compatibility Checker")
        self.setMinimumSize(1000, 850)
        self.resize(1100, 900)
        
        # Set window icon
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))
        
        # Create stacked widget for page switching
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create upload page (index 0)
        upload_page = self._create_upload_page()
        self.stacked_widget.addWidget(upload_page)
        
        # Create results page (index 1)
        results_page = self._create_results_page()
        self.stacked_widget.addWidget(results_page)
        
        # Start with upload page
        self.stacked_widget.setCurrentIndex(0)
        
        # Apply styling
        self.setStyleSheet(get_main_stylesheet())
    
    def _create_upload_page(self) -> QWidget:
        """Create the file upload page."""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        self._create_header(main_layout)
        
        # File selection section
        self._create_file_section(main_layout)
        
        # Action buttons at bottom
        self._create_action_buttons(main_layout)
        
        return page
    
    def _create_results_page(self) -> QWidget:
        """Create the results display page."""
        page = QWidget()
        page.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Top button bar with background
        top_bar_widget = QWidget()
        top_bar_widget.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 8px;")
        top_bar = QHBoxLayout(top_bar_widget)
        top_bar.setContentsMargins(15, 10, 15, 10)
        top_bar.setSpacing(15)
        
        # Back button
        back_btn = QPushButton("← Back to Upload")
        back_btn.setObjectName("backButton")
        back_btn.setMinimumHeight(45)
        back_btn.setMinimumWidth(150)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        top_bar.addWidget(back_btn)
        
        top_bar.addStretch()
        
        # Export label
        export_label = QLabel("Export Report:")
        export_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; padding-right: 10px;")
        top_bar.addWidget(export_label)
        
        # Export PDF button
        export_pdf_btn = QPushButton("PDF")
        export_pdf_btn.setObjectName("exportPdfButton")
        export_pdf_btn.setMinimumHeight(45)
        export_pdf_btn.setMinimumWidth(120)
        export_pdf_btn.clicked.connect(lambda: self.export_manager.export_pdf(self.current_report))
        top_bar.addWidget(export_pdf_btn)
        
        # Export JSON button
        export_json_btn = QPushButton("JSON")
        export_json_btn.setObjectName("exportJsonButton")
        export_json_btn.setMinimumHeight(45)
        export_json_btn.setMinimumWidth(120)
        export_json_btn.clicked.connect(lambda: self.export_manager.export_json(self.current_report))
        top_bar.addWidget(export_json_btn)
        
        layout.addWidget(top_bar_widget)
        
        # Scroll area for results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("resultsScroll")
        
        # Results content widget
        self.results_content = QWidget()
        self.results_layout = QVBoxLayout(self.results_content)
        self.results_layout.setSpacing(20)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.results_content)
        layout.addWidget(scroll)
        
        return page
        
    def _create_header(self, parent_layout):
        """Create the header section with title and description."""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        # Left side - Logo and tagline horizontally
        title_layout = QHBoxLayout()
        title_layout.setSpacing(15)
        
        # Logo (bigger size)
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            title_layout.addWidget(logo_label)
        
        # Tagline (bigger font, next to logo)
        tagline_label = QLabel("Browser Compatibility Checker")
        tagline_font = QFont()
        tagline_font.setPointSize(22)
        tagline_font.setBold(True)
        tagline_label.setFont(tagline_font)
        tagline_label.setStyleSheet("color: #333;")
        tagline_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(tagline_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Right side - Update Database button
        update_db_btn = QPushButton("Update Database")
        update_db_btn.setObjectName("updateDbButton")
        update_db_btn.setMinimumHeight(40)
        update_db_btn.setMinimumWidth(160)
        update_db_btn.clicked.connect(self._update_database)
        header_layout.addWidget(update_db_btn)
        
        parent_layout.addWidget(header_frame)
        
    def _create_file_section(self, parent_layout):
        """Create the file selection section."""
        # HTML Files Section
        self.html_selector = FileSelectorGroup(
            "HTML Files",
            "Add HTML files to analyze",
            "html"
        )
        self.html_selector.files_changed.connect(self._update_status)
        parent_layout.addWidget(self.html_selector)
        
        # CSS Files Section
        self.css_selector = FileSelectorGroup(
            "CSS Files",
            "Add CSS files to analyze",
            "css"
        )
        self.css_selector.files_changed.connect(self._update_status)
        parent_layout.addWidget(self.css_selector)
        
        # JavaScript Files Section
        self.js_selector = FileSelectorGroup(
            "JavaScript Files",
            "Add JavaScript files to analyze",
            "javascript"
        )
        self.js_selector.files_changed.connect(self._update_status)
        parent_layout.addWidget(self.js_selector)
        
    def _create_action_buttons(self, parent_layout):
        """Create the action buttons at the bottom."""
        parent_layout.addStretch()
        
        # Button container
        button_container = QHBoxLayout()
        button_container.setSpacing(15)
        
        # Clear all button
        clear_all_btn = QPushButton("Clear All Files")
        clear_all_btn.setObjectName("clearAllButton")
        clear_all_btn.setMinimumHeight(45)
        clear_all_btn.clicked.connect(self._clear_all_files)
        button_container.addWidget(clear_all_btn)
        
        button_container.addStretch()
        
        # Analyze button (prominent)
        analyze_btn = QPushButton("Analyze Compatibility")
        analyze_btn.setObjectName("analyzeButton")
        analyze_btn.setMinimumHeight(45)
        analyze_btn.setMinimumWidth(200)
        analyze_btn.clicked.connect(self._analyze_files)
        button_container.addWidget(analyze_btn)
        
        parent_layout.addLayout(button_container)
        
    def _clear_all_files(self):
        """Clear all selected files."""
        self.html_selector.clear_files()
        self.css_selector.clear_files()
        self.js_selector.clear_files()
        self._update_status()
    
    def _update_status(self):
        """Update the window title with file count."""
        html_count = len(self.html_selector.get_files())
        css_count = len(self.css_selector.get_files())
        js_count = len(self.js_selector.get_files())
        total_files = html_count + css_count + js_count
        
        if total_files > 0:
            self.setWindowTitle(f"Cross Guard - {total_files} file(s) selected")
        else:
            self.setWindowTitle("Cross Guard - Browser Compatibility Checker")
        
    def _analyze_files(self):
        """Analyze selected files for browser compatibility."""
        # Get files from selectors
        html_files = self.html_selector.get_files()
        css_files = self.css_selector.get_files()
        js_files = self.js_selector.get_files()
        
        # Check if any files are selected
        if not html_files and not css_files and not js_files:
            QMessageBox.warning(
                self,
                "No Files Selected",
                "Please select at least one file to analyze."
            )
            return
        
        # Confirm analysis
        file_count = len(html_files) + len(css_files) + len(js_files)
        reply = QMessageBox.question(
            self,
            "Confirm Analysis",
            f"Analyze {file_count} file(s) for browser compatibility?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._run_analysis(html_files, css_files, js_files)
    
    def _run_analysis(self, html_files, css_files, js_files):
        """Run the compatibility analysis using the API service."""
        try:
            # Show progress dialog
            progress = QProgressDialog("Analyzing files...", None, 0, 100, self)
            progress.setWindowTitle("Analysis in Progress")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(10)

            progress.setLabelText("Initializing analyzer...")
            progress.setValue(30)

            # Use API service instead of direct backend access
            result = self._analyzer_service.analyze_files(
                html_files=html_files if html_files else None,
                css_files=css_files if css_files else None,
                js_files=js_files if js_files else None,
            )
            progress.setValue(90)

            # Close progress dialog
            progress.setValue(100)
            progress.close()

            # Show results
            if result.success:
                # Convert AnalysisResult to dict for display and export
                report = result.to_dict()
                self._show_results(report)
            else:
                QMessageBox.critical(
                    self,
                    "Analysis Failed",
                    f"Analysis failed: {result.error or 'Unknown error'}"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"An error occurred during analysis:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()
    
    def _show_results(self, report: Dict):
        """Show analysis results in the results page."""
        self.current_report = report
        self._clear_results()

        # Build result sections
        self._add_results_title()
        self._add_summary_section(report.get('summary', {}))
        self._add_score_section(report.get('scores', {}))
        self._add_chart_section(report.get('browsers', {}))
        self._add_browser_section(report.get('browsers', {}))
        self._add_recommendations_section(report.get('recommendations', []))

        self.results_layout.addStretch()

        # Switch to results page with animation
        self._switch_to_results_page()

        # Print to console for debugging
        print("\n" + "=" * 50)
        print("FULL ANALYSIS REPORT:")
        print("=" * 50)
        import json
        print(json.dumps(report, indent=2))

    def _clear_results(self):
        """Clear previous results from the layout."""
        for i in reversed(range(self.results_layout.count())):
            item = self.results_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            else:
                self.results_layout.removeItem(item)

    def _add_results_title(self):
        """Add the results title."""
        title = QLabel("Analysis Complete!")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #333; padding: 10px 0;")
        self.results_layout.addWidget(title)

    def _add_summary_section(self, summary: Dict):
        """Add the summary section."""
        summary_group = QGroupBox("Summary")
        summary_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.setSpacing(4)
        summary_layout.setContentsMargins(15, 12, 15, 12)

        labels = [
            (f"Total Features: {summary.get('total_features', 0)}", "font-size: 14px; font-weight: bold; color: #333;"),
            (f"HTML Features: {summary.get('html_features', 0)}", "font-size: 13px; color: #555;"),
            (f"CSS Features: {summary.get('css_features', 0)}", "font-size: 13px; color: #555;"),
            (f"JS Features: {summary.get('js_features', 0)}", "font-size: 13px; color: #555;"),
            (f"Critical Issues: {summary.get('critical_issues', 0)}", "font-size: 13px; color: #F44336; font-weight: bold;"),
        ]

        for text, style in labels:
            label = QLabel(text)
            label.setStyleSheet(style)
            summary_layout.addWidget(label)

        self.results_layout.addWidget(summary_group)

    def _add_score_section(self, scores: Dict):
        """Add the compatibility score section with visual ScoreCard."""
        score_group = QGroupBox("Compatibility Score")
        score_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        score_layout = QHBoxLayout(score_group)
        score_layout.setSpacing(20)
        score_layout.setContentsMargins(15, 12, 15, 12)

        # Visual score card
        weighted_score = scores.get('weighted_score', 0)
        grade = scores.get('grade', 'N/A')
        score_card = ScoreCard(weighted_score, grade, "Weighted Score")
        score_card.set_score(weighted_score, grade, animate=True)
        score_layout.addWidget(score_card)

        # Text details
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(8)
        details_layout.setContentsMargins(0, 0, 0, 0)

        risk_label = QLabel(f"Risk Level: {scores.get('risk_level', 'N/A').upper()}")
        risk_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        details_layout.addWidget(risk_label)

        simple_label = QLabel(f"Simple Score: {scores.get('simple_score', 0):.1f}%")
        simple_label.setStyleSheet("font-size: 14px; color: #555;")
        details_layout.addWidget(simple_label)

        weighted_label = QLabel(f"Weighted Score: {scores.get('weighted_score', 0):.1f}%")
        weighted_label.setStyleSheet("font-size: 14px; color: #555;")
        details_layout.addWidget(weighted_label)

        details_layout.addStretch()
        score_layout.addWidget(details_widget)
        score_layout.addStretch()

        self.results_layout.addWidget(score_group)

    def _add_chart_section(self, browsers: Dict):
        """Add the browser comparison chart."""
        if not browsers:
            return

        chart_group = QGroupBox("Browser Comparison")
        chart_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.setContentsMargins(15, 12, 15, 12)

        # Prepare data for chart
        chart_data = {}
        for browser_name, details in browsers.items():
            chart_data[browser_name] = {
                'supported': details.get('supported', 0),
                'partial': details.get('partial', 0),
                'unsupported': details.get('unsupported', 0),
                'compatibility_percentage': details.get('compatibility_percentage', 0)
            }

        chart = CompatibilityBarChart()
        chart.set_data(chart_data)
        chart_layout.addWidget(chart)

        self.results_layout.addWidget(chart_group)

    def _add_browser_section(self, browsers: Dict):
        """Add the browser compatibility section with enhanced cards."""
        browser_group = QGroupBox("Browser Details")
        browser_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.setSpacing(12)
        browser_layout.setContentsMargins(15, 12, 15, 12)

        for browser_name, details in browsers.items():
            card = BrowserCard(
                browser_name=browser_name,
                version=details.get('version', ''),
                supported=details.get('supported', 0),
                partial=details.get('partial', 0),
                unsupported=details.get('unsupported', 0),
                compatibility_pct=details.get('compatibility_percentage', 0),
                unsupported_features=details.get('unsupported_features', []),
                partial_features=details.get('partial_features', [])
            )
            browser_layout.addWidget(card)

        self.results_layout.addWidget(browser_group)

    def _add_recommendations_section(self, recommendations: List[str]):
        """Add the recommendations section."""
        rec_group = QGroupBox("Recommendations")
        rec_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        rec_layout = QVBoxLayout(rec_group)
        rec_layout.setSpacing(6)
        rec_layout.setContentsMargins(15, 12, 15, 12)

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_label = QLabel(f"{i}. {rec}")
                rec_label.setWordWrap(True)
                rec_label.setStyleSheet(
                    "font-size: 13px; color: #555; background-color: #f9f9f9; "
                    "border-radius: 5px; padding: 8px;"
                )
                rec_layout.addWidget(rec_label)
        else:
            rec_label = QLabel("No issues found! Your code is well-supported.")
            rec_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
            rec_layout.addWidget(rec_label)

        self.results_layout.addWidget(rec_group)

    def _switch_to_results_page(self):
        """Switch to results page with fade animation."""
        # Get the results page widget
        results_page = self.stacked_widget.widget(1)

        # Create opacity effect
        opacity_effect = QGraphicsOpacityEffect(results_page)
        results_page.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)

        # Switch page
        self.stacked_widget.setCurrentIndex(1)

        # Animate fade in
        self._fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self._fade_animation.setDuration(300)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_animation.finished.connect(lambda: results_page.setGraphicsEffect(None))
        self._fade_animation.start()
    
    def _update_database(self):
        """Update the Can I Use database using the API service."""
        try:
            # Get current database info via API
            db_info = self._analyzer_service.get_database_info()

            # Confirm update
            confirm_msg = f"Current database:\n"
            confirm_msg += f"• Features: {db_info.features_count}\n"
            confirm_msg += f"• Last updated: {db_info.last_updated}\n"
            confirm_msg += f"• Git repository: {'Yes' if db_info.is_git_repo else 'No'}\n\n"
            confirm_msg += "Update to the latest version?"

            reply = QMessageBox.question(
                self,
                "Update Database",
                confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Show progress dialog
            progress = QProgressDialog("Updating database...", None, 0, 100, self)
            progress.setWindowTitle("Database Update")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            # Progress callback
            def update_progress(message: str, percentage: int):
                progress.setLabelText(message)
                progress.setValue(percentage)

            # Run update via API service
            result = self._analyzer_service.update_database(update_progress)

            # Close progress
            progress.setValue(100)
            progress.close()

            # Show result
            if result.success:
                if result.no_changes:
                    QMessageBox.information(
                        self,
                        "Database Up to Date",
                        result.message or 'Database is already up to date'
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Update Successful",
                        result.message or 'Database updated successfully!'
                    )
            else:
                QMessageBox.critical(
                    self,
                    "Update Failed",
                    f"{result.message or 'Unknown error'}\n\n{result.error or ''}"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Update Error",
                f"An error occurred while updating the database:\n{str(e)}"
            )
