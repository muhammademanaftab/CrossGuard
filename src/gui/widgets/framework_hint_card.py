"""Contextual hint card for framework projects that need build output analysis."""

from dataclasses import dataclass
from typing import Callable, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING


@dataclass
class FrameworkHint:
    """Hint info for a detected framework."""
    hint_type: str          # 'build_required', 'server_side', 'ready'
    title: str              # "React project detected"
    message: str
    build_command: Optional[str] = None  # "npm run build"
    build_folder: Optional[str] = None   # "build", "dist", etc.
    icon: str = 'info'


class FrameworkHintCard(ctk.CTkFrame):
    """Shows guidance when a framework is detected that needs special handling."""

    def __init__(
        self,
        master,
        on_include_build: Optional[Callable[[str], None]] = None,
        on_dismiss: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS['accent_muted'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['info'],
            **kwargs
        )

        self._on_include_build = on_include_build
        self._on_dismiss = on_dismiss
        self._current_hint: Optional[FrameworkHint] = None
        self._build_folder_exists = False

        self._init_ui()

    def _init_ui(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        self.top_row = ctk.CTkFrame(self.content, fg_color="transparent")
        self.top_row.pack(fill="x")

        self.icon_label = ctk.CTkLabel(
            self.top_row,
            text="\u2139",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['info'],
            width=24,
        )
        self.icon_label.pack(side="left")

        self.title_label = ctk.CTkLabel(
            self.top_row,
            text="Framework detected",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.title_label.pack(side="left", padx=(SPACING['xs'], 0))

        # Shown only when the build folder actually exists on disk
        self.include_btn = ctk.CTkButton(
            self.top_row,
            text="Include build/",
            width=120,
            height=28,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dim'],
            font=ctk.CTkFont(size=11),
            command=self._on_include_click,
        )

        self.dismiss_btn = ctk.CTkButton(
            self.top_row,
            text="Dismiss",
            width=70,
            height=28,
            fg_color="transparent",
            hover_color=COLORS['hover_bg'],
            border_width=1,
            border_color=COLORS['border'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=11),
            command=self._on_dismiss_click,
        )
        self.dismiss_btn.pack(side="right")

        self.message_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.message_frame.pack(fill="x", pady=(SPACING['sm'], 0))

        self.message_label = ctk.CTkLabel(
            self.message_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            justify="left",
            anchor="w",
            wraplength=600,
        )
        self.message_label.pack(side="left", padx=(28, 0))  # aligned with title text

        # Monospace command hint (e.g. "$ npm run build")
        self.command_frame = ctk.CTkFrame(self.content, fg_color="transparent")

        self.command_label = ctk.CTkLabel(
            self.command_frame,
            text="",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=COLORS['text_muted'],
            fg_color=COLORS['bg_dark'],
            corner_radius=4,
            padx=8,
            pady=4,
        )
        self.command_label.pack(side="left", padx=(28, 0))

    def update_hint(self, hint: FrameworkHint, build_folder_exists: bool = False):
        self._current_hint = hint
        self._build_folder_exists = build_folder_exists

        if hint.icon == 'warning':
            self.configure(
                fg_color=COLORS['warning_muted'],
                border_color=COLORS['warning'],
            )
            self.icon_label.configure(
                text="\u26A0",
                text_color=COLORS['warning'],
            )
        else:
            self.configure(
                fg_color=COLORS['accent_muted'],
                border_color=COLORS['info'],
            )
            self.icon_label.configure(
                text="\u2139",
                text_color=COLORS['info'],
            )

        self.title_label.configure(text=hint.title)
        self.message_label.configure(text=hint.message)

        if build_folder_exists and hint.build_folder:
            self.include_btn.configure(text=f"Include {hint.build_folder}/")
            self.include_btn.pack(side="right", padx=(0, SPACING['sm']))
        else:
            self.include_btn.pack_forget()

        # Show build command when there's no build output yet
        if hint.build_command and not build_folder_exists:
            self.command_frame.pack(fill="x", pady=(SPACING['xs'], 0))
            self.command_label.configure(text=f"$ {hint.build_command}")
        else:
            self.command_frame.pack_forget()

    def _on_include_click(self):
        if self._on_include_build and self._current_hint and self._current_hint.build_folder:
            self._on_include_build(self._current_hint.build_folder)

    def _on_dismiss_click(self):
        if self._on_dismiss:
            self._on_dismiss()

    def show(self):
        self.pack(fill="x", pady=(0, SPACING['md']))

    def hide(self):
        self.pack_forget()

    def get_current_hint(self) -> Optional[FrameworkHint]:
        return self._current_hint

    def get_build_folder(self) -> Optional[str]:
        if self._current_hint:
            return self._current_hint.build_folder
        return None
