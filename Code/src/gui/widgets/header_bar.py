"""Top header bar with logo, title, and action buttons."""

from typing import Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, LOGO_SIMPLE


class HeaderBar(ctk.CTkFrame):

    def __init__(
        self,
        master,
        title: str = "Browser Compatibility Checker",
        subtitle: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            master,
            height=56,
            fg_color=COLORS['bg_dark'],
            corner_radius=0,
            **kwargs
        )

        self._title = title
        self._subtitle = subtitle

        self.pack_propagate(False)

        self._init_ui()

    def _init_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['sm'])

        left_frame = ctk.CTkFrame(container, fg_color="transparent")
        left_frame.pack(side="left", fill="y")

        logo_label = ctk.CTkLabel(
            left_frame,
            text=LOGO_SIMPLE,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['accent'],
        )
        logo_label.pack(side="left", padx=(0, SPACING['lg']))

        sep_label = ctk.CTkLabel(
            left_frame,
            text="|",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['border'],
        )
        sep_label.pack(side="left", padx=(0, SPACING['lg']))

        self.title_label = ctk.CTkLabel(
            left_frame,
            text=self._title,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
        )
        self.title_label.pack(side="left")

        if self._subtitle:
            breadcrumb_label = ctk.CTkLabel(
                left_frame,
                text=f"  /  {self._subtitle}",
                font=ctk.CTkFont(size=14),
                text_color=COLORS['text_muted'],
            )
            breadcrumb_label.pack(side="left")

        self.actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.actions_frame.pack(side="right", fill="y")

    def set_title(self, title: str):
        self._title = title
        self.title_label.configure(text=title)

    def set_subtitle(self, subtitle: Optional[str]):
        self._subtitle = subtitle

    def add_action_button(
        self,
        text: str,
        command,
        fg_color: Optional[str] = None,
        hover_color: Optional[str] = None,
        **kwargs
    ) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            self.actions_frame,
            text=text,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            fg_color=fg_color or COLORS['bg_light'],
            hover_color=hover_color or COLORS['hover_bg'],
            command=command,
            **kwargs
        )
        btn.pack(side="right", padx=(SPACING['sm'], 0))
        return btn

    def clear_actions(self):
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
