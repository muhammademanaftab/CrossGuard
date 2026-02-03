"""
File Selector Widget for Cross Guard
Handles file selection UI components with drag-and-drop support using CustomTkinter.
"""

from pathlib import Path
from tkinter import filedialog
from typing import List, Callable, Optional

import customtkinter as ctk

from .theme import COLORS
from .widgets.drop_zone import DropZone


class FileSelectorGroup(ctk.CTkFrame):
    """Frame for selecting files of a specific type with drag-and-drop."""

    # File extensions for each type
    FILE_EXTENSIONS = {
        'html': ['html', 'htm'],
        'css': ['css'],
        'javascript': ['js', 'jsx', 'ts', 'tsx', 'mjs']
    }

    # File dialog filters
    FILE_FILTERS = {
        'html': [("HTML Files", "*.html *.htm")],
        'css': [("CSS Files", "*.css")],
        'javascript': [("JavaScript/TypeScript Files", "*.js *.jsx *.ts *.tsx *.mjs")],
    }

    def __init__(
        self,
        master,
        title: str,
        description: str,
        file_type: str,
        on_files_changed: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """Initialize file selector group.

        Args:
            master: Parent widget
            title: Group title
            description: Description text (unused but kept for API compatibility)
            file_type: Type of files ('html', 'css', or 'javascript')
            on_files_changed: Callback when files change
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            **kwargs
        )

        self.file_type = file_type
        self.files: List[str] = []
        self.on_files_changed = on_files_changed

        self._init_ui(title)

    def _init_ui(self, title: str):
        """Initialize the user interface."""
        # Title label
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title_label.pack(anchor="w", padx=12, pady=(10, 8))

        # Drop zone for drag-and-drop
        extensions = self.FILE_EXTENSIONS.get(self.file_type, [])
        self.drop_zone = DropZone(
            self,
            allowed_extensions=extensions,
            on_files_dropped=self._handle_dropped_files,
        )
        self.drop_zone.pack(fill="x", padx=12, pady=(0, 8))

        # Horizontal layout for list and buttons
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="x", padx=12, pady=(0, 10))

        # File list (CTkTextbox in read-only mode)
        self.file_list = ctk.CTkTextbox(
            content_frame,
            height=80,
            fg_color=COLORS['input_bg'],
            text_color=COLORS['text_primary'],
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            border_width=1,
            border_color=COLORS['border'],
            state="disabled",  # Read-only
        )
        self.file_list.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Bind selection handling
        self.file_list.bind("<Button-1>", self._on_list_click)

        # Button container
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(side="right", fill="y")

        # Add button
        add_btn = ctk.CTkButton(
            button_frame,
            text="Add Files",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110,
            height=38,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_dark'],
            text_color=COLORS['text_primary'],
            command=self._add_files,
        )
        add_btn.pack(pady=(0, 8))

        # Remove button
        remove_btn = ctk.CTkButton(
            button_frame,
            text="Remove",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110,
            height=38,
            fg_color=COLORS['warning'],
            hover_color=COLORS['warning_dark'],
            text_color=COLORS['text_primary'],
            command=self._remove_file,
        )
        remove_btn.pack()

        # Track selected line for removal
        self._selected_index = -1

    def _handle_dropped_files(self, file_paths: List[str]):
        """Handle files dropped onto the drop zone.

        Args:
            file_paths: List of dropped file paths
        """
        added = False
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)
                added = True

        if added:
            self._update_file_list()
            self._notify_change()

    def _add_files(self):
        """Open file dialog to add files."""
        # Get file filter for this type
        filetypes = self.FILE_FILTERS.get(self.file_type, [("All Files", "*.*")])

        # Open file dialog
        files = filedialog.askopenfilenames(
            title=f"Select {self.file_type.upper()} Files",
            filetypes=filetypes,
        )

        if files:
            added = False
            for file_path in files:
                if file_path not in self.files:
                    self.files.append(file_path)
                    added = True

            if added:
                self._update_file_list()
                self._notify_change()

    def _remove_file(self):
        """Remove selected file from the list."""
        if 0 <= self._selected_index < len(self.files):
            del self.files[self._selected_index]
            self._selected_index = -1
            self._update_file_list()
            self._notify_change()

    def _on_list_click(self, event):
        """Handle click in the file list to select a line.

        Args:
            event: Click event
        """
        # Get the line number from click position
        index = self.file_list.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0]) - 1  # Convert to 0-based index

        if 0 <= line_num < len(self.files):
            self._selected_index = line_num
            self._highlight_selection()

    def _highlight_selection(self):
        """Highlight the selected line in the textbox."""
        self.file_list.configure(state="normal")

        # Remove previous highlight
        self.file_list.tag_remove("selected", "1.0", "end")

        if 0 <= self._selected_index < len(self.files):
            # Add highlight to selected line
            line_start = f"{self._selected_index + 1}.0"
            line_end = f"{self._selected_index + 1}.end"
            self.file_list.tag_add("selected", line_start, line_end)
            self.file_list.tag_configure(
                "selected",
                background=COLORS['selected_bg'],
                foreground=COLORS['text_primary']
            )

        self.file_list.configure(state="disabled")

    def _update_file_list(self):
        """Update the file list display."""
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")

        for file_path in self.files:
            filename = Path(file_path).name
            self.file_list.insert("end", filename + "\n")

        # Remove trailing newline
        if self.files:
            self.file_list.delete("end-1c", "end")

        self.file_list.configure(state="disabled")

    def _notify_change(self):
        """Notify that files have changed."""
        if self.on_files_changed:
            self.on_files_changed()

    def clear_files(self):
        """Clear all files from the list."""
        self.files.clear()
        self._selected_index = -1
        self._update_file_list()

    def get_files(self) -> List[str]:
        """Get list of selected files.

        Returns:
            List of file paths
        """
        return self.files.copy()

    def set_callback(self, callback: Callable[[], None]):
        """Set the files changed callback.

        Args:
            callback: Function to call when files change
        """
        self.on_files_changed = callback
