"""Themed message dialogs: info, warning, error, question, and progress."""

from typing import Optional

import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


class MessageDialog(ctk.CTkToplevel):
    """Modal message dialog with icon and configurable buttons."""

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        icon_type: str = "info",
        buttons: list = None,
    ):
        super().__init__(parent)

        self.result = None
        self._buttons = buttons or ["OK"]

        self.title(title)
        self.configure(fg_color=COLORS['bg_medium'])
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._build_ui(message, icon_type)
        self._center_on_parent(parent)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self, message: str, icon_type: str):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])

        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="x", pady=(0, SPACING['xl']))

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

        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_primary'],
            wraplength=300,
            justify="left",
        )
        message_label.pack(side="left", fill="x", expand=True)

        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")

        # First button is treated as primary (accent colored)
        for i, btn_text in enumerate(self._buttons):
            is_primary = i == 0
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
        self.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 350:
            width = 350
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

    def _on_button_click(self, button_text: str):
        self.result = button_text
        self.destroy()

    def _on_close(self):
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[str]:
        """Block until the dialog is closed, then return which button was clicked."""
        self.wait_window()
        return self.result


def show_info(parent, title: str, message: str) -> None:
    dialog = MessageDialog(parent, title, message, icon_type="info")
    dialog.get_result()


def show_warning(parent, title: str, message: str) -> None:
    dialog = MessageDialog(parent, title, message, icon_type="warning")
    dialog.get_result()


def show_error(parent, title: str, message: str) -> None:
    dialog = MessageDialog(parent, title, message, icon_type="error")
    dialog.get_result()


def ask_question(parent, title: str, message: str) -> bool:
    """Returns True if Yes was clicked."""
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
    """Modal progress bar dialog."""

    def __init__(
        self,
        parent,
        title: str,
        message: str = "Processing...",
    ):
        super().__init__(parent)

        self.title(title)
        self.configure(fg_color=COLORS['bg_medium'])
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._build_ui(message)
        self._center_on_parent(parent)

        # Block the X button while in progress
        self.protocol("WM_DELETE_WINDOW", lambda: None)

    def _build_ui(self, message: str):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=SPACING['xxl'], pady=SPACING['xl'])

        self.status_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_primary'],
        )
        self.status_label.pack(pady=(0, SPACING['md']))

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

        self.percent_label = ctk.CTkLabel(
            main_frame,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        )
        self.percent_label.pack(pady=(SPACING['sm'], 0))

    def _center_on_parent(self, parent):
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

    def set_progress(self, current: int, total: int = 100, message: str = None):
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.set(current / total)
        else:
            percent = 0
            self.progress_bar.set(0)

        self.percent_label.configure(text=f"{percent}%")

        if message:
            self.status_label.configure(text=message)

        self.update()

    def show(self):
        self.update_idletasks()
        self.update()

    def set_message(self, message: str):
        self.status_label.configure(text=message)
        self.update()

    def close(self):
        self.grab_release()
        self.destroy()
