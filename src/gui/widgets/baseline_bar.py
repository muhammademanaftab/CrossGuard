"""Horizontal Baseline status bar — Widely Available | Newly Available | Limited."""

import customtkinter as ctk

from ..theme import COLORS, SPACING


class BaselineBar(ctk.CTkFrame):
    """Compact 3-column bar showing W3C Baseline summary counts."""

    BASELINE_COLORS = {
        'widely': '#4CAF50',   # green
        'newly': '#58a6ff',    # blue
        'limited': '#FFA726',  # orange
    }

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            height=56,
            **kwargs
        )
        self.pack_propagate(False)
        self._init_ui()

    def _init_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['xs'])
        container.grid_columnconfigure((0, 1, 2), weight=1)
        container.grid_rowconfigure(0, weight=1)

        self._widely = self._create_cell(container, "0", "Widely Available", self.BASELINE_COLORS['widely'], 0)
        self._create_sep(container, 0)
        self._newly = self._create_cell(container, "0", "Newly Available", self.BASELINE_COLORS['newly'], 1)
        self._create_sep(container, 1)
        self._limited = self._create_cell(container, "0", "Limited", self.BASELINE_COLORS['limited'], 2)

    def _create_cell(self, parent, value, label, color, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="nsew", padx=SPACING['sm'])

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        val_lbl = ctk.CTkLabel(inner, text=value, font=ctk.CTkFont(size=18, weight="bold"), text_color=color)
        val_lbl.pack()

        lbl = ctk.CTkLabel(inner, text=label, font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'])
        lbl.pack()

        return {'value': val_lbl, 'label': lbl}

    def _create_sep(self, parent, after_col):
        sep = ctk.CTkFrame(parent, fg_color=COLORS['border'], width=1)
        sep.grid(row=0, column=after_col, sticky="nse")

    def set_data(self, widely_available: int = 0, newly_available: int = 0, limited: int = 0, **_kwargs):
        self._widely['value'].configure(text=str(widely_available))
        self._newly['value'].configure(text=str(newly_available))
        self._limited['value'].configure(text=str(limited))
