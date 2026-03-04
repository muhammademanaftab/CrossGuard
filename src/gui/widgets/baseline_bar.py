"""Baseline status: compact stats bar (matches QuickStatsBar) + collapsible detail."""

from typing import List, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING


BASELINE_COLORS = {
    'widely': '#4CAF50',
    'newly': '#58a6ff',
    'limited': '#FFA726',
}


class BaselineBar(ctk.CTkFrame):
    """Compact bar matching QuickStatsBar height, with collapsible detail underneath."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._expanded = False
        self._limited_features: List[str] = []
        self._newly_features: List[str] = []
        self._has_details = False
        self._init_ui()

    def _init_ui(self):
        # --- Top bar: fixed height, same as QuickStatsBar (56px) ---
        self._top = ctk.CTkFrame(self, fg_color="transparent", height=56, cursor="hand2")
        self._top.pack(fill="x")
        self._top.pack_propagate(False)

        # Toggle arrow on far left
        self._toggle_icon = ctk.CTkLabel(
            self._top, text="▶", font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted'], width=20,
        )
        self._toggle_icon.pack(side="left", padx=(SPACING['sm'], 0))

        # 3-column stats area (fills remaining space)
        stats = ctk.CTkFrame(self._top, fg_color="transparent")
        stats.pack(side="left", fill="both", expand=True, padx=SPACING['xs'])
        stats.grid_columnconfigure((0, 1, 2), weight=1)
        stats.grid_rowconfigure(0, weight=1)

        self._widely = self._make_cell(stats, "0", "Widely Available", BASELINE_COLORS['widely'], 0)
        self._make_sep(stats, 0)
        self._newly_cell = self._make_cell(stats, "0", "Newly Available", BASELINE_COLORS['newly'], 1)
        self._make_sep(stats, 1)
        self._limited_cell = self._make_cell(stats, "0", "Limited", BASELINE_COLORS['limited'], 2)


        # Bind click on entire top bar
        self._bind_click_recursive(self._top, self._toggle)

        # --- Detail panel (hidden) ---
        self._detail = ctk.CTkFrame(self, fg_color="transparent")

    def _make_cell(self, parent, value, label, color, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="nsew", padx=SPACING['sm'])

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        val_lbl = ctk.CTkLabel(inner, text=value, font=ctk.CTkFont(size=18, weight="bold"), text_color=color)
        val_lbl.pack()
        lbl = ctk.CTkLabel(inner, text=label, font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'])
        lbl.pack()

        return {'value': val_lbl, 'label': lbl}

    def _make_sep(self, parent, after_col):
        ctk.CTkFrame(parent, fg_color=COLORS['border'], width=1).grid(row=0, column=after_col, sticky="nse")

    def _bind_click_recursive(self, widget, callback):
        """Bind click to a widget and all descendants."""
        try:
            widget.configure(cursor="hand2")
        except Exception:
            pass
        widget.bind("<Button-1>", lambda e=None: callback())
        for child in widget.winfo_children():
            self._bind_click_recursive(child, callback)

    def _toggle(self):
        if not self._has_details:
            return
        self._expanded = not self._expanded
        if self._expanded:
            self._toggle_icon.configure(text="▼")
            self._detail.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        else:
            self._toggle_icon.configure(text="▶")
            self._detail.pack_forget()

    def _rebuild_detail(self):
        for child in self._detail.winfo_children():
            child.destroy()

        self._has_details = bool(self._limited_features or self._newly_features)

        if not self._has_details:
            self._toggle_icon.configure(text="")
            return

        self._toggle_icon.configure(text="▶")

        # Separator
        ctk.CTkFrame(self._detail, fg_color=COLORS['border'], height=1).pack(fill="x", pady=(0, SPACING['sm']))

        if self._limited_features:
            ctk.CTkLabel(
                self._detail, text="Limited Availability:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BASELINE_COLORS['limited'],
            ).pack(anchor="w")
            for name in self._limited_features:
                ctk.CTkLabel(
                    self._detail, text=f"  • {name}",
                    font=ctk.CTkFont(size=12), text_color=COLORS['text_muted'],
                ).pack(anchor="w")

        if self._newly_features:
            if self._limited_features:
                ctk.CTkFrame(self._detail, fg_color="transparent", height=4).pack()
            ctk.CTkLabel(
                self._detail, text="Newly Available:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BASELINE_COLORS['newly'],
            ).pack(anchor="w")
            for name in self._newly_features:
                ctk.CTkLabel(
                    self._detail, text=f"  • {name}",
                    font=ctk.CTkFont(size=12), text_color=COLORS['text_muted'],
                ).pack(anchor="w")

    def set_data(
        self,
        widely_available: int = 0,
        newly_available: int = 0,
        limited: int = 0,
        limited_features: Optional[List[str]] = None,
        newly_features: Optional[List[str]] = None,
        **_kwargs,
    ):
        self._widely['value'].configure(text=str(widely_available))
        self._newly_cell['value'].configure(text=str(newly_available))
        self._limited_cell['value'].configure(text=str(limited))

        self._limited_features = limited_features or []
        self._newly_features = newly_features or []
        self._rebuild_detail()
