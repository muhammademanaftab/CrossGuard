"""
ProjectTreeWidget - Interactive file tree for project scanning.

Displays a hierarchical view of project files with checkboxes for selection,
expand/collapse functionality, and file type icons.
"""

from typing import Callable, Dict, List, Optional, Set
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS, get_file_type_color


class TreeItemWidget(ctk.CTkFrame):
    """A single item in the file tree (file or directory)."""

    def __init__(
        self,
        master,
        name: str,
        path: str,
        is_directory: bool,
        file_type: Optional[str] = None,
        is_excluded: bool = False,
        is_minified: bool = False,
        level: int = 0,
        is_selected: bool = True,
        has_children: bool = False,
        is_expanded: bool = False,
        on_toggle_expand: Optional[Callable[['TreeItemWidget'], None]] = None,
        on_toggle_select: Optional[Callable[['TreeItemWidget', bool], None]] = None,
        **kwargs
    ):
        """Initialize a tree item.

        Args:
            master: Parent widget
            name: File/directory name
            path: Full path
            is_directory: Whether this is a directory
            file_type: Type of file ('html', 'css', 'javascript')
            is_excluded: Whether this item is excluded
            is_minified: Whether this file is minified
            level: Nesting level (for indentation)
            is_selected: Whether file is selected for scanning
            has_children: Whether directory has children
            is_expanded: Whether directory is expanded
            on_toggle_expand: Callback when expand is toggled
            on_toggle_select: Callback when selection is toggled
        """
        super().__init__(
            master,
            fg_color="transparent",
            height=28,
            **kwargs
        )

        self.name = name
        self.path = path
        self.is_directory = is_directory
        self.file_type = file_type
        self.is_excluded = is_excluded
        self.is_minified = is_minified
        self.level = level
        self._is_selected = is_selected
        self.has_children = has_children
        self._is_expanded = is_expanded
        self._on_toggle_expand = on_toggle_expand
        self._on_toggle_select = on_toggle_select

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        self.pack_propagate(False)

        # Container for horizontal layout
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", expand=True)

        # Indentation
        indent = self.level * 20 + 8
        spacer = ctk.CTkFrame(container, fg_color="transparent", width=indent)
        spacer.pack(side="left")
        spacer.pack_propagate(False)

        # Expand/collapse button (for directories with children)
        if self.is_directory and self.has_children and not self.is_excluded:
            self.expand_btn = ctk.CTkButton(
                container,
                text=ICONS['chevron_down'] if self._is_expanded else ICONS['chevron_right'],
                width=20,
                height=20,
                fg_color="transparent",
                hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_muted'],
                font=ctk.CTkFont(size=10),
                command=self._on_expand_click,
            )
            self.expand_btn.pack(side="left")
        else:
            # Placeholder for alignment
            placeholder = ctk.CTkFrame(container, fg_color="transparent", width=20)
            placeholder.pack(side="left")
            placeholder.pack_propagate(False)

        # Checkbox (only for files, not excluded items)
        if not self.is_directory and not self.is_excluded:
            self.checkbox = ctk.CTkCheckBox(
                container,
                text="",
                width=20,
                height=20,
                checkbox_width=16,
                checkbox_height=16,
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_bright'],
                border_color=COLORS['border_light'],
                command=self._on_checkbox_change,
            )
            if self._is_selected:
                self.checkbox.select()
            self.checkbox.pack(side="left", padx=(2, 4))
        else:
            # Placeholder
            placeholder = ctk.CTkFrame(container, fg_color="transparent", width=24)
            placeholder.pack(side="left")
            placeholder.pack_propagate(False)

        # Icon
        icon = self._get_icon()
        icon_color = self._get_icon_color()

        self.icon_label = ctk.CTkLabel(
            container,
            text=icon,
            font=ctk.CTkFont(size=14),
            text_color=icon_color,
            width=20,
        )
        self.icon_label.pack(side="left")

        # Name label
        name_color = COLORS['text_muted'] if self.is_excluded else COLORS['text_primary']
        name_style = "italic" if self.is_minified else "normal"

        self.name_label = ctk.CTkLabel(
            container,
            text=self.name,
            font=ctk.CTkFont(size=12),
            text_color=name_color,
            anchor="w",
        )
        self.name_label.pack(side="left", padx=(4, 0))

        # Status badge (excluded/minified)
        if self.is_excluded:
            badge = ctk.CTkLabel(
                container,
                text="excluded",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_muted'],
                fg_color=COLORS['bg_light'],
                corner_radius=4,
                padx=4,
                pady=1,
            )
            badge.pack(side="left", padx=(8, 0))
        elif self.is_minified:
            badge = ctk.CTkLabel(
                container,
                text="minified",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['warning'],
                fg_color=COLORS['warning_muted'],
                corner_radius=4,
                padx=4,
                pady=1,
            )
            badge.pack(side="left", padx=(8, 0))

        # Hover effect
        if not self.is_excluded:
            self.bind("<Enter>", self._on_hover_enter)
            self.bind("<Leave>", self._on_hover_leave)
            container.bind("<Enter>", self._on_hover_enter)
            container.bind("<Leave>", self._on_hover_leave)

    def _get_icon(self) -> str:
        """Get the appropriate icon for this item."""
        if self.is_directory:
            if self.is_excluded:
                return ICONS.get('folder', '\U0001F4C1')
            return ICONS.get('folder_open', '\U0001F4C2') if self._is_expanded else ICONS.get('folder', '\U0001F4C1')

        # File icons by type
        icons = {
            'html': ICONS.get('html', '\u25B6'),
            'css': ICONS.get('css', '\u25C6'),
            'javascript': ICONS.get('js', '\u2605'),
        }
        return icons.get(self.file_type, ICONS.get('file', '\u25A0'))

    def _get_icon_color(self) -> str:
        """Get the icon color."""
        if self.is_excluded:
            return COLORS['text_muted']

        if self.is_directory:
            return COLORS['warning']  # Folder color

        return get_file_type_color(self.file_type or 'file')

    def _on_expand_click(self):
        """Handle expand button click."""
        self._is_expanded = not self._is_expanded
        self.expand_btn.configure(
            text=ICONS['chevron_down'] if self._is_expanded else ICONS['chevron_right']
        )
        # Update folder icon
        self.icon_label.configure(text=self._get_icon())

        if self._on_toggle_expand:
            self._on_toggle_expand(self)

    def _on_checkbox_change(self):
        """Handle checkbox change."""
        self._is_selected = self.checkbox.get() == 1
        if self._on_toggle_select:
            self._on_toggle_select(self, self._is_selected)

    def _on_hover_enter(self, event=None):
        """Handle mouse enter."""
        self.configure(fg_color=COLORS['hover_bg'])

    def _on_hover_leave(self, event=None):
        """Handle mouse leave."""
        self.configure(fg_color="transparent")

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool):
        self._is_selected = value
        if hasattr(self, 'checkbox'):
            if value:
                self.checkbox.select()
            else:
                self.checkbox.deselect()

    @property
    def is_expanded(self) -> bool:
        return self._is_expanded


class ProjectTreeWidget(ctk.CTkFrame):
    """Interactive file tree widget for project scanning."""

    def __init__(
        self,
        master,
        on_selection_change: Optional[Callable[[int], None]] = None,
        max_height: int = 400,
        **kwargs
    ):
        """Initialize the project tree widget.

        Args:
            master: Parent widget
            on_selection_change: Callback when selection changes (receives selected count)
            max_height: Maximum height of the tree view
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._on_selection_change = on_selection_change
        self._max_height = max_height
        self._tree_data = None  # FileTreeNode
        self._item_widgets: Dict[str, TreeItemWidget] = {}  # path -> widget
        self._expanded_paths: Set[str] = set()
        self._selected_paths: Set[str] = set()

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))

        title = ctk.CTkLabel(
            header,
            text="Project Files",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title.pack(side="left")

        # Select all / Deselect all buttons
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        self.select_all_btn = ctk.CTkButton(
            btn_frame,
            text="Select All",
            width=70,
            height=24,
            fg_color="transparent",
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['accent'],
            font=ctk.CTkFont(size=11),
            command=self._select_all,
        )
        self.select_all_btn.pack(side="left", padx=(0, 4))

        self.deselect_all_btn = ctk.CTkButton(
            btn_frame,
            text="Deselect All",
            width=80,
            height=24,
            fg_color="transparent",
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_muted'],
            font=ctk.CTkFont(size=11),
            command=self._deselect_all,
        )
        self.deselect_all_btn.pack(side="left")

        # Separator
        sep = ctk.CTkFrame(self, fg_color=COLORS['border'], height=1)
        sep.pack(fill="x", padx=SPACING['md'])

        # Scrollable tree container
        self.tree_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            height=self._max_height,
        )
        self.tree_container.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])

        # Selection count label
        self.count_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.count_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))

        self.count_label = ctk.CTkLabel(
            self.count_frame,
            text="No files selected",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self.count_label.pack(side="left")

    def set_tree(self, tree_node):
        """
        Set the file tree data and render it.

        Args:
            tree_node: FileTreeNode root to display
        """
        self._tree_data = tree_node
        self._item_widgets.clear()
        self._selected_paths.clear()

        # Clear existing widgets
        for widget in self.tree_container.winfo_children():
            widget.destroy()

        if tree_node is None:
            return

        # Render tree
        self._render_node(tree_node, level=0)
        self._update_count()

    def _render_node(self, node, level: int):
        """Recursively render a tree node and its children."""
        # Skip root node name, show children directly
        if level == 0:
            # Expand root by default
            self._expanded_paths.add(node.path)
            for child in node.children:
                self._render_node(child, 1)  # Start children at level 1
            return

        # Create widget for this node
        widget = TreeItemWidget(
            self.tree_container,
            name=node.name,
            path=node.path,
            is_directory=node.is_directory,
            file_type=node.file_type,
            is_excluded=node.is_excluded,
            is_minified=node.is_minified,
            level=level,
            is_selected=node.is_selected,
            has_children=bool(node.children),
            is_expanded=node.path in self._expanded_paths,
            on_toggle_expand=self._on_item_expand,
            on_toggle_select=self._on_item_select,
        )
        widget.pack(fill="x")
        self._item_widgets[node.path] = widget

        # Track selected files
        if not node.is_directory and not node.is_excluded and node.is_selected:
            self._selected_paths.add(node.path)

        # Render children if expanded
        if node.is_directory and node.path in self._expanded_paths:
            for child in node.children:
                self._render_node(child, level + 1)

    def _on_item_expand(self, item: TreeItemWidget):
        """Handle item expand/collapse."""
        if item.is_expanded:
            self._expanded_paths.add(item.path)
        else:
            self._expanded_paths.discard(item.path)

        # Re-render tree to show/hide children
        self.set_tree(self._tree_data)

    def _on_item_select(self, item: TreeItemWidget, is_selected: bool):
        """Handle item selection change."""
        if is_selected:
            self._selected_paths.add(item.path)
        else:
            self._selected_paths.discard(item.path)

        # Also update the underlying node
        node = self._find_node(self._tree_data, item.path)
        if node:
            node.is_selected = is_selected

        self._update_count()

    def _find_node(self, root, path: str):
        """Find a node by path in the tree."""
        if root is None:
            return None
        if root.path == path:
            return root
        for child in root.children:
            found = self._find_node(child, path)
            if found:
                return found
        return None

    def _update_count(self):
        """Update the selection count label."""
        count = len(self._selected_paths)
        if count == 0:
            self.count_label.configure(text="No files selected")
        elif count == 1:
            self.count_label.configure(text="1 file selected")
        else:
            self.count_label.configure(text=f"{count} files selected")

        if self._on_selection_change:
            self._on_selection_change(count)

    def _select_all(self):
        """Select all files."""
        self._select_all_recursive(self._tree_data, True)
        self.set_tree(self._tree_data)  # Re-render

    def _deselect_all(self):
        """Deselect all files."""
        self._select_all_recursive(self._tree_data, False)
        self.set_tree(self._tree_data)  # Re-render

    def _select_all_recursive(self, node, selected: bool):
        """Recursively set selection state."""
        if node is None:
            return
        if not node.is_directory and not node.is_excluded:
            node.is_selected = selected
        for child in node.children:
            self._select_all_recursive(child, selected)

    def get_selected_files(self) -> Dict[str, List[str]]:
        """
        Get all selected files organized by type.

        Returns:
            Dict with 'html', 'css', 'javascript' lists
        """
        files = {'html': [], 'css': [], 'javascript': []}
        self._collect_selected_files(self._tree_data, files)
        return files

    def _collect_selected_files(self, node, files: Dict[str, List[str]]):
        """Recursively collect selected files."""
        if node is None:
            return
        if not node.is_directory and not node.is_excluded and node.is_selected:
            if node.file_type and node.file_type in files:
                files[node.file_type].append(node.path)
        for child in node.children:
            self._collect_selected_files(child, files)

    def get_selected_count(self) -> int:
        """Get count of selected files."""
        return len(self._selected_paths)

    def expand_all(self):
        """Expand all directories."""
        self._expand_all_recursive(self._tree_data)
        self.set_tree(self._tree_data)

    def _expand_all_recursive(self, node):
        """Recursively expand all directories."""
        if node is None:
            return
        if node.is_directory and not node.is_excluded:
            self._expanded_paths.add(node.path)
        for child in node.children:
            self._expand_all_recursive(child)

    def collapse_all(self):
        """Collapse all directories."""
        self._expanded_paths.clear()
        if self._tree_data:
            self._expanded_paths.add(self._tree_data.path)  # Keep root expanded
        self.set_tree(self._tree_data)
