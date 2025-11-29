"""
File Selector Widget for Cross Guard
Handles file selection UI components.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QFileDialog
)
from PyQt6.QtCore import pyqtSignal
from pathlib import Path
from typing import List, Callable


class FileSelectorGroup(QGroupBox):
    """Group box for selecting files of a specific type."""
    
    # Signal emitted when files change
    files_changed = pyqtSignal()
    
    def __init__(self, title: str, description: str, file_type: str, parent=None):
        """Initialize file selector group.
        
        Args:
            title: Group box title
            description: Description text
            file_type: Type of files ('html', 'css', or 'javascript')
            parent: Parent widget
        """
        super().__init__(title, parent)
        self.file_type = file_type
        self.files: List[str] = []
        
        self.setObjectName("fileGroup")
        self._init_ui(description)
    
    def _init_ui(self, description: str):
        """Initialize the user interface.
        
        Args:
            description: Description text to display
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(8)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px;")
        layout.addWidget(desc_label)
        
        # Horizontal layout for list and buttons
        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setObjectName(f"{self.file_type}_list")
        self.file_list.setMinimumHeight(80)
        self.file_list.setMaximumHeight(80)
        h_layout.addWidget(self.file_list)
        
        # Button layout
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add button
        add_btn = QPushButton("Add Files")
        add_btn.setObjectName("addButton")
        add_btn.setMinimumWidth(110)
        add_btn.setMinimumHeight(38)
        add_btn.clicked.connect(self._add_files)
        button_layout.addWidget(add_btn)

        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("removeButton")
        remove_btn.setMinimumWidth(110)
        remove_btn.setMinimumHeight(38)
        remove_btn.clicked.connect(self._remove_file)
        button_layout.addWidget(remove_btn)
        
        # Add bottom spacer
        button_layout.addStretch()
        
        h_layout.addLayout(button_layout)
        layout.addLayout(h_layout)
        
        self.setLayout(layout)
    
    def _add_files(self):
        """Open file dialog to add files."""
        # Set file filter based on type
        if self.file_type == 'html':
            file_filter = "HTML Files (*.html *.htm)"
        elif self.file_type == 'css':
            file_filter = "CSS Files (*.css)"
        else:  # javascript
            file_filter = "JavaScript Files (*.js)"
        
        # Open file dialog
        files, _ = QFileDialog.getOpenFileNames(
            self,
            f"Select {self.file_type.upper()} Files",
            "",
            file_filter
        )
        
        if files:
            for file_path in files:
                if file_path not in self.files:
                    self.files.append(file_path)
                    filename = Path(file_path).name
                    self.file_list.addItem(filename)
            # Emit signal that files changed
            self.files_changed.emit()
    
    def _remove_file(self):
        """Remove selected file from the list."""
        current_item = self.file_list.currentItem()
        if current_item:
            # Get the filename
            filename = current_item.text()
            
            # Find and remove from files list
            for file_path in self.files[:]:
                if Path(file_path).name == filename:
                    self.files.remove(file_path)
                    break
            
            # Remove from list widget
            self.file_list.takeItem(self.file_list.currentRow())
            
            # Emit signal that files changed
            self.files_changed.emit()
    
    def clear_files(self):
        """Clear all files from the list."""
        self.files.clear()
        self.file_list.clear()
    
    def get_files(self) -> List[str]:
        """Get list of selected files.
        
        Returns:
            List of file paths
        """
        return self.files.copy()
