"""
CollapsibleSection widget - Generic expand/collapse wrapper.
Used for progressive disclosure of technical details.
"""

from typing import Callable, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


class CollapsibleSection(ctk.CTkFrame):
    """A collapsible section with header and expandable content.

    Features:
    - Click header to expand/collapse
    - Animated chevron indicator
    - Optional badge showing count/status
    - Customizable content area
    """

    def __init__(
        self,
        master,
        title: str,
        badge_text: Optional[str] = None,
        badge_color: Optional[str] = None,
        expanded: bool = False,
        on_toggle: Optional[Callable[[bool], None]] = None,
        **kwargs
    ):
        """Initialize the collapsible section.

        Args:
            master: Parent widget
            title: Section title text
            badge_text: Optional badge text (e.g., count)
            badge_color: Badge background color
            expanded: Whether section starts expanded
            on_toggle: Callback when section is toggled (receives expanded state)
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

        self._title = title
        self._badge_text = badge_text
        self._badge_color = badge_color or COLORS['accent']
        self._expanded = expanded
        self._on_toggle = on_toggle

        self._init_ui()
        self._update_state()

    def _init_ui(self):
        """Initialize the user interface."""
        # Header (clickable)
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            cursor="hand2",
        )
        self.header_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        # Bind click events to header
        self.header_frame.bind("<Button-1>", self._on_header_click)

        # Chevron icon
        self.chevron_label = ctk.CTkLabel(
            self.header_frame,
            text=ICONS['chevron_right'],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_muted'],
            width=20,
        )
        self.chevron_label.pack(side="left")
        self.chevron_label.bind("<Button-1>", self._on_header_click)

        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self._title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        self.title_label.pack(side="left", padx=(SPACING['xs'], 0))
        self.title_label.bind("<Button-1>", self._on_header_click)

        # Badge (optional)
        if self._badge_text:
            self.badge_label = ctk.CTkLabel(
                self.header_frame,
                text=f" {self._badge_text} ",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
                fg_color=self._badge_color,
                corner_radius=4,
            )
            self.badge_label.pack(side="left", padx=(SPACING['sm'], 0))
            self.badge_label.bind("<Button-1>", self._on_header_click)

        # Expand/Collapse text
        self.action_label = ctk.CTkLabel(
            self.header_frame,
            text="Expand",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.action_label.pack(side="right")
        self.action_label.bind("<Button-1>", self._on_header_click)

        # Content frame (initially hidden or shown based on expanded)
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        # Will be packed/unpacked based on state

        # Separator line between header and content
        self.separator = ctk.CTkFrame(
            self,
            fg_color=COLORS['border'],
            height=1,
        )

    def _on_header_click(self, event=None):
        """Handle header click - toggle expanded state."""
        self.toggle()

    def _update_state(self):
        """Update UI based on expanded state."""
        if self._expanded:
            self.chevron_label.configure(text=ICONS['chevron_down'])
            self.action_label.configure(text="Collapse")
            self.separator.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
            self.content_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        else:
            self.chevron_label.configure(text=ICONS['chevron_right'])
            self.action_label.configure(text="Expand")
            self.separator.pack_forget()
            self.content_frame.pack_forget()

    def toggle(self):
        """Toggle the expanded state."""
        self._expanded = not self._expanded
        self._update_state()

        if self._on_toggle:
            self._on_toggle(self._expanded)

    def expand(self):
        """Expand the section."""
        if not self._expanded:
            self._expanded = True
            self._update_state()
            if self._on_toggle:
                self._on_toggle(self._expanded)

    def collapse(self):
        """Collapse the section."""
        if self._expanded:
            self._expanded = False
            self._update_state()
            if self._on_toggle:
                self._on_toggle(self._expanded)

    def is_expanded(self) -> bool:
        """Check if section is expanded."""
        return self._expanded

    def get_content_frame(self) -> ctk.CTkFrame:
        """Get the content frame to add widgets to."""
        return self.content_frame

    def set_title(self, title: str):
        """Update the section title."""
        self._title = title
        self.title_label.configure(text=title)

    def set_badge(self, text: Optional[str], color: Optional[str] = None):
        """Update or remove the badge."""
        self._badge_text = text
        if color:
            self._badge_color = color

        if hasattr(self, 'badge_label'):
            if text:
                self.badge_label.configure(text=f" {text} ")
                if color:
                    self.badge_label.configure(fg_color=color)
                self.badge_label.pack(side="left", padx=(SPACING['sm'], 0))
            else:
                self.badge_label.pack_forget()
        elif text:
            # Create badge if it doesn't exist
            self.badge_label = ctk.CTkLabel(
                self.header_frame,
                text=f" {text} ",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
                fg_color=self._badge_color,
                corner_radius=4,
            )
            self.badge_label.pack(side="left", padx=(SPACING['sm'], 0))
            self.badge_label.bind("<Button-1>", self._on_header_click)
