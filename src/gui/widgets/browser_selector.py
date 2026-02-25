"""Browser selector for picking target browsers to check compatibility against."""

import json
from pathlib import Path
from typing import Dict, List, Set, Callable, Optional

import customtkinter as ctk

from ..theme import COLORS, SPACING


BROWSER_INFO = {
    'chrome': {'name': 'Chrome', 'icon': '🌐', 'category': 'desktop'},
    'firefox': {'name': 'Firefox', 'icon': '🦊', 'category': 'desktop'},
    'safari': {'name': 'Safari', 'icon': '🧭', 'category': 'desktop'},
    'edge': {'name': 'Edge', 'icon': '🔷', 'category': 'desktop'},
    'opera': {'name': 'Opera', 'icon': '🔴', 'category': 'desktop'},
    'ie': {'name': 'Internet Explorer', 'icon': '📘', 'category': 'desktop'},
    'ios_saf': {'name': 'Safari on iOS', 'icon': '📱', 'category': 'mobile'},
    'android': {'name': 'Android Browser', 'icon': '🤖', 'category': 'mobile'},
    'and_chr': {'name': 'Chrome for Android', 'icon': '📱', 'category': 'mobile'},
    'and_ff': {'name': 'Firefox for Android', 'icon': '📱', 'category': 'mobile'},
    'samsung': {'name': 'Samsung Internet', 'icon': '📱', 'category': 'mobile'},
    'op_mini': {'name': 'Opera Mini', 'icon': '📱', 'category': 'mobile'},
    'op_mob': {'name': 'Opera Mobile', 'icon': '📱', 'category': 'mobile'},
    'and_uc': {'name': 'UC Browser', 'icon': '📱', 'category': 'mobile'},
    'and_qq': {'name': 'QQ Browser', 'icon': '📱', 'category': 'mobile'},
    'baidu': {'name': 'Baidu Browser', 'icon': '📱', 'category': 'mobile'},
    'kaios': {'name': 'KaiOS Browser', 'icon': '📱', 'category': 'mobile'},
    'bb': {'name': 'Blackberry Browser', 'icon': '📱', 'category': 'mobile'},
    'ie_mob': {'name': 'IE Mobile', 'icon': '📱', 'category': 'mobile'},
}

DEFAULT_SELECTED = {'chrome', 'firefox', 'safari', 'edge'}


def get_available_browsers() -> Dict[str, Dict]:
    """Load all browsers from the Can I Use database with their latest versions."""
    try:
        from src.utils.config import CANIUSE_DB_PATH

        with open(CANIUSE_DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        agents = data.get('agents', {})
        browsers = {}

        for browser_id, browser_data in agents.items():
            versions = browser_data.get('versions', [])
            valid_versions = [v for v in versions if v]
            latest_version = valid_versions[-1] if valid_versions else 'latest'

            info = BROWSER_INFO.get(browser_id, {
                'name': browser_data.get('browser', browser_id),
                'icon': '🌐',
                'category': 'other'
            })

            browsers[browser_id] = {
                'id': browser_id,
                'name': info['name'],
                'icon': info['icon'],
                'category': info['category'],
                'latest_version': latest_version,
                'all_versions': valid_versions[-10:] if valid_versions else [],
            }

        return browsers

    except Exception as e:
        print(f"Error loading browsers: {e}")
        # Fallback defaults if DB is unavailable
        return {
            'chrome': {'id': 'chrome', 'name': 'Chrome', 'icon': '🌐', 'category': 'desktop', 'latest_version': '120'},
            'firefox': {'id': 'firefox', 'name': 'Firefox', 'icon': '🦊', 'category': 'desktop', 'latest_version': '120'},
            'safari': {'id': 'safari', 'name': 'Safari', 'icon': '🧭', 'category': 'desktop', 'latest_version': '17'},
            'edge': {'id': 'edge', 'name': 'Edge', 'icon': '🔷', 'category': 'desktop', 'latest_version': '120'},
        }


class BrowserSelector(ctk.CTkFrame):
    """Lets users pick which browsers to check, organized by category."""

    def __init__(
        self,
        master,
        on_selection_change: Optional[Callable[[Dict[str, str]], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS.get('bg_medium', '#1e293b'),
            corner_radius=8,
            **kwargs
        )

        self._on_selection_change = on_selection_change
        self._browsers = get_available_browsers()
        self._selected: Set[str] = set(DEFAULT_SELECTED)
        self._checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        self._expanded = False

        self._init_ui()

    def _init_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        title_label = ctk.CTkLabel(
            header_frame,
            text="Target Browsers",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title_label.pack(side="left")

        self._count_label = ctk.CTkLabel(
            header_frame,
            text=f"{len(self._selected)} selected",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self._count_label.pack(side="left", padx=(SPACING['sm'], 0))

        self._toggle_btn = ctk.CTkButton(
            header_frame,
            text="▼ Show All",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=COLORS['bg_light'],
            text_color=COLORS['accent'],
            width=100,
            height=28,
            command=self._toggle_expand,
        )
        self._toggle_btn.pack(side="right")

        quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

        ctk.CTkButton(
            quick_frame,
            text="Desktop Only",
            font=ctk.CTkFont(size=10),
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_secondary'],
            width=90,
            height=26,
            command=self._select_desktop,
        ).pack(side="left", padx=(0, SPACING['xs']))

        ctk.CTkButton(
            quick_frame,
            text="Mobile Only",
            font=ctk.CTkFont(size=10),
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_secondary'],
            width=90,
            height=26,
            command=self._select_mobile,
        ).pack(side="left", padx=(0, SPACING['xs']))

        ctk.CTkButton(
            quick_frame,
            text="All Browsers",
            font=ctk.CTkFont(size=10),
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_secondary'],
            width=90,
            height=26,
            command=self._select_all,
        ).pack(side="left", padx=(0, SPACING['xs']))

        ctk.CTkButton(
            quick_frame,
            text="Clear",
            font=ctk.CTkFont(size=10),
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_secondary'],
            width=60,
            height=26,
            command=self._clear_selection,
        ).pack(side="left")

        # Compact view shows selected browsers as badges
        self._compact_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._compact_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        self._update_compact_view()

        # Full browser list, hidden until expanded
        self._expanded_frame = ctk.CTkFrame(self, fg_color="transparent")

        self._create_browser_list()

    def _update_compact_view(self):
        for widget in self._compact_frame.winfo_children():
            widget.destroy()

        if not self._selected:
            ctk.CTkLabel(
                self._compact_frame,
                text="No browsers selected",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted'],
            ).pack(anchor="w")
            return

        row_frame = ctk.CTkFrame(self._compact_frame, fg_color="transparent")
        row_frame.pack(fill="x")

        for browser_id in sorted(self._selected):
            browser = self._browsers.get(browser_id, {})
            name = browser.get('name', browser_id)
            icon = browser.get('icon', '🌐')

            badge = ctk.CTkLabel(
                row_frame,
                text=f"{icon} {name}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_primary'],
                fg_color=COLORS['bg_light'],
                corner_radius=4,
                padx=8,
                pady=4,
            )
            badge.pack(side="left", padx=(0, SPACING['xs']), pady=2)

    def _create_browser_list(self):
        categories = {
            'desktop': [],
            'mobile': [],
            'other': [],
        }

        for browser_id, browser in self._browsers.items():
            category = browser.get('category', 'other')
            if category not in categories:
                category = 'other'
            categories[category].append((browser_id, browser))

        category_names = {
            'desktop': 'Desktop Browsers',
            'mobile': 'Mobile Browsers',
            'other': 'Other Browsers',
        }

        for category, browsers in categories.items():
            if not browsers:
                continue

            cat_label = ctk.CTkLabel(
                self._expanded_frame,
                text=category_names.get(category, category.title()),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_secondary'],
            )
            cat_label.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['xs']))

            grid_frame = ctk.CTkFrame(self._expanded_frame, fg_color="transparent")
            grid_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

            # 3-column grid layout
            for idx, (browser_id, browser) in enumerate(sorted(browsers, key=lambda x: x[1]['name'])):
                col = idx % 3

                if col == 0:
                    row_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
                    row_frame.pack(fill="x", pady=2)
                    self._current_row = row_frame
                else:
                    row_frame = self._current_row

                checkbox = ctk.CTkCheckBox(
                    row_frame,
                    text=f"{browser['icon']} {browser['name']}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text_secondary'],
                    fg_color=COLORS['accent'],
                    hover_color=COLORS['accent_bright'],
                    border_color=COLORS['border'],
                    width=200,
                    command=lambda bid=browser_id: self._on_browser_toggle(bid),
                )
                checkbox.pack(side="left", padx=(0, SPACING['sm']))

                if browser_id in self._selected:
                    checkbox.select()

                self._checkboxes[browser_id] = checkbox

    def _toggle_expand(self):
        self._expanded = not self._expanded

        if self._expanded:
            self._toggle_btn.configure(text="▲ Show Less")
            self._compact_frame.pack_forget()
            self._expanded_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        else:
            self._toggle_btn.configure(text="▼ Show All")
            self._expanded_frame.pack_forget()
            self._compact_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
            self._update_compact_view()

    def _on_browser_toggle(self, browser_id: str):
        if browser_id in self._selected:
            self._selected.discard(browser_id)
        else:
            self._selected.add(browser_id)

        self._update_count()
        self._notify_change()

    def _update_count(self):
        self._count_label.configure(text=f"{len(self._selected)} selected")

    def _notify_change(self):
        if self._on_selection_change:
            self._on_selection_change(self.get_selected_browsers())

    def _select_desktop(self):
        self._selected.clear()
        for browser_id, browser in self._browsers.items():
            if browser.get('category') == 'desktop':
                self._selected.add(browser_id)
                if browser_id in self._checkboxes:
                    self._checkboxes[browser_id].select()
            else:
                if browser_id in self._checkboxes:
                    self._checkboxes[browser_id].deselect()

        self._update_count()
        self._update_compact_view()
        self._notify_change()

    def _select_mobile(self):
        self._selected.clear()
        for browser_id, browser in self._browsers.items():
            if browser.get('category') == 'mobile':
                self._selected.add(browser_id)
                if browser_id in self._checkboxes:
                    self._checkboxes[browser_id].select()
            else:
                if browser_id in self._checkboxes:
                    self._checkboxes[browser_id].deselect()

        self._update_count()
        self._update_compact_view()
        self._notify_change()

    def _select_all(self):
        self._selected = set(self._browsers.keys())
        for checkbox in self._checkboxes.values():
            checkbox.select()

        self._update_count()
        self._update_compact_view()
        self._notify_change()

    def _clear_selection(self):
        self._selected.clear()
        for checkbox in self._checkboxes.values():
            checkbox.deselect()

        self._update_count()
        self._update_compact_view()
        self._notify_change()

    def get_selected_browsers(self) -> Dict[str, str]:
        """Returns {browser_id: latest_version} for all selected browsers."""
        result = {}
        for browser_id in self._selected:
            browser = self._browsers.get(browser_id, {})
            result[browser_id] = browser.get('latest_version', 'latest')
        return result

    def set_selected_browsers(self, browser_ids: List[str]):
        self._selected = set(browser_ids) & set(self._browsers.keys())

        for browser_id, checkbox in self._checkboxes.items():
            if browser_id in self._selected:
                checkbox.select()
            else:
                checkbox.deselect()

        self._update_count()
        self._update_compact_view()
