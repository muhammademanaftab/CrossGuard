"""
Custom message dialog widgets for CustomTkinter.

Provides show_info, show_warning, show_error, and ask_question dialogs
that match the modern charcoal + cyan theme.
"""

from typing import Optional

import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


class MessageDialog(ctk.CTkToplevel):
    """Base class for custom message dialogs."""

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        icon_type: str = "info",
        buttons: list = None,
    ):
        """Initialize the message dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Message to display
            icon_type: Type of icon ("info", "warning", "error", "question")
            buttons: List of button labels (default: ["OK"])
        """
        super().__init__(parent)

        self.result = None
        self._buttons = buttons or ["OK"]

        # Configure window
        self.title(title)
        self.configure(fg_color=COLORS['bg_medium'])
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        self._build_ui(message, icon_type)

        # Center on parent
        self._center_on_parent(parent)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self, message: str, icon_type: str):
        """Build the dialog UI."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])

        # Icon and message row
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="x", pady=(0, SPACING['xl']))

        # Icon
        icon_colors = {
            "info": COLORS['accent'],
            "warning": COLORS['warning'],
            "error": COLORS['danger'],
            "question": COLORS['accent'],
        }
        icon_symbols = {
            "info": ICONS['info'],
            "warning": ICONS['warning'],
            "error": ICONS['error'],
            "question": "?",
        }

        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon_symbols.get(icon_type, ICONS['info']),
            font=ctk.CTkFont(size=32),
            text_color=icon_colors.get(icon_type, COLORS['accent']),
            width=50,
        )
        icon_label.pack(side="left", padx=(0, SPACING['lg']))

        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_primary'],
            wraplength=300,
            justify="left",
        )
        message_label.pack(side="left", fill="x", expand=True)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")

        # Add buttons
        for i, btn_text in enumerate(self._buttons):
            is_primary = i == 0  # First button is primary
            btn = ctk.CTkButton(
                buttons_frame,
                text=btn_text,
                font=ctk.CTkFont(size=13, weight="bold" if is_primary else "normal"),
                width=100,
                height=36,
                fg_color=COLORS['accent'] if is_primary else "transparent",
                border_width=1 if not is_primary else 0,
                border_color=COLORS['border'],
                text_color=COLORS['text_primary'],
                hover_color=COLORS['accent_dim'] if is_primary else COLORS['hover_bg'],
                command=lambda t=btn_text: self._on_button_click(t),
            )
            btn.pack(side="right", padx=(SPACING['sm'], 0))

    def _center_on_parent(self, parent):
        """Center the dialog on the parent window."""
        self.update_idletasks()

        # Get dialog size
        width = self.winfo_width()
        height = self.winfo_height()

        # Ensure minimum size
        if width < 350:
            width = 350
            self.geometry(f"{width}x{height}")

        # Get parent position and size
        if parent:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()

            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
        else:
            # Center on screen
            x = (self.winfo_screenwidth() - width) // 2
            y = (self.winfo_screenheight() - height) // 2

        self.geometry(f"+{x}+{y}")

    def _on_button_click(self, button_text: str):
        """Handle button click."""
        self.result = button_text
        self.destroy()

    def _on_close(self):
        """Handle window close."""
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[str]:
        """Wait for dialog to close and return result."""
        self.wait_window()
        return self.result


def show_info(parent, title: str, message: str) -> None:
    """Show an information dialog.

    Args:
        parent: Parent window
        title: Dialog title
        message: Message to display
    """
    dialog = MessageDialog(parent, title, message, icon_type="info")
    dialog.get_result()


def show_warning(parent, title: str, message: str) -> None:
    """Show a warning dialog.

    Args:
        parent: Parent window
        title: Dialog title
        message: Message to display
    """
    dialog = MessageDialog(parent, title, message, icon_type="warning")
    dialog.get_result()


def show_error(parent, title: str, message: str) -> None:
    """Show an error dialog.

    Args:
        parent: Parent window
        title: Dialog title
        message: Message to display
    """
    dialog = MessageDialog(parent, title, message, icon_type="error")
    dialog.get_result()


def ask_question(parent, title: str, message: str) -> bool:
    """Show a question dialog with Yes/No buttons.

    Args:
        parent: Parent window
        title: Dialog title
        message: Message to display

    Returns:
        True if Yes was clicked, False otherwise
    """
    dialog = MessageDialog(
        parent,
        title,
        message,
        icon_type="question",
        buttons=["Yes", "No"]
    )
    result = dialog.get_result()
    return result == "Yes"


class ProgressDialog(ctk.CTkToplevel):
    """Progress dialog with progress bar and status message."""

    def __init__(
        self,
        parent,
        title: str,
        message: str = "Processing...",
    ):
        """Initialize the progress dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Initial status message
        """
        super().__init__(parent)

        # Configure window
        self.title(title)
        self.configure(fg_color=COLORS['bg_medium'])
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        self._build_ui(message)

        # Center on parent
        self._center_on_parent(parent)

        # Prevent closing with X button during progress
        self.protocol("WM_DELETE_WINDOW", lambda: None)

    def _build_ui(self, message: str):
        """Build the dialog UI."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=SPACING['xxl'], pady=SPACING['xl'])

        # Status message
        self.status_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_primary'],
        )
        self.status_label.pack(pady=(0, SPACING['md']))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            width=300,
            height=12,
            corner_radius=6,
            fg_color=COLORS['bg_light'],
            progress_color=COLORS['accent'],
        )
        self.progress_bar.pack()
        self.progress_bar.set(0)

        # Percentage label
        self.percent_label = ctk.CTkLabel(
            main_frame,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        )
        self.percent_label.pack(pady=(SPACING['sm'], 0))

    def _center_on_parent(self, parent):
        """Center the dialog on the parent window."""
        self.update_idletasks()

        width = max(360, self.winfo_width())
        height = self.winfo_height()
        self.geometry(f"{width}x{height}")

        if parent:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()

            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
        else:
            x = (self.winfo_screenwidth() - width) // 2
            y = (self.winfo_screenheight() - height) // 2

        self.geometry(f"+{x}+{y}")

    def set_progress(self, value: int, message: str = None):
        """Update the progress value and optional message.

        Args:
            value: Progress percentage (0-100)
            message: Optional new status message
        """
        self.progress_bar.set(value / 100.0)
        self.percent_label.configure(text=f"{value}%")

        if message:
            self.status_label.configure(text=message)

        self.update()

    def close(self):
        """Close the progress dialog."""
        self.destroy()
