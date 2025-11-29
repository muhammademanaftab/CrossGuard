"""
Cross Guard Main Window
Main GUI window with file selection interface for browser compatibility analysis.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QProgressDialog,
    QStackedWidget, QScrollArea, QMessageBox, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict

from src.analyzer.main import CrossGuardAnalyzer
from src.analyzer.database import reload_database
from src.analyzer.database_updater import DatabaseUpdater
from src.utils.config import CANIUSE_DIR
from .file_selector import FileSelectorGroup
from .export_manager import ExportManager
from .styles import get_main_stylesheet
from pathlib import Path


class MainWindow(QMainWindow):
    """Main application window for Cross Guard."""
    
    def __init__(self):
        super().__init__()
        self.current_report = None
        self.export_manager = ExportManager(self)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Cross Guard - Browser Compatibility Checker")
        self.setMinimumSize(1000, 750)
        self.resize(1100, 800)
        
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
        export_pdf_btn = QPushButton("📄 PDF")
        export_pdf_btn.setObjectName("exportPdfButton")
        export_pdf_btn.setMinimumHeight(45)
        export_pdf_btn.setMinimumWidth(120)
        export_pdf_btn.clicked.connect(lambda: self.export_manager.export_pdf(self.current_report))
        top_bar.addWidget(export_pdf_btn)
        
        # Export JSON button
        export_json_btn = QPushButton("💾 JSON")
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
        
        # Left side - Title and subtitle
        title_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("🛡️ Cross Guard")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Browser Compatibility Checker")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666;")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Right side - Update Database button
        update_db_btn = QPushButton("🔄 Update Database")
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
        """Run the compatibility analysis."""
        try:
            # Show progress dialog
            progress = QProgressDialog("Analyzing files...", None, 0, 100, self)
            progress.setWindowTitle("Analysis in Progress")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(10)
            
            # Create analyzer
            analyzer = CrossGuardAnalyzer()
            progress.setValue(20)
            
            # Set target browsers
            target_browsers = {
                'chrome': '144',
                'firefox': '146',
                'safari': '18.4',
                'edge': '144'
            }
            progress.setValue(30)
            
            # Run analysis
            report = analyzer.analyze_project(
                html_files=html_files if html_files else None,
                css_files=css_files if css_files else None,
                js_files=js_files if js_files else None,
                target_browsers=target_browsers
            )
            progress.setValue(90)
            
            # Close progress dialog
            progress.setValue(100)
            progress.close()
            
            # Show results
            if report.get('success'):
                self._show_results(report)
            else:
                QMessageBox.critical(
                    self,
                    "Analysis Failed",
                    f"Analysis failed: {report.get('error', 'Unknown error')}"
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
        
        # Clear previous results
        for i in reversed(range(self.results_layout.count())): 
            item = self.results_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            else:
                self.results_layout.removeItem(item)
        
        summary = report.get('summary', {})
        scores = report.get('scores', {})
        
        # Title
        title = QLabel("Analysis Complete!")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #333; padding: 10px 0;")
        self.results_layout.addWidget(title)
        
        # Summary Section
        summary_group = QGroupBox("📊 Summary")
        summary_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.setSpacing(4)
        summary_layout.setContentsMargins(15, 12, 15, 12)
        
        total_label = QLabel(f"Total Features: {summary.get('total_features', 0)}")
        total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        summary_layout.addWidget(total_label)
        
        html_label = QLabel(f"HTML Features: {summary.get('html_features', 0)}")
        html_label.setStyleSheet("font-size: 13px; color: #555;")
        summary_layout.addWidget(html_label)
        
        css_label = QLabel(f"CSS Features: {summary.get('css_features', 0)}")
        css_label.setStyleSheet("font-size: 13px; color: #555;")
        summary_layout.addWidget(css_label)
        
        js_label = QLabel(f"JS Features: {summary.get('js_features', 0)}")
        js_label.setStyleSheet("font-size: 13px; color: #555;")
        summary_layout.addWidget(js_label)
        
        critical_label = QLabel(f"Critical Issues: {summary.get('critical_issues', 0)}")
        critical_label.setStyleSheet("font-size: 13px; color: #F44336; font-weight: bold;")
        summary_layout.addWidget(critical_label)
        
        self.results_layout.addWidget(summary_group)
        
        # Compatibility Score Section
        score_group = QGroupBox("🎯 Compatibility Score")
        score_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        score_layout = QVBoxLayout(score_group)
        score_layout.setSpacing(6)
        score_layout.setContentsMargins(15, 12, 15, 12)
        
        grade_label = QLabel(f"Grade: {scores.get('grade', 'N/A')}")
        grade_label.setStyleSheet("font-size: 32px; color: #2196F3; font-weight: bold;")
        score_layout.addWidget(grade_label)
        
        risk_label = QLabel(f"Risk Level: {scores.get('risk_level', 'N/A').upper()}")
        risk_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        score_layout.addWidget(risk_label)
        
        simple_label = QLabel(f"Simple Score: {scores.get('simple_score', 0):.1f}%")
        simple_label.setStyleSheet("font-size: 13px; color: #555;")
        score_layout.addWidget(simple_label)
        
        weighted_label = QLabel(f"Weighted Score: {scores.get('weighted_score', 0):.1f}%")
        weighted_label.setStyleSheet("font-size: 13px; color: #555;")
        score_layout.addWidget(weighted_label)
        
        self.results_layout.addWidget(score_group)
        
        # Browser Compatibility Section
        browser_group = QGroupBox("🌐 Browser Compatibility")
        browser_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.setSpacing(12)
        browser_layout.setContentsMargins(15, 12, 15, 12)

        browsers = report.get('browsers', {})
        for browser_name, details in browsers.items():
            compat_pct = details.get('compatibility_percentage', 0)
            supported = details.get('supported', 0)
            partial = details.get('partial', 0)
            unsupported = details.get('unsupported', 0)

            browser_card = QFrame()
            browser_card.setObjectName("browserCard")
            card_layout = QVBoxLayout(browser_card)
            card_layout.setSpacing(4)
            card_layout.setContentsMargins(10, 8, 10, 8)

            # Browser header
            browser_label = QLabel(f"{browser_name.upper()} {details.get('version', '')}")
            browser_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #333;")
            card_layout.addWidget(browser_label)

            # Stats in a horizontal layout
            stats_widget = QWidget()
            stats_h_layout = QHBoxLayout(stats_widget)
            stats_h_layout.setContentsMargins(0, 0, 0, 0)
            stats_h_layout.setSpacing(20)

            supported_label = QLabel(f"✅ Supported: {supported}")
            supported_label.setStyleSheet("color: #4CAF50; font-size: 13px; font-weight: bold;")
            stats_h_layout.addWidget(supported_label)
            
            partial_label_widget = QLabel(f"⚠️ Partial: {partial}")
            partial_label_widget.setStyleSheet("color: #FF9800; font-size: 13px; font-weight: bold;")
            stats_h_layout.addWidget(partial_label_widget)
            
            unsupported_label = QLabel(f"❌ Unsupported: {unsupported}")
            unsupported_label.setStyleSheet("color: #F44336; font-size: 13px; font-weight: bold;")
            stats_h_layout.addWidget(unsupported_label)
            
            stats_h_layout.addStretch()
            card_layout.addWidget(stats_widget)

            # Compatibility percentage
            compat_label = QLabel(f"Compatibility: {compat_pct:.1f}%")
            compat_label.setStyleSheet("color: #2196F3; font-size: 14px; font-weight: bold;")
            card_layout.addWidget(compat_label)

            # Show unsupported features if any
            if details.get('unsupported_features'):
                unsup_label = QLabel(f"Not supported: {', '.join(details['unsupported_features'][:5])}")
                unsup_label.setStyleSheet("color: #d32f2f; font-size: 12px;")
                unsup_label.setWordWrap(True)
                card_layout.addWidget(unsup_label)

            # Show partial support features if any
            if details.get('partial_features'):
                partial_feat_label = QLabel(f"Partial support: {', '.join(details['partial_features'][:5])}")
                partial_feat_label.setStyleSheet("color: #f57c00; font-size: 12px;")
                partial_feat_label.setWordWrap(True)
                card_layout.addWidget(partial_feat_label)

            browser_layout.addWidget(browser_card)

        self.results_layout.addWidget(browser_group)

        # Recommendations Section
        rec_group = QGroupBox("📝 Recommendations")
        rec_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        rec_layout = QVBoxLayout(rec_group)
        rec_layout.setSpacing(6)
        rec_layout.setContentsMargins(15, 12, 15, 12)
        
        recommendations = report.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_label = QLabel(f"{i}. {rec}")
                rec_label.setWordWrap(True)
                rec_label.setStyleSheet("font-size: 13px; color: #555; background-color: #f9f9f9; border-radius: 5px; padding: 8px;")
                rec_layout.addWidget(rec_label)
        else:
            rec_label = QLabel("✅ No issues found! Your code is well-supported.")
            rec_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
            rec_layout.addWidget(rec_label)
        
        self.results_layout.addWidget(rec_group)
        
        self.results_layout.addStretch()
        
        # Switch to results page
        self.stacked_widget.setCurrentIndex(1)
        
        # Print to console for debugging
        print("\n" + "="*50)
        print("FULL ANALYSIS REPORT:")
        print("="*50)
        import json
        print(json.dumps(report, indent=2))
    
    def _update_database(self):
        """Update the Can I Use database."""
        try:
            from datetime import datetime
            
            # Create updater
            updater = DatabaseUpdater(Path(CANIUSE_DIR))
            
            # Get current database info
            info = updater.get_database_info()
            
            # Format last updated date
            last_updated = info.get('last_updated', 'Unknown')
            if last_updated != 'Unknown' and isinstance(last_updated, (int, float)):
                # Convert Unix timestamp to readable date
                last_updated = datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M')
            
            # Confirm update
            confirm_msg = f"Current database:\n"
            confirm_msg += f"• Features: {info.get('features_count', 'Unknown')}\n"
            confirm_msg += f"• Last updated: {last_updated}\n"
            confirm_msg += f"• Git repository: {'Yes' if info.get('is_git_repo') else 'No'}\n\n"
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
            
            # Run update
            result = updater.update_database(update_progress)
            
            # Close progress
            progress.setValue(100)
            progress.close()
            
            # Show result
            if result.get('success'):
                if result.get('no_changes'):
                    QMessageBox.information(
                        self,
                        "Database Up to Date",
                        result.get('message', 'Database is already up to date')
                    )
                else:
                    # Reload database
                    reload_progress = QProgressDialog("Reloading database...", None, 0, 100, self)
                    reload_progress.setWindowTitle("Reloading")
                    reload_progress.setWindowModality(Qt.WindowModality.WindowModal)
                    reload_progress.setMinimumDuration(0)
                    reload_progress.setValue(50)
                    
                    reload_database()
                    
                    reload_progress.setValue(100)
                    reload_progress.close()
                    
                    QMessageBox.information(
                        self,
                        "Update Successful",
                        result.get('message', 'Database updated successfully!')
                    )
            else:
                QMessageBox.critical(
                    self,
                    "Update Failed",
                    f"{result.get('message', 'Unknown error')}\n\n{result.get('error', '')}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Update Error",
                f"An error occurred while updating the database:\n{str(e)}"
            )
