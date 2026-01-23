"""
Chart widgets for data visualization using matplotlib with Tkinter backend.
Modern charcoal theme with cyan accents.
"""

from typing import Dict

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from ..theme import COLORS


class CompatibilityBarChart(ctk.CTkFrame):
    """Horizontal bar chart comparing browser compatibility.

    Modern design with charcoal background and semantic colors.
    """

    def __init__(self, master, **kwargs):
        """Initialize the compatibility bar chart.

        Args:
            master: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            **kwargs
        )

        self._browsers_data = {}
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Use dark background style for matplotlib
        plt.style.use('dark_background')

        # Create matplotlib figure with dark theme colors
        self.figure = Figure(figsize=(6, 3), dpi=100, facecolor=COLORS['bg_medium'])
        self.figure.patch.set_facecolor(COLORS['bg_medium'])

        # Create canvas and embed in frame
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS['bg_medium'], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=5, pady=5)

    def set_data(self, browsers_data: Dict):
        """Set the browser compatibility data.

        Args:
            browsers_data: Dictionary with browser data
                {
                    'browser_name': {
                        'supported': int,
                        'partial': int,
                        'unsupported': int,
                        'compatibility_percentage': float
                    }
                }
        """
        self._browsers_data = browsers_data
        self._draw_chart()

    def _draw_chart(self):
        """Draw the horizontal stacked bar chart."""
        self.figure.clear()

        if not self._browsers_data:
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_medium'])

        browsers = list(self._browsers_data.keys())
        supported = []
        partial = []
        unsupported = []

        for browser in browsers:
            data = self._browsers_data[browser]
            supported.append(data.get('supported', 0))
            partial.append(data.get('partial', 0))
            unsupported.append(data.get('unsupported', 0))

        y_pos = range(len(browsers))

        # Create stacked horizontal bars with theme colors
        bars1 = ax.barh(
            y_pos, supported,
            color=COLORS['success'],
            label='Supported',
            height=0.6
        )
        bars2 = ax.barh(
            y_pos, partial,
            left=supported,
            color=COLORS['warning'],
            label='Partial',
            height=0.6
        )
        bars3 = ax.barh(
            y_pos, unsupported,
            left=[s + p for s, p in zip(supported, partial)],
            color=COLORS['danger'],
            label='Unsupported',
            height=0.6
        )

        # Customize appearance for dark theme
        ax.set_yticks(y_pos)
        ax.set_yticklabels(
            [b.title() for b in browsers],
            fontsize=10,
            color=COLORS['text_primary']
        )
        ax.set_xlabel('Features', fontsize=10, color=COLORS['text_secondary'])
        ax.tick_params(axis='x', colors=COLORS['text_muted'])

        # Legend with dark theme styling
        legend = ax.legend(
            loc='upper right',
            fontsize=8,
            facecolor=COLORS['bg_light'],
            edgecolor=COLORS['border'],
            labelcolor=COLORS['text_primary']
        )

        # Add percentage labels on the right
        for i, browser in enumerate(browsers):
            pct = self._browsers_data[browser].get('compatibility_percentage', 0)
            total = supported[i] + partial[i] + unsupported[i]
            ax.text(
                total + 1, i, f'{pct:.0f}%',
                va='center', ha='left',
                fontsize=9, fontweight='bold',
                color=COLORS['text_primary']
            )

        # Style the chart for dark theme
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(COLORS['border'])
        ax.spines['left'].set_color(COLORS['border'])

        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()


class FeatureDistributionChart(ctk.CTkFrame):
    """Donut chart showing feature type distribution.

    Modern design with file type colors (HTML, CSS, JS).
    """

    def __init__(self, master, **kwargs):
        """Initialize the feature distribution chart.

        Args:
            master: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            **kwargs
        )

        self._data = {}
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Use dark background style
        plt.style.use('dark_background')

        # Create matplotlib figure with dark theme
        self.figure = Figure(figsize=(4, 4), dpi=100, facecolor=COLORS['bg_medium'])
        self.figure.patch.set_facecolor(COLORS['bg_medium'])

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=COLORS['bg_medium'], highlightthickness=0)
        canvas_widget.pack(fill="both", expand=True, padx=5, pady=5)

    def set_data(self, html_count: int, css_count: int, js_count: int):
        """Set the feature distribution data.

        Args:
            html_count: Number of HTML features
            css_count: Number of CSS features
            js_count: Number of JavaScript features
        """
        self._data = {
            'HTML': html_count,
            'CSS': css_count,
            'JavaScript': js_count
        }
        self._draw_chart()

    def _draw_chart(self):
        """Draw the donut chart."""
        self.figure.clear()

        # Filter out zero values
        labels = []
        sizes = []
        # Use file type colors from theme
        colors = [COLORS['html_color'], COLORS['css_color'], COLORS['js_color']]
        filtered_colors = []

        for i, (label, size) in enumerate(self._data.items()):
            if size > 0:
                labels.append(f'{label}\n({size})')
                sizes.append(size)
                filtered_colors.append(colors[i])

        if not sizes:
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS['bg_medium'])

        # Create donut chart
        wedges, texts = ax.pie(
            sizes,
            colors=filtered_colors,
            startangle=90,
            wedgeprops=dict(width=0.5, edgecolor=COLORS['bg_medium'])
        )

        # Add legend with dark theme styling
        legend = ax.legend(
            wedges, labels,
            loc='center',
            fontsize=9,
            frameon=False,
            labelcolor=COLORS['text_primary']
        )

        ax.set_aspect('equal')
        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()
