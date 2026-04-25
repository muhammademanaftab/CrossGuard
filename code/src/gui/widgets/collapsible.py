"""Generic expand/collapse section for progressive disclosure."""

from typing import Callable, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


class CollapsibleSection(ctk.CTkFrame):

    def __init__(
        self,
        master,
        title: str,
        badge_text: Optional[str] = None,
        badge_color: Optional[str] = None,
        expanded: bool = False,
        on_toggle: Optional[Callable[[bool], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._title = title
        self._badge_text = badge_text
        self._badge_color = badge_color or COLORS['accent']
        self._expanded = expanded
        self._on_toggle = on_toggle

        self._init_ui()
        self._update_state()

    def _init_ui(self):
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            cursor="hand2",
        )
        self.header_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        # All header children need click bindings for the whole area to be clickable
        self.header_frame.bind("<Button-1>", self._on_header_click)

        self.chevron_label = ctk.CTkLabel(
            self.header_frame,
            text=ICONS['chevron_right'],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_muted'],
            width=20,
        )
        self.chevron_label.pack(side="left")
        self.chevron_label.bind("<Button-1>", self._on_header_click)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self._title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.title_label.pack(side="left", padx=(SPACING['xs'], 0))
        self.title_label.bind("<Button-1>", self._on_header_click)

        if self._badge_text:
            self.badge_label = ctk.CTkLabel(
                self.header_frame,
                text=f" {self._badge_text} ",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
                fg_color=self._badge_color,
                corner_radius=4,
            )
            self.badge_label.pack(side="left", padx=(SPACING['sm'], 0))
            self.badge_label.bind("<Button-1>", self._on_header_click)

        self.action_label = ctk.CTkLabel(
            self.header_frame,
            text="Expand",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.action_label.pack(side="right")
        self.action_label.bind("<Button-1>", self._on_header_click)

        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        self.separator = ctk.CTkFrame(
            self,
            fg_color=COLORS['border'],
            height=1,
        )

    def _on_header_click(self, event=None):
        self.toggle()

    def _update_state(self):
        if self._expanded:
            self.chevron_label.configure(text=ICONS['chevron_down'])
            self.action_label.configure(text="Collapse")
            self.separator.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
            self.content_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        else:
            self.chevron_label.configure(text=ICONS['chevron_right'])
            self.action_label.configure(text="Expand")
            self.separator.pack_forget()
            self.content_frame.pack_forget()

    def toggle(self):
        self._expanded = not self._expanded
        self._update_state()

        if self._on_toggle:
            self._on_toggle(self._expanded)

    def expand(self):
        if not self._expanded:
            self._expanded = True
            self._update_state()
            if self._on_toggle:
                self._on_toggle(self._expanded)

    def collapse(self):
        if self._expanded:
            self._expanded = False
            self._update_state()
            if self._on_toggle:
                self._on_toggle(self._expanded)

    def is_expanded(self) -> bool:
        return self._expanded

    def get_content_frame(self) -> ctk.CTkFrame:
        return self.content_frame

    def set_title(self, title: str):
        self._title = title
        self.title_label.configure(text=title)

    def set_badge(self, text: Optional[str], color: Optional[str] = None):
        self._badge_text = text
        if color:
            self._badge_color = color

        if hasattr(self, 'badge_label'):
            if text:
                self.badge_label.configure(text=f" {text} ")
                if color:
                    self.badge_label.configure(fg_color=color)
                self.badge_label.pack(side="left", padx=(SPACING['sm'], 0))
            else:
                self.badge_label.pack_forget()
        elif text:
            self.badge_label = ctk.CTkLabel(
                self.header_frame,
                text=f" {text} ",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
                fg_color=self._badge_color,
                corner_radius=4,
            )
            self.badge_label.pack(side="left", padx=(SPACING['sm'], 0))
            self.badge_label.bind("<Button-1>", self._on_header_click)
