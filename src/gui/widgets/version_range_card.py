"""
VersionRangeCard widget - Displays browser version ranges like Can I Use.

Shows which versions support a feature with color-coded ranges.
"""

from typing import Dict, List, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


# Browser display names and icons
BROWSER_INFO = {
    'chrome': {'name': 'Chrome', 'icon': '🌐'},
    'firefox': {'name': 'Firefox', 'icon': '🦊'},
    'safari': {'name': 'Safari', 'icon': '🧭'},
    'edge': {'name': 'Edge', 'icon': '🔷'},
    'opera': {'name': 'Opera', 'icon': '🔴'},
    'ie': {'name': 'IE', 'icon': '📘'},
    'android': {'name': 'Android', 'icon': '🤖'},
    'ios_saf': {'name': 'iOS Safari', 'icon': '📱'},
    'samsung': {'name': 'Samsung', 'icon': '📱'},
}

# Status colors matching Can I Use
STATUS_COLORS = {
    'y': COLORS['success'],      # Green - Supported
    'n': COLORS['danger'],       # Red - Not supported
    'a': COLORS['warning'],      # Yellow - Partial
    'p': '#9B59B6',              # Purple - Polyfill
    'x': '#E67E22',              # Orange - Prefix required
    'u': COLORS['text_muted'],   # Gray - Unknown
    'd': '#7F8C8D',              # Gray - Disabled by default
}


class VersionRangeBar(ctk.CTkFrame):
    """A single horizontal bar showing version ranges for one browser."""

    def __init__(
        self,
        master,
        browser: str,
        ranges: List[Dict],
        **kwargs
    ):
        """Initialize the version range bar.

        Args:
            master: Parent widget
            browser: Browser ID (e.g., 'chrome')
            ranges: List of range dicts with start, end, status, status_text
        """
        super().__init__(
            master,
            fg_color="transparent",
            height=36,
            **kwargs
        )

        self._browser = browser
        self._ranges = ranges
        self._init_ui()

    def _init_ui(self):
        """Build the UI."""
        # Browser name label
        browser_info = BROWSER_INFO.get(self._browser, {'name': self._browser.title(), 'icon': '🌐'})

        name_frame = ctk.CTkFrame(self, fg_color="transparent", width=100)
        name_frame.pack(side="left", padx=(0, SPACING['sm']))
        name_frame.pack_propagate(False)

        name_label = ctk.CTkLabel(
            name_frame,
            text=f"{browser_info['icon']} {browser_info['name']}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
            anchor="w",
        )
        name_label.pack(side="left", fill="x")

        # Version ranges container
        ranges_frame = ctk.CTkFrame(self, fg_color="transparent")
        ranges_frame.pack(side="left", fill="x", expand=True)

        # Create range boxes
        for r in self._ranges:
            self._create_range_box(ranges_frame, r)

    def _create_range_box(self, parent, range_data: Dict):
        """Create a single version range box."""
        status = range_data.get('status', 'u')
        color = STATUS_COLORS.get(status, COLORS['text_muted'])

        # Format version text
        start = range_data.get('start', '?')
        end = range_data.get('end', '?')

        if start == end:
            version_text = str(start)
        else:
            version_text = f"{start}-{end}"

        # Create the box
        box = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=4,
            height=24,
        )
        box.pack(side="left", padx=1, pady=2)

        # Version label
        label = ctk.CTkLabel(
            box,
            text=version_text,
            font=ctk.CTkFont(size=10),
            text_color="white" if status in ['y', 'n', 'a'] else COLORS['text_primary'],
        )
        label.pack(padx=SPACING['xs'], pady=2)

        # Tooltip on hover
        tooltip_text = f"{version_text}: {range_data.get('status_text', 'Unknown')}"
        self._add_tooltip(box, tooltip_text)
        self._add_tooltip(label, tooltip_text)

    def _add_tooltip(self, widget, text: str):
        """Add hover tooltip to widget."""
        def show_tooltip(event):
            widget._tooltip = ctk.CTkToplevel(widget)
            widget._tooltip.wm_overrideredirect(True)
            widget._tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = ctk.CTkLabel(
                widget._tooltip,
                text=text,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['bg_dark'],
                corner_radius=4,
                text_color=COLORS['text_primary'],
            )
            label.pack(padx=SPACING['xs'], pady=SPACING['xs'])

        def hide_tooltip(event):
            if hasattr(widget, '_tooltip') and widget._tooltip:
                widget._tooltip.destroy()
                widget._tooltip = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)


class VersionRangeCard(ctk.CTkFrame):
    """Card showing version ranges for a feature across all browsers.

    Similar to Can I Use's browser support table.
    """

    def __init__(
        self,
        master,
        feature_id: str,
        feature_name: str,
        browser_ranges: Dict[str, List[Dict]],
        **kwargs
    ):
        """Initialize the version range card.

        Args:
            master: Parent widget
            feature_id: Can I Use feature ID
            feature_name: Human-readable feature name
            browser_ranges: Dict mapping browser IDs to list of ranges
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._feature_id = feature_id
        self._feature_name = feature_name
        self._browser_ranges = browser_ranges
        self._init_ui()

    def _init_ui(self):
        """Build the UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        title = ctk.CTkLabel(
            header,
            text=self._feature_name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title.pack(side="left")

        feature_id_label = ctk.CTkLabel(
            header,
            text=f"({self._feature_id})",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        feature_id_label.pack(side="left", padx=(SPACING['xs'], 0))

        # Legend
        legend = ctk.CTkFrame(self, fg_color="transparent")
        legend.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

        legend_items = [
            ('y', 'Supported'),
            ('a', 'Partial'),
            ('n', 'Not Supported'),
        ]

        for status, text in legend_items:
            color = STATUS_COLORS.get(status, COLORS['text_muted'])

            dot = ctk.CTkFrame(legend, fg_color=color, width=12, height=12, corner_radius=2)
            dot.pack(side="left", padx=(0, 4))

            label = ctk.CTkLabel(
                legend,
                text=text,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_secondary'],
            )
            label.pack(side="left", padx=(0, SPACING['md']))

        # Browser rows
        browsers_frame = ctk.CTkFrame(self, fg_color="transparent")
        browsers_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))

        # Order browsers: desktop first, then mobile
        browser_order = ['chrome', 'edge', 'safari', 'firefox', 'opera', 'ie']

        for browser in browser_order:
            if browser in self._browser_ranges:
                bar = VersionRangeBar(
                    browsers_frame,
                    browser=browser,
                    ranges=self._browser_ranges[browser],
                )
                bar.pack(fill="x", pady=2)


class VersionRangePopup(ctk.CTkToplevel):
    """Popup window showing detailed version ranges for a feature."""

    def __init__(
        self,
        master,
        feature_id: str,
        feature_name: str,
        **kwargs
    ):
        """Initialize the popup.

        Args:
            master: Parent widget
            feature_id: Can I Use feature ID
            feature_name: Human-readable feature name
        """
        super().__init__(master, **kwargs)

        self.title(f"Browser Support: {feature_name}")
        self.geometry("600x400")
        self.configure(fg_color=COLORS['bg_dark'])

        # Make it modal
        self.transient(master)
        self.grab_set()

        self._feature_id = feature_id
        self._feature_name = feature_name

        self._init_ui()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _init_ui(self):
        """Build the UI."""
        # Import here to avoid circular imports
        from ...analyzer.version_ranges import get_support_summary, BROWSER_NAMES

        # Get version ranges
        summary = get_support_summary(self._feature_id)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        title = ctk.CTkLabel(
            header,
            text=self._feature_name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title.pack(side="left")

        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_muted'],
            command=self.destroy,
        )
        close_btn.pack(side="right")

        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['lg']))

        # Browser rows
        for browser, data in summary.items():
            self._create_browser_row(scroll_frame, browser, data)

    def _create_browser_row(self, parent, browser: str, data: Dict):
        """Create a row for one browser."""
        from ...analyzer.version_ranges import BROWSER_NAMES

        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=6)
        row.pack(fill="x", pady=SPACING['xs'])

        # Browser name
        name_frame = ctk.CTkFrame(row, fg_color="transparent", width=140)
        name_frame.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'])
        name_frame.pack_propagate(False)

        browser_name = BROWSER_NAMES.get(browser, browser.title())
        name_label = ctk.CTkLabel(
            name_frame,
            text=browser_name,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w",
        )
        name_label.pack(side="left")

        # Current status
        status = data.get('current_status', 'u')
        status_text = data.get('current_status_text', 'Unknown')
        color = STATUS_COLORS.get(status, COLORS['text_muted'])

        status_badge = ctk.CTkLabel(
            row,
            text=f" {status_text} ",
            font=ctk.CTkFont(size=11),
            fg_color=color,
            corner_radius=4,
            text_color="white",
        )
        status_badge.pack(side="left", padx=SPACING['xs'])

        # Supported since
        if data.get('supported_since'):
            since_label = ctk.CTkLabel(
                row,
                text=f"since v{data['supported_since']}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted'],
            )
            since_label.pack(side="left", padx=SPACING['sm'])

        # Version ranges (compact)
        ranges_text = self._format_ranges(data.get('ranges', []))
        ranges_label = ctk.CTkLabel(
            row,
            text=ranges_text,
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary'],
        )
        ranges_label.pack(side="right", padx=SPACING['sm'])

    def _format_ranges(self, ranges: List[Dict]) -> str:
        """Format ranges as compact text."""
        parts = []
        for r in ranges[-3:]:  # Show last 3 ranges
            start = r.get('start', '?')
            end = r.get('end', '?')
            status = r.get('status', 'u')

            if start == end:
                ver = str(start)
            else:
                ver = f"{start}-{end}"

            symbol = {'y': '✓', 'n': '✗', 'a': '~'}.get(status, '?')
            parts.append(f"{ver}:{symbol}")

        return " | ".join(parts)
