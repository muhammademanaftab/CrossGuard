"""
File table widget for Cross Guard - Table-based file list with sorting.
"""

import os
from pathlib import Path
from typing import List, Callable, Optional, Tuple, Dict
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS, get_file_type_color


class FileTableRow(ctk.CTkFrame):
    """Individual row in the file table."""

    def __init__(
        self,
        master,
        file_path: str,
        index: int,
        selected: bool = False,
        on_select: Optional[Callable] = None,
        on_remove: Optional[Callable] = None,
        **kwargs
    ):
        """Initialize file table row.

        Args:
            master: Parent widget
            file_path: Full path to the file
            index: Row index
            selected: Whether row is selected
            on_select: Callback when row is clicked
            on_remove: Callback when remove button is clicked
        """
        bg_color = COLORS['table_row_odd'] if index % 2 else COLORS['table_row_even']
        super().__init__(
            master,
            height=40,
            fg_color=bg_color,
            corner_radius=0,
            **kwargs
        )

        self.file_path = file_path
        self.index = index
        self._selected = selected
        self._bg_color = bg_color
        self.on_select = on_select
        self.on_remove = on_remove

        # Parse file info
        path_obj = Path(file_path)
        self.filename = path_obj.name
        self.extension = path_obj.suffix.lower().lstrip('.')
        self.size = self._format_size(path_obj.stat().st_size if path_obj.exists() else 0)
        self.directory = str(path_obj.parent)

        # Prevent resize
        self.pack_propagate(False)

        self._init_ui()
        self._update_selection_style()

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _init_ui(self):
        """Initialize the user interface."""
        # Container with grid layout
        self.grid_columnconfigure(0, weight=0, minsize=40)   # Checkbox
        self.grid_columnconfigure(1, weight=3, minsize=200)  # Filename
        self.grid_columnconfigure(2, weight=0, minsize=70)   # Type
        self.grid_columnconfigure(3, weight=0, minsize=80)   # Size
        self.grid_columnconfigure(4, weight=2, minsize=150)  # Path
        self.grid_columnconfigure(5, weight=0, minsize=40)   # Remove

        # Checkbox (simulated with label)
        self.checkbox = ctk.CTkLabel(
            self,
            text=ICONS['check'] if self._selected else "",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['accent'],
            width=40,
        )
        self.checkbox.grid(row=0, column=0, sticky="w", padx=(SPACING['sm'], 0))

        # File type icon + name
        name_frame = ctk.CTkFrame(self, fg_color="transparent")
        name_frame.grid(row=0, column=1, sticky="ew", padx=SPACING['xs'])

        type_color = get_file_type_color(self.extension)
        type_badge = ctk.CTkLabel(
            name_frame,
            text=self.extension.upper() if self.extension else "?",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS['bg_darkest'],
            fg_color=type_color,
            corner_radius=3,
            width=32,
            height=18,
        )
        type_badge.pack(side="left", padx=(0, SPACING['sm']))

        name_label = ctk.CTkLabel(
            name_frame,
            text=self.filename,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
            anchor="w",
        )
        name_label.pack(side="left", fill="x", expand=True)

        # Type column
        type_label = ctk.CTkLabel(
            self,
            text=self._get_type_name(),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
            anchor="w",
        )
        type_label.grid(row=0, column=2, sticky="w", padx=SPACING['xs'])

        # Size column
        size_label = ctk.CTkLabel(
            self,
            text=self.size,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
            anchor="w",
        )
        size_label.grid(row=0, column=3, sticky="w", padx=SPACING['xs'])

        # Path column (truncated)
        short_path = self._truncate_path(self.directory, 25)
        path_label = ctk.CTkLabel(
            self,
            text=short_path,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_disabled'],
            anchor="w",
        )
        path_label.grid(row=0, column=4, sticky="w", padx=SPACING['xs'])

        # Remove button
        remove_btn = ctk.CTkButton(
            self,
            text=ICONS['close'],
            font=ctk.CTkFont(size=12),
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=COLORS['danger_muted'],
            text_color=COLORS['text_muted'],
            command=self._on_remove_click,
        )
        remove_btn.grid(row=0, column=5, sticky="e", padx=(0, SPACING['sm']))

        # Bind click events
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Bind children too
        for child in self.winfo_children():
            if not isinstance(child, ctk.CTkButton):
                child.bind("<Button-1>", self._on_click)

    def _get_type_name(self) -> str:
        """Get human-readable file type name."""
        type_names = {
            'html': 'HTML',
            'htm': 'HTML',
            'css': 'CSS',
            'js': 'JavaScript',
        }
        return type_names.get(self.extension, self.extension.upper())

    def _truncate_path(self, path: str, max_length: int) -> str:
        """Truncate path to max length."""
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length - 3):]

    def _on_click(self, event):
        """Handle row click."""
        self._selected = not self._selected
        self._update_selection_style()
        if self.on_select:
            self.on_select(self.file_path, self._selected)

    def _on_remove_click(self):
        """Handle remove button click."""
        if self.on_remove:
            self.on_remove(self.file_path)

    def _on_enter(self, event):
        """Handle mouse enter."""
        if not self._selected:
            self.configure(fg_color=COLORS['table_row_hover'])

    def _on_leave(self, event):
        """Handle mouse leave."""
        self._update_selection_style()

    def _update_selection_style(self):
        """Update visual style based on selection state."""
        if self._selected:
            self.configure(fg_color=COLORS['table_row_selected'])
            self.checkbox.configure(text=ICONS['check'])
        else:
            self.configure(fg_color=self._bg_color)
            self.checkbox.configure(text="")

    def set_selected(self, selected: bool):
        """Set selection state."""
        self._selected = selected
        self._update_selection_style()

    def is_selected(self) -> bool:
        """Get selection state."""
        return self._selected


class FileTableHeader(ctk.CTkFrame):
    """Header row for the file table with sortable columns."""

    def __init__(
        self,
        master,
        on_sort: Optional[Callable[[str, bool], None]] = None,
        on_select_all: Optional[Callable[[bool], None]] = None,
        **kwargs
    ):
        """Initialize file table header.

        Args:
            master: Parent widget
            on_sort: Callback when column header is clicked (column_name, ascending)
            on_select_all: Callback when select all checkbox is clicked
        """
        super().__init__(
            master,
            height=36,
            fg_color=COLORS['table_header_bg'],
            corner_radius=0,
            **kwargs
        )

        self.on_sort = on_sort
        self.on_select_all = on_select_all
        self._sort_column = "name"
        self._sort_ascending = True
        self._all_selected = False

        # Prevent resize
        self.pack_propagate(False)

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=0, minsize=40)   # Checkbox
        self.grid_columnconfigure(1, weight=3, minsize=200)  # Filename
        self.grid_columnconfigure(2, weight=0, minsize=70)   # Type
        self.grid_columnconfigure(3, weight=0, minsize=80)   # Size
        self.grid_columnconfigure(4, weight=2, minsize=150)  # Path
        self.grid_columnconfigure(5, weight=0, minsize=40)   # Remove

        # Select all checkbox
        self.select_all_btn = ctk.CTkButton(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            width=24,
            height=24,
            fg_color=COLORS['border'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['accent'],
            corner_radius=4,
            command=self._toggle_select_all,
        )
        self.select_all_btn.grid(row=0, column=0, sticky="w", padx=(SPACING['sm'], 0))

        # Column headers
        columns = [
            ("name", "NAME", 1),
            ("type", "TYPE", 2),
            ("size", "SIZE", 3),
            ("path", "PATH", 4),
        ]

        for col_id, col_text, col_num in columns:
            header_btn = ctk.CTkButton(
                self,
                text=f"{col_text} {self._get_sort_indicator(col_id)}",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="transparent",
                hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_muted'],
                anchor="w",
                command=lambda c=col_id: self._on_column_click(c),
            )
            header_btn.grid(row=0, column=col_num, sticky="w", padx=SPACING['xs'])

    def _get_sort_indicator(self, column: str) -> str:
        """Get sort direction indicator for column."""
        if column == self._sort_column:
            return ICONS['arrow_up'] if self._sort_ascending else ICONS['arrow_down']
        return ""

    def _on_column_click(self, column: str):
        """Handle column header click."""
        if column == self._sort_column:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = column
            self._sort_ascending = True

        if self.on_sort:
            self.on_sort(column, self._sort_ascending)

        # Update UI
        self._init_ui()

    def _toggle_select_all(self):
        """Toggle select all state."""
        self._all_selected = not self._all_selected
        self.select_all_btn.configure(
            text=ICONS['check'] if self._all_selected else ""
        )
        if self.on_select_all:
            self.on_select_all(self._all_selected)

    def set_all_selected(self, selected: bool):
        """Set the select all checkbox state."""
        self._all_selected = selected
        self.select_all_btn.configure(
            text=ICONS['check'] if self._all_selected else ""
        )


class FileTable(ctk.CTkFrame):
    """Table widget for displaying and managing files."""

    def __init__(
        self,
        master,
        on_files_changed: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """Initialize file table.

        Args:
            master: Parent widget
            on_files_changed: Callback when files are added/removed
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_darkest'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._files: List[str] = []
        self._selected_files: set = set()
        self._rows: Dict[str, FileTableRow] = {}
        self.on_files_changed = on_files_changed

        self._sort_column = "name"
        self._sort_ascending = True

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Header
        self.header = FileTableHeader(
            self,
            on_sort=self._on_sort,
            on_select_all=self._on_select_all,
        )
        self.header.pack(fill="x")

        # Separator
        separator = ctk.CTkFrame(self, height=1, fg_color=COLORS['border'])
        separator.pack(fill="x")

        # Scrollable rows container
        self.rows_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        self.rows_container.pack(fill="both", expand=True)

        # Empty state label
        self.empty_label = ctk.CTkLabel(
            self.rows_container,
            text="No files added yet",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_muted'],
        )

    def _on_sort(self, column: str, ascending: bool):
        """Handle sort column change."""
        self._sort_column = column
        self._sort_ascending = ascending
        self._rebuild_rows()

    def _on_select_all(self, selected: bool):
        """Handle select all toggle."""
        if selected:
            self._selected_files = set(self._files)
        else:
            self._selected_files.clear()

        for row in self._rows.values():
            row.set_selected(selected)

    def _on_row_select(self, file_path: str, selected: bool):
        """Handle row selection change."""
        if selected:
            self._selected_files.add(file_path)
        else:
            self._selected_files.discard(file_path)

        # Update header checkbox
        all_selected = len(self._selected_files) == len(self._files) and len(self._files) > 0
        self.header.set_all_selected(all_selected)

    def _on_row_remove(self, file_path: str):
        """Handle row remove button click."""
        self.remove_file(file_path)

    def _sort_files(self) -> List[str]:
        """Sort files according to current sort settings."""
        def get_sort_key(file_path: str):
            path_obj = Path(file_path)
            if self._sort_column == "name":
                return path_obj.name.lower()
            elif self._sort_column == "type":
                return path_obj.suffix.lower()
            elif self._sort_column == "size":
                return path_obj.stat().st_size if path_obj.exists() else 0
            elif self._sort_column == "path":
                return str(path_obj.parent).lower()
            return path_obj.name.lower()

        sorted_files = sorted(self._files, key=get_sort_key, reverse=not self._sort_ascending)
        return sorted_files

    def _rebuild_rows(self):
        """Rebuild all table rows."""
        # Clear existing rows
        for widget in self.rows_container.winfo_children():
            widget.destroy()
        self._rows.clear()

        if not self._files:
            self.empty_label = ctk.CTkLabel(
                self.rows_container,
                text="No files added yet",
                font=ctk.CTkFont(size=13),
                text_color=COLORS['text_muted'],
            )
            self.empty_label.pack(pady=SPACING['xl'])
            return

        # Create sorted rows
        sorted_files = self._sort_files()
        for i, file_path in enumerate(sorted_files):
            row = FileTableRow(
                self.rows_container,
                file_path=file_path,
                index=i,
                selected=file_path in self._selected_files,
                on_select=self._on_row_select,
                on_remove=self._on_row_remove,
            )
            row.pack(fill="x")
            self._rows[file_path] = row

    def add_files(self, file_paths: List[str]):
        """Add files to the table.

        Args:
            file_paths: List of file paths to add
        """
        added = False
        for file_path in file_paths:
            if file_path not in self._files:
                self._files.append(file_path)
                added = True

        if added:
            self._rebuild_rows()
            if self.on_files_changed:
                self.on_files_changed()

    def remove_file(self, file_path: str):
        """Remove a file from the table.

        Args:
            file_path: File path to remove
        """
        if file_path in self._files:
            self._files.remove(file_path)
            self._selected_files.discard(file_path)
            self._rebuild_rows()
            if self.on_files_changed:
                self.on_files_changed()

    def remove_selected(self):
        """Remove all selected files."""
        for file_path in list(self._selected_files):
            self._files.remove(file_path)
        self._selected_files.clear()
        self._rebuild_rows()
        if self.on_files_changed:
            self.on_files_changed()

    def clear_files(self):
        """Remove all files."""
        self._files.clear()
        self._selected_files.clear()
        self._rebuild_rows()
        if self.on_files_changed:
            self.on_files_changed()

    def get_files(self) -> List[str]:
        """Get all file paths."""
        return self._files.copy()

    def get_selected_files(self) -> List[str]:
        """Get selected file paths."""
        return list(self._selected_files)

    def get_file_count(self) -> int:
        """Get total number of files."""
        return len(self._files)

    def get_files_by_type(self, file_type: str) -> List[str]:
        """Get files of a specific type.

        Args:
            file_type: Extension to filter by ('html', 'css', 'js')

        Returns:
            List of matching file paths
        """
        extensions = {
            'html': ['html', 'htm'],
            'css': ['css'],
            'javascript': ['js'],
            'js': ['js'],
        }
        allowed = extensions.get(file_type.lower(), [file_type.lower()])
        return [f for f in self._files if Path(f).suffix.lower().lstrip('.') in allowed]
