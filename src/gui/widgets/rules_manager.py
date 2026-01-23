"""
Custom Rules Manager Dialog for Cross Guard.

Provides a UI interface for users to add, edit, and delete custom detection rules
without manually editing the JSON file.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Callable

import customtkinter as ctk

from ..theme import COLORS, SPACING
from .messagebox import show_info, show_error, show_warning, ask_question


# Path to the custom rules file
CUSTOM_RULES_PATH = Path(__file__).parent.parent.parent / "parsers" / "custom_rules.json"


class RulesManagerDialog(ctk.CTkToplevel):
    """Dialog for managing custom detection rules."""

    def __init__(self, parent, on_rules_changed: Optional[Callable] = None):
        """Initialize the rules manager dialog.
        
        Args:
            parent: Parent window
            on_rules_changed: Callback when rules are modified
        """
        super().__init__(parent)

        self.parent = parent
        self.on_rules_changed = on_rules_changed
        self._rules_data = {}
        self._selected_rule = None
        self._selected_category = "css"

        # Configure window
        self.title("Custom Rules Manager")
        self.configure(fg_color=COLORS['bg_dark'])
        self.geometry("850x700")
        self.minsize(750, 600)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Load existing rules
        self._load_rules()

        # Build UI
        self._build_ui()

        # Center on parent
        self._center_on_parent()

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

    def _load_rules(self):
        """Load rules from JSON file."""
        try:
            if CUSTOM_RULES_PATH.exists():
                with open(CUSTOM_RULES_PATH, 'r', encoding='utf-8') as f:
                    self._rules_data = json.load(f)
            else:
                self._rules_data = {"css": {}, "javascript": {}, "html": {}}
        except Exception as e:
            show_error(self, "Error", f"Failed to load rules: {e}")
            self._rules_data = {"css": {}, "javascript": {}, "html": {}}

    def _save_rules(self):
        """Save rules to JSON file."""
        try:
            # Preserve description and instructions
            self._rules_data["_description"] = "Custom detection rules for Cross Guard. Users can extend the built-in feature detection by adding rules here."
            self._rules_data["_instructions"] = "Each rule maps a pattern to a Can I Use feature ID. Patterns are regular expressions."
            
            with open(CUSTOM_RULES_PATH, 'w', encoding='utf-8') as f:
                json.dump(self._rules_data, f, indent=2)
            
            if self.on_rules_changed:
                self.on_rules_changed()
                
            return True
        except Exception as e:
            show_error(self, "Error", f"Failed to save rules: {e}")
            return False

    def _build_ui(self):
        """Build the dialog UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'], corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)

        ctk.CTkLabel(
            header,
            text="⚙ Custom Rules Manager",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            header,
            text="Add custom detection rules for CSS, JavaScript, and HTML",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(side="left", padx=10, pady=15)

        # Main content
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left panel - Category tabs and rules list
        left_panel = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'], corner_radius=8, width=280)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)

        # Category tabs
        tabs_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=10, pady=10)

        self._tab_buttons = {}
        for category in ["css", "javascript", "html"]:
            btn = ctk.CTkButton(
                tabs_frame,
                text=category.upper(),
                font=ctk.CTkFont(size=11, weight="bold"),
                width=80,
                height=30,
                fg_color=COLORS['primary'] if category == "css" else COLORS['bg_light'],
                hover_color=COLORS['primary_dark'],
                command=lambda c=category: self._select_category(c),
            )
            btn.pack(side="left", padx=2)
            self._tab_buttons[category] = btn

        # Rules list
        list_label = ctk.CTkLabel(
            left_panel,
            text="Rules:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary'],
        )
        list_label.pack(anchor="w", padx=15, pady=(10, 5))

        self._rules_list_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color=COLORS['bg_light'],
            corner_radius=6,
        )
        self._rules_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Add rule button
        add_btn = ctk.CTkButton(
            left_panel,
            text="+ Add New Rule",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_dark'],
            command=self._add_new_rule,
        )
        add_btn.pack(fill="x", padx=10, pady=(0, 10))

        # Right panel - Rule editor (scrollable)
        right_panel = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'], corner_radius=8)
        right_panel.pack(side="right", fill="both", expand=True)

        self._editor_frame = ctk.CTkScrollableFrame(
            right_panel, 
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['primary'],
        )
        self._editor_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self._build_editor_placeholder()

        # Refresh the rules list
        self._refresh_rules_list()

    def _build_editor_placeholder(self):
        """Show placeholder when no rule is selected."""
        for widget in self._editor_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self._editor_frame,
            text="Select a rule to edit\nor click '+ Add New Rule'",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_muted'],
        ).pack(expand=True)

    def _build_editor(self, rule_id: str, rule_data: Dict):
        """Build the rule editor form."""
        for widget in self._editor_frame.winfo_children():
            widget.destroy()

        self._selected_rule = rule_id

        # Title
        ctk.CTkLabel(
            self._editor_frame,
            text="Edit Rule" if rule_id else "New Rule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, 15))

        # Rule ID
        ctk.CTkLabel(
            self._editor_frame,
            text="Feature ID (Can I Use ID):",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        self._id_entry = ctk.CTkEntry(
            self._editor_frame,
            placeholder_text="e.g., css-container-queries",
            font=ctk.CTkFont(size=13),
            height=38,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        self._id_entry.pack(fill="x", pady=(0, 15))
        if rule_id:
            self._id_entry.insert(0, rule_id)

        # Description
        ctk.CTkLabel(
            self._editor_frame,
            text="Description:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        self._desc_entry = ctk.CTkEntry(
            self._editor_frame,
            placeholder_text="e.g., CSS Container Queries",
            font=ctk.CTkFont(size=13),
            height=38,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        self._desc_entry.pack(fill="x", pady=(0, 15))
        if rule_data.get('description'):
            self._desc_entry.insert(0, rule_data['description'])

        # Patterns
        ctk.CTkLabel(
            self._editor_frame,
            text="Patterns (regex, one per line):",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        self._patterns_text = ctk.CTkTextbox(
            self._editor_frame,
            font=ctk.CTkFont(size=12, family="Courier"),
            height=80,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            border_width=1,
        )
        self._patterns_text.pack(fill="x", pady=(0, 10))
        if rule_data.get('patterns'):
            self._patterns_text.insert("1.0", "\n".join(rule_data['patterns']))

        # Keywords (optional)
        ctk.CTkLabel(
            self._editor_frame,
            text="Keywords (comma-separated, optional):",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(0, 5))

        self._keywords_entry = ctk.CTkEntry(
            self._editor_frame,
            placeholder_text="e.g., container, @container",
            font=ctk.CTkFont(size=13),
            height=38,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
        )
        self._keywords_entry.pack(fill="x", pady=(0, 15))
        if rule_data.get('keywords'):
            self._keywords_entry.insert(0, ", ".join(rule_data['keywords']))

        # Buttons row
        btn_frame = ctk.CTkFrame(self._editor_frame, fg_color="transparent", height=50)
        btn_frame.pack(fill="x", pady=(5, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Save Rule",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=130,
            height=40,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            command=self._save_rule,
        )
        save_btn.pack(side="left", padx=(0, 10))

        if rule_id:
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="🗑 Delete",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=100,
                height=40,
                fg_color=COLORS['danger'],
                hover_color=COLORS['danger_dark'],
                command=lambda: self._delete_rule(rule_id),
            )
            delete_btn.pack(side="left", padx=(0, 10))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=13),
            width=100,
            height=40,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_primary'],
            command=self._build_editor_placeholder,
        )
        cancel_btn.pack(side="left")

    def _select_category(self, category: str):
        """Switch to a different category tab."""
        self._selected_category = category
        
        # Update tab button colors
        for cat, btn in self._tab_buttons.items():
            if cat == category:
                btn.configure(fg_color=COLORS['primary'])
            else:
                btn.configure(fg_color=COLORS['bg_light'])
        
        self._refresh_rules_list()
        self._build_editor_placeholder()

    def _refresh_rules_list(self):
        """Refresh the rules list for current category."""
        # Clear existing items
        for widget in self._rules_list_frame.winfo_children():
            widget.destroy()

        category_data = self._rules_data.get(self._selected_category, {})
        
        # Filter out metadata keys
        rules = {k: v for k, v in category_data.items() if not k.startswith('_') and isinstance(v, dict)}

        if not rules:
            ctk.CTkLabel(
                self._rules_list_frame,
                text="No custom rules yet",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_muted'],
            ).pack(pady=20)
            return

        for rule_id, rule_data in rules.items():
            rule_btn = ctk.CTkButton(
                self._rules_list_frame,
                text=rule_id,
                font=ctk.CTkFont(size=12),
                height=32,
                anchor="w",
                fg_color="transparent",
                hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_primary'],
                command=lambda rid=rule_id, rdata=rule_data: self._build_editor(rid, rdata),
            )
            rule_btn.pack(fill="x", pady=2, padx=5)

    def _add_new_rule(self):
        """Open editor for a new rule."""
        self._build_editor("", {})

    def _save_rule(self):
        """Save the current rule being edited."""
        rule_id = self._id_entry.get().strip()
        description = self._desc_entry.get().strip()
        patterns_text = self._patterns_text.get("1.0", "end").strip()
        keywords_text = self._keywords_entry.get().strip()

        # Validation
        if not rule_id:
            show_warning(self, "Validation", "Feature ID is required")
            return

        if not patterns_text:
            show_warning(self, "Validation", "At least one pattern is required")
            return

        # Parse patterns
        patterns = [p.strip() for p in patterns_text.split('\n') if p.strip()]
        
        # Parse keywords
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()] if keywords_text else []

        # Build rule data
        rule_data = {
            "patterns": patterns,
            "description": description,
        }
        if keywords:
            rule_data["keywords"] = keywords

        # Handle HTML category specially (different structure)
        if self._selected_category == "html":
            # For HTML, we need to handle elements, attributes, etc.
            show_info(self, "Note", "For HTML rules, please edit the JSON file directly.\nHTML rules have a different structure (elements, attributes, etc.)")
            return

        # Delete old rule if ID changed
        if self._selected_rule and self._selected_rule != rule_id:
            if self._selected_rule in self._rules_data.get(self._selected_category, {}):
                del self._rules_data[self._selected_category][self._selected_rule]

        # Ensure category exists
        if self._selected_category not in self._rules_data:
            self._rules_data[self._selected_category] = {}

        # Save rule
        self._rules_data[self._selected_category][rule_id] = rule_data

        if self._save_rules():
            show_info(self, "Success", f"Rule '{rule_id}' saved successfully!")
            self._refresh_rules_list()
            self._build_editor_placeholder()

    def _delete_rule(self, rule_id: str):
        """Delete a rule."""
        if not ask_question(self, "Confirm Delete", f"Delete rule '{rule_id}'?"):
            return

        if rule_id in self._rules_data.get(self._selected_category, {}):
            del self._rules_data[self._selected_category][rule_id]
            
            if self._save_rules():
                show_info(self, "Deleted", f"Rule '{rule_id}' deleted")
                self._refresh_rules_list()
                self._build_editor_placeholder()


def show_rules_manager(parent, on_rules_changed: Optional[Callable] = None):
    """Show the rules manager dialog.
    
    Args:
        parent: Parent window
        on_rules_changed: Callback when rules are modified
    """
    dialog = RulesManagerDialog(parent, on_rules_changed)
    dialog.wait_window()
