"""
Tag widgets for displaying and managing tags on analyses.

Provides tag chips, tag selector, and tag manager components.
"""

from typing import Callable, Optional, List, Dict, Any
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


class TagChip(ctk.CTkFrame):
    """Small tag chip displaying a single tag.

    Shows tag name with colored background and optional remove button.
    """

    def __init__(
        self,
        master,
        tag_data: Dict[str, Any],
        on_remove: Optional[Callable[[int], None]] = None,
        removable: bool = True,
        **kwargs
    ):
        """Initialize the tag chip.

        Args:
            master: Parent widget
            tag_data: Tag dictionary with 'id', 'name', 'color'
            on_remove: Callback when remove is clicked (receives tag_id)
            removable: Whether to show remove button
        """
        self._tag_data = tag_data
        self._on_remove = on_remove
        self._tag_id = tag_data.get('id')

        # Use tag color as background (muted version)
        tag_color = tag_data.get('color', '#58a6ff')

        super().__init__(
            master,
            fg_color=self._get_muted_color(tag_color),
            corner_radius=4,
            **kwargs
        )

        self._init_ui(tag_data, tag_color, removable)

    def _get_muted_color(self, hex_color: str) -> str:
        """Create a muted/darker version of the color for background."""
        # Simple approach: blend with dark background
        try:
            # Parse hex color
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            # Darken by blending with dark background
            factor = 0.3
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)

            return f'#{r:02x}{g:02x}{b:02x}'
        except (ValueError, IndexError):
            return COLORS['bg_light']

    def _init_ui(self, tag_data: Dict, tag_color: str, removable: bool):
        """Initialize the UI components."""
        # Tag name label
        name_label = ctk.CTkLabel(
            self,
            text=tag_data.get('name', 'Tag'),
            font=ctk.CTkFont(size=10),
            text_color=tag_color,
            padx=SPACING['xs'],
        )
        name_label.pack(side="left", padx=(SPACING['xs'], 0), pady=2)

        # Remove button (optional)
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
        """Handle remove button click."""
        if self._on_remove and self._tag_id:
            self._on_remove(self._tag_id)


class TagList(ctk.CTkFrame):
    """Horizontal list of tag chips."""

    def __init__(
        self,
        master,
        tags: List[Dict[str, Any]] = None,
        on_tag_remove: Optional[Callable[[int], None]] = None,
        removable: bool = True,
        max_visible: int = 5,
        **kwargs
    ):
        """Initialize the tag list.

        Args:
            master: Parent widget
            tags: List of tag dictionaries
            on_tag_remove: Callback when a tag is removed
            removable: Whether tags can be removed
            max_visible: Maximum visible tags before showing "+N more"
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        self._tags = tags or []
        self._on_tag_remove = on_tag_remove
        self._removable = removable
        self._max_visible = max_visible

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        self._refresh_tags()

    def _refresh_tags(self):
        """Refresh the tag display."""
        # Clear existing chips
        for widget in self.winfo_children():
            widget.destroy()

        if not self._tags:
            return

        # Display tags up to max_visible
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

        # Show "+N more" if there are hidden tags
        if remaining > 0:
            more_label = ctk.CTkLabel(
                self,
                text=f"+{remaining}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_muted'],
            )
            more_label.pack(side="left", padx=SPACING['xs'])

    def set_tags(self, tags: List[Dict[str, Any]]):
        """Update the displayed tags.

        Args:
            tags: New list of tag dictionaries
        """
        self._tags = tags or []
        self._refresh_tags()

    def add_tag(self, tag: Dict[str, Any]):
        """Add a tag to the list.

        Args:
            tag: Tag dictionary to add
        """
        self._tags.append(tag)
        self._refresh_tags()

    def remove_tag(self, tag_id: int):
        """Remove a tag from the list.

        Args:
            tag_id: Tag ID to remove
        """
        self._tags = [t for t in self._tags if t.get('id') != tag_id]
        self._refresh_tags()


class TagSelector(ctk.CTkFrame):
    """Dropdown-style tag selector for adding tags to an analysis."""

    # Predefined color palette for new tags
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
        """Initialize the tag selector.

        Args:
            master: Parent widget
            available_tags: All available tags
            selected_tags: Currently selected tags
            on_tag_add: Callback when existing tag is added (receives tag_id)
            on_tag_create: Callback when new tag is created (receives name, color)
        """
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
        """Initialize the UI components."""
        # Header with "Add Tag" label
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['sm'], pady=SPACING['sm'])

        header_label = ctk.CTkLabel(
            header,
            text="Add Tags",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_secondary'],
        )
        header_label.pack(side="left")

        # Input for new tag
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

        # Available tags list
        self._tags_container = ctk.CTkFrame(self, fg_color="transparent")
        self._tags_container.pack(fill="x", padx=SPACING['sm'], pady=(0, SPACING['sm']))

        self._refresh_available_tags()

    def _refresh_available_tags(self):
        """Refresh the list of available tags."""
        # Clear existing
        for widget in self._tags_container.winfo_children():
            widget.destroy()

        # Get IDs of already selected tags
        selected_ids = {t.get('id') for t in self._selected_tags}

        # Filter to unselected tags
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

        # Create clickable chips for each available tag
        chips_frame = ctk.CTkFrame(self._tags_container, fg_color="transparent")
        chips_frame.pack(fill="x")

        for tag in unselected[:10]:  # Show max 10 tags
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
        """Create a muted version of the color."""
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
        """Add an existing tag."""
        if self._on_tag_add:
            self._on_tag_add(tag.get('id'))
        self._selected_tags.append(tag)
        self._refresh_available_tags()

    def _create_new_tag(self, event=None):
        """Create a new tag from the entry field."""
        name = self._tag_entry.get().strip()
        if not name:
            return

        # Get next color from palette
        color = self.TAG_COLORS[self._color_index % len(self.TAG_COLORS)]
        self._color_index += 1

        if self._on_tag_create:
            self._on_tag_create(name, color)

        # Clear entry
        self._tag_entry.delete(0, 'end')

    def set_available_tags(self, tags: List[Dict[str, Any]]):
        """Update available tags list."""
        self._available_tags = tags or []
        self._refresh_available_tags()

    def set_selected_tags(self, tags: List[Dict[str, Any]]):
        """Update selected tags list."""
        self._selected_tags = tags or []
        self._refresh_available_tags()


class TagManagerDialog(ctk.CTkToplevel):
    """Dialog for managing all tags (create, edit, delete)."""

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
        """Initialize the tag manager dialog.

        Args:
            master: Parent window
            tags: List of all tags
            on_create: Callback for creating tag (name, color)
            on_delete: Callback for deleting tag (tag_id)
            on_update: Callback for updating tag (tag_id, name, color)
        """
        super().__init__(master, **kwargs)

        self._tags = tags or []
        self._on_create = on_create
        self._on_delete = on_delete
        self._on_update = on_update
        self._color_index = 0

        self.title("Manage Tags")
        self.geometry("400x500")
        self.configure(fg_color=COLORS['bg_dark'])

        # Center on parent
        self.transient(master)
        self.grab_set()

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Header
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

        # Create new tag section
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
        self._name_entry.bind("<Return>", lambda e: self._create_tag())

        # Color selector (simple button that cycles colors)
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

        # Tags list
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
        """Cycle to next color in palette."""
        self._color_index = (self._color_index + 1) % len(self.TAG_COLORS)
        self._selected_color = self.TAG_COLORS[self._color_index]
        self._color_btn.configure(fg_color=self._selected_color, hover_color=self._selected_color)

    def _create_tag(self):
        """Create a new tag."""
        name = self._name_entry.get().strip()
        if not name:
            return

        if self._on_create:
            self._on_create(name, self._selected_color)

        # Clear and refresh
        self._name_entry.delete(0, 'end')
        self._cycle_color()

    def _refresh_tags_list(self):
        """Refresh the tags list."""
        # Clear existing
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
        """Create a row for a single tag."""
        row = ctk.CTkFrame(self._tags_list, fg_color="transparent")
        row.pack(fill="x", pady=SPACING['xs'])

        # Color indicator
        color_indicator = ctk.CTkLabel(
            row,
            text=ICONS.get('tag', '\u2302'),
            font=ctk.CTkFont(size=14),
            text_color=tag.get('color', COLORS['accent']),
            width=24,
        )
        color_indicator.pack(side="left")

        # Name
        name_label = ctk.CTkLabel(
            row,
            text=tag.get('name', 'Tag'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
        )
        name_label.pack(side="left", fill="x", expand=True, padx=SPACING['sm'])

        # Delete button
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
        """Delete a tag."""
        if self._on_delete and tag_id:
            self._on_delete(tag_id)

    def set_tags(self, tags: List[Dict[str, Any]]):
        """Update the tags list."""
        self._tags = tags or []
        self._refresh_tags_list()
