"""Bottom status bar -- file count, status message, last analysis time."""

from typing import Optional
from datetime import datetime
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


class StatusBar(ctk.CTkFrame):

    def __init__(
        self,
        master,
        **kwargs
    ):
        super().__init__(
            master,
            height=28,
            fg_color=COLORS['bg_darkest'],
            corner_radius=0,
            **kwargs
        )

        self._file_count = 0
        self._status_message = "Ready"
        self._last_analysis: Optional[datetime] = None

        self.pack_propagate(False)

        self._init_ui()

    def _init_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['md'])

        left_frame = ctk.CTkFrame(container, fg_color="transparent")
        left_frame.pack(side="left", fill="y")

        self.status_dot = ctk.CTkLabel(
            left_frame,
            text=ICONS['dot'],
            font=ctk.CTkFont(size=10),
            text_color=COLORS['success'],
        )
        self.status_dot.pack(side="left", padx=(0, SPACING['xs']))

        self.status_label = ctk.CTkLabel(
            left_frame,
            text=self._status_message,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.status_label.pack(side="left")

        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.pack(side="left", fill="y", padx=SPACING['xl'])

        self.file_count_label = ctk.CTkLabel(
            center_frame,
            text=self._format_file_count(),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.file_count_label.pack(side="left")

        right_frame = ctk.CTkFrame(container, fg_color="transparent")
        right_frame.pack(side="right", fill="y")

        self.analysis_label = ctk.CTkLabel(
            right_frame,
            text=self._format_last_analysis(),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.analysis_label.pack(side="right")

    def _format_file_count(self) -> str:
        if self._file_count == 0:
            return "No files selected"
        elif self._file_count == 1:
            return "1 file selected"
        return f"{self._file_count} files selected"

    def _format_last_analysis(self) -> str:
        if self._last_analysis is None:
            return "Last analysis: Never"
        time_str = self._last_analysis.strftime("%H:%M")
        return f"Last analysis: {time_str}"

    def set_status(self, message: str, status_type: str = "normal"):
        """Update the status message and dot color (normal/success/warning/error/info)."""
        self._status_message = message
        self.status_label.configure(text=message)

        dot_colors = {
            "normal": COLORS['text_muted'],
            "success": COLORS['success'],
            "warning": COLORS['warning'],
            "error": COLORS['danger'],
            "info": COLORS['accent'],
        }
        self.status_dot.configure(text_color=dot_colors.get(status_type, COLORS['text_muted']))

    def set_file_count(self, count: int):
        self._file_count = count
        self.file_count_label.configure(text=self._format_file_count())

    def set_last_analysis(self, timestamp: Optional[datetime] = None):
        """Set timestamp; defaults to now if None."""
        if timestamp is None:
            timestamp = datetime.now()
        self._last_analysis = timestamp
        self.analysis_label.configure(text=self._format_last_analysis())

    def clear_last_analysis(self):
        self._last_analysis = None
        self.analysis_label.configure(text=self._format_last_analysis())
