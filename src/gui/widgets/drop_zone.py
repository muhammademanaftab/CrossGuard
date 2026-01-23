"""
DropZone widget for drag-and-drop file selection using tkinterdnd2.

This implementation fixes the drag-drop bug from PyQt6 by implementing
ALL required DnD events, including the critical <<DropPosition>> handler
that was missing in the previous version.
"""

import re
from pathlib import Path
from typing import List, Callable, Optional

import customtkinter as ctk
from tkinterdnd2 import DND_FILES

from ..theme import COLORS


class DropZone(ctk.CTkFrame):
    """A drag-and-drop zone for file selection with tkinterdnd2.

    This widget provides a visual drop target for files with proper
    drag-and-drop event handling. It fixes the PyQt6 drag-drop bug
    by implementing the <<DropPosition>> event handler.
    """

    def __init__(
        self,
        master,
        allowed_extensions: List[str],
        on_files_dropped: Optional[Callable[[List[str]], None]] = None,
        **kwargs
    ):
        """Initialize the drop zone.

        Args:
            master: Parent widget
            allowed_extensions: List of allowed file extensions (e.g., ['html', 'htm'])
            on_files_dropped: Callback function called with list of valid file paths
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Remove custom kwargs before passing to parent
        super().__init__(
            master,
            fg_color=COLORS['drop_zone_normal'],
            corner_radius=8,
            **kwargs
        )

        self.allowed_extensions = [ext.lower().lstrip('.') for ext in allowed_extensions]
        self.on_files_dropped = on_files_dropped
        self._is_drag_over = False

        self._init_ui()
        self._setup_dnd()

    def _init_ui(self):
        """Initialize the user interface."""
        self.configure(height=60)

        # Instruction label
        self.label = ctk.CTkLabel(
            self,
            text="Drop files here or click Add Files",
            text_color=COLORS['text_muted'],
            font=ctk.CTkFont(size=13),
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        # Create dashed border effect using a canvas overlay
        self._update_style()

    def _setup_dnd(self):
        """Set up drag-and-drop event handlers.

        CRITICAL: This implementation includes ALL required DnD events:
        - <<DropEnter>>: Visual feedback when drag enters
        - <<DropPosition>>: CRITICAL - Accept during drag (was MISSING in PyQt6!)
        - <<DropLeave>>: Reset visual state when drag leaves
        - <<Drop>>: Process dropped files
        """
        # Register as a drop target for files
        self.drop_target_register(DND_FILES)

        # Bind ALL required events
        self.dnd_bind('<<DropEnter>>', self._on_drag_enter)
        self.dnd_bind('<<DropPosition>>', self._on_drag_over)  # FIX: This was missing!
        self.dnd_bind('<<DropLeave>>', self._on_drag_leave)
        self.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drag_enter(self, event):
        """Handle drag enter event - show visual feedback.

        Args:
            event: TkinterDnD event

        Returns:
            event.action to accept the drag
        """
        # Check if any files in the drag are valid
        files = self._parse_dropped_data(event.data)
        has_valid = any(self._is_valid_file(f) for f in files)

        if has_valid:
            self._is_drag_over = True
            self._update_style()
            return event.action

        return None

    def _on_drag_over(self, event):
        """Handle drag over/position event - CRITICAL for accepting drops.

        This method was MISSING in the PyQt6 version (dragMoveEvent).
        Without it, the drop zone would not properly accept the drag
        during mouse movement, causing the "not allowed" cursor.

        Args:
            event: TkinterDnD event

        Returns:
            event.action to continue accepting the drag
        """
        # Must return event.action to accept the drag at this position
        if self._is_drag_over:
            return event.action

        # Check validity if not already in drag state
        files = self._parse_dropped_data(event.data)
        has_valid = any(self._is_valid_file(f) for f in files)

        if has_valid:
            self._is_drag_over = True
            self._update_style()
            return event.action

        return None

    def _on_drag_leave(self, event):
        """Handle drag leave event - reset visual state.

        Args:
            event: TkinterDnD event
        """
        self._is_drag_over = False
        self._update_style()

    def _on_drop(self, event):
        """Handle drop event - process dropped files.

        Args:
            event: TkinterDnD event

        Returns:
            event.action to confirm the drop was handled
        """
        self._is_drag_over = False
        self._update_style()

        # Parse and filter files
        all_files = self._parse_dropped_data(event.data)
        valid_files = [f for f in all_files if self._is_valid_file(f)]

        if valid_files and self.on_files_dropped:
            self.on_files_dropped(valid_files)
            return event.action

        return None

    def _parse_dropped_data(self, data: str) -> List[str]:
        """Parse the dropped data string into file paths.

        tkinterdnd2 returns paths in different formats depending on the OS:
        - macOS/Linux: Space-separated, paths with spaces in braces {/path/with spaces}
        - Windows: Space-separated, paths may be quoted

        Args:
            data: Raw dropped data string

        Returns:
            List of file paths
        """
        if not data:
            return []

        files = []

        # Handle brace-enclosed paths (macOS/Linux paths with spaces)
        # Pattern matches {/path/with spaces} or regular paths
        pattern = r'\{([^}]+)\}|(\S+)'
        matches = re.findall(pattern, data)

        for match in matches:
            # match is a tuple of (brace_content, non_brace_content)
            path = match[0] if match[0] else match[1]
            if path:
                # Clean up the path
                path = path.strip('"\'')
                if path and Path(path).exists():
                    files.append(path)

        return files

    def _is_valid_file(self, file_path: str) -> bool:
        """Check if a file has a valid extension.

        Args:
            file_path: Path to the file

        Returns:
            True if file extension is in allowed list
        """
        ext = Path(file_path).suffix.lower().lstrip('.')
        return ext in self.allowed_extensions

    def _update_style(self):
        """Update the visual style based on drag state."""
        if self._is_drag_over:
            # Active drag state - highlighted
            self.configure(
                fg_color=COLORS['drop_zone_active'],
                border_width=2,
                border_color=COLORS['primary'],
            )
            self.label.configure(
                text="Release to add files",
                text_color=COLORS['primary_light'],
                font=ctk.CTkFont(size=13, weight="bold"),
            )
        else:
            # Normal state - dashed border effect
            self.configure(
                fg_color=COLORS['drop_zone_normal'],
                border_width=2,
                border_color=COLORS['border'],
            )
            self.label.configure(
                text="Drop files here or click Add Files",
                text_color=COLORS['text_muted'],
                font=ctk.CTkFont(size=13),
            )

    def set_extensions(self, extensions: List[str]):
        """Update the allowed file extensions.

        Args:
            extensions: New list of allowed extensions
        """
        self.allowed_extensions = [ext.lower().lstrip('.') for ext in extensions]

    def set_callback(self, callback: Callable[[List[str]], None]):
        """Set the callback for when files are dropped.

        Args:
            callback: Function to call with list of file paths
        """
        self.on_files_dropped = callback
