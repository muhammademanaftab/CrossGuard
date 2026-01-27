"""
QuickStatsBar widget - Horizontal metrics strip showing key stats.
Displays score, grade, browsers, and features in a compact format.
"""

from typing import Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, get_score_color, get_grade_color


class QuickStatsBar(ctk.CTkFrame):
    """Horizontal stats bar showing key metrics.

    Displays: [Score] | [Grade] | [Browsers] | [Features]
    """

    def __init__(
        self,
        master,
        score: float = 0.0,
        grade: str = "N/A",
        browsers_count: int = 0,
        features_count: int = 0,
        **kwargs
    ):
        """Initialize the quick stats bar.

        Args:
            master: Parent widget
            score: Compatibility score percentage
            grade: Letter grade (A-F)
            browsers_count: Number of browsers checked
            features_count: Number of features detected
            **kwargs: Additional arguments passed to CTkFrame
        """
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

        self._score = score
        self._grade = grade
        self._browsers_count = browsers_count
        self._features_count = features_count

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Container for horizontal layout
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['xs'])

        # Configure equal columns
        container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Stat 1: Score
        self.score_stat = self._create_stat(
            container,
            value=f"{self._score:.0f}%",
            label="Score",
            value_color=get_score_color(self._score),
            column=0
        )

        # Separator
        self._create_separator(container, 0)

        # Stat 2: Grade
        self.grade_stat = self._create_stat(
            container,
            value=self._grade,
            label="Grade",
            value_color=get_grade_color(self._grade),
            column=1
        )

        # Separator
        self._create_separator(container, 1)

        # Stat 3: Browsers
        self.browsers_stat = self._create_stat(
            container,
            value=str(self._browsers_count),
            label="Browsers",
            value_color=COLORS['accent'],
            column=2
        )

        # Separator
        self._create_separator(container, 2)

        # Stat 4: Features
        self.features_stat = self._create_stat(
            container,
            value=str(self._features_count),
            label="Features",
            value_color=COLORS['accent'],
            column=3
        )

    def _create_stat(
        self,
        parent,
        value: str,
        label: str,
        value_color: str,
        column: int
    ) -> dict:
        """Create a single stat display.

        Returns dict with 'value_label' and 'label_label' for updates.
        """
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="nsew", padx=SPACING['sm'])

        # Center content vertically
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        # Value (large)
        value_label = ctk.CTkLabel(
            inner,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=value_color,
        )
        value_label.pack()

        # Label (small, muted)
        label_label = ctk.CTkLabel(
            inner,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        label_label.pack()

        return {'value_label': value_label, 'label_label': label_label, 'frame': frame}

    def _create_separator(self, parent, after_column: int):
        """Create a vertical separator after the specified column."""
        # We use a thin frame as separator
        # Position it between columns using grid
        sep = ctk.CTkFrame(
            parent,
            fg_color=COLORS['border'],
            width=1,
        )
        # Place separator at right edge of column
        sep.grid(row=0, column=after_column, sticky="nse", padx=(0, 0))

    def set_data(
        self,
        score: float,
        grade: str,
        browsers_count: int,
        features_count: int
    ):
        """Update all stats.

        Args:
            score: Compatibility score percentage
            grade: Letter grade (A-F)
            browsers_count: Number of browsers checked
            features_count: Number of features detected
        """
        self._score = score
        self._grade = grade
        self._browsers_count = browsers_count
        self._features_count = features_count

        # Update score
        self.score_stat['value_label'].configure(
            text=f"{score:.0f}%",
            text_color=get_score_color(score)
        )

        # Update grade
        self.grade_stat['value_label'].configure(
            text=grade,
            text_color=get_grade_color(grade)
        )

        # Update browsers
        self.browsers_stat['value_label'].configure(text=str(browsers_count))

        # Update features
        self.features_stat['value_label'].configure(text=str(features_count))


class StatCard(ctk.CTkFrame):
    """Individual stat card for flexible layouts."""

    def __init__(
        self,
        master,
        value: str,
        label: str,
        value_color: Optional[str] = None,
        icon: Optional[str] = None,
        **kwargs
    ):
        """Initialize the stat card.

        Args:
            master: Parent widget
            value: The main value to display
            label: Description label
            value_color: Color for the value text
            icon: Optional icon character
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._value = value
        self._label = label
        self._value_color = value_color or COLORS['accent']
        self._icon = icon

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])

        # Icon (if provided)
        if self._icon:
            icon_label = ctk.CTkLabel(
                container,
                text=self._icon,
                font=ctk.CTkFont(size=20),
                text_color=COLORS['text_muted'],
            )
            icon_label.pack(side="left", padx=(0, SPACING['sm']))

        # Text content
        text_frame = ctk.CTkFrame(container, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        # Value
        self.value_label = ctk.CTkLabel(
            text_frame,
            text=self._value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self._value_color,
        )
        self.value_label.pack(anchor="w")

        # Label
        self.label_label = ctk.CTkLabel(
            text_frame,
            text=self._label,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.label_label.pack(anchor="w")

    def set_value(self, value: str, color: Optional[str] = None):
        """Update the value."""
        self._value = value
        self.value_label.configure(text=value)
        if color:
            self._value_color = color
            self.value_label.configure(text_color=color)

    def set_label(self, label: str):
        """Update the label."""
        self._label = label
        self.label_label.configure(text=label)
