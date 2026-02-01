"""
History card widget for displaying past analysis records.

Shows file name, type icon, score, grade, date, bookmark status,
tags, and provides delete functionality.
"""

from typing import Callable, Optional, Dict, Any, List
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS, get_score_color, get_file_type_color


class HistoryCard(ctk.CTkFrame):
    """Card widget for displaying a single history item.

    Shows:
    - File type icon
    - File name
    - Score and grade
    - Bookmark indicator
    - Tags
    - Date/time analyzed
    - Delete button
    """

    def __init__(
        self,
        master,
        analysis_data: Dict[str, Any],
        on_click: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        on_bookmark_toggle: Optional[Callable[[int, bool], None]] = None,
        is_bookmarked: bool = False,
        tags: List[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize the history card.

        Args:
            master: Parent widget
            analysis_data: Dictionary with analysis info (from to_dict())
            on_click: Callback when card is clicked (receives analysis_id)
            on_delete: Callback when delete is clicked (receives analysis_id)
            on_bookmark_toggle: Callback when bookmark is toggled (receives analysis_id, new_state)
            is_bookmarked: Whether this analysis is bookmarked
            tags: List of tag dictionaries for this analysis
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._data = analysis_data
        self._on_click = on_click
        self._on_delete = on_delete
        self._on_bookmark_toggle = on_bookmark_toggle
        self._is_bookmarked = is_bookmarked
        self._tags = tags or []
        self._analysis_id = analysis_data.get('id')

        self._init_ui()
        self._bind_events()

    def _init_ui(self):
        """Initialize the user interface."""
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])

        # Left side: Icon + File info
        left_frame = ctk.CTkFrame(container, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)

        # File type icon
        file_type = self._data.get('file_type', 'unknown')
        icon_colors = {
            'html': COLORS['html_color'],
            'htm': COLORS['html_color'],
            'css': COLORS['css_color'],
            'js': COLORS['js_color'],
            'mixed': COLORS['accent'],
        }
        icon_color = icon_colors.get(file_type.lower(), COLORS['text_muted'])

        icons = {
            'html': ICONS.get('html', '\u25B6'),
            'htm': ICONS.get('html', '\u25B6'),
            'css': ICONS.get('css', '\u25C6'),
            'js': ICONS.get('js', '\u2605'),
            'mixed': '\u25A0',
        }
        icon = icons.get(file_type.lower(), ICONS.get('file', '\u25A0'))

        icon_label = ctk.CTkLabel(
            left_frame,
            text=icon,
            font=ctk.CTkFont(size=18),
            text_color=icon_color,
            width=30,
        )
        icon_label.pack(side="left")

        # File info container
        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=(SPACING['xs'], 0))

        # File name
        file_name = self._data.get('file_name', 'Unknown file')
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w",
        )
        name_label.pack(anchor="w")

        # Score, grade, features, and date
        score = self._data.get('overall_score', 0)
        grade = self._data.get('grade', 'N/A')
        total_features = self._data.get('total_features', 0)
        score_color = get_score_color(score)

        # Format the date
        analyzed_at = self._data.get('analyzed_at')
        date_str = self._format_date(analyzed_at)

        details_text = f"Score: {score:.0f}% ({grade})  |  {total_features} features  |  {date_str}"

        details_label = ctk.CTkLabel(
            info_frame,
            text=details_text,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
            anchor="w",
        )
        details_label.pack(anchor="w")

        # Tags row (if any tags)
        if self._tags:
            tags_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            tags_frame.pack(anchor="w", pady=(SPACING['xs'], 0))

            for tag in self._tags[:3]:  # Show max 3 tags
                tag_color = tag.get('color', '#58a6ff')
                # Create muted background color
                try:
                    hex_c = tag_color.lstrip('#')
                    r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
                    muted = f'#{int(r*0.3):02x}{int(g*0.3):02x}{int(b*0.3):02x}'
                except:
                    muted = COLORS['bg_light']

                tag_chip = ctk.CTkLabel(
                    tags_frame,
                    text=f" {tag.get('name', 'Tag')} ",
                    font=ctk.CTkFont(size=9),
                    text_color=tag_color,
                    fg_color=muted,
                    corner_radius=3,
                )
                tag_chip.pack(side="left", padx=(0, SPACING['xs']))

            if len(self._tags) > 3:
                more_label = ctk.CTkLabel(
                    tags_frame,
                    text=f"+{len(self._tags) - 3}",
                    font=ctk.CTkFont(size=9),
                    text_color=COLORS['text_muted'],
                )
                more_label.pack(side="left")

        # Right side: Bookmark + Score badge + Delete button
        right_frame = ctk.CTkFrame(container, fg_color="transparent")
        right_frame.pack(side="right")

        # Bookmark button
        bookmark_icon = ICONS.get('bookmark_filled', '\u2605') if self._is_bookmarked else ICONS.get('bookmark', '\u2606')
        bookmark_color = COLORS['warning'] if self._is_bookmarked else COLORS['text_muted']

        self._bookmark_btn = ctk.CTkButton(
            right_frame,
            text=bookmark_icon,
            font=ctk.CTkFont(size=14),
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=COLORS['bg_light'],
            text_color=bookmark_color,
            command=self._handle_bookmark_toggle,
        )
        self._bookmark_btn.pack(side="left", padx=(0, SPACING['xs']))

        # Score badge
        score_badge = ctk.CTkLabel(
            right_frame,
            text=f" {score:.0f}% ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_primary'],
            fg_color=score_color,
            corner_radius=4,
        )
        score_badge.pack(side="left", padx=(0, SPACING['sm']))

        # Delete button
        delete_btn = ctk.CTkButton(
            right_frame,
            text=ICONS.get('delete', '\u2715'),
            font=ctk.CTkFont(size=12),
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['danger_muted'],
            text_color=COLORS['text_muted'],
            command=self._handle_delete,
        )
        delete_btn.pack(side="left")

        # Store labels for hover effects
        self._name_label = name_label
        self._details_label = details_label

    def _format_date(self, date_str: str) -> str:
        """Format the date string for display.

        Args:
            date_str: ISO format date string

        Returns:
            Human-readable date string
        """
        if not date_str:
            return 'Unknown'

        from datetime import datetime

        try:
            dt = datetime.fromisoformat(date_str)
            now = datetime.now()
            diff = now - dt

            if diff.days == 0:
                return f"Today {dt.strftime('%I:%M %p')}"
            elif diff.days == 1:
                return "Yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            else:
                return dt.strftime('%b %d, %Y')
        except (ValueError, TypeError):
            return str(date_str)[:16]

    def _bind_events(self):
        """Bind mouse events for interactivity."""
        # Bind click to self and children
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Bind to container children too
        for child in self.winfo_children():
            child.bind("<Button-1>", self._handle_click)
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

            for subchild in child.winfo_children():
                if not isinstance(subchild, ctk.CTkButton):
                    subchild.bind("<Button-1>", self._handle_click)
                    subchild.bind("<Enter>", self._on_enter)
                    subchild.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Handle mouse enter."""
        self.configure(
            fg_color=COLORS['bg_light'],
            border_color=COLORS['accent'],
        )

    def _on_leave(self, event):
        """Handle mouse leave."""
        self.configure(
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['border'],
        )

    def _handle_click(self, event):
        """Handle card click."""
        if self._on_click and self._analysis_id:
            self._on_click(self._analysis_id)

    def _handle_delete(self):
        """Handle delete button click."""
        if self._on_delete and self._analysis_id:
            self._on_delete(self._analysis_id)

    def _handle_bookmark_toggle(self):
        """Handle bookmark button click."""
        self._is_bookmarked = not self._is_bookmarked
        self._update_bookmark_appearance()

        if self._on_bookmark_toggle and self._analysis_id:
            self._on_bookmark_toggle(self._analysis_id, self._is_bookmarked)

    def _update_bookmark_appearance(self):
        """Update bookmark button appearance."""
        if self._is_bookmarked:
            self._bookmark_btn.configure(
                text=ICONS.get('bookmark_filled', '\u2605'),
                text_color=COLORS['warning'],
            )
        else:
            self._bookmark_btn.configure(
                text=ICONS.get('bookmark', '\u2606'),
                text_color=COLORS['text_muted'],
            )

    def set_bookmarked(self, is_bookmarked: bool):
        """Set bookmark state without triggering callback."""
        self._is_bookmarked = is_bookmarked
        self._update_bookmark_appearance()

    def set_tags(self, tags: List[Dict[str, Any]]):
        """Update the tags displayed on this card.

        Note: This requires rebuilding the UI, so use sparingly.
        """
        self._tags = tags or []
        # Would need to rebuild UI to show updated tags


class EmptyHistoryCard(ctk.CTkFrame):
    """Placeholder card shown when history is empty."""

    def __init__(self, master, **kwargs):
        """Initialize the empty state card."""
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])

        # Icon
        icon_label = ctk.CTkLabel(
            container,
            text="\u23F3",  # Hourglass
            font=ctk.CTkFont(size=36),
            text_color=COLORS['text_disabled'],
        )
        icon_label.pack(pady=(SPACING['lg'], SPACING['md']))

        # Title
        title_label = ctk.CTkLabel(
            container,
            text="No Analysis History",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_muted'],
        )
        title_label.pack()

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            container,
            text="Your past analyses will appear here.\nAnalyze some files to get started!",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_disabled'],
            justify="center",
        )
        subtitle_label.pack(pady=(SPACING['sm'], SPACING['lg']))
