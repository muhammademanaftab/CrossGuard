"""
ProjectStatsCard - Display project overview statistics.

Shows framework badge, file counts, and warnings about minified files.
"""

from typing import Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING


class ProjectStatsCard(ctk.CTkFrame):
    """Project overview statistics card."""

    def __init__(
        self,
        master,
        **kwargs
    ):
        """Initialize the project stats card.

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

        # State
        self._framework_name = None
        self._framework_version = None
        self._framework_color = COLORS['accent']
        self._build_tool = None
        self._html_count = 0
        self._css_count = 0
        self._js_count = 0
        self._minified_count = 0
        self._has_typescript = False

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Project Overview",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))

        # Separator
        sep = ctk.CTkFrame(self, fg_color=COLORS['border'], height=1)
        sep.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

        # Content frame
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))

        # Framework row
        self.framework_row = ctk.CTkFrame(self.content, fg_color="transparent")
        self.framework_row.pack(fill="x", pady=(0, SPACING['sm']))

        framework_label = ctk.CTkLabel(
            self.framework_row,
            text="Framework:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
            width=80,
            anchor="w",
        )
        framework_label.pack(side="left")

        self.framework_badge = ctk.CTkLabel(
            self.framework_row,
            text="Not detected",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_primary'],
            fg_color=COLORS['bg_light'],
            corner_radius=4,
            padx=8,
            pady=2,
        )
        self.framework_badge.pack(side="left")

        # Build tool (optional)
        self.build_tool_label = ctk.CTkLabel(
            self.framework_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.build_tool_label.pack(side="left", padx=(8, 0))

        # File counts row
        self.counts_row = ctk.CTkFrame(self.content, fg_color="transparent")
        self.counts_row.pack(fill="x", pady=(0, SPACING['sm']))

        counts_label = ctk.CTkLabel(
            self.counts_row,
            text="Files:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
            width=80,
            anchor="w",
        )
        counts_label.pack(side="left")

        # Total count
        self.total_count_label = ctk.CTkLabel(
            self.counts_row,
            text="0 total",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.total_count_label.pack(side="left")

        # Breakdown
        self.breakdown_label = ctk.CTkLabel(
            self.counts_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.breakdown_label.pack(side="left", padx=(8, 0))

        # TypeScript indicator
        self.typescript_label = ctk.CTkLabel(
            self.counts_row,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['info'],
            fg_color=COLORS['accent_muted'],
            corner_radius=4,
            padx=4,
            pady=1,
        )
        # Only pack when TypeScript is detected

        # Minified files warning
        self.warning_row = ctk.CTkFrame(self.content, fg_color="transparent")
        # Only pack when there are minified files

        self.warning_icon = ctk.CTkLabel(
            self.warning_row,
            text="\u26A0",  # Warning sign
            font=ctk.CTkFont(size=12),
            text_color=COLORS['warning'],
        )

        self.warning_label = ctk.CTkLabel(
            self.warning_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['warning'],
        )

    def update_stats(
        self,
        framework_name: Optional[str] = None,
        framework_version: Optional[str] = None,
        framework_color: str = None,
        build_tool: Optional[str] = None,
        html_count: int = 0,
        css_count: int = 0,
        js_count: int = 0,
        minified_count: int = 0,
        has_typescript: bool = False,
    ):
        """Update the displayed statistics.

        Args:
            framework_name: Detected framework name (e.g., "React")
            framework_version: Framework version
            framework_color: Badge color for framework
            build_tool: Build tool name (e.g., "Vite")
            html_count: Number of HTML files
            css_count: Number of CSS files
            js_count: Number of JavaScript files
            minified_count: Number of minified files detected
            has_typescript: Whether TypeScript is used
        """
        # Update internal state
        self._framework_name = framework_name
        self._framework_version = framework_version
        self._framework_color = framework_color or COLORS['accent']
        self._build_tool = build_tool
        self._html_count = html_count
        self._css_count = css_count
        self._js_count = js_count
        self._minified_count = minified_count
        self._has_typescript = has_typescript

        # Update framework badge
        if framework_name:
            badge_text = framework_name
            if framework_version and framework_version != "unknown":
                badge_text += f" {framework_version}"
            self.framework_badge.configure(
                text=badge_text,
                fg_color=self._framework_color,
            )
        else:
            self.framework_badge.configure(
                text="Not detected",
                fg_color=COLORS['bg_light'],
            )

        # Update build tool
        if build_tool:
            self.build_tool_label.configure(text=f"| {build_tool}")
        else:
            self.build_tool_label.configure(text="")

        # Update file counts
        total = html_count + css_count + js_count
        self.total_count_label.configure(text=f"{total} total")

        parts = []
        if html_count > 0:
            parts.append(f"HTML: {html_count}")
        if css_count > 0:
            parts.append(f"CSS: {css_count}")
        if js_count > 0:
            parts.append(f"JS: {js_count}")

        if parts:
            self.breakdown_label.configure(text=f"({', '.join(parts)})")
        else:
            self.breakdown_label.configure(text="")

        # TypeScript indicator
        if has_typescript:
            self.typescript_label.configure(text="TypeScript")
            self.typescript_label.pack(side="left", padx=(8, 0))
        else:
            self.typescript_label.pack_forget()

        # Minified files warning
        if minified_count > 0:
            self.warning_row.pack(fill="x", pady=(SPACING['xs'], 0))
            self.warning_icon.pack(side="left")
            self.warning_label.pack(side="left", padx=(4, 0))
            self.warning_label.configure(
                text=f"{minified_count} minified file{'s' if minified_count > 1 else ''} detected"
            )
        else:
            self.warning_row.pack_forget()

    def clear(self):
        """Clear all statistics."""
        self.update_stats()

    def get_total_files(self) -> int:
        """Get total file count."""
        return self._html_count + self._css_count + self._js_count


class ProjectSummaryBadge(ctk.CTkFrame):
    """Compact badge showing framework and file count."""

    def __init__(
        self,
        master,
        framework: Optional[str] = None,
        file_count: int = 0,
        color: str = None,
        **kwargs
    ):
        """Initialize the summary badge.

        Args:
            master: Parent widget
            framework: Framework name
            file_count: Total file count
            color: Badge accent color
        """
        super().__init__(
            master,
            fg_color=color or COLORS['bg_light'],
            corner_radius=6,
            **kwargs
        )

        self._init_ui(framework, file_count, color)

    def _init_ui(self, framework: Optional[str], file_count: int, color: str):
        """Initialize the user interface."""
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=SPACING['sm'], pady=SPACING['xs'])

        if framework:
            framework_label = ctk.CTkLabel(
                inner,
                text=framework,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['text_primary'],
            )
            framework_label.pack(side="left")

            sep = ctk.CTkLabel(
                inner,
                text="|",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted'],
            )
            sep.pack(side="left", padx=4)

        count_label = ctk.CTkLabel(
            inner,
            text=f"{file_count} files",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
        )
        count_label.pack(side="left")
