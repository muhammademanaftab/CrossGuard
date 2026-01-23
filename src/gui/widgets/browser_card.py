"""
BrowserCard widget for displaying browser compatibility with visual bar chart.
Canvas-based implementation for CustomTkinter.
"""

from typing import List, Optional

import customtkinter as ctk

from ..theme import COLORS, get_score_color, ANIMATION


class StackedBarWidget(ctk.CTkCanvas):
    """Canvas-based horizontal stacked bar showing support breakdown."""

    def __init__(
        self,
        master,
        height: int = 20,
        **kwargs
    ):
        """Initialize the stacked bar widget.

        Args:
            master: Parent widget
            height: Height of the bar
            **kwargs: Additional arguments passed to CTkCanvas
        """
        super().__init__(
            master,
            height=height,
            bg=COLORS['bg_medium'],
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
        self.create_rectangle(
            0, 0, width, height,
            fill=COLORS['bg_light'],
            outline="",
            tags="background"
        )

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

        # Draw partial (orange)
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

    def _animate_fill(self, duration: int = None):
        """Animate the bar filling.

        Args:
            duration: Animation duration in milliseconds
        """
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
    """Card displaying browser compatibility with mini bar chart."""

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
        header_frame.pack(fill="x", padx=12, pady=(10, 8))

        # Browser name and version
        name_label = ctk.CTkLabel(
            header_frame,
            text=f"{self.browser_name.upper()} {self.version}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        name_label.pack(side="left")

        # Compatibility percentage
        color = get_score_color(self.compatibility_pct)
        pct_label = ctk.CTkLabel(
            header_frame,
            text=f"{self.compatibility_pct:.1f}%",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color,
        )
        pct_label.pack(side="right")

        # Stacked bar chart
        bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        bar_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.bar_widget = StackedBarWidget(bar_frame, height=16)
        self.bar_widget.pack(fill="x", expand=True)
        self.bar_widget.set_values(self.supported, self.partial, self.unsupported)

        # Stats row
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=12, pady=(0, 10))

        # Supported count
        supported_label = ctk.CTkLabel(
            stats_frame,
            text=f"Supported: {self.supported}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['success'],
        )
        supported_label.pack(side="left", padx=(0, 16))

        # Partial count
        partial_label = ctk.CTkLabel(
            stats_frame,
            text=f"Partial: {self.partial}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['warning'],
        )
        partial_label.pack(side="left", padx=(0, 16))

        # Unsupported count
        unsupported_label = ctk.CTkLabel(
            stats_frame,
            text=f"Unsupported: {self.unsupported}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['danger'],
        )
        unsupported_label.pack(side="left")

        # Toggle details button (only if there are issues)
        if self.unsupported_features or self.partial_features:
            self.toggle_btn = ctk.CTkButton(
                stats_frame,
                text="Show Details",
                font=ctk.CTkFont(size=11),
                width=100,
                height=28,
                fg_color="transparent",
                border_width=1,
                border_color=COLORS['border'],
                text_color=COLORS['text_muted'],
                hover_color=COLORS['hover_bg'],
                command=self._toggle_details,
            )
            self.toggle_btn.pack(side="right")

        # Details section (hidden by default)
        self.details_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        # Don't pack initially - hidden

        if self.unsupported_features:
            features_text = ', '.join(self.unsupported_features[:8])
            if len(self.unsupported_features) > 8:
                features_text += f" (+{len(self.unsupported_features) - 8} more)"

            unsup_frame = ctk.CTkFrame(
                self.details_frame,
                fg_color="#3d2020",  # Dark red background
                corner_radius=4,
            )
            unsup_frame.pack(fill="x", padx=12, pady=(0, 4))

            unsup_label = ctk.CTkLabel(
                unsup_frame,
                text=f"Not supported: {features_text}",
                font=ctk.CTkFont(size=11),
                text_color="#ff8080",
                wraplength=500,
                justify="left",
            )
            unsup_label.pack(padx=8, pady=6, anchor="w")

        if self.partial_features:
            features_text = ', '.join(self.partial_features[:8])
            if len(self.partial_features) > 8:
                features_text += f" (+{len(self.partial_features) - 8} more)"

            part_frame = ctk.CTkFrame(
                self.details_frame,
                fg_color="#3d3020",  # Dark orange background
                corner_radius=4,
            )
            part_frame.pack(fill="x", padx=12, pady=(0, 4))

            part_label = ctk.CTkLabel(
                part_frame,
                text=f"Partial support: {features_text}",
                font=ctk.CTkFont(size=11),
                text_color="#ffb366",
                wraplength=500,
                justify="left",
            )
            part_label.pack(padx=8, pady=6, anchor="w")

    def _on_hover_enter(self, event):
        """Handle mouse enter - highlight border."""
        self.configure(border_width=1, border_color=COLORS['primary'])

    def _on_hover_leave(self, event):
        """Handle mouse leave - remove border highlight."""
        self.configure(border_width=0)

    def _toggle_details(self):
        """Toggle the details section visibility."""
        self._details_visible = not self._details_visible

        if self._details_visible:
            self.details_frame.pack(fill="x", pady=(0, 10))
            self.toggle_btn.configure(text="Hide Details")
        else:
            self.details_frame.pack_forget()
            self.toggle_btn.configure(text="Show Details")
