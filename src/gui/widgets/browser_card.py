"""
BrowserCard widget for displaying browser compatibility with visual bar chart.
Canvas-based implementation for CustomTkinter with modern charcoal theme.
Includes version range display like Can I Use website.
"""

from typing import List, Optional, Dict

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


class VersionRangeWidget(ctk.CTkFrame):
    """Widget showing version ranges like Can I Use for a single feature."""

    # Status colors
    STATUS_COLORS = {
        'y': COLORS['success'],      # Green - Supported
        'n': COLORS['danger'],       # Red - Not supported
        'a': COLORS['warning'],      # Yellow - Partial
        'p': '#9B59B6',              # Purple - Polyfill
        'x': '#E67E22',              # Orange - Prefix required
        'u': COLORS['text_muted'],   # Gray - Unknown
        'd': '#7F8C8D',              # Gray - Disabled by default
    }

    def __init__(
        self,
        master,
        feature_id: str,
        feature_name: str,
        ranges: List[Dict],
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._feature_id = feature_id
        self._feature_name = feature_name
        self._ranges = ranges

        self._init_ui()

    def _init_ui(self):
        """Build the UI."""
        # Feature name
        name_label = ctk.CTkLabel(
            self,
            text=self._feature_name,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            width=140,
            anchor="w",
        )
        name_label.pack(side="left", padx=(0, SPACING['sm']))

        # Version range boxes
        ranges_frame = ctk.CTkFrame(self, fg_color="transparent")
        ranges_frame.pack(side="left", fill="x", expand=True)

        for r in self._ranges:
            self._create_range_box(ranges_frame, r)

    def _create_range_box(self, parent, range_data: Dict):
        """Create a colored version range box."""
        status = range_data.get('status', 'u')
        color = self.STATUS_COLORS.get(status, COLORS['text_muted'])

        start = range_data.get('start', '?')
        end = range_data.get('end', '?')

        if start == end:
            version_text = str(start)
        else:
            version_text = f"{start}-{end}"

        box = ctk.CTkLabel(
            parent,
            text=version_text,
            font=ctk.CTkFont(size=9),
            fg_color=color,
            corner_radius=3,
            text_color="white",
            height=20,
        )
        box.pack(side="left", padx=1, pady=1)


class BrowserCard(ctk.CTkFrame):
    """Card displaying browser compatibility with mini bar chart.

    Modern compact design with collapsible details section.
    Shows version ranges like Can I Use when expanded.
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
        supported_features: Optional[List[str]] = None,
        all_features: Optional[List[str]] = None,
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
            unsupported_features: List of unsupported feature IDs
            partial_features: List of partially supported feature IDs
            supported_features: List of supported feature IDs
            all_features: List of all detected feature IDs (for version ranges)
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
        self.supported_features = supported_features or []
        self.all_features = all_features or []
        self._details_visible = False
        self._version_ranges_loaded = False

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

        # Toggle details button (only if there are features)
        if self.unsupported_features or self.partial_features or self.all_features:
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
        # Issues section (unsupported/partial)
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

        # Version Ranges Section (like Can I Use)
        self.version_ranges_frame = ctk.CTkFrame(
            self.details_frame,
            fg_color=COLORS['bg_light'],
            corner_radius=6,
        )
        self.version_ranges_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['xs'], 0))

        # Header for version ranges
        vr_header = ctk.CTkFrame(self.version_ranges_frame, fg_color="transparent")
        vr_header.pack(fill="x", padx=SPACING['sm'], pady=(SPACING['sm'], SPACING['xs']))

        ctk.CTkLabel(
            vr_header,
            text="📊 Version Support History",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        # Legend
        legend_frame = ctk.CTkFrame(vr_header, fg_color="transparent")
        legend_frame.pack(side="right")

        for color, text in [(COLORS['success'], 'Yes'), (COLORS['warning'], 'Partial'), (COLORS['danger'], 'No')]:
            ctk.CTkLabel(
                legend_frame,
                text="●",
                font=ctk.CTkFont(size=8),
                text_color=color,
            ).pack(side="left", padx=(4, 1))
            ctk.CTkLabel(
                legend_frame,
                text=text,
                font=ctk.CTkFont(size=9),
                text_color=COLORS['text_muted'],
            ).pack(side="left")

        # Content frame for version ranges (will be populated when expanded)
        self.vr_content = ctk.CTkFrame(self.version_ranges_frame, fg_color="transparent")
        self.vr_content.pack(fill="x", padx=SPACING['sm'], pady=(0, SPACING['sm']))

        # Placeholder
        self._vr_placeholder = ctk.CTkLabel(
            self.vr_content,
            text="Loading version ranges...",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted'],
        )
        self._vr_placeholder.pack(anchor="w")

    def _load_version_ranges(self):
        """Load and display version ranges for detected features."""
        if self._version_ranges_loaded:
            return

        try:
            from src.analyzer.version_ranges import get_version_ranges
            from src.utils.feature_names import get_feature_name

            # Clear placeholder
            self._vr_placeholder.destroy()

            # Map browser name to Can I Use browser ID
            browser_map = {
                'chrome': 'chrome',
                'firefox': 'firefox',
                'safari': 'safari',
                'edge': 'edge',
                'opera': 'opera',
                'ie': 'ie',
                'internet explorer': 'ie',
            }
            browser_id = browser_map.get(self.browser_name.lower(), self.browser_name.lower())

            # Get features to show (combine all)
            features_to_show = list(set(
                self.unsupported_features +
                self.partial_features +
                self.supported_features +
                self.all_features
            ))  # Show all features (removed limit)

            if not features_to_show:
                ctk.CTkLabel(
                    self.vr_content,
                    text="No feature data available",
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS['text_muted'],
                ).pack(anchor="w")
                return

            # Create version range display for each feature
            for feature_id in features_to_show:
                ranges = get_version_ranges(feature_id, browser_id)
                if ranges:
                    feature_name = get_feature_name(feature_id)
                    widget = VersionRangeWidget(
                        self.vr_content,
                        feature_id=feature_id,
                        feature_name=feature_name[:20] + "..." if len(feature_name) > 20 else feature_name,
                        ranges=ranges[-4:],  # Show last 4 ranges (most recent)
                    )
                    widget.pack(fill="x", pady=1)

            self._version_ranges_loaded = True

        except Exception as e:
            self._vr_placeholder.configure(text=f"Could not load: {str(e)[:30]}")

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
            # Load version ranges when expanded
            self._load_version_ranges()
        else:
            self.details_frame.pack_forget()
            self.toggle_btn.configure(text=f"{ICONS['chevron_right']} Details")
