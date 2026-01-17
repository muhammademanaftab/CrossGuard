"""
Chart widgets for data visualization using matplotlib.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from typing import Dict


class CompatibilityBarChart(QWidget):
    """Horizontal bar chart comparing browser compatibility."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._browsers_data = {}
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create matplotlib figure
        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.canvas.setMinimumHeight(180)

        layout.addWidget(self.canvas)

    def set_data(self, browsers_data: Dict):
        """
        Set the browser compatibility data.

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
            return

        ax = self.figure.add_subplot(111)

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

        # Create stacked horizontal bars
        bars1 = ax.barh(y_pos, supported, color='#4CAF50', label='Supported', height=0.6)
        bars2 = ax.barh(y_pos, partial, left=supported, color='#FF9800', label='Partial', height=0.6)
        bars3 = ax.barh(y_pos, unsupported,
                        left=[s + p for s, p in zip(supported, partial)],
                        color='#F44336', label='Unsupported', height=0.6)

        # Customize appearance
        ax.set_yticks(y_pos)
        ax.set_yticklabels([b.capitalize() for b in browsers])
        ax.set_xlabel('Features', fontsize=10)
        ax.legend(loc='upper right', fontsize=8)

        # Add percentage labels on the right
        for i, browser in enumerate(browsers):
            pct = self._browsers_data[browser].get('compatibility_percentage', 0)
            total = supported[i] + partial[i] + unsupported[i]
            ax.text(total + 1, i, f'{pct:.0f}%',
                    va='center', ha='left', fontsize=9, fontweight='bold',
                    color='#333')

        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='both', which='major', labelsize=9)

        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()


class FeatureDistributionChart(QWidget):
    """Donut chart showing feature type distribution."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = {}
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create matplotlib figure
        self.figure = Figure(figsize=(4, 4), dpi=100)
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.canvas.setFixedSize(200, 200)

        layout.addWidget(self.canvas)

    def set_data(self, html_count: int, css_count: int, js_count: int):
        """
        Set the feature distribution data.

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
        colors = ['#E34C26', '#264DE4', '#F7DF1E']  # HTML red, CSS blue, JS yellow
        filtered_colors = []

        for i, (label, size) in enumerate(self._data.items()):
            if size > 0:
                labels.append(f'{label}\n({size})')
                sizes.append(size)
                filtered_colors.append(colors[i])

        if not sizes:
            return

        ax = self.figure.add_subplot(111)

        # Create donut chart
        wedges, texts = ax.pie(sizes, colors=filtered_colors, startangle=90,
                               wedgeprops=dict(width=0.5, edgecolor='white'))

        # Add legend
        ax.legend(wedges, labels, loc='center', fontsize=8, frameon=False)

        ax.set_aspect('equal')
        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()
