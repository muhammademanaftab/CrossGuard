"""
Cross Guard Main Window
Main GUI window with file selection interface for browser compatibility analysis.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QListWidget, QGroupBox,
    QFileDialog, QMessageBox, QFrame, QProgressDialog,
    QStackedWidget, QScrollArea, QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from pathlib import Path
from typing import List, Dict, Optional
import sys
import os

# Import analyzer
from src.analyzer.main import CrossGuardAnalyzer


class MainWindow(QMainWindow):
    """Main application window for Cross Guard."""
    
    def __init__(self):
        super().__init__()
        self.html_files = []
        self.css_files = []
        self.js_files = []
        self.current_report = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Cross Guard - Browser Compatibility Checker")
        self.setMinimumSize(900, 700)
        
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
        self._apply_styles()
    
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
        export_pdf_btn.clicked.connect(self._export_pdf)
        top_bar.addWidget(export_pdf_btn)
        
        # Export JSON button
        export_json_btn = QPushButton("💾 JSON")
        export_json_btn.setObjectName("exportJsonButton")
        export_json_btn.setMinimumHeight(45)
        export_json_btn.setMinimumWidth(120)
        export_json_btn.clicked.connect(self._export_json)
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
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("🛡️ Cross Guard")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Browser Compatibility Checker")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        parent_layout.addWidget(header_frame)
        
    def _create_file_section(self, parent_layout):
        """Create the file selection section."""
        # HTML Files Section
        self.html_group = self._create_file_group(
            "HTML Files",
            "Add HTML files to analyze",
            "html_list"
        )
        parent_layout.addWidget(self.html_group)
        
        # CSS Files Section
        self.css_group = self._create_file_group(
            "CSS Files",
            "Add CSS files to analyze",
            "css_list"
        )
        parent_layout.addWidget(self.css_group)
        
        # JavaScript Files Section
        self.js_group = self._create_file_group(
            "JavaScript Files",
            "Add JavaScript files to analyze",
            "js_list"
        )
        parent_layout.addWidget(self.js_group)
        
    def _create_file_group(self, title: str, description: str, list_name: str) -> QGroupBox:
        """Create a file selection group box.
        
        Args:
            title: Group box title
            description: Description text
            list_name: Name for the list widget attribute
            
        Returns:
            QGroupBox containing file selection UI
        """
        group_box = QGroupBox(title)
        group_box.setObjectName("fileGroup")
        layout = QVBoxLayout()
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # Horizontal layout for list and buttons
        h_layout = QHBoxLayout()
        
        # File list
        file_list = QListWidget()
        file_list.setObjectName(list_name)
        file_list.setMinimumHeight(120)
        file_list.setMaximumHeight(200)
        setattr(self, list_name, file_list)
        h_layout.addWidget(file_list)
        
        # Button layout
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add button
        add_btn = QPushButton()
        add_btn.setText("Add Files")
        add_btn.setObjectName("addButton")
        add_btn.setMinimumWidth(110)
        add_btn.setMinimumHeight(38)
        add_btn.clicked.connect(lambda: self._add_files(title.split()[0].lower()))
        button_layout.addWidget(add_btn)

        # Remove button
        remove_btn = QPushButton()
        remove_btn.setText("Remove")
        remove_btn.setObjectName("removeButton")
        remove_btn.setMinimumWidth(110)
        remove_btn.setMinimumHeight(38)
        remove_btn.clicked.connect(lambda: self._remove_file(file_list))
        button_layout.addWidget(remove_btn)
        
        # Add bottom spacer to push buttons to top
        button_layout.addStretch()
        
        h_layout.addLayout(button_layout)
        layout.addLayout(h_layout)
        
        group_box.setLayout(layout)
        return group_box
        
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
        analyze_btn = QPushButton()
        analyze_btn.setText("Analyze Compatibility")
        analyze_btn.setObjectName("analyzeButton")
        analyze_btn.setMinimumHeight(45)
        analyze_btn.setMinimumWidth(200)
        analyze_btn.clicked.connect(self._analyze_files)
        button_container.addWidget(analyze_btn)
        
        parent_layout.addLayout(button_container)
        
    def _add_files(self, file_type: str):
        """Open file dialog to add files.
        
        Args:
            file_type: Type of files to add ('html', 'css', or 'javascript')
        """
        # Set file filter based on type
        if file_type == 'html':
            file_filter = "HTML Files (*.html *.htm)"
            file_list = self.html_list
            storage = self.html_files
        elif file_type == 'css':
            file_filter = "CSS Files (*.css)"
            file_list = self.css_list
            storage = self.css_files
        else:  # javascript
            file_filter = "JavaScript Files (*.js)"
            file_list = self.js_list
            storage = self.js_files
        
        # Open file dialog
        files, _ = QFileDialog.getOpenFileNames(
            self,
            f"Select {file_type.upper()} Files",
            "",
            file_filter
        )
        
        # Add selected files
        if files:
            print(f"Selected {len(files)} file(s)")
            for file_path in files:
                print(f"Adding: {file_path}")
                if file_path not in storage:
                    storage.append(file_path)
                    filename = Path(file_path).name
                    file_list.addItem(filename)
                    print(f"Added to list: {filename}")
            
            print(f"Total files in storage: {len(storage)}")
            print(f"Total items in list: {file_list.count()}")
            self._update_status()
        else:
            print("No files selected")
                    
    def _remove_file(self, file_list: QListWidget):
        """Remove selected file from list.
        
        Args:
            file_list: The list widget to remove from
        """
        current_row = file_list.currentRow()
        if current_row >= 0:
            # Remove from display
            file_list.takeItem(current_row)
            
            # Remove from storage
            if file_list == self.html_list:
                self.html_files.pop(current_row)
            elif file_list == self.css_list:
                self.css_files.pop(current_row)
            else:
                self.js_files.pop(current_row)
            
            self._update_status()
                
    def _clear_files(self, file_list: QListWidget):
        """Clear all files from a specific list.
        
        Args:
            file_list: The list widget to clear
        """
        file_list.clear()
        
        # Clear from storage
        if file_list == self.html_list:
            self.html_files.clear()
        elif file_list == self.css_list:
            self.css_files.clear()
        else:
            self.js_files.clear()
        
        self._update_status()
            
    def _clear_all_files(self):
        """Clear all files from all lists."""
        self.html_list.clear()
        self.css_list.clear()
        self.js_list.clear()
        
        self.html_files.clear()
        self.css_files.clear()
        self.js_files.clear()
        
        self._update_status()
        
    def _update_status(self):
        """Update the status display."""
        total_files = len(self.html_files) + len(self.css_files) + len(self.js_files)
        
        # Update window title with file count
        if total_files > 0:
            self.setWindowTitle(f"Cross Guard - {total_files} file(s) selected")
        else:
            self.setWindowTitle("Cross Guard - Browser Compatibility Checker")
            
    def _analyze_files(self):
        """Start the analysis process."""
        # Check if any files are selected
        total_files = len(self.html_files) + len(self.css_files) + len(self.js_files)
        
        if total_files == 0:
            QMessageBox.warning(
                self,
                "No Files Selected",
                "Please add at least one HTML, CSS, or JavaScript file to analyze."
            )
            return
        
        # Show confirmation
        file_summary = []
        if self.html_files:
            file_summary.append(f"{len(self.html_files)} HTML file(s)")
        if self.css_files:
            file_summary.append(f"{len(self.css_files)} CSS file(s)")
        if self.js_files:
            file_summary.append(f"{len(self.js_files)} JavaScript file(s)")
        
        summary_text = ", ".join(file_summary)
        
        reply = QMessageBox.question(
            self,
            "Start Analysis",
            f"Ready to analyze:\n\n{summary_text}\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Run the analysis
            self._run_analysis()
    
    def _run_analysis(self):
        """Run the compatibility analysis."""
        try:
            # Show progress dialog
            progress = QProgressDialog("Analyzing files...", "Cancel", 0, 100, self)
            progress.setWindowTitle("Analysis in Progress")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setValue(10)
            
            # Create analyzer
            analyzer = CrossGuardAnalyzer()
            progress.setValue(20)
            
            # Default target browsers (latest versions)
            target_browsers = {
                'chrome': '144',
                'firefox': '146',
                'safari': '18.4',
                'edge': '144'
            }
            progress.setValue(30)
            
            # Run analysis
            print("Starting analysis...")
            report = analyzer.analyze_project(
                html_files=self.html_files if self.html_files else None,
                css_files=self.css_files if self.css_files else None,
                js_files=self.js_files if self.js_files else None,
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
                    "Analysis Error",
                    f"Analysis failed:\n{report.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"An error occurred during analysis:\n{str(e)}"
            )
            print(f"Analysis error: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_results(self, report: Dict):
        """Show analysis results in the results page.
        
        Args:
            report: Analysis report dictionary
        """
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
    
    def _export_json(self):
        """Export analysis report as JSON file."""
        if not self.current_report:
            QMessageBox.warning(self, "No Report", "No analysis report to export.")
            return
        
        # Ask user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report as JSON",
            "compatibility_report.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w') as f:
                    json.dump(self.current_report, f, indent=2)
                
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Report saved to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to save JSON file:\n{str(e)}"
                )
    
    def _export_pdf(self):
        """Export analysis report as PDF file."""
        if not self.current_report:
            QMessageBox.warning(self, "No Report", "No analysis report to export.")
            return
        
        # Ask user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report as PDF",
            "compatibility_report.pdf",
            "PDF Files (*.pdf)"
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
                summary = self.current_report.get('summary', {})
                scores = self.current_report.get('scores', {})
                
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
                browsers = self.current_report.get('browsers', {})
                
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
                recommendations = self.current_report.get('recommendations', [])
                if recommendations:
                    story.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
                    for i, rec in enumerate(recommendations, 1):
                        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                
                # Build PDF
                doc.build(story)
                
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"PDF report saved to:\n{file_path}"
                )
                
            except ImportError:
                QMessageBox.critical(
                    self,
                    "Missing Library",
                    "ReportLab library is required for PDF export.\n\n"
                    "Install it with: pip install reportlab"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to create PDF:\n{str(e)}"
                )
            
    def _apply_styles(self):
        """Apply custom styles to the window."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            #headerFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 10px;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 18px;
                padding-bottom: 5px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #333;
            }
            
            #browserCard {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
            }
            
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: #fafafa;
                font-size: 13px;
                color: #333;
            }
            
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
                color: #333;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 14px;
                color: #FFFFFF;
                text-align: center;
            }
            
            #addButton {
                background-color: #4CAF50;
                color: white;
                font-size: 12px;
                margin-bottom: 8px;
            }
            
            #addButton:hover {
                background-color: #45a049;
            }
            
            #removeButton {
                background-color: #FF9800;
                color: white;
                font-size: 12px;
                margin-top: 8px;
            }
            
            #removeButton:hover {
                background-color: #e68900;
            }
            
            #clearButton {
                background-color: #f44336;
                color: white;
            }
            
            #clearButton:hover {
                background-color: #da190b;
            }
            
            #clearAllButton {
                background-color: #9e9e9e;
                color: white;
                font-size: 13px;
            }
            
            #clearAllButton:hover {
                background-color: #757575;
            }
            
            #analyzeButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
            }
            
            #analyzeButton:hover {
                background-color: #0b7dda;
            }
            
            #backButton {
                background-color: #f8f9fa;
                color: #333;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ddd;
            }
            
            #backButton:hover {
                background-color: #e9ecef;
            }
            
            #exportPdfButton {
                background-color: #f8f9fa;
                color: #333;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            
            #exportPdfButton:hover {
                background-color: #e9ecef;
            }
            
            #exportJsonButton {
                background-color: #f8f9fa;
                color: #333;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            
            #exportJsonButton:hover {
                background-color: #e9ecef;
            }
            
            #resultsScroll {
                border: none;
                background-color: transparent;
            }
            
            QPushButton:pressed {
                padding-top: 10px;
                padding-bottom: 6px;
            }
        """)
        
    def get_selected_files(self) -> dict:
        """Get all selected files.
        
        Returns:
            Dict with 'html', 'css', and 'js' file lists
        """
        return {
            'html': self.html_files.copy(),
            'css': self.css_files.copy(),
            'js': self.js_files.copy()
        }
