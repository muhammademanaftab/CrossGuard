"""VS Code-style icon rail sidebar for navigation."""

from typing import Callable, Optional, Dict
import customtkinter as ctk

from ..theme import COLORS, SIDEBAR, ICONS, SPACING


class SidebarItem(ctk.CTkFrame):
    """Single nav item with icon, tooltip, and active indicator."""

    def __init__(
        self,
        master,
        icon: str,
        label: str,
        command: Optional[Callable] = None,
        is_active: bool = False,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="transparent",
            corner_radius=0,
            height=48,
            **kwargs
        )

        self.command = command
        self._is_active = is_active
        self._label = label

        self.pack_propagate(False)
        self.grid_propagate(False)

        # Left accent bar when active
        self.indicator = ctk.CTkFrame(
            self,
            width=3,
            height=32,
            fg_color=COLORS['sidebar_indicator'] if is_active else "transparent",
            corner_radius=0,
        )
        self.indicator.place(x=0, rely=0.5, anchor="w")

        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=20),
            text_color=COLORS['accent'] if is_active else COLORS['text_muted'],
            width=SIDEBAR['width_collapsed'],
            height=48,
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Need events on both the frame and the icon label
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.icon_label.bind("<Enter>", self._on_enter)
        self.icon_label.bind("<Leave>", self._on_leave)
        self.icon_label.bind("<Button-1>", self._on_click)

        self._tooltip = None

    def _on_enter(self, event):
        if not self._is_active:
            self.configure(fg_color=COLORS['sidebar_hover'])
            self.icon_label.configure(text_color=COLORS['text_secondary'])
        self._show_tooltip()

    def _on_leave(self, event):
        if not self._is_active:
            self.configure(fg_color="transparent")
            self.icon_label.configure(text_color=COLORS['text_muted'])
        self._hide_tooltip()

    def _on_click(self, event):
        if self.command:
            self.command()

    def _show_tooltip(self):
        if self._tooltip:
            return

        x = self.winfo_rootx() + self.winfo_width() + 5
        y = self.winfo_rooty() + self.winfo_height() // 2

        self._tooltip = ctk.CTkToplevel(self)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{x}+{y-12}")

        label = ctk.CTkLabel(
            self._tooltip,
            text=self._label,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
            fg_color=COLORS['bg_elevated'],
            corner_radius=4,
            padx=8,
            pady=4,
        )
        label.pack()

        self._tooltip.lift()
        self._tooltip.attributes('-topmost', True)

    def _hide_tooltip(self):
        if self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None

    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.configure(fg_color=COLORS['sidebar_active'])
            self.icon_label.configure(text_color=COLORS['accent'])
            self.indicator.configure(fg_color=COLORS['sidebar_indicator'])
        else:
            self.configure(fg_color="transparent")
            self.icon_label.configure(text_color=COLORS['text_muted'])
            self.indicator.configure(fg_color="transparent")


class Sidebar(ctk.CTkFrame):
    """VS Code-style sidebar with icon rail and bottom help link."""

    def __init__(
        self,
        master,
        on_navigate: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            width=SIDEBAR['width_collapsed'],
            fg_color=COLORS['sidebar_bg'],
            corner_radius=0,
            **kwargs
        )

        self.on_navigate = on_navigate
        self._current_view = "files"
        self._items: Dict[str, SidebarItem] = {}

        self.pack_propagate(False)
        self.grid_propagate(False)

        self._init_ui()

    def _init_ui(self):
        logo_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=56,
        )
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="\u25C7",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['accent'],
        )
        logo_label.place(relx=0.5, rely=0.5, anchor="center")

        separator = ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS['border'],
        )
        separator.pack(fill="x", padx=8)

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", pady=SPACING['sm'])

        nav_items = [
            ("files", ICONS['files'], "Files"),
            ("project", ICONS.get('project', '\U0001F4C1'), "Project"),
            ("results", ICONS['results'], "Results"),
            ("history", ICONS.get('history', '\u23F3'), "History"),
            ("settings", ICONS['settings'], "Settings"),
        ]

        for view_id, icon, label in nav_items:
            item = SidebarItem(
                nav_frame,
                icon=icon,
                label=label,
                command=lambda v=view_id: self._navigate(v),
                is_active=(view_id == self._current_view),
            )
            item.pack(fill="x")
            self._items[view_id] = item

        # Push help to the bottom
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        separator_bottom = ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS['border'],
        )
        separator_bottom.pack(fill="x", padx=8, side="bottom", pady=(0, SPACING['sm']))

        help_item = SidebarItem(
            self,
            icon=ICONS['help'],
            label="Help",
            command=lambda: self._navigate("help"),
        )
        help_item.pack(fill="x", side="bottom")
        self._items["help"] = help_item

    def _navigate(self, view_id: str):
        if view_id == self._current_view:
            return

        if self._current_view in self._items:
            self._items[self._current_view].set_active(False)

        self._current_view = view_id

        if view_id in self._items:
            self._items[view_id].set_active(True)

        if self.on_navigate:
            self.on_navigate(view_id)

    def set_active_view(self, view_id: str):
        self._navigate(view_id)

    def get_active_view(self) -> str:
        return self._current_view
