"""Browser selector with version dropdowns for picking target browsers."""

import json
from pathlib import Path
from typing import Dict, List, Set, Callable, Optional

import customtkinter as ctk

from ..theme import COLORS, SPACING


BROWSER_INFO = {
    'chrome': {'name': 'Chrome', 'icon': '\U0001F310', 'category': 'desktop'},
    'firefox': {'name': 'Firefox', 'icon': '\U0001F98A', 'category': 'desktop'},
    'safari': {'name': 'Safari', 'icon': '\U0001F9ED', 'category': 'desktop'},
    'edge': {'name': 'Edge', 'icon': '\U0001F537', 'category': 'desktop'},
    'opera': {'name': 'Opera', 'icon': '\U0001F534', 'category': 'desktop'},
    'ie': {'name': 'Internet Explorer', 'icon': '\U0001F4D8', 'category': 'desktop'},
    'ios_saf': {'name': 'Safari on iOS', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'android': {'name': 'Android Browser', 'icon': '\U0001F916', 'category': 'mobile'},
    'and_chr': {'name': 'Chrome for Android', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'and_ff': {'name': 'Firefox for Android', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'samsung': {'name': 'Samsung Internet', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'op_mini': {'name': 'Opera Mini', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'op_mob': {'name': 'Opera Mobile', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'and_uc': {'name': 'UC Browser', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'and_qq': {'name': 'QQ Browser', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'baidu': {'name': 'Baidu Browser', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'kaios': {'name': 'KaiOS Browser', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'bb': {'name': 'Blackberry Browser', 'icon': '\U0001F4F1', 'category': 'mobile'},
    'ie_mob': {'name': 'IE Mobile', 'icon': '\U0001F4F1', 'category': 'mobile'},
}

DEFAULT_SELECTED = {'chrome', 'firefox', 'safari', 'edge'}


def get_available_browsers() -> Dict[str, Dict]:
    """Load all browsers from the Can I Use database with their versions."""
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
                'icon': '\U0001F310',
                'category': 'other'
            })

            browsers[browser_id] = {
                'id': browser_id,
                'name': info['name'],
                'icon': info['icon'],
                'category': info['category'],
                'latest_version': latest_version,
                'all_versions': valid_versions,
            }

        return browsers

    except Exception as e:
        print(f"Error loading browsers: {e}")
        return {
            'chrome': {'id': 'chrome', 'name': 'Chrome', 'icon': '\U0001F310', 'category': 'desktop', 'latest_version': '120', 'all_versions': ['120']},
            'firefox': {'id': 'firefox', 'name': 'Firefox', 'icon': '\U0001F98A', 'category': 'desktop', 'latest_version': '120', 'all_versions': ['120']},
            'safari': {'id': 'safari', 'name': 'Safari', 'icon': '\U0001F9ED', 'category': 'desktop', 'latest_version': '17', 'all_versions': ['17']},
            'edge': {'id': 'edge', 'name': 'Edge', 'icon': '\U0001F537', 'category': 'desktop', 'latest_version': '120', 'all_versions': ['120']},
        }


class BrowserSelector(ctk.CTkFrame):
    """Browser selector with checkboxes and version dropdowns."""

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
        self._version_menus: Dict[str, ctk.CTkOptionMenu] = {}
        self._selected_versions: Dict[str, str] = {}
        self._expanded = False

        # Initialize selected versions to "Latest"
        for browser_id in self._selected:
            browser = self._browsers.get(browser_id, {})
            self._selected_versions[browser_id] = browser.get('latest_version', 'latest')

        self._init_ui()

    def _init_ui(self):
        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        ctk.CTkLabel(
            header_frame, text="Target Browsers",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS['text_primary'],
        ).pack(side="left")

        self._count_label = ctk.CTkLabel(
            header_frame, text=f"{len(self._selected)} selected",
            font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'],
        )
        self._count_label.pack(side="left", padx=(SPACING['sm'], 0))

        self._toggle_btn = ctk.CTkButton(
            header_frame, text="\u25BC Show All",
            font=ctk.CTkFont(size=11), fg_color="transparent",
            hover_color=COLORS['bg_light'], text_color=COLORS['accent'],
            width=100, height=28, command=self._toggle_expand,
        )
        self._toggle_btn.pack(side="right")

        # --- Quick select buttons ---
        quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

        for text, cmd in [("Desktop Only", self._select_desktop), ("Mobile Only", self._select_mobile),
                          ("All Browsers", self._select_all), ("Clear", self._clear_selection)]:
            ctk.CTkButton(
                quick_frame, text=text, font=ctk.CTkFont(size=10),
                fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_secondary'],
                width=90 if text != "Clear" else 60, height=26, command=cmd,
            ).pack(side="left", padx=(0, SPACING['xs']))

        # --- Compact view (badges with versions) ---
        self._compact_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._compact_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        self._update_compact_view()

        # --- Expanded browser list (hidden initially) ---
        self._expanded_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._create_browser_list()

    def _update_compact_view(self):
        for widget in self._compact_frame.winfo_children():
            widget.destroy()

        if not self._selected:
            ctk.CTkLabel(
                self._compact_frame, text="No browsers selected",
                font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'],
            ).pack(anchor="w")
            return

        row_frame = ctk.CTkFrame(self._compact_frame, fg_color="transparent")
        row_frame.pack(fill="x")

        for browser_id in sorted(self._selected):
            browser = self._browsers.get(browser_id, {})
            name = browser.get('name', browser_id)
            icon = browser.get('icon', '\U0001F310')
            version = self._selected_versions.get(browser_id, browser.get('latest_version', ''))
            latest = browser.get('latest_version', '')

            # Show version in badge, mark if not latest
            version_text = f"v{version}" if version != latest else "latest"
            badge_color = COLORS['bg_light'] if version == latest else COLORS['info']

            badge = ctk.CTkLabel(
                row_frame,
                text=f"{icon} {name} ({version_text})",
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_primary'],
                fg_color=badge_color,
                corner_radius=4, padx=8, pady=4,
            )
            badge.pack(side="left", padx=(0, SPACING['xs']), pady=2)

    def _create_browser_list(self):
        categories = {'desktop': [], 'mobile': [], 'other': []}

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

            ctk.CTkLabel(
                self._expanded_frame,
                text=category_names.get(category, category.title()),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_secondary'],
            ).pack(anchor="w", padx=SPACING['md'], pady=(SPACING['sm'], 4))

            list_frame = ctk.CTkFrame(self._expanded_frame, fg_color="transparent")
            list_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

            for browser_id, browser in sorted(browsers, key=lambda x: x[1]['name']):
                # One row per browser: [checkbox] [name] ... [version dropdown]
                row = ctk.CTkFrame(list_frame, fg_color=COLORS['bg_dark'], corner_radius=4, height=36)
                row.pack(fill="x", pady=1)
                row.pack_propagate(False)

                checkbox = ctk.CTkCheckBox(
                    row,
                    text=f"{browser['icon']}  {browser['name']}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text_secondary'],
                    fg_color=COLORS['accent'],
                    hover_color=COLORS['accent_bright'],
                    border_color=COLORS['border'],
                    checkbox_width=18, checkbox_height=18,
                    command=lambda bid=browser_id: self._on_browser_toggle(bid),
                )
                checkbox.pack(side="left", padx=(8, 0))

                if browser_id in self._selected:
                    checkbox.select()

                self._checkboxes[browser_id] = checkbox

                # Version dropdown on the right
                all_versions = browser.get('all_versions', [])
                latest = browser.get('latest_version', 'latest')

                version_choices = [f"Latest ({latest})"]
                recent = all_versions
                for v in reversed(recent):
                    if v != latest:
                        version_choices.append(str(v))

                current_version = self._selected_versions.get(browser_id, latest)
                current_display = f"Latest ({latest})" if current_version == latest else str(current_version)

                version_menu = ctk.CTkOptionMenu(
                    row,
                    values=version_choices,
                    width=130, height=26,
                    font=ctk.CTkFont(size=10),
                    fg_color=COLORS['bg_medium'],
                    button_color=COLORS['bg_light'],
                    button_hover_color=COLORS['hover_bg'],
                    dropdown_fg_color=COLORS['bg_elevated'],
                    dropdown_hover_color=COLORS['hover_bg'],
                    text_color=COLORS['text_muted'],
                    command=lambda val, bid=browser_id: self._on_version_change(bid, val),
                )
                version_menu.set(current_display)
                version_menu.pack(side="right", padx=6, pady=4)

                self._version_menus[browser_id] = version_menu

    def _on_version_change(self, browser_id: str, value: str):
        """Handle version dropdown change."""
        browser = self._browsers.get(browser_id, {})
        latest = browser.get('latest_version', 'latest')

        if value.startswith("Latest"):
            self._selected_versions[browser_id] = latest
        else:
            self._selected_versions[browser_id] = value

        # Auto-select the browser if not already selected
        if browser_id not in self._selected:
            self._selected.add(browser_id)
            if browser_id in self._checkboxes:
                self._checkboxes[browser_id].select()
            self._update_count()

        self._notify_change()

    def _toggle_expand(self):
        self._expanded = not self._expanded

        if self._expanded:
            self._toggle_btn.configure(text="\u25B2 Show Less")
            self._compact_frame.pack_forget()
            self._expanded_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        else:
            self._toggle_btn.configure(text="\u25BC Show All")
            self._expanded_frame.pack_forget()
            self._compact_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
            self._update_compact_view()

    def _on_browser_toggle(self, browser_id: str):
        if browser_id in self._selected:
            self._selected.discard(browser_id)
        else:
            self._selected.add(browser_id)
            # Set default version if not already set
            if browser_id not in self._selected_versions:
                browser = self._browsers.get(browser_id, {})
                self._selected_versions[browser_id] = browser.get('latest_version', 'latest')

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
                self._selected_versions[browser_id] = browser.get('latest_version', 'latest')
                if browser_id in self._checkboxes:
                    self._checkboxes[browser_id].select()
                if browser_id in self._version_menus:
                    self._version_menus[browser_id].set(f"Latest ({browser.get('latest_version', '')})")
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
                self._selected_versions[browser_id] = browser.get('latest_version', 'latest')
                if browser_id in self._checkboxes:
                    self._checkboxes[browser_id].select()
                if browser_id in self._version_menus:
                    self._version_menus[browser_id].set(f"Latest ({browser.get('latest_version', '')})")
            else:
                if browser_id in self._checkboxes:
                    self._checkboxes[browser_id].deselect()

        self._update_count()
        self._update_compact_view()
        self._notify_change()

    def _select_all(self):
        self._selected = set(self._browsers.keys())
        for browser_id, browser in self._browsers.items():
            self._selected_versions[browser_id] = browser.get('latest_version', 'latest')
            if browser_id in self._checkboxes:
                self._checkboxes[browser_id].select()
            if browser_id in self._version_menus:
                self._version_menus[browser_id].set(f"Latest ({browser.get('latest_version', '')})")

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
        """Returns {browser_id: version} for all selected browsers."""
        result = {}
        for browser_id in self._selected:
            browser = self._browsers.get(browser_id, {})
            version = self._selected_versions.get(browser_id, browser.get('latest_version', 'latest'))
            result[browser_id] = version
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
