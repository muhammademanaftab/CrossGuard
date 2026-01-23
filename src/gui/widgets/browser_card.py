"""
BrowserCard widget for displaying browser compatibility with visual bar chart.
Canvas-based implementation for CustomTkinter with modern charcoal theme.
"""

from typing import List, Optional

import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS, get_score_color, ANIMATION


class StackedBarWidget(ctk.CTkCanvas):
    """Canvas-based horizontal stacked bar showing support breakdown."""

    def __init__(
        self,
        master,
        height: int = 20,
        bg_color: Optional[str] = None,
        **kwargs
    ):
        """Initialize the stacked bar widget.

        Args:
            master: Parent widget
            height: Height of the bar
            bg_color: Background color
            **kwargs: Additional arguments passed to CTkCanvas
        """
        self._bg_color = bg_color or COLORS['bg_medium']
        super().__init__(
            master,
            height=height,
            bg=self._bg_color,
            highlightthickness=0,
            **kwargs
        )

        self._height = height
        self._supported = 0
        self._partial = 0
        self._unsupported = 0
        self._total = 0
        self._animation_progress = 0.0
        self._animation_id = None

        # Bind resize event
        self.bind("<Configure>", self._on_resize)

    def set_values(
        self,
        supported: int,
        partial: int,
        unsupported: int,
        animate: bool = True
    ):
        """Set the bar values.

        Args:
            supported: Number of supported features
            partial: Number of partially supported features
            unsupported: Number of unsupported features
            animate: Whether to animate the fill
        """
        self._supported = supported
        self._partial = partial
        self._unsupported = unsupported
        self._total = supported + partial + unsupported

        if animate and self._total > 0:
            self._animate_fill()
        else:
            self._animation_progress = 1.0
            self._draw()

    def _on_resize(self, event):
        """Handle resize event."""
        self._draw()

    def _draw(self):
        """Draw the stacked bar."""
        self.delete("all")

        width = self.winfo_width()
        height = self._height
        radius = 4

        # Draw background
        self._draw_rounded_rect(0, 0, width, height, radius, COLORS['bg_light'])

        if self._total == 0:
            return

        # Calculate widths with animation
        animated_width = width * self._animation_progress
        supported_width = (self._supported / self._total) * animated_width
        partial_width = (self._partial / self._total) * animated_width
        unsupported_width = (self._unsupported / self._total) * animated_width

        x = 0

        # Draw supported (green)
        if supported_width > 0:
            self.create_rectangle(
                x, 0, x + supported_width, height,
                fill=COLORS['success'],
                outline="",
                tags="supported"
            )
            x += supported_width

        # Draw partial (amber)
        if partial_width > 0:
            self.create_rectangle(
                x, 0, x + partial_width, height,
                fill=COLORS['warning'],
                outline="",
                tags="partial"
            )
            x += partial_width

        # Draw unsupported (red)
        if unsupported_width > 0:
            self.create_rectangle(
                x, 0, x + unsupported_width, height,
                fill=COLORS['danger'],
                outline="",
                tags="unsupported"
            )

    def _draw_rounded_rect(self, x0, y0, x1, y1, radius, fill):
        """Draw a rounded rectangle."""
        self.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")

    def _animate_fill(self, duration: int = None):
        """Animate the bar filling."""
        if duration is None:
            duration = ANIMATION['normal']

        # Cancel any existing animation
        if self._animation_id:
            self.after_cancel(self._animation_id)

        self._animation_progress = 0.0
        steps = max(1, duration // 16)  # ~60fps

        def animate_step(step: int):
            if step >= steps:
                self._animation_progress = 1.0
                self._draw()
                self._animation_id = None
                return

            # Ease out cubic
            t = step / steps
            self._animation_progress = 1 - pow(1 - t, 3)
            self._draw()

            self._animation_id = self.after(16, lambda: animate_step(step + 1))

        animate_step(0)


class BrowserCard(ctk.CTkFrame):
    """Card displaying browser compatibility with mini bar chart.

    Modern compact design with collapsible details section.
    """

    def __init__(
        self,
        master,
        browser_name: str,
        version: str,
        supported: int,
        partial: int,
        unsupported: int,
        compatibility_pct: float,
        unsupported_features: Optional[List[str]] = None,
        partial_features: Optional[List[str]] = None,
        **kwargs
    ):
        """Initialize the browser card.

        Args:
            master: Parent widget
            browser_name: Name of the browser
            version: Browser version
            supported: Number of supported features
            partial: Number of partially supported features
            unsupported: Number of unsupported features
            compatibility_pct: Compatibility percentage
            unsupported_features: List of unsupported feature names
            partial_features: List of partially supported feature names
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

        self.browser_name = browser_name
        self.version = version
        self.supported = supported
        self.partial = partial
        self.unsupported = unsupported
        self.compatibility_pct = compatibility_pct
        self.unsupported_features = unsupported_features or []
        self.partial_features = partial_features or []
        self._details_visible = False

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Configure hover effect
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)

        # Header row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))

        # Browser name and version
        name_label = ctk.CTkLabel(
            header_frame,
            text=f"{self.browser_name.title()} {self.version}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        name_label.pack(side="left")

        # Compatibility percentage
        color = get_score_color(self.compatibility_pct)
        pct_label = ctk.CTkLabel(
            header_frame,
            text=f"{self.compatibility_pct:.0f}%",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color,
        )
        pct_label.pack(side="right")

        # Stacked bar chart
        bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        bar_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

        self.bar_widget = StackedBarWidget(bar_frame, height=12, bg_color=COLORS['bg_medium'])
        self.bar_widget.pack(fill="x", expand=True)
        self.bar_widget.set_values(self.supported, self.partial, self.unsupported)

        # Stats row
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))

        # Compact stats with colored dots
        stats_data = [
            (COLORS['success'], f"{self.supported}"),
            (COLORS['warning'], f"{self.partial}"),
            (COLORS['danger'], f"{self.unsupported}"),
        ]

        for color, count in stats_data:
            dot = ctk.CTkLabel(
                stats_frame,
                text=ICONS['dot'],
                font=ctk.CTkFont(size=10),
                text_color=color,
            )
            dot.pack(side="left")

            count_label = ctk.CTkLabel(
                stats_frame,
                text=count,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary'],
            )
            count_label.pack(side="left", padx=(0, SPACING['md']))

        # Toggle details button (only if there are issues)
        if self.unsupported_features or self.partial_features:
            self.toggle_btn = ctk.CTkButton(
                stats_frame,
                text=f"{ICONS['chevron_right']} Details",
                font=ctk.CTkFont(size=11),
                width=80,
                height=24,
                fg_color="transparent",
                hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_muted'],
                command=self._toggle_details,
            )
            self.toggle_btn.pack(side="right")

        # Details section (hidden by default)
        self.details_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        # Don't pack initially - hidden

        self._build_details_content()

    def _build_details_content(self):
        """Build the details section content."""
        if self.unsupported_features:
            features_text = ', '.join(self.unsupported_features[:6])
            if len(self.unsupported_features) > 6:
                features_text += f" (+{len(self.unsupported_features) - 6} more)"

            unsup_frame = ctk.CTkFrame(
                self.details_frame,
                fg_color=COLORS['danger_muted'],
                corner_radius=6,
            )
            unsup_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['xs']))

            unsup_header = ctk.CTkLabel(
                unsup_frame,
                text=f"{ICONS['error']} Not supported",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['danger'],
            )
            unsup_header.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['sm'], 0))

            unsup_label = ctk.CTkLabel(
                unsup_frame,
                text=features_text,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary'],
                wraplength=450,
                justify="left",
            )
            unsup_label.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], SPACING['sm']))

        if self.partial_features:
            features_text = ', '.join(self.partial_features[:6])
            if len(self.partial_features) > 6:
                features_text += f" (+{len(self.partial_features) - 6} more)"

            part_frame = ctk.CTkFrame(
                self.details_frame,
                fg_color=COLORS['warning_muted'],
                corner_radius=6,
            )
            part_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['xs']))

            part_header = ctk.CTkLabel(
                part_frame,
                text=f"{ICONS['warning']} Partial support",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['warning'],
            )
            part_header.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['sm'], 0))

            part_label = ctk.CTkLabel(
                part_frame,
                text=features_text,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary'],
                wraplength=450,
                justify="left",
            )
            part_label.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], SPACING['sm']))

    def _on_hover_enter(self, event):
        """Handle mouse enter - highlight border."""
        self.configure(border_color=COLORS['accent'])

    def _on_hover_leave(self, event):
        """Handle mouse leave - remove border highlight."""
        self.configure(border_color=COLORS['border'])

    def _toggle_details(self):
        """Toggle the details section visibility."""
        self._details_visible = not self._details_visible

        if self._details_visible:
            self.details_frame.pack(fill="x", pady=(0, SPACING['md']))
            self.toggle_btn.configure(text=f"{ICONS['chevron_down']} Details")
        else:
            self.details_frame.pack_forget()
            self.toggle_btn.configure(text=f"{ICONS['chevron_right']} Details")
