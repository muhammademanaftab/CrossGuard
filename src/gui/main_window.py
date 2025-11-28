"""
Cross Guard Main Window
Main GUI window with file selection interface for browser compatibility analysis.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QListWidget, QGroupBox,
    QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from pathlib import Path
from typing import List


class MainWindow(QMainWindow):
    """Main application window for Cross Guard."""
    
    def __init__(self):
        super().__init__()
        self.html_files = []
        self.css_files = []
        self.js_files = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Cross Guard - Browser Compatibility Checker")
        self.setMinimumSize(900, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        self._create_header(main_layout)
        
        # File selection section
        self._create_file_section(main_layout)
        
        # Action buttons at bottom
        self._create_action_buttons(main_layout)
        
        # Apply styling
        self._apply_styles()
        
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
        file_list.setMinimumHeight(100)
        file_list.setMaximumHeight(150)
        setattr(self, list_name, file_list)
        h_layout.addWidget(file_list)
        
        # Button layout
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # Add button
        add_btn = QPushButton("➕ Add Files")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(lambda: self._add_files(title.split()[0].lower()))
        button_layout.addWidget(add_btn)
        
        # Remove button
        remove_btn = QPushButton("➖ Remove")
        remove_btn.setObjectName("removeButton")
        remove_btn.clicked.connect(lambda: self._remove_file(file_list))
        button_layout.addWidget(remove_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setObjectName("clearButton")
        clear_btn.clicked.connect(lambda: self._clear_files(file_list))
        button_layout.addWidget(clear_btn)
        
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
        analyze_btn = QPushButton("🔍 Analyze Compatibility")
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
            for file_path in files:
                if file_path not in storage:
                    storage.append(file_path)
                    file_list.addItem(Path(file_path).name)
            
            self._update_status()
                    
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
            # TODO: This will be connected to the analyzer in the next step
            QMessageBox.information(
                self,
                "Analysis Started",
                "Analysis functionality will be implemented in the next step!\n\n"
                f"Files to analyze:\n{summary_text}"
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
                padding-top: 15px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #333;
            }
            
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: #fafafa;
                font-size: 12px;
            }
            
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            
            #addButton {
                background-color: #4CAF50;
                color: white;
            }
            
            #addButton:hover {
                background-color: #45a049;
            }
            
            #removeButton {
                background-color: #ff9800;
                color: white;
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
