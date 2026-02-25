"""Tag chips, tag list, tag selector, and tag manager dialog."""

from typing import Callable, Optional, List, Dict, Any
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


class TagChip(ctk.CTkFrame):
    """Small colored chip for a single tag, with optional remove button."""

    def __init__(
        self,
        master,
        tag_data: Dict[str, Any],
        on_remove: Optional[Callable[[int], None]] = None,
        removable: bool = True,
        **kwargs
    ):
        self._tag_data = tag_data
        self._on_remove = on_remove
        self._tag_id = tag_data.get('id')

        tag_color = tag_data.get('color', '#58a6ff')

        super().__init__(
            master,
            fg_color=self._get_muted_color(tag_color),
            corner_radius=4,
            **kwargs
        )

        self._init_ui(tag_data, tag_color, removable)

    def _get_muted_color(self, hex_color: str) -> str:
        """Darken a color by blending toward black -- used for chip backgrounds."""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            factor = 0.3
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)

            return f'#{r:02x}{g:02x}{b:02x}'
        except (ValueError, IndexError):
            return COLORS['bg_light']

    def _init_ui(self, tag_data: Dict, tag_color: str, removable: bool):
        name_label = ctk.CTkLabel(
            self,
            text=tag_data.get('name', 'Tag'),
            font=ctk.CTkFont(size=10),
            text_color=tag_color,
            padx=SPACING['xs'],
        )
        name_label.pack(side="left", padx=(SPACING['xs'], 0), pady=2)

        if removable and self._on_remove:
            remove_btn = ctk.CTkButton(
                self,
                text=ICONS.get('close', '\u2715'),
                font=ctk.CTkFont(size=8),
                width=14,
                height=14,
                fg_color="transparent",
                hover_color=COLORS['danger_muted'],
                text_color=tag_color,
                command=self._handle_remove,
            )
            remove_btn.pack(side="left", padx=(0, 2), pady=2)

    def _handle_remove(self):
        if self._on_remove and self._tag_id:
            self._on_remove(self._tag_id)


class TagList(ctk.CTkFrame):
    """Horizontal row of tag chips with "+N more" overflow."""

    def __init__(
        self,
        master,
        tags: List[Dict[str, Any]] = None,
        on_tag_remove: Optional[Callable[[int], None]] = None,
        removable: bool = True,
        max_visible: int = 5,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._tags = tags or []
        self._on_tag_remove = on_tag_remove
        self._removable = removable
        self._max_visible = max_visible

        self._init_ui()

    def _init_ui(self):
        self._refresh_tags()

    def _refresh_tags(self):
        for widget in self.winfo_children():
            widget.destroy()

        if not self._tags:
            return

        visible_tags = self._tags[:self._max_visible]
        remaining = len(self._tags) - self._max_visible

        for tag in visible_tags:
            chip = TagChip(
                self,
                tag_data=tag,
                on_remove=self._on_tag_remove,
                removable=self._removable,
            )
            chip.pack(side="left", padx=(0, SPACING['xs']))

        if remaining > 0:
            more_label = ctk.CTkLabel(
                self,
                text=f"+{remaining}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_muted'],
            )
            more_label.pack(side="left", padx=SPACING['xs'])

    def set_tags(self, tags: List[Dict[str, Any]]):
        self._tags = tags or []
        self._refresh_tags()

    def add_tag(self, tag: Dict[str, Any]):
        self._tags.append(tag)
        self._refresh_tags()

    def remove_tag(self, tag_id: int):
        self._tags = [t for t in self._tags if t.get('id') != tag_id]
        self._refresh_tags()


class TagSelector(ctk.CTkFrame):
    """Dropdown-style picker for adding existing or new tags to an analysis."""

    TAG_COLORS = [
        '#58a6ff',  # Blue (default)
        '#3fb950',  # Green
        '#d29922',  # Amber
        '#f85149',  # Red
        '#a371f7',  # Purple
        '#f778ba',  # Pink
        '#79c0ff',  # Light blue
        '#56d364',  # Light green
    ]

    def __init__(
        self,
        master,
        available_tags: List[Dict[str, Any]] = None,
        selected_tags: List[Dict[str, Any]] = None,
        on_tag_add: Optional[Callable[[int], None]] = None,
        on_tag_create: Optional[Callable[[str, str], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            **kwargs
        )

        self._available_tags = available_tags or []
        self._selected_tags = selected_tags or []
        self._on_tag_add = on_tag_add
        self._on_tag_create = on_tag_create
        self._color_index = 0

        self._init_ui()

    def _init_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['sm'], pady=SPACING['sm'])

        header_label = ctk.CTkLabel(
            header,
            text="Add Tags",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_secondary'],
        )
        header_label.pack(side="left")

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=SPACING['sm'], pady=(0, SPACING['sm']))

        self._tag_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="New tag name...",
            font=ctk.CTkFont(size=11),
            height=28,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        self._tag_entry.pack(side="left", fill="x", expand=True)
        self._tag_entry.bind("<Return>", self._create_new_tag)

        add_btn = ctk.CTkButton(
            input_frame,
            text=ICONS.get('add', '+'),
            font=ctk.CTkFont(size=12),
            width=28,
            height=28,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_bright'],
            command=self._create_new_tag,
        )
        add_btn.pack(side="left", padx=(SPACING['xs'], 0))

        self._tags_container = ctk.CTkFrame(self, fg_color="transparent")
        self._tags_container.pack(fill="x", padx=SPACING['sm'], pady=(0, SPACING['sm']))

        self._refresh_available_tags()

    def _refresh_available_tags(self):
        for widget in self._tags_container.winfo_children():
            widget.destroy()

        selected_ids = {t.get('id') for t in self._selected_tags}
        unselected = [t for t in self._available_tags if t.get('id') not in selected_ids]

        if not unselected:
            empty_label = ctk.CTkLabel(
                self._tags_container,
                text="No more tags available",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_disabled'],
            )
            empty_label.pack(pady=SPACING['xs'])
            return

        chips_frame = ctk.CTkFrame(self._tags_container, fg_color="transparent")
        chips_frame.pack(fill="x")

        for tag in unselected[:10]:
            chip = ctk.CTkButton(
                chips_frame,
                text=tag.get('name', 'Tag'),
                font=ctk.CTkFont(size=10),
                height=24,
                fg_color=self._get_muted_color(tag.get('color', '#58a6ff')),
                hover_color=COLORS['bg_light'],
                text_color=tag.get('color', '#58a6ff'),
                corner_radius=4,
                command=lambda t=tag: self._add_tag(t),
            )
            chip.pack(side="left", padx=(0, SPACING['xs']), pady=SPACING['xs'])

    def _get_muted_color(self, hex_color: str) -> str:
        """Darken color for chip background."""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            factor = 0.3
            return f'#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}'
        except (ValueError, IndexError):
            return COLORS['bg_light']

    def _add_tag(self, tag: Dict[str, Any]):
        if self._on_tag_add:
            self._on_tag_add(tag.get('id'))
        self._selected_tags.append(tag)
        self._refresh_available_tags()

    def _create_new_tag(self, event=None):
        name = self._tag_entry.get().strip()
        if not name:
            return

        # Cycle through the color palette
        color = self.TAG_COLORS[self._color_index % len(self.TAG_COLORS)]
        self._color_index += 1

        if self._on_tag_create:
            self._on_tag_create(name, color)

        self._tag_entry.delete(0, 'end')

    def set_available_tags(self, tags: List[Dict[str, Any]]):
        self._available_tags = tags or []
        self._refresh_available_tags()

    def set_selected_tags(self, tags: List[Dict[str, Any]]):
        self._selected_tags = tags or []
        self._refresh_available_tags()


class TagManagerDialog(ctk.CTkToplevel):
    """Modal dialog for creating, editing, and deleting tags."""

    TAG_COLORS = TagSelector.TAG_COLORS

    def __init__(
        self,
        master,
        tags: List[Dict[str, Any]] = None,
        on_create: Optional[Callable[[str, str], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        on_update: Optional[Callable[[int, str, str], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self._tags = tags or []
        self._on_create = on_create
        self._on_delete = on_delete
        self._on_update = on_update
        self._color_index = 0

        self.title("Manage Tags")
        self.geometry("400x500")
        self.configure(fg_color=COLORS['bg_dark'])

        self.transient(master)
        self.grab_set()

        self._init_ui()

    def _init_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        title = ctk.CTkLabel(
            header,
            text="Manage Tags",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title.pack(side="left")

        close_btn = ctk.CTkButton(
            header,
            text=ICONS.get('close', '\u2715'),
            font=ctk.CTkFont(size=14),
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['bg_light'],
            text_color=COLORS['text_muted'],
            command=self.destroy,
        )
        close_btn.pack(side="right")

        create_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'], corner_radius=8)
        create_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))

        create_inner = ctk.CTkFrame(create_frame, fg_color="transparent")
        create_inner.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        ctk.CTkLabel(
            create_inner,
            text="Create New Tag",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w")

        input_row = ctk.CTkFrame(create_inner, fg_color="transparent")
        input_row.pack(fill="x", pady=(SPACING['sm'], 0))

        self._name_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Tag name",
            font=ctk.CTkFont(size=12),
            height=32,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        self._name_entry.pack(side="left", fill="x", expand=True)
        self._name_entry.bind("<Return>", lambda e=None: self._create_tag())

        # Clicks cycle through the color palette
        self._selected_color = self.TAG_COLORS[0]
        self._color_btn = ctk.CTkButton(
            input_row,
            text="",
            width=32,
            height=32,
            fg_color=self._selected_color,
            hover_color=self._selected_color,
            corner_radius=4,
            command=self._cycle_color,
        )
        self._color_btn.pack(side="left", padx=(SPACING['sm'], 0))

        create_btn = ctk.CTkButton(
            input_row,
            text="Create",
            font=ctk.CTkFont(size=12),
            height=32,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_bright'],
            command=self._create_tag,
        )
        create_btn.pack(side="left", padx=(SPACING['sm'], 0))

        list_label = ctk.CTkLabel(
            self,
            text="Existing Tags",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary'],
        )
        list_label.pack(anchor="w", padx=SPACING['lg'])

        self._tags_list = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
        )
        self._tags_list.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['md'])

        self._refresh_tags_list()

    def _cycle_color(self):
        self._color_index = (self._color_index + 1) % len(self.TAG_COLORS)
        self._selected_color = self.TAG_COLORS[self._color_index]
        self._color_btn.configure(fg_color=self._selected_color, hover_color=self._selected_color)

    def _create_tag(self):
        name = self._name_entry.get().strip()
        if not name:
            return

        if self._on_create:
            self._on_create(name, self._selected_color)

        self._name_entry.delete(0, 'end')
        self._cycle_color()

    def _refresh_tags_list(self):
        for widget in self._tags_list.winfo_children():
            widget.destroy()

        if not self._tags:
            empty_label = ctk.CTkLabel(
                self._tags_list,
                text="No tags created yet",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_disabled'],
            )
            empty_label.pack(pady=SPACING['xl'])
            return

        for tag in self._tags:
            self._create_tag_row(tag)

    def _create_tag_row(self, tag: Dict[str, Any]):
        row = ctk.CTkFrame(self._tags_list, fg_color="transparent")
        row.pack(fill="x", pady=SPACING['xs'])

        color_indicator = ctk.CTkLabel(
            row,
            text=ICONS.get('tag', '\u2302'),
            font=ctk.CTkFont(size=14),
            text_color=tag.get('color', COLORS['accent']),
            width=24,
        )
        color_indicator.pack(side="left")

        name_label = ctk.CTkLabel(
            row,
            text=tag.get('name', 'Tag'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
        )
        name_label.pack(side="left", fill="x", expand=True, padx=SPACING['sm'])

        delete_btn = ctk.CTkButton(
            row,
            text=ICONS.get('delete', '\u2715'),
            font=ctk.CTkFont(size=10),
            width=24,
            height=24,
            fg_color="transparent",
            hover_color=COLORS['danger_muted'],
            text_color=COLORS['text_muted'],
            command=lambda: self._delete_tag(tag.get('id')),
        )
        delete_btn.pack(side="right")

    def _delete_tag(self, tag_id: int):
        if self._on_delete and tag_id:
            self._on_delete(tag_id)

    def set_tags(self, tags: List[Dict[str, Any]]):
        self._tags = tags or []
        self._refresh_tags_list()
