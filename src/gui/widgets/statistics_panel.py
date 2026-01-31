"""
Statistics panel widget for displaying aggregated analysis insights.

Shows:
- Total analyses count
- Average, best, and worst scores
- Top problematic features
- Most analyzed files
"""

from typing import Dict, Any, List, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS, get_score_color


class StatisticsPanel(ctk.CTkFrame):
    """Panel widget for displaying comprehensive statistics.

    Shows aggregated insights from all analyses including
    counts, scores, trends, and top issues.
    """

    def __init__(self, master, **kwargs):
        """Initialize the statistics panel.

        Args:
            master: Parent widget
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._stats: Dict[str, Any] = {}
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['md'])

        # Statistics icon and title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")

        icon_label = ctk.CTkLabel(
            title_frame,
            text="\u2261",  # Statistics bars icon
            font=ctk.CTkFont(size=18),
            text_color=COLORS['accent'],
        )
        icon_label.pack(side="left")

        title_label = ctk.CTkLabel(
            title_frame,
            text="Your Statistics",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title_label.pack(side="left", padx=(SPACING['sm'], 0))

        # Main stats container
        self._stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self._stats_container.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))

        # Key metrics row
        self._metrics_frame = ctk.CTkFrame(self._stats_container, fg_color="transparent")
        self._metrics_frame.pack(fill="x", pady=(0, SPACING['md']))

        # Create metric placeholders
        self._total_label = self._create_metric(self._metrics_frame, "Total Analyses", "0")
        self._avg_label = self._create_metric(self._metrics_frame, "Average Score", "0%")
        self._best_label = self._create_metric(self._metrics_frame, "Best Score", "0%")

        # Separator
        separator = ctk.CTkFrame(
            self._stats_container,
            height=1,
            fg_color=COLORS['border'],
        )
        separator.pack(fill="x", pady=SPACING['sm'])

        # Problematic features section
        self._problems_frame = ctk.CTkFrame(self._stats_container, fg_color="transparent")
        self._problems_frame.pack(fill="x", pady=(SPACING['sm'], 0))

        warning_icon = ICONS.get('warning', '\u26A0')
        problems_header = ctk.CTkLabel(
            self._problems_frame,
            text=f"{warning_icon} Top Problematic Features:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary'],
        )
        problems_header.pack(anchor="w")

        self._problems_list = ctk.CTkFrame(self._problems_frame, fg_color="transparent")
        self._problems_list.pack(fill="x", pady=(SPACING['xs'], 0))

        # Initial empty state
        self._empty_problems = ctk.CTkLabel(
            self._problems_list,
            text="No issues detected yet",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_disabled'],
        )
        self._empty_problems.pack(anchor="w")

    def _create_metric(self, parent, label: str, value: str) -> ctk.CTkLabel:
        """Create a metric display widget.

        Args:
            parent: Parent frame
            label: Metric label
            value: Initial value

        Returns:
            The value label widget (for updating)
        """
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", expand=True)

        # Value (large)
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        value_label.pack()

        # Label (small, below)
        label_widget = ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        label_widget.pack()

        return value_label

    def set_statistics(self, stats: Dict[str, Any]):
        """Update the panel with new statistics.

        Args:
            stats: Statistics dictionary from get_statistics()
        """
        self._stats = stats

        # Update key metrics
        total = stats.get('total_analyses', 0)
        avg = stats.get('average_score', 0)
        best = stats.get('best_score', 0)

        self._total_label.configure(text=str(total))
        self._avg_label.configure(text=f"{avg:.0f}%")
        self._best_label.configure(text=f"{best:.0f}%")

        # Color the scores
        avg_color = get_score_color(avg) if avg > 0 else COLORS['text_primary']
        best_color = get_score_color(best) if best > 0 else COLORS['text_primary']
        self._avg_label.configure(text_color=avg_color)
        self._best_label.configure(text_color=best_color)

        # Update problematic features list
        self._update_problems_list(stats.get('top_problematic_features', []))

    def _update_problems_list(self, features: List[Dict[str, Any]]):
        """Update the problematic features list.

        Args:
            features: List of feature dicts with name and fail_count
        """
        # Clear existing items
        for widget in self._problems_list.winfo_children():
            widget.destroy()

        if not features:
            empty_label = ctk.CTkLabel(
                self._problems_list,
                text="No issues detected yet",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_disabled'],
            )
            empty_label.pack(anchor="w")
            return

        # Add feature items
        for i, feature in enumerate(features[:5], 1):
            name = feature.get('feature_name', feature.get('feature_id', 'Unknown'))
            count = feature.get('fail_count', 0)
            category = feature.get('category', '').upper()

            item_frame = ctk.CTkFrame(self._problems_list, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)

            # Rank number
            rank_label = ctk.CTkLabel(
                item_frame,
                text=f"{i}.",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted'],
                width=20,
            )
            rank_label.pack(side="left")

            # Feature name
            name_label = ctk.CTkLabel(
                item_frame,
                text=name,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary'],
            )
            name_label.pack(side="left")

            # Failure count
            count_label = ctk.CTkLabel(
                item_frame,
                text=f"({count} failures)",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['danger'],
            )
            count_label.pack(side="right")


class CompactStatsBar(ctk.CTkFrame):
    """Compact statistics bar for inline display.

    Shows key stats in a single horizontal row.
    """

    def __init__(self, master, **kwargs):
        """Initialize the compact stats bar.

        Args:
            master: Parent widget
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=6,
            height=40,
            **kwargs
        )

        self.pack_propagate(False)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['md'])

        # Icon
        icon_label = ctk.CTkLabel(
            container,
            text="\u2261",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['accent'],
        )
        icon_label.pack(side="left")

        # Stats text
        self._stats_label = ctk.CTkLabel(
            container,
            text="Total: 0 analyses | Avg Score: 0% | Best: 0%",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
        )
        self._stats_label.pack(side="left", padx=(SPACING['sm'], 0))

    def set_statistics(self, stats: Dict[str, Any]):
        """Update the stats display.

        Args:
            stats: Statistics dictionary
        """
        total = stats.get('total_analyses', 0)
        avg = stats.get('average_score', 0)
        best = stats.get('best_score', 0)

        text = f"Total: {total} analyses | Avg Score: {avg:.0f}% | Best: {best:.0f}%"
        self._stats_label.configure(text=text)
