"""AI fix suggestion card."""

from typing import List
import customtkinter as ctk

from ..theme import COLORS, SPACING


class AIFixCard(ctk.CTkFrame):

    def __init__(self, master, suggestions: List, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._suggestions = suggestions
        self._init_ui()

    def _init_ui(self):
        for i, s in enumerate(self._suggestions):
            self._add_suggestion(s, is_last=(i == len(self._suggestions) - 1))

    def _add_suggestion(self, suggestion, is_last=False):
        card = ctk.CTkFrame(
            self, fg_color=COLORS['bg_medium'], corner_radius=8,
            border_width=1, border_color=COLORS['border'],
        )
        bottom_pad = 0 if is_last else SPACING['sm']
        card.pack(fill="x", pady=(0, bottom_pad))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, SPACING['sm']))

        ctk.CTkLabel(
            top_row, text=suggestion.feature_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        ctk.CTkLabel(
            top_row,
            text=f" {suggestion.feature_id} ",
            font=ctk.CTkFont(size=9),
            text_color=COLORS['text_muted'],
            fg_color=COLORS['bg_dark'],
            corner_radius=4,
        ).pack(side="left", padx=(SPACING['sm'], 0))

        ctk.CTkLabel(
            inner, text=suggestion.suggestion,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            wraplength=600, justify="left", anchor="w",
        ).pack(fill="x", pady=(0, SPACING['sm']))

        if suggestion.code_example:
            code_outer = ctk.CTkFrame(
                inner, fg_color=COLORS['bg_darkest'], corner_radius=6,
            )
            code_outer.pack(fill="x")

            code_header = ctk.CTkFrame(code_outer, fg_color="transparent")
            code_header.pack(fill="x", padx=SPACING['sm'], pady=(SPACING['xs'], 0))

            ctk.CTkLabel(
                code_header, text="Example fix",
                font=ctk.CTkFont(size=9),
                text_color=COLORS['text_muted'],
            ).pack(side="left")

            ctk.CTkLabel(
                code_outer, text=suggestion.code_example,
                font=ctk.CTkFont(family="Courier", size=11),
                text_color=COLORS['accent'],
                wraplength=560, justify="left", anchor="w",
            ).pack(fill="x", padx=SPACING['md'], pady=(SPACING['xs'], SPACING['sm']))
