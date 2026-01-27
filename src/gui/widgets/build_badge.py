"""
BuildBadge widget - GitHub CI-style status badge with shield icon.
Shows PASSING/WARNING/FAILING status based on compatibility score.
"""

from typing import Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, FONTS, ANIMATION


class BuildBadge(ctk.CTkFrame):
    """GitHub CI-style build badge showing compatibility status.

    Badge States:
    - PASSING (green, score >= 90%): "All features supported" + check icon
    - WARNING (yellow, score 70-89%): "X features need attention" + warning icon
    - FAILING (red, score < 70%): "X features unsupported" + X icon
    """

    def __init__(
        self,
        master,
        score: float = 0.0,
        total_features: int = 0,
        issues_count: int = 0,
        browsers_count: int = 0,
        **kwargs
    ):
        """Initialize the build badge.

        Args:
            master: Parent widget
            score: Compatibility score percentage (0-100)
            total_features: Total number of features detected
            issues_count: Number of features with issues
            browsers_count: Number of browsers checked
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=12,
            border_width=2,
            **kwargs
        )

        self._score = score
        self._total_features = total_features
        self._issues_count = issues_count
        self._browsers_count = browsers_count
        self._animation_id = None
        self._current_progress = 0.0

        self._init_ui()
        self._update_badge_state()

    def _get_badge_config(self) -> dict:
        """Get badge configuration based on score."""
        if self._score >= 90:
            return {
                'status': 'PASSING',
                'color': COLORS['success'],
                'bg_color': COLORS['success_muted'],
                'icon': '\u2713',  # Check mark
                'message': f'All {self._total_features} features supported in {self._browsers_count} browsers'
                           if self._issues_count == 0
                           else f'{self._total_features - self._issues_count} of {self._total_features} features fully supported'
            }
        elif self._score >= 70:
            return {
                'status': 'WARNING',
                'color': COLORS['warning'],
                'bg_color': COLORS['warning_muted'],
                'icon': '\u26A0',  # Warning sign
                'message': f'{self._issues_count} feature{"s" if self._issues_count != 1 else ""} need attention'
            }
        else:
            return {
                'status': 'FAILING',
                'color': COLORS['danger'],
                'bg_color': COLORS['danger_muted'],
                'icon': '\u2715',  # X mark
                'message': f'{self._issues_count} feature{"s" if self._issues_count != 1 else ""} unsupported'
            }

    def _init_ui(self):
        """Initialize the user interface."""
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])

        # Top section: Badge with icon and status
        badge_section = ctk.CTkFrame(container, fg_color="transparent")
        badge_section.pack(fill="x")

        # Shield icon placeholder (will be styled as badge)
        self.shield_frame = ctk.CTkFrame(
            badge_section,
            fg_color=COLORS['success_muted'],
            corner_radius=8,
            height=50,
        )
        self.shield_frame.pack(side="left", padx=(0, SPACING['lg']))
        self.shield_frame.pack_propagate(False)

        # Shield inner content
        shield_inner = ctk.CTkFrame(self.shield_frame, fg_color="transparent")
        shield_inner.pack(fill="both", expand=True, padx=SPACING['md'])

        self.shield_icon = ctk.CTkLabel(
            shield_inner,
            text="\u2713",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['success'],
        )
        self.shield_icon.pack(side="left", padx=(0, SPACING['xs']))

        # Badge text container
        badge_text = ctk.CTkFrame(badge_section, fg_color="transparent")
        badge_text.pack(side="left", fill="x", expand=True)

        # Status line: "COMPATIBILITY: PASSING"
        status_line = ctk.CTkFrame(badge_text, fg_color="transparent")
        status_line.pack(fill="x")

        self.compat_label = ctk.CTkLabel(
            status_line,
            text="COMPATIBILITY:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_muted'],
        )
        self.compat_label.pack(side="left")

        self.status_label = ctk.CTkLabel(
            status_line,
            text="PASSING",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['success'],
        )
        self.status_label.pack(side="left", padx=(SPACING['xs'], 0))

        # Score percentage on the right
        self.score_label = ctk.CTkLabel(
            status_line,
            text="98%",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['success'],
        )
        self.score_label.pack(side="right")

        # Progress bar section
        progress_section = ctk.CTkFrame(container, fg_color="transparent")
        progress_section.pack(fill="x", pady=(SPACING['md'], SPACING['sm']))

        # Progress bar background
        self.progress_bg = ctk.CTkFrame(
            progress_section,
            fg_color=COLORS['bg_light'],
            corner_radius=6,
            height=16,
        )
        self.progress_bg.pack(fill="x")
        self.progress_bg.pack_propagate(False)

        # Progress bar fill
        self.progress_fill = ctk.CTkFrame(
            self.progress_bg,
            fg_color=COLORS['success'],
            corner_radius=6,
            height=16,
        )
        self.progress_fill.place(relx=0, rely=0, relheight=1, relwidth=0)

        # Message line
        self.message_label = ctk.CTkLabel(
            container,
            text="All 12 features supported in 4 browsers",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary'],
        )
        self.message_label.pack(anchor="w", pady=(SPACING['sm'], 0))

    def _update_badge_state(self):
        """Update badge appearance based on current score."""
        config = self._get_badge_config()

        # Update shield
        self.shield_frame.configure(fg_color=config['bg_color'])
        self.shield_icon.configure(text=config['icon'], text_color=config['color'])

        # Update status text
        self.status_label.configure(text=config['status'], text_color=config['color'])

        # Update score
        self.score_label.configure(
            text=f"{self._score:.0f}%",
            text_color=config['color']
        )

        # Update progress bar color
        self.progress_fill.configure(fg_color=config['color'])

        # Update message
        self.message_label.configure(text=config['message'])

        # Update border color
        self.configure(border_color=config['color'])

    def set_data(
        self,
        score: float,
        total_features: int,
        issues_count: int,
        browsers_count: int,
        animate: bool = True
    ):
        """Update the badge with new data.

        Args:
            score: Compatibility score percentage (0-100)
            total_features: Total number of features detected
            issues_count: Number of features with issues
            browsers_count: Number of browsers checked
            animate: Whether to animate the progress bar
        """
        self._score = score
        self._total_features = total_features
        self._issues_count = issues_count
        self._browsers_count = browsers_count

        self._update_badge_state()

        if animate:
            self._animate_progress()
        else:
            self.progress_fill.place(relx=0, rely=0, relheight=1, relwidth=score/100)

    def _animate_progress(self, duration: int = None):
        """Animate the progress bar filling."""
        if duration is None:
            duration = ANIMATION['progress']

        # Cancel any existing animation
        if self._animation_id:
            self.after_cancel(self._animation_id)

        start_progress = self._current_progress
        target_progress = self._score / 100
        steps = max(1, duration // 16)  # ~60fps

        def animate_step(step: int):
            if step >= steps:
                self._current_progress = target_progress
                self.progress_fill.place(relx=0, rely=0, relheight=1, relwidth=target_progress)
                self._animation_id = None
                return

            # Ease out cubic
            t = step / steps
            eased_t = 1 - pow(1 - t, 3)
            self._current_progress = start_progress + (target_progress - start_progress) * eased_t
            self.progress_fill.place(relx=0, rely=0, relheight=1, relwidth=self._current_progress)

            self._animation_id = self.after(16, lambda: animate_step(step + 1))

        animate_step(0)
