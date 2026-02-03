"""
Enhanced DropZone widget for drag-and-drop file selection.

Professional design with animated border and better visual feedback.
"""

import re
from pathlib import Path
from typing import List, Callable, Optional

import customtkinter as ctk
from tkinterdnd2 import DND_FILES

from ..theme import COLORS, SPACING, ICONS


class DropZone(ctk.CTkFrame):
    """Enhanced drag-and-drop zone for file selection.

    Features:
    - Large, prominent drop area
    - Animated border on drag
    - Better visual feedback
    - Support for multiple file types
    """

    def __init__(
        self,
        master,
        allowed_extensions: Optional[List[str]] = None,
        on_files_dropped: Optional[Callable[[List[str]], None]] = None,
        height: int = 160,
        show_instructions: bool = True,
        **kwargs
    ):
        """Initialize the drop zone.

        Args:
            master: Parent widget
            allowed_extensions: List of allowed file extensions (e.g., ['html', 'css', 'js'])
                               If None, all extensions are allowed
            on_files_dropped: Callback function called with list of valid file paths
            height: Height of the drop zone
            show_instructions: Whether to show instruction text
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            master,
            fg_color=COLORS['drop_zone_normal'],
            corner_radius=8,
            border_width=2,
            border_color=COLORS['drop_zone_border'],
            **kwargs
        )

        if allowed_extensions:
            self.allowed_extensions = [ext.lower().lstrip('.') for ext in allowed_extensions]
        else:
            self.allowed_extensions = ['html', 'htm', 'css', 'js', 'jsx', 'ts', 'tsx', 'mjs']  # Default extensions

        self.on_files_dropped = on_files_dropped
        self._is_drag_over = False
        self._is_hovering = False
        self._height = height
        self._show_instructions = show_instructions

        self._init_ui()
        self._setup_dnd()
        self._setup_hover()

    def _init_ui(self):
        """Initialize the user interface."""
        self.configure(height=self._height)

        # Main container
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Icon
        icon_label = ctk.CTkLabel(
            content,
            text=ICONS['upload'],
            font=ctk.CTkFont(size=32),
            text_color=COLORS['text_muted'],
        )
        icon_label.pack(pady=(0, SPACING['md']))

        # Primary text
        self.primary_label = ctk.CTkLabel(
            content,
            text="Drop files here or click to browse",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_secondary'],
        )
        self.primary_label.pack()

        if self._show_instructions:
            # Secondary text with supported formats
            extensions_text = ", ".join(f".{ext}" for ext in self.allowed_extensions[:4])
            if len(self.allowed_extensions) > 4:
                extensions_text += "..."

            self.secondary_label = ctk.CTkLabel(
                content,
                text=f"Supported formats: {extensions_text}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted'],
            )
            self.secondary_label.pack(pady=(SPACING['xs'], 0))

        # Make entire area clickable
        self.bind("<Button-1>", self._on_click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._on_click)
            for subchild in child.winfo_children():
                subchild.bind("<Button-1>", self._on_click)

        # Store references for hover binding
        self._icon_label = icon_label
        self._content_frame = content

    def _setup_dnd(self):
        """Set up drag-and-drop event handlers."""
        # Register as a drop target for files
        self.drop_target_register(DND_FILES)

        # Bind ALL required events
        self.dnd_bind('<<DropEnter>>', self._on_drag_enter)
        self.dnd_bind('<<DropPosition>>', self._on_drag_over)
        self.dnd_bind('<<DropLeave>>', self._on_drag_leave)
        self.dnd_bind('<<Drop>>', self._on_drop)

    def _setup_hover(self):
        """Set up hover effects for better clickability indication."""
        # Bind hover events to main frame and all children
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)

        # Also bind to all children so hover works everywhere
        for child in self.winfo_children():
            child.bind("<Enter>", self._on_hover_enter)
            child.bind("<Leave>", self._on_hover_leave)
            for subchild in child.winfo_children():
                subchild.bind("<Enter>", self._on_hover_enter)
                subchild.bind("<Leave>", self._on_hover_leave)

    def _on_hover_enter(self, event):
        """Handle mouse entering the drop zone."""
        if self._is_drag_over:
            return  # Don't override drag state

        self._is_hovering = True
        # Change cursor to hand pointer
        self.configure(cursor="hand2")
        # Subtle background change
        self.configure(
            fg_color=COLORS['drop_zone_hover'],
            border_color=COLORS['accent'],
        )
        # Brighten text
        self.primary_label.configure(text_color=COLORS['text_primary'])
        if hasattr(self, '_icon_label'):
            self._icon_label.configure(text_color=COLORS['accent'])

    def _on_hover_leave(self, event):
        """Handle mouse leaving the drop zone."""
        if self._is_drag_over:
            return  # Don't override drag state

        # Check if we're still inside (moved to child widget)
        x, y = self.winfo_pointerxy()
        widget_x = self.winfo_rootx()
        widget_y = self.winfo_rooty()
        widget_w = self.winfo_width()
        widget_h = self.winfo_height()

        if widget_x <= x <= widget_x + widget_w and widget_y <= y <= widget_y + widget_h:
            return  # Still inside, don't reset

        self._is_hovering = False
        # Reset cursor
        self.configure(cursor="")
        # Reset to normal state
        self.configure(
            fg_color=COLORS['drop_zone_normal'],
            border_color=COLORS['drop_zone_border'],
        )
        self.primary_label.configure(text_color=COLORS['text_secondary'])
        if hasattr(self, '_icon_label'):
            self._icon_label.configure(text_color=COLORS['text_muted'])

    def _on_drag_enter(self, event):
        """Handle drag enter event - show visual feedback."""
        files = self._parse_dropped_data(event.data)
        has_valid = any(self._is_valid_file(f) for f in files)

        if has_valid:
            self._is_drag_over = True
            self._update_style()
            return event.action

        return None

    def _on_drag_over(self, event):
        """Handle drag over/position event."""
        if self._is_drag_over:
            return event.action

        files = self._parse_dropped_data(event.data)
        has_valid = any(self._is_valid_file(f) for f in files)

        if has_valid:
            self._is_drag_over = True
            self._update_style()
            return event.action

        return None

    def _on_drag_leave(self, event):
        """Handle drag leave event - reset visual state."""
        self._is_drag_over = False
        self._update_style()

    def _on_drop(self, event):
        """Handle drop event - process dropped files."""
        self._is_drag_over = False
        self._update_style()

        all_files = self._parse_dropped_data(event.data)
        valid_files = [f for f in all_files if self._is_valid_file(f)]

        if valid_files and self.on_files_dropped:
            self.on_files_dropped(valid_files)
            return event.action

        return None

    def _on_click(self, event):
        """Handle click - open file dialog."""
        from tkinter import filedialog

        # Build file type filter
        file_types = []
        if 'html' in self.allowed_extensions or 'htm' in self.allowed_extensions:
            file_types.append(("HTML Files", "*.html *.htm"))
        if 'css' in self.allowed_extensions:
            file_types.append(("CSS Files", "*.css"))
        if 'js' in self.allowed_extensions:
            file_types.append(("JavaScript Files", "*.js"))
        file_types.append(("All Files", "*.*"))

        files = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=file_types,
        )

        if files:
            valid_files = [f for f in files if self._is_valid_file(f)]
            if valid_files and self.on_files_dropped:
                self.on_files_dropped(valid_files)

    def _parse_dropped_data(self, data: str) -> List[str]:
        """Parse the dropped data string into file paths."""
        if not data:
            return []

        files = []
        pattern = r'\{([^}]+)\}|(\S+)'
        matches = re.findall(pattern, data)

        for match in matches:
            path = match[0] if match[0] else match[1]
            if path:
                path = path.strip('"\'')
                if path and Path(path).exists():
                    files.append(path)

        return files

    def _is_valid_file(self, file_path: str) -> bool:
        """Check if a file has a valid extension."""
        ext = Path(file_path).suffix.lower().lstrip('.')
        return ext in self.allowed_extensions

    def _update_style(self):
        """Update the visual style based on drag state."""
        if self._is_drag_over:
            # Active drag state (highest priority)
            self.configure(
                fg_color=COLORS['drop_zone_active'],
                border_color=COLORS['drop_zone_border_active'],
                cursor="hand2",
            )
            self.primary_label.configure(
                text="Release to add files",
                text_color=COLORS['accent_bright'],
            )
            if hasattr(self, '_icon_label'):
                self._icon_label.configure(text_color=COLORS['accent_bright'])
        elif self._is_hovering:
            # Hover state
            self.configure(
                fg_color=COLORS['drop_zone_hover'],
                border_color=COLORS['accent'],
                cursor="hand2",
            )
            self.primary_label.configure(
                text="Drop files here or click to browse",
                text_color=COLORS['text_primary'],
            )
            if hasattr(self, '_icon_label'):
                self._icon_label.configure(text_color=COLORS['accent'])
        else:
            # Normal state
            self.configure(
                fg_color=COLORS['drop_zone_normal'],
                border_color=COLORS['drop_zone_border'],
                cursor="",
            )
            self.primary_label.configure(
                text="Drop files here or click to browse",
                text_color=COLORS['text_secondary'],
            )
            if hasattr(self, '_icon_label'):
                self._icon_label.configure(text_color=COLORS['text_muted'])

    def set_extensions(self, extensions: List[str]):
        """Update the allowed file extensions."""
        self.allowed_extensions = [ext.lower().lstrip('.') for ext in extensions]

    def set_callback(self, callback: Callable[[List[str]], None]):
        """Set the callback for when files are dropped."""
        self.on_files_dropped = callback
