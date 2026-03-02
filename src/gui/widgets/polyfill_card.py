"""Polyfill recommendation card with collapsible sections."""

from typing import List, Callable, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, FONTS, ICONS


class _ToggleSection(ctk.CTkFrame):
    """Lightweight collapsible section used inside the polyfill card."""

    def __init__(self, master, title: str, badge_text: str = "", expanded: bool = False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._expanded = expanded

        # Header row
        self._header = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'], corner_radius=6, cursor="hand2")
        self._header.pack(fill="x")

        self._chevron = ctk.CTkLabel(
            self._header, text=ICONS['chevron_down'] if expanded else ICONS['chevron_right'],
            font=ctk.CTkFont(size=12), text_color=COLORS['text_muted'], width=20,
        )
        self._chevron.pack(side="left", padx=(SPACING['sm'], 0), pady=SPACING['sm'])

        self._title_lbl = ctk.CTkLabel(
            self._header, text=title,
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS['text_primary'],
        )
        self._title_lbl.pack(side="left", padx=(SPACING['xs'], 0), pady=SPACING['sm'])

        if badge_text:
            badge = ctk.CTkLabel(
                self._header, text=f" {badge_text} ",
                font=ctk.CTkFont(size=10), text_color=COLORS['text_primary'],
                fg_color=COLORS['info'], corner_radius=8,
            )
            badge.pack(side="left", padx=(SPACING['sm'], 0))
            badge.bind("<Button-1>", lambda e=None: self._toggle())

        # Bind clicks on all header children
        for w in (self._header, self._chevron, self._title_lbl):
            w.bind("<Button-1>", lambda e=None: self._toggle())

        # Content area
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        if expanded:
            self._content.pack(fill="x", pady=(SPACING['xs'], 0))

    def _toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            self._chevron.configure(text=ICONS['chevron_down'])
            self._content.pack(fill="x", pady=(SPACING['xs'], 0))
        else:
            self._chevron.configure(text=ICONS['chevron_right'])
            self._content.pack_forget()

    def get_content(self) -> ctk.CTkFrame:
        return self._content


class PolyfillCard(ctk.CTkFrame):
    """Organized polyfill recommendations with collapsible sub-sections."""

    def __init__(
        self,
        master,
        install_command: str,
        import_statements: List[str],
        npm_recommendations: List,
        css_fallbacks: List,
        total_size_kb: float = 0.0,
        on_generate_file: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(
            master, fg_color=COLORS['bg_medium'], corner_radius=8,
            border_width=1, border_color=COLORS['info'], **kwargs
        )

        self._install_command = install_command
        self._import_statements = import_statements
        self._npm_recommendations = npm_recommendations
        self._css_fallbacks = css_fallbacks
        self._total_size_kb = total_size_kb
        self._on_generate_file = on_generate_file

        self._init_ui()

    def _init_ui(self):
        npm_count = len(self._npm_recommendations)
        css_count = len(self._css_fallbacks)

        # --- Summary header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        ctk.CTkLabel(
            header, text="\U0001F4E6", font=ctk.CTkFont(size=16)
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="Polyfill Recommendations",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS['text_primary'],
        ).pack(side="left", padx=(SPACING['xs'], 0))

        # Summary chips on the right
        chips_frame = ctk.CTkFrame(header, fg_color="transparent")
        chips_frame.pack(side="right")

        if self._total_size_kb > 0:
            ctk.CTkLabel(
                chips_frame, text=f"~{self._total_size_kb:.1f} KB total",
                font=ctk.CTkFont(size=10), text_color=COLORS['text_muted'],
            ).pack(side="right", padx=(SPACING['sm'], 0))

        if css_count > 0:
            ctk.CTkLabel(
                chips_frame, text=f" {css_count} fallback{'s' if css_count != 1 else ''} ",
                font=ctk.CTkFont(size=10), text_color=COLORS['text_primary'],
                fg_color=COLORS['warning'], corner_radius=8,
            ).pack(side="right", padx=(SPACING['xs'], 0))

        if npm_count > 0:
            ctk.CTkLabel(
                chips_frame, text=f" {npm_count} package{'s' if npm_count != 1 else ''} ",
                font=ctk.CTkFont(size=10), text_color=COLORS['text_primary'],
                fg_color=COLORS['success'], corner_radius=8,
            ).pack(side="right", padx=(SPACING['xs'], 0))

        # Separator
        ctk.CTkFrame(self, fg_color=COLORS['border'], height=1).pack(fill="x", padx=SPACING['md'])

        # --- Action buttons row ---
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])

        if self._install_command:
            install_btn = ctk.CTkButton(
                actions, text="Copy Install Command", width=160, height=30,
                fg_color=COLORS['accent'], hover_color=COLORS['accent_dim'],
                font=ctk.CTkFont(size=11),
            )
            install_btn.configure(command=lambda b=install_btn: self._copy_to_clipboard(self._install_command, b))
            install_btn.pack(side="left", padx=(0, SPACING['sm']))

        if self._import_statements:
            imports_btn = ctk.CTkButton(
                actions, text="Copy Imports", width=120, height=30,
                fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=11),
            )
            imports_btn.configure(command=lambda b=imports_btn: self._copy_to_clipboard("\n".join(self._import_statements), b))
            imports_btn.pack(side="left", padx=(0, SPACING['sm']))

        if self._on_generate_file and self._npm_recommendations:
            ctk.CTkButton(
                actions, text="Generate polyfills.js", width=150, height=30,
                fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=11),
                command=self._on_generate_click,
            ).pack(side="left")

        # --- NPM Packages section (collapsible) ---
        if self._npm_recommendations:
            npm_section = _ToggleSection(
                self, title="NPM Packages",
                badge_text=str(npm_count), expanded=False,
            )
            npm_section.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], 0))
            self._build_npm_list(npm_section.get_content())

        # --- CSS Fallbacks section (collapsible) ---
        if self._css_fallbacks:
            css_section = _ToggleSection(
                self, title="CSS Fallbacks",
                badge_text=str(css_count), expanded=False,
            )
            css_section.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], 0))
            self._build_fallbacks_list(css_section.get_content())

        # Bottom padding
        ctk.CTkFrame(self, fg_color="transparent", height=SPACING['sm']).pack(fill="x")

    def _build_npm_list(self, parent):
        """Compact npm package list — one row per polyfill."""
        for rec in self._npm_recommendations:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=1)

            inner = ctk.CTkFrame(row, fg_color=COLORS['bg_dark'], corner_radius=4)
            inner.pack(fill="x", pady=1)

            # Left side: bullet + name + package
            ctk.CTkLabel(
                inner, text="\u2022", font=ctk.CTkFont(size=11),
                text_color=COLORS['success'], width=14,
            ).pack(side="left", padx=(SPACING['sm'], 0), pady=4)

            ctk.CTkLabel(
                inner, text=rec.feature_name,
                font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS['text_primary'],
            ).pack(side="left", pady=4)

            if rec.packages:
                pkg = rec.packages[0]
                ctk.CTkLabel(
                    inner, text=pkg.npm_package,
                    font=ctk.CTkFont(family=FONTS['family_mono'], size=10),
                    text_color=COLORS['text_muted'],
                ).pack(side="left", padx=(SPACING['sm'], 0), pady=4)

                # Right side: size + copy button
                if pkg.size_kb:
                    ctk.CTkLabel(
                        inner, text=f"{pkg.size_kb} KB",
                        font=ctk.CTkFont(size=9), text_color=COLORS['text_disabled'],
                    ).pack(side="right", padx=(0, SPACING['sm']), pady=4)

                copy_btn = ctk.CTkButton(
                    inner, text="Copy", width=50, height=22,
                    fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
                    text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=9),
                )
                copy_btn.configure(command=lambda p=pkg, b=copy_btn: self._copy_to_clipboard(p.import_statement, b))
                copy_btn.pack(side="right", padx=2, pady=2)

    def _build_fallbacks_list(self, parent):
        """CSS fallback items — each one expandable to show code."""
        for rec in self._css_fallbacks:
            item_section = _ToggleSection(
                parent, title=rec.feature_name, expanded=False,
            )
            item_section.pack(fill="x", pady=2)

            content = item_section.get_content()

            if rec.fallback_description:
                ctk.CTkLabel(
                    content, text=rec.fallback_description,
                    font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'],
                    wraplength=500, justify="left", anchor="w",
                ).pack(anchor="w", pady=(0, SPACING['xs']))

            if rec.fallback_code:
                code_frame = ctk.CTkFrame(content, fg_color=COLORS['bg_darkest'], corner_radius=4)
                code_frame.pack(fill="x")

                lines = rec.fallback_code.split('\n')
                code_text = ctk.CTkTextbox(
                    code_frame,
                    font=ctk.CTkFont(family=FONTS['family_mono'], size=10),
                    text_color=COLORS['text_muted'], fg_color=COLORS['bg_darkest'],
                    height=min(120, 14 * len(lines)), wrap="none",
                )
                code_text.pack(fill="x", padx=SPACING['xs'], pady=SPACING['xs'])
                code_text.insert("1.0", rec.fallback_code)
                code_text.configure(state="disabled")

                css_btn = ctk.CTkButton(
                    code_frame, text="Copy CSS", width=70, height=22,
                    fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
                    text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=9),
                )
                css_btn.configure(command=lambda code=rec.fallback_code, b=css_btn: self._copy_to_clipboard(code, b))
                css_btn.pack(anchor="e", padx=SPACING['xs'], pady=(0, SPACING['xs']))

    def _copy_to_clipboard(self, text: str, button: ctk.CTkButton = None):
        """Copy text and show brief 'Copied!' feedback on the button."""
        self.clipboard_clear()
        self.clipboard_append(text)

        if button:
            original_text = button.cget("text")
            original_fg = button.cget("fg_color")
            button.configure(text="\u2713 Copied!", fg_color=COLORS['success'])
            button.after(1500, lambda: button.configure(text=original_text, fg_color=original_fg))

    def _on_generate_click(self):
        if self._on_generate_file:
            self._on_generate_file("polyfills.js")


class PolyfillEmptyCard(ctk.CTkFrame):
    """Shown when no polyfills are needed."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master, fg_color=COLORS['bg_medium'], corner_radius=8,
            border_width=1, border_color=COLORS['border'], **kwargs
        )
        self._init_ui()

    def _init_ui(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        ctk.CTkLabel(
            content, text="\u2713", font=ctk.CTkFont(size=24),
            text_color=COLORS['success'],
        ).pack()

        ctk.CTkLabel(
            content, text="No polyfills needed",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS['text_primary'],
        ).pack(pady=(SPACING['xs'], 0))

        ctk.CTkLabel(
            content,
            text="All detected features are fully supported in your target browsers,\nor no polyfills are available for the unsupported features.",
            font=ctk.CTkFont(size=12), text_color=COLORS['text_muted'],
            wraplength=400, justify="center",
        ).pack(pady=(SPACING['xs'], 0))
