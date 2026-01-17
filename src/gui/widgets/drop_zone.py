"""
DropZone widget for drag-and-drop file selection.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from typing import List
from pathlib import Path


class DropZone(QFrame):
    """A drag-and-drop zone for file selection."""

    files_dropped = pyqtSignal(list)  # Emits list of valid file paths

    def __init__(self, allowed_extensions: List[str], parent=None):
        """
        Initialize the drop zone.

        Args:
            allowed_extensions: List of allowed file extensions (e.g., ['html', 'htm'])
            parent: Parent widget
        """
        super().__init__(parent)
        self.allowed_extensions = [ext.lower().lstrip('.') for ext in allowed_extensions]
        self._is_drag_over = False
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setMinimumHeight(60)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Instruction label
        self.label = QLabel("Drop files here or click Add Files")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            color: #888;
            font-size: 13px;
            font-weight: normal;
        """)
        layout.addWidget(self.label)

        self._update_style()

    def _update_style(self):
        """Update the visual style based on state."""
        if self._is_drag_over:
            self.setStyleSheet("""
                QFrame {
                    border: 2px solid #2196F3;
                    border-radius: 8px;
                    background-color: #e3f2fd;
                }
            """)
            self.label.setStyleSheet("""
                color: #1976D2;
                font-size: 13px;
                font-weight: bold;
            """)
            self.label.setText("Release to add files")
        else:
            self.setStyleSheet("""
                QFrame {
                    border: 2px dashed #ccc;
                    border-radius: 8px;
                    background-color: #fafafa;
                }
                QFrame:hover {
                    border-color: #2196F3;
                    background-color: #f5f5f5;
                }
            """)
            self.label.setStyleSheet("""
                color: #888;
                font-size: 13px;
                font-weight: normal;
            """)
            self.label.setText("Drop files here or click Add Files")

    def _is_valid_file(self, file_path: str) -> bool:
        """Check if a file has a valid extension."""
        ext = Path(file_path).suffix.lower().lstrip('.')
        return ext in self.allowed_extensions

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any file is valid
            for url in event.mimeData().urls():
                if url.isLocalFile() and self._is_valid_file(url.toLocalFile()):
                    event.acceptProposedAction()
                    self._is_drag_over = True
                    self._update_style()
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self._is_drag_over = False
        self._update_style()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        self._is_drag_over = False
        self._update_style()

        valid_files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if self._is_valid_file(file_path):
                    valid_files.append(file_path)

        if valid_files:
            event.acceptProposedAction()
            self.files_dropped.emit(valid_files)
        else:
            event.ignore()

    def set_extensions(self, extensions: List[str]):
        """Update the allowed file extensions."""
        self.allowed_extensions = [ext.lower().lstrip('.') for ext in extensions]
