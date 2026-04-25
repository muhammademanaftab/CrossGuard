"""Polyfill recommendation card."""

from typing import List, Callable, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, FONTS


class PolyfillCard(ctk.CTkFrame):

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
        super().__init__(master, fg_color="transparent", **kwargs)

        self._npm = npm_recommendations
        self._css = css_fallbacks
        self._install_command = install_command
        self._imports = import_statements or []
        self._total_size = total_size_kb
        self._on_generate_file = on_generate_file

        self._init_ui()

    def _init_ui(self):
        for rec in self._npm:
            row = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'], corner_radius=4, height=32)
            row.pack(fill="x", pady=(0, 1))
            row.pack_propagate(False)

            ctk.CTkLabel(
                row, text=rec['feature_name'],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['text_primary'],
            ).pack(side="left", padx=SPACING['sm'])

            if rec['packages']:
                pkg = rec['packages'][0]
                ctk.CTkLabel(
                    row, text=pkg['npm_package'],
                    font=ctk.CTkFont(family=FONTS['family_mono'], size=10),
                    text_color=COLORS['text_muted'],
                ).pack(side="left", padx=(SPACING['xs'], 0))

                if pkg.get('size_kb'):
                    ctk.CTkLabel(
                        row, text=f"{pkg['size_kb']} KB",
                        font=ctk.CTkFont(size=9), text_color=COLORS['text_disabled'],
                    ).pack(side="right", padx=SPACING['sm'])

        for rec in self._css:
            row = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'], corner_radius=4, height=32)
            row.pack(fill="x", pady=(0, 1))
            row.pack_propagate(False)

            ctk.CTkLabel(
                row, text=rec['feature_name'],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['text_primary'],
            ).pack(side="left", padx=SPACING['sm'])

            if rec.get('fallback_description'):
                ctk.CTkLabel(
                    row, text=rec['fallback_description'],
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS['text_muted'],
                ).pack(side="left", padx=(SPACING['xs'], 0))

        if self._install_command:
            cmd_row = ctk.CTkFrame(self, fg_color=COLORS['bg_darkest'], corner_radius=4)
            cmd_row.pack(fill="x", pady=(SPACING['sm'], 0))

            ctk.CTkLabel(
                cmd_row, text=self._install_command,
                font=ctk.CTkFont(family=FONTS['family_mono'], size=10),
                text_color=COLORS['accent'],
            ).pack(side="left", padx=SPACING['sm'], pady=SPACING['xs'])

            copy_btn = ctk.CTkButton(
                cmd_row, text="Copy", width=45, height=20,
                fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=9),
            )
            copy_btn.configure(command=lambda b=copy_btn: self._copy(b))
            copy_btn.pack(side="right", padx=SPACING['xs'], pady=SPACING['xs'])

            if self._total_size and self._total_size > 0:
                ctk.CTkLabel(
                    cmd_row, text=f"~{self._total_size:.1f} KB",
                    font=ctk.CTkFont(size=9),
                    text_color=COLORS['text_disabled'],
                ).pack(side="right", padx=(0, SPACING['xs']), pady=SPACING['xs'])

        if self._imports:
            ctk.CTkLabel(
                self, text="Add to your code:",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS['text_secondary'],
                anchor="w",
            ).pack(fill="x", pady=(SPACING['sm'], 2))

            imports_block = ctk.CTkFrame(self, fg_color=COLORS['bg_darkest'], corner_radius=4)
            imports_block.pack(fill="x")
            for imp in self._imports:
                ctk.CTkLabel(
                    imports_block, text=imp,
                    font=ctk.CTkFont(family=FONTS['family_mono'], size=10),
                    text_color=COLORS['accent'],
                    anchor="w",
                ).pack(fill="x", padx=SPACING['sm'], pady=2)

        if self._on_generate_file and self._npm:
            gen_row = ctk.CTkFrame(self, fg_color="transparent")
            gen_row.pack(fill="x", pady=(SPACING['xs'], 0))
            ctk.CTkButton(
                gen_row, text="Generate polyfills.js", width=150, height=28,
                fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
                text_color=COLORS['text_secondary'], font=ctk.CTkFont(size=10),
                command=lambda: self._on_generate_file("polyfills.js"),
            ).pack(side="left")

    def _copy(self, button):
        self.clipboard_clear()
        self.clipboard_append(self._install_command)
        original = button.cget("text")
        button.configure(text="Copied", fg_color=COLORS['success'])
        button.after(1500, lambda: button.configure(text=original, fg_color=COLORS['bg_light']))


class PolyfillEmptyCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(
            self, text="No polyfills needed.",
            font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'],
        ).pack(anchor="w")
