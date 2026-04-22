"""Horizontal stats strip -- score, grade, browsers, features at a glance."""

from typing import Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, get_score_color, get_grade_color


class QuickStatsBar(ctk.CTkFrame):
    """Compact horizontal bar: [Score] | [Grade] | [Browsers] | [Features]."""

    def __init__(
        self,
        master,
        score: float = 0.0,
        grade: str = "N/A",
        browsers_count: int = 0,
        features_count: int = 0,
        **kwargs
    ):
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
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['xs'])

        container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.score_stat = self._create_stat(
            container,
            value=f"{self._score:.0f}%",
            label="Score",
            value_color=get_score_color(self._score),
            column=0
        )

        self._create_separator(container, 0)

        self.grade_stat = self._create_stat(
            container,
            value=self._grade,
            label="Grade",
            value_color=get_grade_color(self._grade),
            column=1
        )

        self._create_separator(container, 1)

        self.browsers_stat = self._create_stat(
            container,
            value=str(self._browsers_count),
            label="Browsers",
            value_color=COLORS['accent'],
            column=2
        )

        self._create_separator(container, 2)

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
        """Create a single stat cell. Returns dict with widget refs for updates."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="nsew", padx=SPACING['sm'])

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        value_label = ctk.CTkLabel(
            inner,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=value_color,
        )
        value_label.pack()

        label_label = ctk.CTkLabel(
            inner,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        label_label.pack()

        return {'value_label': value_label, 'label_label': label_label, 'frame': frame}

    def _create_separator(self, parent, after_column: int):
        """Thin vertical line between stat columns."""
        sep = ctk.CTkFrame(
            parent,
            fg_color=COLORS['border'],
            width=1,
        )
        sep.grid(row=0, column=after_column, sticky="nse", padx=(0, 0))

    def set_data(
        self,
        score: float,
        grade: str,
        browsers_count: int,
        features_count: int
    ):
        """Update all four stats at once."""
        self._score = score
        self._grade = grade
        self._browsers_count = browsers_count
        self._features_count = features_count

        self.score_stat['value_label'].configure(
            text=f"{score:.0f}%",
            text_color=get_score_color(score)
        )

        self.grade_stat['value_label'].configure(
            text=grade,
            text_color=get_grade_color(grade)
        )

        self.browsers_stat['value_label'].configure(text=str(browsers_count))

        self.features_stat['value_label'].configure(text=str(features_count))


class StatCard(ctk.CTkFrame):
    """Standalone stat card for flexible layouts."""

    def __init__(
        self,
        master,
        value: str,
        label: str,
        value_color: Optional[str] = None,
        icon: Optional[str] = None,
        **kwargs
    ):
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
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])

        if self._icon:
            icon_label = ctk.CTkLabel(
                container,
                text=self._icon,
                font=ctk.CTkFont(size=20),
                text_color=COLORS['text_muted'],
            )
            icon_label.pack(side="left", padx=(0, SPACING['sm']))

        text_frame = ctk.CTkFrame(container, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        self.value_label = ctk.CTkLabel(
            text_frame,
            text=self._value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self._value_color,
        )
        self.value_label.pack(anchor="w")

        self.label_label = ctk.CTkLabel(
            text_frame,
            text=self._label,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.label_label.pack(anchor="w")

    def set_value(self, value: str, color: Optional[str] = None):
        self._value = value
        self.value_label.configure(text=value)
        if color:
            self._value_color = color
            self.value_label.configure(text_color=color)

    def set_label(self, label: str):
        self._label = label
        self.label_label.configure(text=label)
