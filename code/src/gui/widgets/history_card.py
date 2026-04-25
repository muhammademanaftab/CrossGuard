"""History card showing a past analysis with score and bookmark status."""

from typing import Callable, Optional, Dict, Any
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS, get_score_color


class HistoryCard(ctk.CTkFrame):

    def __init__(
        self,
        master,
        analysis_data: Dict[str, Any],
        on_click: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        on_bookmark_toggle: Optional[Callable[[int, bool], None]] = None,
        is_bookmarked: bool = False,
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

        self._data = analysis_data
        self._on_click = on_click
        self._on_delete = on_delete
        self._on_bookmark_toggle = on_bookmark_toggle
        self._is_bookmarked = is_bookmarked
        self._analysis_id = analysis_data.get('id')

        self._init_ui()
        self._bind_events()

    def _init_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])

        left_frame = ctk.CTkFrame(container, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)

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

        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=(SPACING['xs'], 0))

        file_name = self._data.get('file_name', 'Unknown file')
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w",
        )
        name_label.pack(anchor="w")

        score = self._data.get('overall_score', 0)
        grade = self._data.get('grade', 'N/A')
        total_features = self._data.get('total_features', 0)
        score_color = get_score_color(score)

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

        right_frame = ctk.CTkFrame(container, fg_color="transparent")
        right_frame.pack(side="right")

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

        score_badge = ctk.CTkLabel(
            right_frame,
            text=f" {score:.0f}% ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_primary'],
            fg_color=score_color,
            corner_radius=4,
        )
        score_badge.pack(side="left", padx=(0, SPACING['sm']))

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

        self._name_label = name_label
        self._details_label = details_label

    def _format_date(self, date_str: str) -> str:
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
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        for child in self.winfo_children():
            child.bind("<Button-1>", self._handle_click)
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

            for subchild in child.winfo_children():
                # Don't hijack clicks on buttons
                if not isinstance(subchild, ctk.CTkButton):
                    subchild.bind("<Button-1>", self._handle_click)
                    subchild.bind("<Enter>", self._on_enter)
                    subchild.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.configure(
            fg_color=COLORS['bg_light'],
            border_color=COLORS['accent'],
        )

    def _on_leave(self, event):
        self.configure(
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['border'],
        )

    def _handle_click(self, event):
        if self._on_click and self._analysis_id:
            self._on_click(self._analysis_id)

    def _handle_delete(self):
        if self._on_delete and self._analysis_id:
            self._on_delete(self._analysis_id)

    def _handle_bookmark_toggle(self):
        self._is_bookmarked = not self._is_bookmarked
        self._update_bookmark_appearance()

        if self._on_bookmark_toggle and self._analysis_id:
            self._on_bookmark_toggle(self._analysis_id, self._is_bookmarked)

    def _update_bookmark_appearance(self):
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
        self._is_bookmarked = is_bookmarked
        self._update_bookmark_appearance()


class EmptyHistoryCard(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
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
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])

        icon_label = ctk.CTkLabel(
            container,
            text="\u23F3",
            font=ctk.CTkFont(size=36),
            text_color=COLORS['text_disabled'],
        )
        icon_label.pack(pady=(SPACING['lg'], SPACING['md']))

        title_label = ctk.CTkLabel(
            container,
            text="No Analysis History",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_muted'],
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            container,
            text="Your past analyses will appear here.\nAnalyze some files to get started!",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_disabled'],
            justify="center",
        )
        subtitle_label.pack(pady=(SPACING['sm'], SPACING['lg']))
