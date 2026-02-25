"""File selector with drag-and-drop support."""

from pathlib import Path
from tkinter import filedialog
from typing import List, Callable, Optional

import customtkinter as ctk

from .theme import COLORS
from .widgets.drop_zone import DropZone


class FileSelectorGroup(ctk.CTkFrame):
    """File picker for a specific type (HTML/CSS/JS) with drag-and-drop."""

    FILE_EXTENSIONS = {
        'html': ['html', 'htm'],
        'css': ['css'],
        'javascript': ['js', 'jsx', 'ts', 'tsx', 'mjs']
    }

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
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title_label.pack(anchor="w", padx=12, pady=(10, 8))

        extensions = self.FILE_EXTENSIONS.get(self.file_type, [])
        self.drop_zone = DropZone(
            self,
            allowed_extensions=extensions,
            on_files_dropped=self._handle_dropped_files,
        )
        self.drop_zone.pack(fill="x", padx=12, pady=(0, 8))

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="x", padx=12, pady=(0, 10))

        # Read-only textbox as a simple file list display
        self.file_list = ctk.CTkTextbox(
            content_frame,
            height=80,
            fg_color=COLORS['input_bg'],
            text_color=COLORS['text_primary'],
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            border_width=1,
            border_color=COLORS['border'],
            state="disabled",
        )
        self.file_list.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.file_list.bind("<Button-1>", self._on_list_click)

        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(side="right", fill="y")

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

        self._selected_index = -1

    def _handle_dropped_files(self, file_paths: List[str]):
        added = False
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)
                added = True

        if added:
            self._update_file_list()
            self._notify_change()

    def _add_files(self):
        filetypes = self.FILE_FILTERS.get(self.file_type, [("All Files", "*.*")])
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
        if 0 <= self._selected_index < len(self.files):
            del self.files[self._selected_index]
            self._selected_index = -1
            self._update_file_list()
            self._notify_change()

    def _on_list_click(self, event):
        """Select a line in the file list based on click position."""
        index = self.file_list.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0]) - 1

        if 0 <= line_num < len(self.files):
            self._selected_index = line_num
            self._highlight_selection()

    def _highlight_selection(self):
        self.file_list.configure(state="normal")
        self.file_list.tag_remove("selected", "1.0", "end")

        if 0 <= self._selected_index < len(self.files):
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
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")

        for file_path in self.files:
            filename = Path(file_path).name
            self.file_list.insert("end", filename + "\n")

        if self.files:
            self.file_list.delete("end-1c", "end")

        self.file_list.configure(state="disabled")

    def _notify_change(self):
        if self.on_files_changed:
            self.on_files_changed()

    def clear_files(self):
        self.files.clear()
        self._selected_index = -1
        self._update_file_list()

    def get_files(self) -> List[str]:
        return self.files.copy()

    def set_callback(self, callback: Callable[[], None]):
        self.on_files_changed = callback
