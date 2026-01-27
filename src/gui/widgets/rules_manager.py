"""
Professional Rules Manager Dialog for Cross Guard.

A unified UI where users can browse ALL existing feature detection rules
(built-in + custom) and add their own new rules seamlessly.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Callable, List, Tuple

import customtkinter as ctk

from ..theme import COLORS, SPACING, enable_smooth_scrolling
from .messagebox import show_info, show_error, show_warning, ask_question

# Import built-in feature maps
from ...parsers.css_feature_maps import (
    ALL_CSS_FEATURES,
    CSS_LAYOUT_FEATURES, CSS_TRANSFORM_ANIMATION, CSS_COLOR_BACKGROUND,
    CSS_TYPOGRAPHY, CSS_BOX_MODEL, CSS_BORDER_OUTLINE, CSS_SHADOW_EFFECTS,
    CSS_SELECTORS, CSS_MEDIA_QUERIES, CSS_UNITS, CSS_VARIABLES, CSS_AT_RULES,
    CSS_POSITIONING, CSS_OVERFLOW, CSS_INTERACTION, CSS_MISC, CSS_CONTAINER,
    CSS_SUBGRID, CSS_CASCADE, CSS_NESTING, CSS_ADDITIONAL_1, CSS_ADDITIONAL_2,
    CSS_ADDITIONAL_3
)
from ...parsers.js_feature_maps import (
    ALL_JS_FEATURES,
    JS_SYNTAX_FEATURES, JS_API_FEATURES, JS_ARRAY_METHODS, JS_STRING_METHODS,
    JS_OBJECT_METHODS, JS_STORAGE_APIS, JS_DOM_APIS
)
from ...parsers.html_feature_maps import (
    HTML_ELEMENTS, HTML_ATTRIBUTES, HTML_INPUT_TYPES, HTML_ATTRIBUTE_VALUES
)
from ...parsers.custom_rules_loader import (
    is_user_rule, save_custom_rules, load_raw_custom_rules, reload_custom_rules
)


# Category mappings for CSS features
CSS_CATEGORIES = {
    'Layout': CSS_LAYOUT_FEATURES,
    'Transforms & Animation': CSS_TRANSFORM_ANIMATION,
    'Colors & Background': CSS_COLOR_BACKGROUND,
    'Typography': CSS_TYPOGRAPHY,
    'Box Model': CSS_BOX_MODEL,
    'Border & Outline': CSS_BORDER_OUTLINE,
    'Shadow & Effects': CSS_SHADOW_EFFECTS,
    'Selectors': CSS_SELECTORS,
    'Media Queries': CSS_MEDIA_QUERIES,
    'Units': CSS_UNITS,
    'Variables': CSS_VARIABLES,
    'At-Rules': CSS_AT_RULES,
    'Positioning': CSS_POSITIONING,
    'Overflow': CSS_OVERFLOW,
    'Interaction': CSS_INTERACTION,
    'Container': CSS_CONTAINER,
    'Subgrid': CSS_SUBGRID,
    'Cascade': CSS_CASCADE,
    'Nesting': CSS_NESTING,
    'Other': {**CSS_MISC, **CSS_ADDITIONAL_1, **CSS_ADDITIONAL_2, **CSS_ADDITIONAL_3},
}

# Category mappings for JS features
JS_CATEGORIES = {
    'Syntax': JS_SYNTAX_FEATURES,
    'Web APIs': JS_API_FEATURES,
    'Array Methods': JS_ARRAY_METHODS,
    'String Methods': JS_STRING_METHODS,
    'Object Methods': JS_OBJECT_METHODS,
    'Storage': JS_STORAGE_APIS,
    'DOM APIs': JS_DOM_APIS,
}

# HTML types
HTML_TYPES = ['Elements', 'Attributes', 'Input Types', 'Attribute Values']


def get_css_category(feature_id: str) -> str:
    """Get the category name for a CSS feature."""
    for cat_name, cat_features in CSS_CATEGORIES.items():
        if feature_id in cat_features:
            return cat_name
    return 'Custom'


def get_js_category(feature_id: str) -> str:
    """Get the category name for a JS feature."""
    for cat_name, cat_features in JS_CATEGORIES.items():
        if feature_id in cat_features:
            return cat_name
    return 'Custom'


class RulesManagerDialog(ctk.CTkToplevel):
    """Professional dialog for managing feature detection rules."""

    def __init__(self, parent, on_rules_changed: Optional[Callable] = None):
        super().__init__(parent)

        self.parent = parent
        self.on_rules_changed = on_rules_changed
        self._custom_rules = load_raw_custom_rules()
        self._selected_rule_id = None
        self._selected_category = "css"
        self._search_var = ctk.StringVar()
        self._category_filter_var = ctk.StringVar(value="All")
        self._html_type_filter_var = ctk.StringVar(value="All")

        # Configure window
        self.title("Feature Detection Rules")
        self.configure(fg_color=COLORS['bg_dark'])
        self.geometry("1000x700")
        self.minsize(900, 600)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        self._build_ui()
        self._center_on_parent()

        # Bind search
        self._search_var.trace_add('write', lambda *args: self._refresh_rules_list())

    def _center_on_parent(self):
        """Center the dialog on the parent window."""
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
        """Build the complete UI."""
        # Header
        self._build_header()

        # Main content container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Tab bar
        self._build_tab_bar(main_frame)

        # Search and filter bar
        self._build_filter_bar(main_frame)

        # Split view container
        split_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Left panel - Rules list
        self._build_rules_list_panel(split_frame)

        # Right panel - Details
        self._build_details_panel(split_frame)

        # Initial load
        self._refresh_rules_list()

    def _build_header(self):
        """Build the header section."""
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'], corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="Feature Detection Rules",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left", padx=20, pady=15)

        # Close button
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
        """Build the category tab bar."""
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, 10))

        self._tab_buttons = {}
        for category in ["css", "javascript", "html"]:
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
        """Build the search and filter bar."""
        filter_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8)
        filter_frame.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(filter_frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        # Search box
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

        # Category/Type filter (changes based on tab)
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
            values=["All"] + list(CSS_CATEGORIES.keys()),
            width=160,
            height=32,
            fg_color=COLORS['input_bg'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_dim'],
            dropdown_fg_color=COLORS['bg_medium'],
            command=lambda _: self._refresh_rules_list(),
        )
        self._category_dropdown.pack(side="left")

        # HTML type dropdown (hidden by default)
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

    def _build_rules_list_panel(self, parent):
        """Build the left panel with rules list."""
        left_panel = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=8, width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        # Header
        header_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        self._rules_count_label = ctk.CTkLabel(
            header_frame,
            text="RULES (0)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_muted'],
        )
        self._rules_count_label.pack(side="left")

        # Add New Rule button - in the rules panel header
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

        # Scrollable list
        self._rules_list_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color=COLORS['bg_light'],
            corner_radius=6,
        )
        self._rules_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        enable_smooth_scrolling(self._rules_list_frame)

    def _build_details_panel(self, parent):
        """Build the right panel for rule details."""
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
        """Switch to a different category tab."""
        self._selected_category = category
        self._selected_rule_id = None
        self._search_var.set("")

        # Update tab button colors
        for cat, btn in self._tab_buttons.items():
            btn.configure(fg_color=COLORS['accent'] if cat == category else COLORS['bg_medium'])

        # Update filter dropdown
        if category == "css":
            self._filter_label.configure(text="Category:")
            self._category_dropdown.configure(values=["All"] + list(CSS_CATEGORIES.keys()))
            self._category_filter_var.set("All")
            self._category_dropdown.pack(side="left")
            self._html_type_dropdown.pack_forget()
        elif category == "javascript":
            self._filter_label.configure(text="Category:")
            self._category_dropdown.configure(values=["All"] + list(JS_CATEGORIES.keys()))
            self._category_filter_var.set("All")
            self._category_dropdown.pack(side="left")
            self._html_type_dropdown.pack_forget()
        else:  # html
            self._filter_label.configure(text="Type:")
            self._category_dropdown.pack_forget()
            self._html_type_filter_var.set("All")
            self._html_type_dropdown.pack(side="left")

        self._refresh_rules_list()
        self._show_details_placeholder()

    def _get_all_rules(self) -> List[Tuple[str, dict, bool, str]]:
        """Get all rules for current category.

        Returns:
            List of (feature_id, rule_data, is_custom, category/type) tuples
        """
        rules = []
        search = self._search_var.get().lower().strip()
        category_filter = self._category_filter_var.get()
        html_type_filter = self._html_type_filter_var.get()

        if self._selected_category == "css":
            # Built-in CSS rules
            for feature_id, rule_data in ALL_CSS_FEATURES.items():
                cat = get_css_category(feature_id)
                if category_filter != "All" and cat != category_filter:
                    continue
                if search and not self._matches_search(feature_id, rule_data, search):
                    continue
                rules.append((feature_id, rule_data, False, cat))

            # Custom CSS rules
            for feature_id, rule_data in self._custom_rules.get('css', {}).items():
                if search and not self._matches_search(feature_id, rule_data, search):
                    continue
                if category_filter != "All" and category_filter != "Custom":
                    continue
                rules.append((feature_id, rule_data, True, 'Custom'))

        elif self._selected_category == "javascript":
            # Built-in JS rules
            for feature_id, rule_data in ALL_JS_FEATURES.items():
                cat = get_js_category(feature_id)
                if category_filter != "All" and cat != category_filter:
                    continue
                if search and not self._matches_search(feature_id, rule_data, search):
                    continue
                rules.append((feature_id, rule_data, False, cat))

            # Custom JS rules
            for feature_id, rule_data in self._custom_rules.get('javascript', {}).items():
                if search and not self._matches_search(feature_id, rule_data, search):
                    continue
                if category_filter != "All" and category_filter != "Custom":
                    continue
                rules.append((feature_id, rule_data, True, 'Custom'))

        else:  # html
            rules = self._get_html_rules(search, html_type_filter)

        return rules

    def _get_html_rules(self, search: str, type_filter: str) -> List[Tuple[str, dict, bool, str]]:
        """Get all HTML rules."""
        rules = []

        # Elements
        if type_filter in ("All", "Elements"):
            for name, feature_id in HTML_ELEMENTS.items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, False, 'Elements'))
            for name, feature_id in self._custom_rules.get('html', {}).get('elements', {}).items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, True, 'Elements'))

        # Attributes
        if type_filter in ("All", "Attributes"):
            for name, feature_id in HTML_ATTRIBUTES.items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, False, 'Attributes'))
            for name, feature_id in self._custom_rules.get('html', {}).get('attributes', {}).items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, True, 'Attributes'))

        # Input Types
        if type_filter in ("All", "Input Types"):
            for name, feature_id in HTML_INPUT_TYPES.items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, False, 'Input Types'))
            for name, feature_id in self._custom_rules.get('html', {}).get('input_types', {}).items():
                if search and search not in name.lower() and search not in feature_id.lower():
                    continue
                rules.append((name, {'maps_to': feature_id}, True, 'Input Types'))

        # Attribute Values
        if type_filter in ("All", "Attribute Values"):
            for (attr, val), feature_id in HTML_ATTRIBUTE_VALUES.items():
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
        """Check if a rule matches the search query."""
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
        """Refresh the rules list."""
        # Clear existing items
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

        # Group by category/type for HTML
        if self._selected_category == "html":
            self._render_html_rules_list(rules)
        else:
            self._render_css_js_rules_list(rules)

    def _render_css_js_rules_list(self, rules: List[Tuple[str, dict, bool, str]]):
        """Render the CSS/JS rules list."""
        # Sort: custom first, then alphabetical
        rules.sort(key=lambda r: (0 if r[2] else 1, r[0].lower()))

        for feature_id, rule_data, is_custom, category in rules:
            self._create_rule_list_item(feature_id, is_custom, category)

    def _render_html_rules_list(self, rules: List[Tuple[str, dict, bool, str]]):
        """Render the HTML rules list grouped by type."""
        # Group by type
        by_type = {}
        for name, rule_data, is_custom, rule_type in rules:
            if rule_type not in by_type:
                by_type[rule_type] = []
            by_type[rule_type].append((name, rule_data, is_custom))

        for rule_type in HTML_TYPES:
            if rule_type not in by_type:
                continue

            items = by_type[rule_type]
            # Sort: custom first
            items.sort(key=lambda r: (0 if r[2] else 1, r[0].lower()))

            # Type header
            ctk.CTkLabel(
                self._rules_list_frame,
                text=rule_type,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['accent_bright'],
            ).pack(anchor="w", padx=10, pady=(10, 5))

            for name, rule_data, is_custom in items:
                self._create_html_rule_list_item(name, rule_data, is_custom, rule_type)

    def _create_rule_list_item(self, feature_id: str, is_custom: bool, category: str):
        """Create a rule list item."""
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
        """Create an HTML rule list item."""
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
        """Show placeholder in details panel."""
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self._details_frame,
            text="Select a rule to view details\nor click '+ Add New Rule'",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_muted'],
        ).pack(expand=True, pady=100)

    def _show_rule_details(self, feature_id: str, is_custom: bool):
        """Show details for a CSS/JS rule."""
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        self._selected_rule_id = feature_id

        # Get rule data
        if self._selected_category == "css":
            if is_custom:
                rule_data = self._custom_rules.get('css', {}).get(feature_id, {})
            else:
                rule_data = ALL_CSS_FEATURES.get(feature_id, {})
            category = get_css_category(feature_id) if not is_custom else 'Custom'
        else:
            if is_custom:
                rule_data = self._custom_rules.get('javascript', {}).get(feature_id, {})
            else:
                rule_data = ALL_JS_FEATURES.get(feature_id, {})
            category = get_js_category(feature_id) if not is_custom else 'Custom'

        # Title
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

        # Description
        desc = rule_data.get('description', 'No description')
        ctk.CTkLabel(
            self._details_frame,
            text=desc,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            wraplength=400,
        ).pack(anchor="w", pady=(0, 15))

        # Category
        ctk.CTkLabel(
            self._details_frame,
            text=f"Category: {category}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, 15))

        # Patterns
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

        # Keywords
        keywords = rule_data.get('keywords', [])
        if keywords:
            ctk.CTkLabel(
                self._details_frame,
                text=f"Keywords: {', '.join(keywords)}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_muted'],
            ).pack(anchor="w", pady=(0, 15))

        # Edit/Delete buttons (only for custom rules)
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
        """Show details for an HTML rule."""
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        self._selected_rule_id = name

        # Title
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

        # Type
        ctk.CTkLabel(
            self._details_frame,
            text=f"Type: {rule_type}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 10))

        # Maps to
        maps_to = rule_data.get('maps_to', '')
        ctk.CTkLabel(
            self._details_frame,
            text=f"Maps to: {maps_to}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 15))

        # Description
        ctk.CTkLabel(
            self._details_frame,
            text=f"This {rule_type.lower().rstrip('s')} is detected and checked against\nthe \"{maps_to}\" feature in Can I Use database.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
            justify="left",
        ).pack(anchor="w", pady=(0, 15))

        # Edit/Delete buttons (only for custom rules)
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
        """Show the add new rule form."""
        if self._selected_category == "html":
            self._show_html_add_form()
        else:
            self._show_css_js_add_form()

    def _show_css_js_add_form(self, edit_id: str = None, edit_data: dict = None):
        """Show add/edit form for CSS/JS rules."""
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        is_edit = edit_id is not None
        cat_type = self._selected_category.upper()

        # Title
        ctk.CTkLabel(
            self._details_frame,
            text=f"{'Edit' if is_edit else 'Add New'} {cat_type} Rule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 20))

        # Feature ID
        ctk.CTkLabel(
            self._details_frame,
            text="Feature ID (Can I Use ID)*:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        id_entry = ctk.CTkEntry(
            self._details_frame,
            placeholder_text="e.g., css-container-queries",
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        id_entry.pack(fill="x", pady=(0, 15))
        if edit_id:
            id_entry.insert(0, edit_id)

        # Description
        ctk.CTkLabel(
            self._details_frame,
            text="Description:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        desc_entry = ctk.CTkEntry(
            self._details_frame,
            placeholder_text="e.g., CSS Container Queries",
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        desc_entry.pack(fill="x", pady=(0, 15))
        if edit_data and edit_data.get('description'):
            desc_entry.insert(0, edit_data['description'])

        # Patterns
        ctk.CTkLabel(
            self._details_frame,
            text="Patterns (regex, one per line)*:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        patterns_text = ctk.CTkTextbox(
            self._details_frame,
            font=ctk.CTkFont(size=11, family="Courier"),
            height=100,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            border_width=1,
        )
        patterns_text.pack(fill="x", pady=(0, 15))
        if edit_data and edit_data.get('patterns'):
            patterns_text.insert("1.0", "\n".join(edit_data['patterns']))

        # Keywords
        ctk.CTkLabel(
            self._details_frame,
            text="Keywords (comma-separated, optional):",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        keywords_entry = ctk.CTkEntry(
            self._details_frame,
            placeholder_text="e.g., container, @container",
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        keywords_entry.pack(fill="x", pady=(0, 20))
        if edit_data and edit_data.get('keywords'):
            keywords_entry.insert(0, ", ".join(edit_data['keywords']))

        # Buttons
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
        """Show the edit form for a CSS/JS rule."""
        self._show_css_js_add_form(feature_id, rule_data)

    def _show_html_add_form(self, rule_type: str = None):
        """Show add form for HTML rules."""
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        # Title
        ctk.CTkLabel(
            self._details_frame,
            text="Add New HTML Rule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 20))

        # Type selection
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

        # Name
        ctk.CTkLabel(
            self._details_frame,
            text="Name*:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        name_entry = ctk.CTkEntry(
            self._details_frame,
            placeholder_text="e.g., popover (or attr:value for Attribute Values)",
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        name_entry.pack(fill="x", pady=(0, 15))

        # Feature ID
        ctk.CTkLabel(
            self._details_frame,
            text="Can I Use Feature ID*:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        feature_entry = ctk.CTkEntry(
            self._details_frame,
            placeholder_text="e.g., popover-api",
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        feature_entry.pack(fill="x", pady=(0, 20))

        # Buttons
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
        """Show edit form for an HTML rule."""
        for widget in self._details_frame.winfo_children():
            widget.destroy()

        # Title
        ctk.CTkLabel(
            self._details_frame,
            text=f"Edit HTML Rule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 20))

        # Type (read-only)
        ctk.CTkLabel(
            self._details_frame,
            text=f"Type: {rule_type}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, 15))

        # Name
        ctk.CTkLabel(
            self._details_frame,
            text="Name*:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        name_entry = ctk.CTkEntry(
            self._details_frame,
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        name_entry.pack(fill="x", pady=(0, 15))
        name_entry.insert(0, name)

        # Feature ID
        ctk.CTkLabel(
            self._details_frame,
            text="Can I Use Feature ID*:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        feature_entry = ctk.CTkEntry(
            self._details_frame,
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        feature_entry.pack(fill="x", pady=(0, 20))
        feature_entry.insert(0, feature_id)

        # Buttons
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
        """Save a CSS/JS rule."""
        feature_id = feature_id.strip()
        description = description.strip()
        patterns_text = patterns_text.strip()
        keywords_text = keywords_text.strip()

        # Validation
        if not feature_id:
            show_warning(self, "Validation", "Feature ID is required")
            return

        if not patterns_text:
            show_warning(self, "Validation", "At least one pattern is required")
            return

        # Check if ID conflicts with built-in
        built_in = ALL_CSS_FEATURES if self._selected_category == "css" else ALL_JS_FEATURES
        if feature_id in built_in and (not old_id or old_id != feature_id):
            show_warning(self, "Validation", f"Feature ID '{feature_id}' already exists as a built-in rule")
            return

        # Parse patterns
        patterns = [p.strip() for p in patterns_text.split('\n') if p.strip()]

        # Parse keywords
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()] if keywords_text else []

        # Build rule data
        rule_data = {"patterns": patterns}
        if description:
            rule_data["description"] = description
        if keywords:
            rule_data["keywords"] = keywords

        # Delete old rule if ID changed
        if old_id and old_id != feature_id:
            if old_id in self._custom_rules.get(self._selected_category, {}):
                del self._custom_rules[self._selected_category][old_id]

        # Ensure category exists
        if self._selected_category not in self._custom_rules:
            self._custom_rules[self._selected_category] = {}

        # Save rule
        self._custom_rules[self._selected_category][feature_id] = rule_data

        if save_custom_rules(self._custom_rules):
            show_info(self, "Success", f"Rule '{feature_id}' saved successfully!")
            if self.on_rules_changed:
                self.on_rules_changed()
            self._refresh_rules_list()
            self._show_rule_details(feature_id, True)

    def _save_html_rule(self, rule_type: str, name: str, feature_id: str, old_name: str = None):
        """Save an HTML rule."""
        name = name.strip()
        feature_id = feature_id.strip()

        # Validation
        if not name:
            show_warning(self, "Validation", "Name is required")
            return

        if not feature_id:
            show_warning(self, "Validation", "Feature ID is required")
            return

        # Map type to key
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

        # Check if conflicts with built-in
        built_in_map = {
            'elements': HTML_ELEMENTS,
            'attributes': HTML_ATTRIBUTES,
            'input_types': HTML_INPUT_TYPES,
            'attribute_values': {f"{k[0]}:{k[1]}": v for k, v in HTML_ATTRIBUTE_VALUES.items()},
        }
        if name in built_in_map.get(key, {}) and (not old_name or old_name != name):
            show_warning(self, "Validation", f"'{name}' already exists as a built-in rule")
            return

        # Ensure structure exists
        if 'html' not in self._custom_rules:
            self._custom_rules['html'] = {}
        if key not in self._custom_rules['html']:
            self._custom_rules['html'][key] = {}

        # Delete old if name changed
        if old_name and old_name != name:
            if old_name in self._custom_rules['html'].get(key, {}):
                del self._custom_rules['html'][key][old_name]

        # Save
        self._custom_rules['html'][key][name] = feature_id

        if save_custom_rules(self._custom_rules):
            show_info(self, "Success", f"Rule '{name}' saved successfully!")
            if self.on_rules_changed:
                self.on_rules_changed()
            self._refresh_rules_list()
            self._show_html_rule_details(name, {'maps_to': feature_id}, True, rule_type)

    def _delete_rule(self, feature_id: str):
        """Delete a CSS/JS custom rule."""
        if not ask_question(self, "Confirm Delete", f"Delete rule '{feature_id}'?"):
            return

        if feature_id in self._custom_rules.get(self._selected_category, {}):
            del self._custom_rules[self._selected_category][feature_id]

            if save_custom_rules(self._custom_rules):
                show_info(self, "Deleted", f"Rule '{feature_id}' deleted")
                if self.on_rules_changed:
                    self.on_rules_changed()
                self._refresh_rules_list()
                self._show_details_placeholder()

    def _delete_html_rule(self, name: str, rule_type: str):
        """Delete an HTML custom rule."""
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

            if save_custom_rules(self._custom_rules):
                show_info(self, "Deleted", f"Rule '{name}' deleted")
                if self.on_rules_changed:
                    self.on_rules_changed()
                self._refresh_rules_list()
                self._show_details_placeholder()


def show_rules_manager(parent, on_rules_changed: Optional[Callable] = None):
    """Show the rules manager dialog.

    Args:
        parent: Parent window
        on_rules_changed: Callback when rules are modified
    """
    dialog = RulesManagerDialog(parent, on_rules_changed)
    dialog.wait_window()
