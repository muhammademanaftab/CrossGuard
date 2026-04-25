"""Score card with animated circular progress indicator."""

from typing import Optional

import customtkinter as ctk

from ..theme import COLORS, SPACING, get_score_color, ANIMATION


class CircularProgress(ctk.CTkCanvas):

    def __init__(
        self,
        master,
        size: int = 120,
        line_width: int = 8,
        bg_color: Optional[str] = None,
        **kwargs
    ):
        self._bg_color = bg_color or COLORS['bg_medium']
        super().__init__(
            master,
            width=size,
            height=size,
            bg=self._bg_color,
            highlightthickness=0,
            **kwargs
        )

        self._size = size
        self._line_width = line_width
        self._progress = 0.0
        self._target_progress = 0.0
        self._animation_id = None

        self._draw()

    def _draw(self):
        self.delete("all")

        padding = self._line_width + 2
        x0 = padding
        y0 = padding
        x1 = self._size - padding
        y1 = self._size - padding

        self.create_arc(
            x0, y0, x1, y1,
            start=90,
            extent=-360,
            style="arc",
            outline=COLORS['bg_light'],
            width=self._line_width,
            tags="background"
        )

        if self._progress > 0:
            color = get_score_color(self._progress)
            extent = -(self._progress / 100.0) * 360
            self.create_arc(
                x0, y0, x1, y1,
                start=90,
                extent=extent,
                style="arc",
                outline=color,
                width=self._line_width,
                tags="progress"
            )

    def set_progress(self, value: float, animate: bool = False):
        value = max(0.0, min(100.0, value))

        if animate:
            self._animate_to(value)
        else:
            self._progress = value
            self._draw()

    def _animate_to(self, target: float, duration: int = None):
        if duration is None:
            duration = ANIMATION['progress']

        if self._animation_id:
            self.after_cancel(self._animation_id)

        self._target_progress = target
        start_value = self._progress
        steps = max(1, duration // 16)  # ~60fps

        def animate_step(step: int):
            if step >= steps:
                self._progress = target
                self._draw()
                self._animation_id = None
                return

            t = step / steps
            eased_t = 1 - pow(1 - t, 3)
            self._progress = start_value + (target - start_value) * eased_t
            self._draw()

            self._animation_id = self.after(16, lambda: animate_step(step + 1))

        animate_step(0)

    def get_progress(self) -> float:
        return self._progress

    def set_bg_color(self, color: str):
        self._bg_color = color
        self.configure(bg=color)
        self._draw()


class ScoreCard(ctk.CTkFrame):

    def __init__(
        self,
        master,
        score: float = 0.0,
        grade: str = "N/A",
        label: str = "Compatibility",
        compact: bool = False,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._score = score
        self._grade = grade
        self._label = label
        self._compact = compact

        self._init_ui()

    def _init_ui(self):
        if self._compact:
            self._init_compact_ui()
        else:
            self._init_full_ui()

    def _init_full_ui(self):
        self.grid_columnconfigure(0, weight=1)

        progress_size = 120
        progress_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            width=progress_size,
            height=progress_size,
        )
        progress_container.pack(pady=(SPACING['xl'], SPACING['sm']))

        self.progress_widget = CircularProgress(
            progress_container,
            size=progress_size,
            line_width=8,
            bg_color=COLORS['bg_medium'],
        )
        self.progress_widget.place(relx=0.5, rely=0.5, anchor="center")

        self.grade_label = ctk.CTkLabel(
            progress_container,
            text=self._grade,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['accent'],
        )
        self.grade_label.place(relx=0.5, rely=0.5, anchor="center")

        self.score_label = ctk.CTkLabel(
            self,
            text=f"{self._score:.1f}%",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.score_label.pack(pady=(SPACING['xs'], SPACING['xs']))

        self.label_widget = ctk.CTkLabel(
            self,
            text=self._label,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        )
        self.label_widget.pack(pady=(0, SPACING['xl']))

    def _init_compact_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        progress_size = 60
        progress_container = ctk.CTkFrame(
            container,
            fg_color="transparent",
            width=progress_size,
            height=progress_size,
        )
        progress_container.pack(side="left", padx=(0, SPACING['md']))

        self.progress_widget = CircularProgress(
            progress_container,
            size=progress_size,
            line_width=4,
            bg_color=COLORS['bg_medium'],
        )
        self.progress_widget.place(relx=0.5, rely=0.5, anchor="center")

        self.grade_label = ctk.CTkLabel(
            progress_container,
            text=self._grade,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['accent'],
        )
        self.grade_label.place(relx=0.5, rely=0.5, anchor="center")

        text_frame = ctk.CTkFrame(container, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        self.score_label = ctk.CTkLabel(
            text_frame,
            text=f"{self._score:.1f}%",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w",
        )
        self.score_label.pack(anchor="w")

        self.label_widget = ctk.CTkLabel(
            text_frame,
            text=self._label,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
            anchor="w",
        )
        self.label_widget.pack(anchor="w")

    def set_score(
        self,
        score: float,
        grade: Optional[str] = None,
        animate: bool = True
    ):
        self._score = score
        self.score_label.configure(text=f"{score:.1f}%")

        if grade:
            self._grade = grade
            self.grade_label.configure(text=grade)
            self.grade_label.configure(text_color=get_score_color(score))

        self.progress_widget.set_progress(score, animate=animate)

    def set_label(self, label: str):
        self._label = label
        self.label_widget.configure(text=label)

    def get_score(self) -> float:
        return self._score

    def get_grade(self) -> str:
        return self._grade
