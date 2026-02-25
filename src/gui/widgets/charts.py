"""Matplotlib chart widgets for data visualization."""

from typing import Dict, List
import math

import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch, Wedge, Circle, Polygon
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

from ..theme import COLORS


class BrowserRadarChart(ctk.CTkFrame):
    """Radar/spider chart comparing browser compatibility scores."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=12,
            **kwargs
        )

        self._browsers_data = {}
        self._init_ui()

    def _init_ui(self):
        plt.style.use('dark_background')

        self.title_label = ctk.CTkLabel(
            self,
            text="Browser Compatibility Radar",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.title_label.pack(anchor="w", padx=16, pady=(12, 4))

        self.figure = Figure(figsize=(5, 4.5), dpi=100, facecolor=COLORS['bg_medium'])
        self.figure.patch.set_facecolor(COLORS['bg_medium'])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS['bg_medium'], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=8, pady=(0, 12))

    def set_data(self, browsers_data: Dict):
        self._browsers_data = browsers_data
        self._draw_chart()

    def _draw_chart(self):
        self.figure.clear()

        if not self._browsers_data:
            self.canvas.draw()
            return

        browsers = list(self._browsers_data.keys())
        n_browsers = len(browsers)

        if n_browsers < 3:
            # Radar needs at least 3 points, fall back to bars
            self._draw_fallback_bar()
            return

        angles = np.linspace(0, 2 * np.pi, n_browsers, endpoint=False).tolist()
        angles += angles[:1]  # close the polygon

        values = []
        for browser in browsers:
            data = self._browsers_data[browser]
            pct = data.get('compatibility_percentage', 0) or 0
            values.append(pct)
        values += values[:1]

        ax = self.figure.add_subplot(111, projection='polar')
        ax.set_facecolor(COLORS['bg_medium'])

        # Background rings at 25% intervals
        for ring_val in [25, 50, 75, 100]:
            ring_angles = np.linspace(0, 2 * np.pi, 100)
            ring_values = [ring_val] * 100
            ax.plot(ring_angles, ring_values, color=COLORS['border'],
                   linewidth=0.5, linestyle='-', alpha=0.4)

        for angle in angles[:-1]:
            ax.plot([angle, angle], [0, 100], color=COLORS['border'],
                   linewidth=0.5, alpha=0.4)

        # Layered fill for depth effect
        ax.fill(angles, values, alpha=0.1, color='#58a6ff')
        ax.fill(angles, values, alpha=0.3, color='#58a6ff')
        ax.plot(angles, values, 'o-', linewidth=2.5, color='#58a6ff',
               markersize=8, markerfacecolor='#79c0ff', markeredgecolor='#58a6ff',
               markeredgewidth=2)

        # Glow behind markers
        ax.plot(angles, values, 'o', markersize=12, color='#58a6ff', alpha=0.3)

        ax.set_xticks(angles[:-1])
        browser_labels = []
        for i, browser in enumerate(browsers):
            pct = values[i]
            browser_labels.append(f'{browser.title()}\n{pct:.0f}%')

        ax.set_xticklabels(browser_labels, fontsize=10, fontweight='bold',
                          color=COLORS['text_primary'])

        ax.set_yticklabels([])
        ax.set_ylim(0, 105)

        ax.spines['polar'].set_color(COLORS['border'])
        ax.spines['polar'].set_linewidth(1)
        ax.grid(False)

        avg_score = sum(values[:-1]) / n_browsers
        ax.text(0, 0, f'{avg_score:.0f}%\navg', ha='center', va='center',
               fontsize=14, fontweight='bold', color=COLORS['accent'],
               transform=ax.transData)

        self.figure.tight_layout(pad=1)
        self.canvas.draw()

    def _draw_fallback_bar(self):
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_medium'])

        browsers = list(self._browsers_data.keys())
        percentages = [self._browsers_data[b].get('compatibility_percentage', 0) or 0
                      for b in browsers]

        bars = ax.barh(browsers, percentages, color='#58a6ff', height=0.5)

        ax.set_xlim(0, 100)
        ax.set_xlabel('Compatibility %', color=COLORS['text_muted'])
        ax.tick_params(colors=COLORS['text_primary'])

        for spine in ax.spines.values():
            spine.set_visible(False)

        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.canvas.draw()


class CompatibilityBarChart(ctk.CTkFrame):
    """Horizontal stacked bar chart: supported/partial/unsupported per browser."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=12,
            **kwargs
        )

        self._browsers_data = {}
        self._init_ui()

    def _init_ui(self):
        plt.style.use('dark_background')

        self.title_label = ctk.CTkLabel(
            self,
            text="Feature Support Breakdown",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.title_label.pack(anchor="w", padx=16, pady=(12, 4))

        self.figure = Figure(figsize=(7, 3.5), dpi=100, facecolor=COLORS['bg_medium'])
        self.figure.patch.set_facecolor(COLORS['bg_medium'])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS['bg_medium'], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=8, pady=(0, 12))

    def set_data(self, browsers_data: Dict):
        self._browsers_data = browsers_data
        self._draw_chart()

    def _draw_chart(self):
        self.figure.clear()

        if not self._browsers_data:
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_medium'])

        browsers = list(self._browsers_data.keys())
        n_browsers = len(browsers)

        supported = []
        partial = []
        unsupported = []
        percentages = []

        for browser in browsers:
            data = self._browsers_data[browser]
            supported.append(data.get('supported', 0) or 0)
            partial.append(data.get('partial', 0) or 0)
            unsupported.append(data.get('unsupported', 0) or 0)
            percentages.append(data.get('compatibility_percentage', 0) or 0)

        y_pos = np.arange(n_browsers)
        bar_height = 0.6

        colors = {
            'supported': '#3fb950',
            'partial': '#d29922',
            'unsupported': '#f85149',
        }

        bars1 = ax.barh(y_pos, supported, height=bar_height, color=colors['supported'],
                       label='Supported', edgecolor='none')
        bars2 = ax.barh(y_pos, partial, left=supported, height=bar_height,
                       color=colors['partial'], label='Partial', edgecolor='none')
        bars3 = ax.barh(y_pos, unsupported, left=[s+p for s,p in zip(supported, partial)],
                       height=bar_height, color=colors['unsupported'],
                       label='Unsupported', edgecolor='none')

        ax.set_yticks(y_pos)
        ax.set_yticklabels([b.title() for b in browsers], fontsize=11,
                          color=COLORS['text_primary'])

        max_total = max([s+p+u for s,p,u in zip(supported, partial, unsupported)]) or 1
        for i, pct in enumerate(percentages):
            pct_color = colors['supported'] if pct >= 80 else (
                colors['partial'] if pct >= 50 else colors['unsupported'])
            ax.text(max_total + 1, i, f'{pct:.0f}%', va='center', ha='left',
                   fontsize=11, fontweight='bold', color=pct_color)

        ax.set_xlabel('Features', fontsize=10, color=COLORS['text_muted'])
        ax.set_xlim(0, max_total + 8)
        ax.tick_params(axis='x', colors=COLORS['text_muted'])

        for spine in ax.spines.values():
            spine.set_visible(False)

        legend = ax.legend(loc='upper right', fontsize=9, frameon=True,
                          facecolor=COLORS['bg_dark'], edgecolor=COLORS['border'],
                          labelcolor=COLORS['text_primary'])
        legend.get_frame().set_alpha(0.95)

        ax.invert_yaxis()
        self.figure.tight_layout(pad=1.5)
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.canvas.draw()


class FeatureDistributionChart(ctk.CTkFrame):
    """Donut chart showing HTML/CSS/JS feature distribution."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=12,
            **kwargs
        )

        self._data = {}
        self._total_unique = None
        self._init_ui()

    def _init_ui(self):
        plt.style.use('dark_background')

        self.title_label = ctk.CTkLabel(
            self,
            text="Feature Distribution",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.title_label.pack(anchor="w", padx=16, pady=(12, 4))

        self.figure = Figure(figsize=(4, 4), dpi=100, facecolor=COLORS['bg_medium'])
        self.figure.patch.set_facecolor(COLORS['bg_medium'])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS['bg_medium'], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=8, pady=(0, 12))

    def set_data(self, html_count: int, css_count: int, js_count: int, total_unique: int = None):
        """If total_unique is None, the sum of counts is used instead."""
        self._data = {
            'HTML': html_count or 0,
            'CSS': css_count or 0,
            'JavaScript': js_count or 0
        }
        self._total_unique = total_unique
        self._draw_chart()

    def _draw_chart(self):
        self.figure.clear()

        labels = []
        sizes = []
        colors = []

        color_map = {
            'HTML': '#e34c26',
            'CSS': '#264de4',
            'JavaScript': '#f7df1e'
        }

        for label, size in self._data.items():
            if size > 0:
                labels.append(label)
                sizes.append(size)
                colors.append(color_map[label])

        if not sizes:
            ax = self.figure.add_subplot(111)
            ax.set_facecolor(COLORS['bg_medium'])
            ax.text(0.5, 0.5, 'No features\ndetected',
                   ha='center', va='center', fontsize=12,
                   color=COLORS['text_muted'], transform=ax.transAxes)
            ax.axis('off')
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_medium'])

        total = self._total_unique if self._total_unique is not None else sum(sizes)

        wedges, texts = ax.pie(
            sizes,
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor=COLORS['bg_medium'], linewidth=2),
            counterclock=False
        )

        for wedge in wedges:
            wedge.set_alpha(0.9)

        center_circle = Circle((0, 0), 0.55, fc=COLORS['bg_medium'], ec='none', zorder=10)
        ax.add_patch(center_circle)

        ax.text(0, 0.08, str(total), ha='center', va='center',
               fontsize=28, fontweight='bold', color=COLORS['text_primary'], zorder=11)
        ax.text(0, -0.18, 'features', ha='center', va='center',
               fontsize=10, color=COLORS['text_muted'], zorder=11)

        legend_labels = []
        for label, size in zip(labels, sizes):
            pct = (size / total) * 100
            legend_labels.append(f'{label}  {size} ({pct:.0f}%)')

        legend = ax.legend(wedges, legend_labels, loc='center left',
                          bbox_to_anchor=(1.05, 0.5), fontsize=9, frameon=True,
                          facecolor=COLORS['bg_dark'], edgecolor=COLORS['border'],
                          labelcolor=COLORS['text_primary'])
        legend.get_frame().set_alpha(0.95)

        ax.set_aspect('equal')
        self.figure.tight_layout(pad=0.5)
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.canvas.draw()


class ScoreGaugeChart(ctk.CTkFrame):
    """Semi-circular arc gauge for displaying the compatibility score."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=12,
            **kwargs
        )

        self._score = 0
        self._grade = 'N/A'
        self._init_ui()

    def _init_ui(self):
        plt.style.use('dark_background')

        self.figure = Figure(figsize=(3.5, 3.5), dpi=100, facecolor=COLORS['bg_medium'])
        self.figure.patch.set_facecolor(COLORS['bg_medium'])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS['bg_medium'], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=8, pady=8)

    def set_score(self, score: float, grade: str = None):
        self._score = max(0, min(100, score or 0))
        self._grade = grade or self._calculate_grade(self._score)
        self._draw_gauge()

    def _calculate_grade(self, score: float) -> str:
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _draw_gauge(self):
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_medium'])
        ax.set_aspect('equal')
        ax.axis('off')

        if self._score >= 90:
            score_color = '#3fb950'
        elif self._score >= 75:
            score_color = '#56d364'
        elif self._score >= 60:
            score_color = '#d29922'
        elif self._score >= 40:
            score_color = '#f0883e'
        else:
            score_color = '#f85149'

        # 270-degree arc from bottom-left to bottom-right
        theta1, theta2 = 225, -45
        track = Wedge((0, 0), 0.9, theta2, theta1, width=0.15,
                     facecolor=COLORS['bg_light'], edgecolor='none', zorder=1)
        ax.add_patch(track)

        if self._score > 0:
            arc_range = 270
            score_angle = (self._score / 100) * arc_range
            score_theta2 = 225 - score_angle

            score_arc = Wedge((0, 0), 0.9, score_theta2, theta1, width=0.15,
                             facecolor=score_color, edgecolor='none', zorder=2)
            ax.add_patch(score_arc)

        center = Circle((0, 0), 0.65, fc=COLORS['bg_medium'], ec='none', zorder=3)
        ax.add_patch(center)

        ax.text(0, 0.08, f'{self._score:.0f}', ha='center', va='center',
               fontsize=36, fontweight='bold', color=score_color, zorder=10)
        ax.text(0.35, 0.15, '%', ha='center', va='center',
               fontsize=14, fontweight='bold', color=score_color, alpha=0.7, zorder=10)
        ax.text(0, -0.22, f'Grade {self._grade}', ha='center', va='center',
               fontsize=12, fontweight='bold', color=COLORS['text_primary'], zorder=10)

        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)

        self.figure.tight_layout(pad=0)
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.canvas.draw()


class SupportStatusChart(ctk.CTkFrame):
    """Pie chart showing supported/partial/unsupported distribution."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=12,
            **kwargs
        )

        self._data = {}
        self._init_ui()

    def _init_ui(self):
        plt.style.use('dark_background')

        self.title_label = ctk.CTkLabel(
            self,
            text="Overall Support Status",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.title_label.pack(anchor="w", padx=16, pady=(12, 4))

        self.figure = Figure(figsize=(4, 3.5), dpi=100, facecolor=COLORS['bg_medium'])
        self.figure.patch.set_facecolor(COLORS['bg_medium'])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS['bg_medium'], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=8, pady=(0, 12))

    def set_data(self, supported: int, partial: int, unsupported: int):
        self._data = {
            'Supported': supported or 0,
            'Partial': partial or 0,
            'Unsupported': unsupported or 0
        }
        self._draw_chart()

    def _draw_chart(self):
        self.figure.clear()

        colors = {
            'Supported': '#3fb950',
            'Partial': '#d29922',
            'Unsupported': '#f85149'
        }

        labels = []
        sizes = []
        chart_colors = []

        for label, size in self._data.items():
            if size > 0:
                labels.append(label)
                sizes.append(size)
                chart_colors.append(colors[label])

        if not sizes:
            ax = self.figure.add_subplot(111)
            ax.set_facecolor(COLORS['bg_medium'])
            ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                   fontsize=12, color=COLORS['text_muted'], transform=ax.transAxes)
            ax.axis('off')
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_medium'])

        total = sum(sizes)

        # Pop out the largest segment slightly
        explode = [0.02] * len(sizes)
        max_idx = sizes.index(max(sizes))
        explode[max_idx] = 0.08

        wedges, texts, autotexts = ax.pie(
            sizes,
            explode=explode,
            colors=chart_colors,
            autopct=lambda p: f'{p:.0f}%' if p > 5 else '',
            startangle=90,
            wedgeprops=dict(edgecolor=COLORS['bg_medium'], linewidth=2),
            textprops={'fontsize': 11, 'fontweight': 'bold', 'color': 'white'}
        )

        for autotext in autotexts:
            autotext.set_path_effects([
                path_effects.withStroke(linewidth=2, foreground=COLORS['bg_dark'])
            ])

        legend_labels = [f'{l}  ({s})' for l, s in zip(labels, sizes)]
        legend = ax.legend(wedges, legend_labels, loc='center left',
                          bbox_to_anchor=(1, 0.5), fontsize=9, frameon=True,
                          facecolor=COLORS['bg_dark'], edgecolor=COLORS['border'],
                          labelcolor=COLORS['text_primary'])
        legend.get_frame().set_alpha(0.95)

        ax.set_aspect('equal')
        self.figure.tight_layout(pad=0.5)
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.canvas.draw()
