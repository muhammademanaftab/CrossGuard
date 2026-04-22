"""Native CTk chart widgets."""

from typing import Dict
import customtkinter as ctk

from ..theme import COLORS, SPACING
from .browser_card import StackedBarWidget


class BrowserRadarChart(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_medium'], corner_radius=8, **kwargs)
        self._data = {}

        ctk.CTkLabel(
            self, text="Browser Compatibility",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))

    def set_data(self, browsers_data: Dict):
        self._data = browsers_data
        self._draw()

    def _draw(self, **kwargs):
        if not hasattr(self, '_data'):
            return
        for w in self.winfo_children()[1:]:
            w.destroy()

        if not self._data:
            return

        for name, data in self._data.items():
            supported = data.get('supported', 0) or 0
            partial = data.get('partial', 0) or 0
            unsupported = data.get('unsupported', 0) or 0
            pct = data.get('compatibility_percentage', 0) or 0

            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

            ctk.CTkLabel(
                row, text=name.title(),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['text_primary'],
                width=70, anchor="w",
            ).pack(side="left")

            bar = StackedBarWidget(row, height=16, bg_color=COLORS['bg_medium'])
            bar.pack(side="left", fill="x", expand=True, padx=SPACING['sm'])
            bar.set_values(supported, partial, unsupported, animate=False)

            if pct >= 80:
                pct_color = COLORS['success']
            elif pct >= 50:
                pct_color = COLORS['warning']
            else:
                pct_color = COLORS['danger']

            ctk.CTkLabel(
                row, text=f"{pct:.0f}%",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=pct_color,
                width=45, anchor="e",
            ).pack(side="right")

        legend = ctk.CTkFrame(self, fg_color="transparent")
        legend.pack(fill="x", padx=SPACING['md'], pady=(SPACING['xs'], SPACING['md']))

        for label, color in [("Supported", COLORS['success']), ("Partial", COLORS['warning']), ("Unsupported", COLORS['danger'])]:
            dot = ctk.CTkFrame(legend, fg_color=color, width=8, height=8, corner_radius=4)
            dot.pack(side="left", padx=(0, 3))
            ctk.CTkLabel(
                legend, text=label,
                font=ctk.CTkFont(size=9),
                text_color=COLORS['text_muted'],
            ).pack(side="left", padx=(0, SPACING['md']))

    def clear(self):
        for w in self.winfo_children()[1:]:
            w.destroy()


class FeatureDistributionChart(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_medium'], corner_radius=8, **kwargs)
        self._total_label = None

        ctk.CTkLabel(
            self, text="Feature Distribution",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))

        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))

    def set_data(self, html_count: int, css_count: int, js_count: int, total_unique: int = None):
        html_count = html_count or 0
        css_count = css_count or 0
        js_count = js_count or 0
        total = total_unique if total_unique is not None else (html_count + css_count + js_count)

        for w in self._content.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self._content,
            text=f"{total} features detected",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, SPACING['sm']))

        types = [
            ("HTML", html_count, COLORS.get('html_color', '#e34c26')),
            ("CSS", css_count, COLORS.get('css_color', '#264de4')),
            ("JavaScript", js_count, COLORS.get('js_color', '#f7df1e')),
        ]

        for name, count, color in types:
            if count == 0 and total == 0:
                continue

            row = ctk.CTkFrame(self._content, fg_color="transparent")
            row.pack(fill="x", pady=(0, SPACING['xs']))

            label_row = ctk.CTkFrame(row, fg_color="transparent")
            label_row.pack(fill="x")

            dot = ctk.CTkFrame(label_row, fg_color=color, width=8, height=8, corner_radius=4)
            dot.pack(side="left", pady=2)

            ctk.CTkLabel(
                label_row, text=name,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
            ).pack(side="left", padx=(SPACING['xs'], 0))

            pct_text = f"{(count / total * 100):.0f}%" if total > 0 else "0%"
            ctk.CTkLabel(
                label_row, text=f"{count} ({pct_text})",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_muted'],
            ).pack(side="right")

            bar_bg = ctk.CTkFrame(row, fg_color=COLORS['bg_light'], height=6, corner_radius=3)
            bar_bg.pack(fill="x", pady=(2, 0))
            bar_bg.pack_propagate(False)

            fill_pct = (count / total) if total > 0 else 0
            if fill_pct > 0:
                bar_fill = ctk.CTkFrame(bar_bg, fg_color=color, corner_radius=3)
                bar_fill.place(relx=0, rely=0, relwidth=fill_pct, relheight=1)

    def clear(self):
        for w in self._content.winfo_children():
            w.destroy()


class CompatibilityBarChart(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_medium'], corner_radius=8, **kwargs)

        ctk.CTkLabel(
            self, text="Support Summary",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))

        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))

    def set_data(self, browsers_data: Dict):
        for w in self._content.winfo_children():
            w.destroy()

        if not browsers_data:
            return

        total_supported = 0
        total_partial = 0
        total_unsupported = 0

        for data in browsers_data.values():
            total_supported += data.get('supported', 0) or 0
            total_partial += data.get('partial', 0) or 0
            total_unsupported += data.get('unsupported', 0) or 0

        grand_total = total_supported + total_partial + total_unsupported

        stats_row = ctk.CTkFrame(self._content, fg_color="transparent")
        stats_row.pack(fill="x")
        stats_row.grid_columnconfigure(0, weight=1)
        stats_row.grid_columnconfigure(1, weight=1)
        stats_row.grid_columnconfigure(2, weight=1)

        stats = [
            ("Supported", total_supported, COLORS['success']),
            ("Partial", total_partial, COLORS['warning']),
            ("Unsupported", total_unsupported, COLORS['danger']),
        ]

        for col, (label, count, color) in enumerate(stats):
            block = ctk.CTkFrame(stats_row, fg_color=COLORS['bg_dark'], corner_radius=6)
            block.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else SPACING['xs'], 0))

            inner = ctk.CTkFrame(block, fg_color="transparent")
            inner.pack(padx=SPACING['sm'], pady=SPACING['sm'])

            ctk.CTkLabel(
                inner, text=str(count),
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=color,
            ).pack()

            pct = f"{(count / grand_total * 100):.0f}%" if grand_total > 0 else "0%"
            ctk.CTkLabel(
                inner, text=pct,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_muted'],
            ).pack()

            ctk.CTkLabel(
                inner, text=label,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_secondary'],
            ).pack(pady=(2, 0))

    def clear(self):
        for w in self._content.winfo_children():
            w.destroy()


# Stubs kept for backward compatibility
class ScoreGaugeChart(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

    def set_score(self, score: float, grade: str = None):
        pass

    def clear(self):
        pass


class SupportStatusChart(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

    def set_data(self, supported: int, partial: int, unsupported: int):
        pass

    def clear(self):
        pass
