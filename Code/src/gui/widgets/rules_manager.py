"""Rules manager dialog -- browse, add, edit, and delete feature detection rules."""

import json
from pathlib import Path
from typing import Dict, Optional, Callable, List, Tuple

import customtkinter as ctk

from ..theme import COLORS, SPACING, enable_smooth_scrolling
from .messagebox import show_info, show_error, show_warning, ask_question

from ...api import get_analyzer_service


HTML_TYPES = ['Elements', 'Attributes', 'Input Types', 'Attribute Values']

POLYFILL_TYPES = ['JavaScript', 'CSS', 'HTML']


def _category_for(feature_id: str, categories: Dict) -> str:
    for cat_name, cat_features in categories.items():
        if feature_id in cat_features:
            return cat_name
    return 'Custom'


class RulesManagerDialog(ctk.CTkToplevel):
    """Modal dialog for browsing and managing all feature detection rules."""

    def __init__(self, parent, on_rules_changed: Optional[Callable] = None):
        super().__init__(parent)

        self.parent = parent
        self.on_rules_changed = on_rules_changed
        self._service = get_analyzer_service()
        self._custom_rules = self._service.get_custom_rules()
        self._catalogs = self._service.get_feature_catalogs()
        self._css_categories = self._catalogs['css']['categories']
        self._js_categories = self._catalogs['js']['categories']
        self._all_css = self._catalogs['css']['all']
        self._all_js = self._catalogs['js']['all']
        self._html_elements = self._catalogs['html']['elements']
        self._html_attributes = self._catalogs['html']['attributes']
        self._html_input_types = self._catalogs['html']['input_types']
        self._html_attribute_values = self._catalogs['html']['attribute_values']
        self._selected_rule_id = None
        self._selected_category = "css"
        self._search_var = ctk.StringVar()
        self._category_filter_var = ctk.StringVar(value="All")
        self._html_type_filter_var = ctk.StringVar(value="All")
        self._polyfill_type_filter_var = ctk.StringVar(value="All")
        self._polyfill_data = self._service.get_polyfill_map()

        self.title("Feature Detection Rules")
        self.configure(fg_color=COLORS['bg_dark'])
        self.geometry("1000x700")
        self.minsize(900, 600)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_on_parent()

        self._search_var.trace_add('write', lambda *args: self._refresh_rules_list())

    def _form_field(
        self,
        label: str,
        placeholder: str = "",
        initial: str = "",
        *,
        textbox: bool = False,
        textbox_height: int = 100,
        bottom_pad: int = 15,
    ):
        """Label + entry (or textbox) pair, matching the form styling used across all rules forms."""
        ctk.CTkLabel(
            self._details_frame,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        if textbox:
            widget = ctk.CTkTextbox(
                self._details_frame,
                font=ctk.CTkFont(size=11, family="Courier"),
                height=textbox_height,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                border_width=1,
            )
            widget.pack(fill="x", pady=(0, bottom_pad))
            if initial:
                widget.insert("1.0", initial)
        else:
            widget = ctk.CTkEntry(
                self._details_frame,
                placeholder_text=placeholder,
                font=ctk.CTkFont(size=12),
                height=36,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
            )
            widget.pack(fill="x", pady=(0, bottom_pad))
            if initial:
                widget.insert(0, initial)

        return widget

    def _center_on_parent(self):
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()

        w = self.winfo_width()
        h = self.winfo_height()

        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2

        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        self._build_header()

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self._build_tab_bar(main_frame)
        self._build_filter_bar(main_frame)

        split_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, pady=(10, 0))

        self._build_rules_list_panel(split_frame)
        self._build_details_panel(split_frame)

        self._refresh_rules_list()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'], corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="Feature Detection Rules",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left", padx=20, pady=15)

        close_btn = ctk.CTkButton(
            header,
            text="X",
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['danger'],
            text_color=COLORS['text_primary'],
            command=self.destroy,
        )
        close_btn.pack(side="right", padx=15, pady=10)

    def _build_tab_bar(self, parent):
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, 10))

        self._tab_buttons = {}
        for category in ["css", "javascript", "html", "polyfills"]:
            btn = ctk.CTkButton(
                tab_frame,
                text=category.upper(),
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                height=35,
                corner_radius=6,
                fg_color=COLORS['accent'] if category == "css" else COLORS['bg_medium'],
                hover_color=COLORS['accent_dim'],
                command=lambda c=category: self._select_tab(c),
            )
            btn.pack(side="left", padx=(0, 8))
            self._tab_buttons[category] = btn

    def _build_filter_bar(self, parent):
        filter_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8)
        filter_frame.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(filter_frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        search_frame = ctk.CTkFrame(inner, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(side="left", padx=(0, 8))

        self._search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self._search_var,
            placeholder_text="Search rules...",
            width=250,
            height=32,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        self._search_entry.pack(side="left")

        # Filter dropdown changes based on active tab (CSS categories vs HTML types)
        filter_right = ctk.CTkFrame(inner, fg_color="transparent")
        filter_right.pack(side="right")

        self._filter_label = ctk.CTkLabel(
            filter_right,
            text="Category:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        )
        self._filter_label.pack(side="left", padx=(0, 8))

        self._category_dropdown = ctk.CTkOptionMenu(
            filter_right,
            variable=self._category_filter_var,
            values=["All"] + list(self._css_categories.keys()),
            width=160,
            height=32,
            fg_color=COLORS['input_bg'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_dim'],
            dropdown_fg_color=COLORS['bg_medium'],
            command=lambda _: self._refresh_rules_list(),
        )
        self._category_dropdown.pack(side="left")

        # Hidden by default, shown on HTML tab
        self._html_type_dropdown = ctk.CTkOptionMenu(
            filter_right,
            variable=self._html_type_filter_var,
            values=["All"] + HTML_TYPES,
            width=160,
            height=32,
            fg_color=COLORS['input_bg'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_dim'],
            dropdown_fg_color=COLORS['bg_medium'],
            command=lambda _: self._refresh_rules_list(),
        )

        # Hidden by default, shown on Polyfills tab
        self._polyfill_type_dropdown = ctk.CTkOptionMenu(
            filter_right,
            variable=self._polyfill_type_filter_var,
            values=["All"] + POLYFILL_TYPES,
            width=160,
            height=32,
            fg_color=COLORS['input_bg'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_dim'],
            dropdown_fg_color=COLORS['bg_medium'],
            command=lambda _: self._refresh_rules_list(),
        )

    def _build_rules_list_panel(self, parent):
        left_panel = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8, width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        header_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        self._rules_count_label = ctk.CTkLabel(
            header_frame,
            text="RULES (0)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_muted'],
        )
        self._rules_count_label.pack(side="left")

        self._add_btn = ctk.CTkButton(
            header_frame,
            text="+",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=28,
            height=28,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dim'],
            text_color=COLORS['bg_darkest'],
            corner_radius=6,
            command=self._show_add_form,
        )
        self._add_btn.pack(side="right")

        self._rules_list_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color=COLORS['bg_light'],
            corner_radius=6,
        )
        self._rules_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        enable_smooth_scrolling(self._rules_list_frame)

    def _build_details_panel(self, parent):
        self._details_panel = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8)
        self._details_panel.pack(side="right", fill="both", expand=True)

        self._details_frame = ctk.CTkScrollableFrame(
            self._details_panel,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        self._details_frame.pack(fill="both", expand=True, padx=15, pady=15)
        enable_smooth_scrolling(self._details_frame)

        self._show_details_placeholder()

    def _select_tab(self, category: str):
        self._selected_category = category
        self._selected_rule_id = None
        self._search_var.set("")

        for cat, btn in self._tab_buttons.items():
            btn.configure(fg_color=COLORS['accent'] if cat == category else COLORS['bg_medium'])

        self._category_dropdown.pack_forget()
        self._html_type_dropdown.pack_forget()
        self._polyfill_type_dropdown.pack_forget()

        if category == "css":
            self._filter_label.configure(text="Category:")
            self._category_dropdown.configure(values=["All"] + list(self._css_categories.keys()))
            self._category_filter_var.set("All")
            self._category_dropdown.pack(side="left")
        elif category == "javascript":
            self._filter_label.configure(text="Category:")
            self._category_dropdown.configure(values=["All"] + list(self._js_categories.keys()))
            self._category_filter_var.set("All")
            self._category_dropdown.pack(side="left")
        elif category == "polyfills":
            self._filter_label.configure(text="Type:")
            self._polyfill_type_filter_var.set("All")
            self._polyfill_type_dropdown.pack(side="left")
        else:
            self._filter_label.configure(text="Type:")
            self._html_type_filter_var.set("All")
            self._html_type_dropdown.pack(side="left")

        self._refresh_rules_list()
        self._show_details_placeholder()

    def _get_all_rules(self) -> List[Tuple[str, dict, bool, str]]:
        """Get filtered rules for current tab. Returns (id, data, is_custom, category) tuples."""
        rules = []
        search = self._search_var.get().lower().strip()
        category_filter = self._category_filter_var.get()
        html_type_filter = self._html_type_filter_var.get()

        if self._selected_category == "css":
            for feature_id, rule_data in self._all_css.items():
                cat = _category_for(feature_id, self._css_categories)
                if category_filter != "All" and cat != category_filter:
                    continue
                if search and not self._matches_search(feature_id, rule_data, search):
                    continue
                rules.append((feature_id, rule_data, False, cat))

            for feature_id, rule_data in self._custom_rules.get('css', {}).items():
                if search and not self._matches_search(feature_id, rule_data, search):
                    continue
                if category_filter != "All" and category_filter != "Custom":
                    continue
                rules.append((feature_id, rule_data, True, 'Custom'))

        elif self._selected_category == "javascript":
            for feature_id, rule_data in self._all_js.items():
                cat = _category_for(feature_id, self._js_categories)
                if category_filter != "All" and cat != category_filter:
                    continue
                if search and not self._matches_search(feature_id, rule_data, search):
                    continue
                rules.append((feature_id, rule_data, False, cat))

            for feature_id, rule_data in self._custom_rules.get('javascript', {}).items():
                if search and not self._matches_search(feature_id, rule_data, search):
                    continue
                if category_filter != "All" and category_filter != "Custom":
                    continue
                rules.append((feature_id, rule_data, True, 'Custom'))

        elif self._selected_category == "polyfills":
            return self._get_polyfill_rules()
        else:
            return self._get_html_rules(search, html_type_filter)

        return rules

    def _get_html_rules(self, search: str, type_filter: str) -> List[Tuple[str, dict, bool, str]]:
        rules = []

        if type_filter in ("All", "Elements"):
            for name, feature_id in self._html_elements.items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, False, 'Elements'))
            for name, feature_id in self._custom_rules.get('html', {}).get('elements', {}).items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, True, 'Elements'))

        if type_filter in ("All", "Attributes"):
            for name, feature_id in self._html_attributes.items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, False, 'Attributes'))
            for name, feature_id in self._custom_rules.get('html', {}).get('attributes', {}).items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, True, 'Attributes'))

        if type_filter in ("All", "Input Types"):
            for name, feature_id in self._html_input_types.items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, False, 'Input Types'))
            for name, feature_id in self._custom_rules.get('html', {}).get('input_types', {}).items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, True, 'Input Types'))

        if type_filter in ("All", "Attribute Values"):
            for (attr, val), feature_id in self._html_attribute_values.items():
                display_name = f"{attr}:{val}"
                if search and search not in display_name.lower() and search not in feature_id.lower():
                    continue
                rules.append((display_name, {'maps_to': feature_id}, False, 'Attribute Values'))
            for key, feature_id in self._custom_rules.get('html', {}).get('attribute_values', {}).items():
                if search and search not in key.lower() and search not in feature_id.lower():
                    continue
                rules.append((key, {'maps_to': feature_id}, True, 'Attribute Values'))

        return rules

    def _matches_search(self, feature_id: str, rule_data: dict, search: str) -> bool:
        if search in feature_id.lower():
            return True
        desc = rule_data.get('description', '').lower()
        if search in desc:
            return True
        keywords = rule_data.get('keywords', [])
        for kw in keywords:
            if search in kw.lower():
                return True
        return False

    def _refresh_rules_list(self):
        for widget in self._rules_list_frame.winfo_children():
            widget.destroy()

        rules = self._get_all_rules()
        self._rules_count_label.configure(text=f"RULES ({len(rules)})")

        if not rules:
            ctk.CTkLabel(
                self._rules_list_frame,
                text="No rules found",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_muted'],
            ).pack(pady=30)
            return

        if self._selected_category == "polyfills":
            self._render_polyfill_rules_list(rules)
        elif self._selected_category == "html":
            self._render_html_rules_list(rules)
        else:
            self._render_css_js_rules_list(rules)

    def _render_css_js_rules_list(self, rules: List[Tuple[str, dict, bool, str]]):
        rules.sort(key=lambda r: (0 if r[2] else 1, r[0].lower()))

        for feature_id, rule_data, is_custom, category in rules:
            self._create_rule_list_item(feature_id, is_custom, category)

    def _render_html_rules_list(self, rules: List[Tuple[str, dict, bool, str]]):
        by_type = {}
        for name, rule_data, is_custom, rule_type in rules:
            if rule_type not in by_type:
                by_type[rule_type] = []
            by_type[rule_type].append((name, rule_data, is_custom))

        for rule_type in HTML_TYPES:
            if rule_type not in by_type:
                continue

            items = by_type[rule_type]
            items.sort(key=lambda r: (0 if r[2] else 1, r[0].lower()))

            ctk.CTkLabel(
                self._rules_list_frame,
                text=rule_type,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['accent_bright'],
            ).pack(anchor="w", padx=10, pady=(10, 5))

            for name, rule_data, is_custom in items:
                self._create_html_rule_list_item(name, rule_data, is_custom, rule_type)

    def _create_rule_list_item(self, feature_id: str, is_custom: bool, category: str):
        item_frame = ctk.CTkFrame(self._rules_list_frame, fg_color="transparent", height=32)
        item_frame.pack(fill="x", pady=1, padx=5)

        btn = ctk.CTkButton(
            item_frame,
            text=feature_id,
            font=ctk.CTkFont(size=12),
            height=28,
            anchor="w",
            fg_color="transparent",
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_primary'],
            command=lambda fid=feature_id, ic=is_custom: self._show_rule_details(fid, ic),
        )
        btn.pack(side="left", fill="x", expand=True)

        if is_custom:
            badge = ctk.CTkLabel(
                item_frame,
                text="Custom",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=COLORS['accent'],
                fg_color=COLORS['bg_dark'],
                corner_radius=4,
                width=50,
                height=20,
            )
            badge.pack(side="right", padx=5)

    def _create_html_rule_list_item(self, name: str, rule_data: dict, is_custom: bool, rule_type: str):
        item_frame = ctk.CTkFrame(self._rules_list_frame, fg_color="transparent", height=32)
        item_frame.pack(fill="x", pady=1, padx=5)

        display_text = f"{name} -> {rule_data.get('maps_to', '')}"

        btn = ctk.CTkButton(
            item_frame,
            text=display_text,
            font=ctk.CTkFont(size=11),
            height=26,
            anchor="w",
            fg_color="transparent",
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_primary'],
            command=lambda n=name, rd=rule_data, ic=is_custom, rt=rule_type: self._show_html_rule_details(n, rd, ic, rt),
        )
        btn.pack(side="left", fill="x", expand=True)

        if is_custom:
            badge = ctk.CTkLabel(
                item_frame,
                text="Custom",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=COLORS['accent'],
                fg_color=COLORS['bg_dark'],
                corner_radius=4,
                width=50,
                height=20,
            )
            badge.pack(side="right", padx=5)

    def _show_details_placeholder(self):
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self._details_frame,
            text="Select a rule to view details\nor click '+ Add New Rule'",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_muted'],
        ).pack(expand=True, pady=100)

    def _show_rule_details(self, feature_id: str, is_custom: bool):
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        self._selected_rule_id = feature_id

        if self._selected_category == "css":
            if is_custom:
                rule_data = self._custom_rules.get('css', {}).get(feature_id, {})
            else:
                rule_data = self._all_css.get(feature_id, {})
            category = _category_for(feature_id, self._css_categories) if not is_custom else 'Custom'
        else:
            if is_custom:
                rule_data = self._custom_rules.get('javascript', {}).get(feature_id, {})
            else:
                rule_data = self._all_js.get(feature_id, {})
            category = _category_for(feature_id, self._js_categories) if not is_custom else 'Custom'

        title_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            title_frame,
            text=feature_id,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        if is_custom:
            ctk.CTkLabel(
                title_frame,
                text="Custom",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS['text_primary'],
                fg_color=COLORS['accent'],
                corner_radius=4,
                width=60,
                height=22,
            ).pack(side="left", padx=10)

        desc = rule_data.get('description', 'No description')
        ctk.CTkLabel(
            self._details_frame,
            text=desc,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            wraplength=400,
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(
            self._details_frame,
            text=f"Category: {category}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, 15))

        patterns = rule_data.get('patterns', [])
        if patterns:
            ctk.CTkLabel(
                self._details_frame,
                text="Patterns:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_secondary'],
            ).pack(anchor="w", pady=(0, 5))

            patterns_box = ctk.CTkTextbox(
                self._details_frame,
                font=ctk.CTkFont(size=11, family="Courier"),
                height=min(100, 20 * len(patterns)),
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                border_width=1,
                state="normal",
            )
            patterns_box.pack(fill="x", pady=(0, 15))
            patterns_box.insert("1.0", "\n".join(patterns))
            patterns_box.configure(state="disabled")

        keywords = rule_data.get('keywords', [])
        if keywords:
            ctk.CTkLabel(
                self._details_frame,
                text=f"Keywords: {', '.join(keywords)}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_muted'],
            ).pack(anchor="w", pady=(0, 15))

        if is_custom:
            btn_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(20, 0))

            ctk.CTkButton(
                btn_frame,
                text="Edit",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                height=35,
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_dim'],
                command=lambda: self._show_edit_form(feature_id, rule_data),
            ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(
                btn_frame,
                text="Delete",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                height=35,
                fg_color=COLORS['danger'],
                hover_color=COLORS['danger_dark'],
                command=lambda: self._delete_rule(feature_id),
            ).pack(side="left")

    def _show_html_rule_details(self, name: str, rule_data: dict, is_custom: bool, rule_type: str):
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        self._selected_rule_id = name

        title_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            title_frame,
            text=name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        if is_custom:
            ctk.CTkLabel(
                title_frame,
                text="Custom",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS['text_primary'],
                fg_color=COLORS['accent'],
                corner_radius=4,
                width=60,
                height=22,
            ).pack(side="left", padx=10)

        ctk.CTkLabel(
            self._details_frame,
            text=f"Type: {rule_type}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 10))

        maps_to = rule_data.get('maps_to', '')
        ctk.CTkLabel(
            self._details_frame,
            text=f"Maps to: {maps_to}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(
            self._details_frame,
            text=f"This {rule_type.lower().rstrip('s')} is detected and checked against\nthe \"{maps_to}\" feature in Can I Use database.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
            justify="left",
        ).pack(anchor="w", pady=(0, 15))

        if is_custom:
            btn_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(20, 0))

            ctk.CTkButton(
                btn_frame,
                text="Edit",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                height=35,
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_dim'],
                command=lambda: self._show_html_edit_form(name, maps_to, rule_type),
            ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(
                btn_frame,
                text="Delete",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                height=35,
                fg_color=COLORS['danger'],
                hover_color=COLORS['danger_dark'],
                command=lambda: self._delete_html_rule(name, rule_type),
            ).pack(side="left")

    def _show_add_form(self):
        if self._selected_category == "polyfills":
            self._show_polyfill_add_form()
        elif self._selected_category == "html":
            self._show_html_add_form()
        else:
            self._show_css_js_add_form()

    def _show_css_js_add_form(self, edit_id: str = None, edit_data: dict = None):
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        is_edit = edit_id is not None
        cat_type = self._selected_category.upper()

        ctk.CTkLabel(
            self._details_frame,
            text=f"{'Edit' if is_edit else 'Add New'} {cat_type} Rule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 20))

        id_entry = self._form_field(
            "Feature ID (Can I Use ID)*:",
            placeholder="e.g., css-container-queries",
            initial=edit_id or "",
        )

        desc_entry = self._form_field(
            "Description:",
            placeholder="e.g., CSS Container Queries",
            initial=(edit_data.get('description', '') if edit_data else ''),
        )

        patterns_text = self._form_field(
            "Patterns (regex, one per line)*:",
            textbox=True,
            initial=("\n".join(edit_data['patterns']) if edit_data and edit_data.get('patterns') else ''),
        )

        keywords_entry = self._form_field(
            "Keywords (comma-separated, optional):",
            placeholder="e.g., container, @container",
            initial=(", ".join(edit_data['keywords']) if edit_data and edit_data.get('keywords') else ''),
            bottom_pad=20,
        )

        btn_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            width=100,
            height=35,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_primary'],
            command=self._show_details_placeholder,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Save Rule",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            height=35,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_dark'],
            command=lambda: self._save_css_js_rule(
                id_entry.get(),
                desc_entry.get(),
                patterns_text.get("1.0", "end"),
                keywords_entry.get(),
                edit_id
            ),
        ).pack(side="left")

    def _show_edit_form(self, feature_id: str, rule_data: dict):
        self._show_css_js_add_form(feature_id, rule_data)

    def _show_html_add_form(self, rule_type: str = None):
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self._details_frame,
            text="Add New HTML Rule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(
            self._details_frame,
            text="Type*:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        type_var = ctk.StringVar(value=rule_type or "Elements")
        type_dropdown = ctk.CTkOptionMenu(
            self._details_frame,
            variable=type_var,
            values=HTML_TYPES,
            width=200,
            height=36,
            fg_color=COLORS['input_bg'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_dim'],
            dropdown_fg_color=COLORS['bg_medium'],
        )
        type_dropdown.pack(anchor="w", pady=(0, 15))

        name_entry = self._form_field(
            "Name*:",
            placeholder="e.g., popover (or attr:value for Attribute Values)",
        )

        feature_entry = self._form_field(
            "Can I Use Feature ID*:",
            placeholder="e.g., popover-api",
            bottom_pad=20,
        )

        btn_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            width=100,
            height=35,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_primary'],
            command=self._show_details_placeholder,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Save Rule",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            height=35,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_dark'],
            command=lambda: self._save_html_rule(
                type_var.get(),
                name_entry.get(),
                feature_entry.get()
            ),
        ).pack(side="left")

    def _show_html_edit_form(self, name: str, feature_id: str, rule_type: str):
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self._details_frame,
            text="Edit HTML Rule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(
            self._details_frame,
            text=f"Type: {rule_type}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, 15))

        name_entry = self._form_field("Name*:", initial=name)

        feature_entry = self._form_field(
            "Can I Use Feature ID*:",
            initial=feature_id,
            bottom_pad=20,
        )

        btn_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            width=100,
            height=35,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_primary'],
            command=self._show_details_placeholder,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Save Rule",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            height=35,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_dark'],
            command=lambda: self._save_html_rule(
                rule_type,
                name_entry.get(),
                feature_entry.get(),
                old_name=name
            ),
        ).pack(side="left")

    def _save_css_js_rule(self, feature_id: str, description: str, patterns_text: str, keywords_text: str, old_id: str = None):
        feature_id = feature_id.strip()
        description = description.strip()
        patterns_text = patterns_text.strip()
        keywords_text = keywords_text.strip()

        if not feature_id:
            show_warning(self, "Validation", "Feature ID is required")
            return

        if not patterns_text:
            show_warning(self, "Validation", "At least one pattern is required")
            return

        # Don't let custom rules shadow built-in ones
        built_in = self._all_css if self._selected_category == "css" else self._all_js
        if feature_id in built_in and (not old_id or old_id != feature_id):
            show_warning(self, "Validation", f"Feature ID '{feature_id}' already exists as a built-in rule")
            return

        patterns = [p.strip() for p in patterns_text.split('\n') if p.strip()]
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()] if keywords_text else []

        rule_data = {"patterns": patterns}
        if description:
            rule_data["description"] = description
        if keywords:
            rule_data["keywords"] = keywords

        # Clean up old entry if ID was renamed
        if old_id and old_id != feature_id:
            if old_id in self._custom_rules.get(self._selected_category, {}):
                del self._custom_rules[self._selected_category][old_id]

        if self._selected_category not in self._custom_rules:
            self._custom_rules[self._selected_category] = {}

        self._custom_rules[self._selected_category][feature_id] = rule_data

        if self._service.save_custom_rules(self._custom_rules):
            show_info(self, "Success", f"Rule '{feature_id}' saved successfully!")
            if self.on_rules_changed:
                self.on_rules_changed()
            self._refresh_rules_list()
            self._show_rule_details(feature_id, True)

    def _save_html_rule(self, rule_type: str, name: str, feature_id: str, old_name: str = None):
        name = name.strip()
        feature_id = feature_id.strip()

        if not name:
            show_warning(self, "Validation", "Name is required")
            return

        if not feature_id:
            show_warning(self, "Validation", "Feature ID is required")
            return

        type_key_map = {
            'Elements': 'elements',
            'Attributes': 'attributes',
            'Input Types': 'input_types',
            'Attribute Values': 'attribute_values',
        }
        key = type_key_map.get(rule_type)
        if not key:
            show_error(self, "Error", "Invalid rule type")
            return

        # Don't shadow built-in rules
        built_in_map = {
            'elements': self._html_elements,
            'attributes': self._html_attributes,
            'input_types': self._html_input_types,
            'attribute_values': {f"{k[0]}:{k[1]}": v for k, v in self._html_attribute_values.items()},
        }
        if name in built_in_map.get(key, {}) and (not old_name or old_name != name):
            show_warning(self, "Validation", f"'{name}' already exists as a built-in rule")
            return

        if 'html' not in self._custom_rules:
            self._custom_rules['html'] = {}
        if key not in self._custom_rules['html']:
            self._custom_rules['html'][key] = {}

        if old_name and old_name != name:
            if old_name in self._custom_rules['html'].get(key, {}):
                del self._custom_rules['html'][key][old_name]

        self._custom_rules['html'][key][name] = feature_id

        if self._service.save_custom_rules(self._custom_rules):
            show_info(self, "Success", f"Rule '{name}' saved successfully!")
            if self.on_rules_changed:
                self.on_rules_changed()
            self._refresh_rules_list()
            self._show_html_rule_details(name, {'maps_to': feature_id}, True, rule_type)

    def _delete_rule(self, feature_id: str):
        if not ask_question(self, "Confirm Delete", f"Delete rule '{feature_id}'?"):
            return

        if feature_id in self._custom_rules.get(self._selected_category, {}):
            del self._custom_rules[self._selected_category][feature_id]

            if self._service.save_custom_rules(self._custom_rules):
                show_info(self, "Deleted", f"Rule '{feature_id}' deleted")
                if self.on_rules_changed:
                    self.on_rules_changed()
                self._refresh_rules_list()
                self._show_details_placeholder()

    def _delete_html_rule(self, name: str, rule_type: str):
        if not ask_question(self, "Confirm Delete", f"Delete rule '{name}'?"):
            return

        type_key_map = {
            'Elements': 'elements',
            'Attributes': 'attributes',
            'Input Types': 'input_types',
            'Attribute Values': 'attribute_values',
        }
        key = type_key_map.get(rule_type)

        if key and name in self._custom_rules.get('html', {}).get(key, {}):
            del self._custom_rules['html'][key][name]

            if self._service.save_custom_rules(self._custom_rules):
                show_info(self, "Deleted", f"Rule '{name}' deleted")
                if self.on_rules_changed:
                    self.on_rules_changed()
                self._refresh_rules_list()
                self._show_details_placeholder()

    def _get_polyfill_rules(self) -> List[Tuple[str, dict, bool, str]]:
        """Get filtered polyfill entries. Returns (feature_id, data, False, type_key) tuples."""
        rules = []
        search = self._search_var.get().lower().strip()
        type_filter = self._polyfill_type_filter_var.get()

        type_map = {'JavaScript': 'javascript', 'CSS': 'css', 'HTML': 'html'}

        for type_label, type_key in type_map.items():
            if type_filter != "All" and type_filter != type_label:
                continue
            for feature_id, data in self._polyfill_data.get(type_key, {}).items():
                if search:
                    name = data.get('name', '').lower()
                    if search not in feature_id.lower() and search not in name:
                        continue
                rules.append((feature_id, data, False, type_key))

        return rules

    def _render_polyfill_rules_list(self, rules: List[Tuple[str, dict, bool, str]]):
        by_type = {}
        for fid, data, _, type_key in rules:
            if type_key not in by_type:
                by_type[type_key] = []
            by_type[type_key].append((fid, data, type_key))

        label_map = {'javascript': 'JavaScript', 'css': 'CSS', 'html': 'HTML'}

        for type_key in ['javascript', 'css', 'html']:
            if type_key not in by_type:
                continue

            items = by_type[type_key]
            items.sort(key=lambda r: r[0].lower())

            ctk.CTkLabel(
                self._rules_list_frame,
                text=label_map[type_key],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['accent_bright'],
            ).pack(anchor="w", padx=10, pady=(10, 5))

            for fid, data, tk in items:
                self._create_polyfill_list_item(fid, data, tk)

    def _create_polyfill_list_item(self, feature_id: str, data: dict, type_key: str):
        item_frame = ctk.CTkFrame(self._rules_list_frame, fg_color="transparent", height=32)
        item_frame.pack(fill="x", pady=1, padx=5)

        btn = ctk.CTkButton(
            item_frame,
            text=feature_id,
            font=ctk.CTkFont(size=11),
            height=26,
            anchor="w",
            fg_color="transparent",
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_primary'],
            command=lambda fid=feature_id, d=data, tk=type_key: self._show_polyfill_details(fid, d, tk),
        )
        btn.pack(side="left", fill="x", expand=True)

        is_poly = data.get('polyfillable', False)
        has_fallback = 'fallback' in data
        if is_poly and has_fallback:
            badge_text, badge_color = "Both", COLORS['info']
        elif is_poly:
            badge_text, badge_color = "NPM", COLORS['success']
        else:
            badge_text, badge_color = "Fallback", COLORS['warning']

        ctk.CTkLabel(
            item_frame,
            text=badge_text,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS['text_primary'],
            fg_color=badge_color,
            corner_radius=4,
            width=55,
            height=20,
        ).pack(side="right", padx=5)

    def _show_polyfill_details(self, feature_id: str, data: dict, type_key: str):
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        self._selected_rule_id = feature_id
        label_map = {'javascript': 'JavaScript', 'css': 'CSS', 'html': 'HTML'}

        ctk.CTkLabel(
            self._details_frame,
            text=data.get('name', feature_id),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            self._details_frame,
            text=f"Feature ID: {feature_id}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(
            self._details_frame,
            text=f"Type: {label_map.get(type_key, type_key)}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, 5))

        is_poly = data.get('polyfillable', False)
        status_text = "Yes — NPM package available" if is_poly else "No — CSS fallback only"
        status_color = COLORS['success'] if is_poly else COLORS['warning']
        ctk.CTkLabel(
            self._details_frame,
            text=f"Polyfillable: {status_text}",
            font=ctk.CTkFont(size=12),
            text_color=status_color,
        ).pack(anchor="w", pady=(0, 15))

        packages = data.get('packages', [])
        if packages:
            ctk.CTkLabel(
                self._details_frame,
                text=f"Packages ({len(packages)}):",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS['text_secondary'],
            ).pack(anchor="w", pady=(0, 8))

            for pkg in packages:
                pkg_frame = ctk.CTkFrame(self._details_frame, fg_color=COLORS['bg_dark'], corner_radius=6)
                pkg_frame.pack(fill="x", pady=(0, 8))

                inner = ctk.CTkFrame(pkg_frame, fg_color="transparent")
                inner.pack(fill="x", padx=12, pady=10)

                ctk.CTkLabel(
                    inner,
                    text=pkg.get('name', pkg.get('npm', '')),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS['text_primary'],
                ).pack(anchor="w")

                if pkg.get('npm'):
                    ctk.CTkLabel(
                        inner,
                        text=f"npm: {pkg['npm']}",
                        font=ctk.CTkFont(size=11, family="Courier"),
                        text_color=COLORS['text_muted'],
                    ).pack(anchor="w", pady=(4, 0))

                if pkg.get('import'):
                    ctk.CTkLabel(
                        inner, text="Import:",
                        font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'],
                    ).pack(anchor="w", pady=(6, 2))

                    import_lines = pkg['import'].split('\n')
                    import_box = ctk.CTkTextbox(
                        inner,
                        font=ctk.CTkFont(size=10, family="Courier"),
                        height=min(60, 16 * len(import_lines)),
                        fg_color=COLORS['input_bg'],
                        text_color=COLORS['text_secondary'],
                        wrap="none",
                    )
                    import_box.pack(fill="x", pady=(0, 4))
                    import_box.insert("1.0", pkg['import'])
                    import_box.configure(state="disabled")

                info_parts = []
                if pkg.get('size_kb'):
                    info_parts.append(f"{pkg['size_kb']} KB")
                if pkg.get('cdn'):
                    info_parts.append("CDN available")
                if pkg.get('note'):
                    info_parts.append(pkg['note'])

                if info_parts:
                    ctk.CTkLabel(
                        inner,
                        text=" · ".join(info_parts),
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS['text_disabled'],
                    ).pack(anchor="w", pady=(4, 0))

        fallback = data.get('fallback')
        if fallback:
            ctk.CTkLabel(
                self._details_frame,
                text="CSS Fallback:",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS['text_secondary'],
            ).pack(anchor="w", pady=(10, 8))

            if fallback.get('description'):
                ctk.CTkLabel(
                    self._details_frame,
                    text=fallback['description'],
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text_muted'],
                    wraplength=400, justify="left",
                ).pack(anchor="w", pady=(0, 8))

            if fallback.get('code'):
                code_lines = fallback['code'].split('\n')
                code_box = ctk.CTkTextbox(
                    self._details_frame,
                    font=ctk.CTkFont(size=10, family="Courier"),
                    height=min(150, 14 * len(code_lines)),
                    fg_color=COLORS['input_bg'],
                    text_color=COLORS['text_secondary'],
                    wrap="none",
                )
                code_box.pack(fill="x", pady=(0, 8))
                code_box.insert("1.0", fallback['code'])
                code_box.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            btn_frame, text="Edit",
            font=ctk.CTkFont(size=12, weight="bold"), width=100, height=35,
            fg_color=COLORS['accent'], hover_color=COLORS['accent_dim'],
            command=lambda: self._show_polyfill_add_form(feature_id, data, type_key),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="Delete",
            font=ctk.CTkFont(size=12, weight="bold"), width=100, height=35,
            fg_color=COLORS['danger'], hover_color=COLORS['danger_dark'],
            command=lambda: self._delete_polyfill_rule(feature_id, type_key),
        ).pack(side="left")

    def _show_polyfill_add_form(self, edit_id: str = None, edit_data: dict = None, edit_type_key: str = None):
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        is_edit = edit_id is not None

        ctk.CTkLabel(
            self._details_frame,
            text=f"{'Edit' if is_edit else 'Add New'} Polyfill",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 20))

        id_entry = self._form_field(
            "Feature ID (Can I Use)*:",
            placeholder="e.g., fetch",
            initial=edit_id or "",
            bottom_pad=12,
        )

        name_entry = self._form_field(
            "Display Name*:",
            placeholder="e.g., Fetch API",
            initial=(edit_data.get('name', '') if edit_data else ''),
            bottom_pad=12,
        )

        ctk.CTkLabel(
            self._details_frame, text="Type*:",
            font=ctk.CTkFont(size=12), text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        type_var = ctk.StringVar(value=edit_type_key or "javascript")
        ctk.CTkOptionMenu(
            self._details_frame, variable=type_var,
            values=["javascript", "css", "html"],
            width=200, height=36,
            fg_color=COLORS['input_bg'], button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_dim'], dropdown_fg_color=COLORS['bg_medium'],
        ).pack(anchor="w", pady=(0, 12))

        poly_var = ctk.BooleanVar(value=edit_data.get('polyfillable', True) if edit_data else True)
        ctk.CTkCheckBox(
            self._details_frame, text="Polyfillable (NPM package available)",
            variable=poly_var, font=ctk.CTkFont(size=12),
            fg_color=COLORS['accent'], hover_color=COLORS['accent_dim'],
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(
            self._details_frame, text="Package Info",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, 8))

        npm_entry = self._form_field(
            "NPM Package:",
            placeholder="e.g., whatwg-fetch",
            bottom_pad=10,
        )

        import_text = self._form_field(
            "Import Statement:",
            textbox=True,
            textbox_height=60,
            bottom_pad=10,
        )

        size_note_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        size_note_frame.pack(fill="x", pady=(0, 10))

        size_col = ctk.CTkFrame(size_note_frame, fg_color="transparent")
        size_col.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(
            size_col, text="Size (KB):",
            font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary'],
        ).pack(anchor="w")
        size_entry = ctk.CTkEntry(
            size_col, placeholder_text="3.2",
            font=ctk.CTkFont(size=12), height=32,
            fg_color=COLORS['input_bg'], border_color=COLORS['border'],
        )
        size_entry.pack(fill="x")

        note_col = ctk.CTkFrame(size_note_frame, fg_color="transparent")
        note_col.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(
            note_col, text="Note:",
            font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary'],
        ).pack(anchor="w")
        note_entry = ctk.CTkEntry(
            note_col, placeholder_text="Optional note",
            font=ctk.CTkFont(size=12), height=32,
            fg_color=COLORS['input_bg'], border_color=COLORS['border'],
        )
        note_entry.pack(fill="x")

        ctk.CTkLabel(
            self._details_frame, text="CSS Fallback (optional)",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(10, 8))

        fb_desc_entry = self._form_field(
            "Fallback Description:",
            placeholder="e.g., Use Flexbox as fallback",
            bottom_pad=10,
        )

        fb_code_text = self._form_field(
            "Fallback CSS Code:",
            textbox=True,
            textbox_height=80,
        )

        if edit_data:
            packages = edit_data.get('packages', [])
            if packages:
                pkg = packages[0]
                npm_entry.insert(0, pkg.get('npm', ''))
                import_text.insert("1.0", pkg.get('import', ''))
                if pkg.get('size_kb'):
                    size_entry.insert(0, str(pkg['size_kb']))
                if pkg.get('note'):
                    note_entry.insert(0, pkg['note'])

            fallback = edit_data.get('fallback', {})
            if fallback:
                fb_desc_entry.insert(0, fallback.get('description', ''))
                fb_code_text.insert("1.0", fallback.get('code', ''))

        btn_frame = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(
            btn_frame, text="Cancel", font=ctk.CTkFont(size=12),
            width=100, height=35,
            fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_primary'],
            command=self._show_details_placeholder,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="Save", font=ctk.CTkFont(size=12, weight="bold"),
            width=120, height=35,
            fg_color=COLORS['success'], hover_color=COLORS['success_dark'],
            command=lambda: self._save_polyfill_rule(
                id_entry.get(), name_entry.get(), type_var.get(), poly_var.get(),
                npm_entry.get(), import_text.get("1.0", "end"), size_entry.get(),
                note_entry.get(), fb_desc_entry.get(), fb_code_text.get("1.0", "end"),
                edit_id, edit_type_key,
            ),
        ).pack(side="left")

    def _save_polyfill_rule(self, feature_id, name, type_key, polyfillable,
                            npm_pkg, import_stmt, size_kb_str, note,
                            fb_desc, fb_code, old_id=None, old_type_key=None):
        feature_id = feature_id.strip()
        name = name.strip()
        npm_pkg = npm_pkg.strip()
        import_stmt = import_stmt.strip()
        size_kb_str = size_kb_str.strip()
        note = note.strip()
        fb_desc = fb_desc.strip()
        fb_code = fb_code.strip()

        if not feature_id:
            show_warning(self, "Validation", "Feature ID is required")
            return
        if not name:
            show_warning(self, "Validation", "Display name is required")
            return

        entry = {"name": name, "polyfillable": polyfillable}

        if npm_pkg:
            pkg = {"name": npm_pkg, "npm": npm_pkg}
            if import_stmt:
                pkg["import"] = import_stmt
            if size_kb_str:
                try:
                    pkg["size_kb"] = float(size_kb_str)
                except ValueError:
                    pass
            if note:
                pkg["note"] = note
            entry["packages"] = [pkg]

        if fb_desc or fb_code:
            entry["fallback"] = {"type": "css"}
            if fb_desc:
                entry["fallback"]["description"] = fb_desc
            if fb_code:
                entry["fallback"]["code"] = fb_code

        # Remove old entry if type or ID changed
        if old_id and old_type_key:
            if old_id != feature_id or old_type_key != type_key:
                if old_id in self._polyfill_data.get(old_type_key, {}):
                    del self._polyfill_data[old_type_key][old_id]

        if type_key not in self._polyfill_data:
            self._polyfill_data[type_key] = {}

        self._polyfill_data[type_key][feature_id] = entry

        if self._service.save_polyfill_map(self._polyfill_data):
            show_info(self, "Success", f"Polyfill '{feature_id}' saved!")
            self._refresh_rules_list()
            self._show_polyfill_details(feature_id, entry, type_key)

    def _delete_polyfill_rule(self, feature_id: str, type_key: str):
        if not ask_question(self, "Confirm Delete", f"Delete polyfill '{feature_id}'?"):
            return

        if feature_id in self._polyfill_data.get(type_key, {}):
            del self._polyfill_data[type_key][feature_id]

            if self._service.save_polyfill_map(self._polyfill_data):
                show_info(self, "Deleted", f"Polyfill '{feature_id}' deleted")
                self._refresh_rules_list()
                self._show_details_placeholder()


def show_rules_manager(parent, on_rules_changed: Optional[Callable] = None):
    """Open the rules manager as a modal dialog."""
    dialog = RulesManagerDialog(parent, on_rules_changed)
    dialog.wait_window()
