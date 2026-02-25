"""Polyfill recommendation card with copy-to-clipboard and file generation."""

from typing import List, Callable, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, FONTS


class PolyfillCard(ctk.CTkFrame):
    """Shows polyfill recommendations: npm commands, imports, CSS fallbacks."""

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
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['info'],
            **kwargs
        )

        self._install_command = install_command
        self._import_statements = import_statements
        self._npm_recommendations = npm_recommendations
        self._css_fallbacks = css_fallbacks
        self._total_size_kb = total_size_kb
        self._on_generate_file = on_generate_file

        self._init_ui()

    def _init_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))

        icon = ctk.CTkLabel(
            header,
            text="\U0001F4E6",
            font=ctk.CTkFont(size=16)
        )
        icon.pack(side="left")

        title = ctk.CTkLabel(
            header,
            text="Polyfill Recommendations",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title.pack(side="left", padx=(SPACING['xs'], 0))

        count = len(self._npm_recommendations) + len(self._css_fallbacks)
        badge = ctk.CTkLabel(
            header,
            text=f" {count} ",
            font=ctk.CTkFont(size=11),
            fg_color=COLORS['info'],
            corner_radius=10,
            text_color=COLORS['text_primary'],
        )
        badge.pack(side="left", padx=(SPACING['sm'], 0))

        if self._total_size_kb > 0:
            size_label = ctk.CTkLabel(
                header,
                text=f"~{self._total_size_kb:.1f} KB",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted']
            )
            size_label.pack(side="right")

        sep = ctk.CTkFrame(self, fg_color=COLORS['border'], height=1)
        sep.pack(fill="x", padx=SPACING['md'])

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        if self._install_command:
            self._build_command_section(
                content,
                "Install packages:",
                self._install_command,
                is_multiline=False
            )

        if self._import_statements:
            imports_text = "\n".join(self._import_statements)
            self._build_command_section(
                content,
                "Add to your entry file:",
                imports_text,
                is_multiline=True
            )

        if self._npm_recommendations:
            self._build_polyfill_list(content)

        if self._css_fallbacks:
            self._build_fallbacks_section(content)

        if self._on_generate_file and self._npm_recommendations:
            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))

            gen_btn = ctk.CTkButton(
                btn_frame,
                text="\U0001F4C4  Generate polyfills.js",
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_dim'],
                font=ctk.CTkFont(size=12),
                height=32,
                command=self._on_generate_click
            )
            gen_btn.pack(side="left")

            hint = ctk.CTkLabel(
                btn_frame,
                text="Creates a ready-to-import file",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted']
            )
            hint.pack(side="left", padx=(SPACING['sm'], 0))

    def _build_command_section(
        self,
        parent,
        label: str,
        command: str,
        is_multiline: bool = False
    ):
        """Build a copyable command block."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, SPACING['md']))

        lbl = ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        lbl.pack(anchor="w")

        cmd_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_dark'], corner_radius=4)
        cmd_frame.pack(fill="x", pady=(SPACING['xs'], 0))

        if is_multiline:
            cmd_text = ctk.CTkTextbox(
                cmd_frame,
                font=ctk.CTkFont(family=FONTS['family_mono'], size=11),
                text_color=COLORS['text_muted'],
                fg_color=COLORS['bg_dark'],
                height=min(100, 20 * len(command.split('\n'))),
                wrap="none",
                activate_scrollbars=False
            )
            cmd_text.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'], fill="x", expand=True)
            cmd_text.insert("1.0", command)
            cmd_text.configure(state="disabled")
        else:
            cmd_text = ctk.CTkLabel(
                cmd_frame,
                text=command,
                font=ctk.CTkFont(family=FONTS['family_mono'], size=11),
                text_color=COLORS['text_muted'],
                justify="left",
                anchor="w"
            )
            cmd_text.pack(side="left", padx=SPACING['sm'], pady=SPACING['sm'], fill="x", expand=True)

        copy_btn = ctk.CTkButton(
            cmd_frame,
            text="Copy",
            width=60,
            height=28,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(size=11),
            command=lambda: self._copy_to_clipboard(command)
        )
        copy_btn.pack(side="right", padx=SPACING['xs'], pady=SPACING['xs'])

    def _build_polyfill_list(self, parent):
        """Build the list of individual polyfill packages."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, SPACING['sm']))

        lbl = ctk.CTkLabel(
            frame,
            text="Polyfills needed:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        lbl.pack(anchor="w")

        list_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_dark'], corner_radius=4)
        list_frame.pack(fill="x", pady=(SPACING['xs'], 0))

        for rec in self._npm_recommendations:
            item = ctk.CTkFrame(list_frame, fg_color="transparent")
            item.pack(fill="x", padx=SPACING['sm'], pady=SPACING['xs'])

            bullet = ctk.CTkLabel(
                item,
                text="\u2022",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['success'],
                width=16
            )
            bullet.pack(side="left")

            name_lbl = ctk.CTkLabel(
                item,
                text=rec.feature_name,
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_primary']
            )
            name_lbl.pack(side="left")

            if rec.packages:
                pkg_name = rec.packages[0].npm_package
                pkg_lbl = ctk.CTkLabel(
                    item,
                    text=f"({pkg_name})",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text_muted']
                )
                pkg_lbl.pack(side="left", padx=(SPACING['xs'], 0))

                if rec.packages[0].size_kb:
                    size_lbl = ctk.CTkLabel(
                        item,
                        text=f"{rec.packages[0].size_kb} KB",
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS['text_disabled']
                    )
                    size_lbl.pack(side="right")

    def _build_fallbacks_section(self, parent):
        """Build CSS fallback code blocks."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(SPACING['sm'], 0))

        lbl = ctk.CTkLabel(
            frame,
            text="CSS Fallback Strategies:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        lbl.pack(anchor="w")

        for rec in self._css_fallbacks:
            fallback_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_dark'], corner_radius=4)
            fallback_frame.pack(fill="x", pady=(SPACING['xs'], 0))

            header = ctk.CTkFrame(fallback_frame, fg_color="transparent")
            header.pack(fill="x", padx=SPACING['sm'], pady=(SPACING['sm'], 0))

            name_lbl = ctk.CTkLabel(
                header,
                text=f"\u26A0  {rec.feature_name}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['warning']
            )
            name_lbl.pack(side="left")

            if rec.fallback_description:
                desc_lbl = ctk.CTkLabel(
                    fallback_frame,
                    text=rec.fallback_description,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text_muted'],
                    wraplength=500,
                    justify="left"
                )
                desc_lbl.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))

            if rec.fallback_code:
                code_frame = ctk.CTkFrame(fallback_frame, fg_color=COLORS['bg_darkest'], corner_radius=4)
                code_frame.pack(fill="x", padx=SPACING['sm'], pady=SPACING['sm'])

                code_text = ctk.CTkTextbox(
                    code_frame,
                    font=ctk.CTkFont(family=FONTS['family_mono'], size=10),
                    text_color=COLORS['text_muted'],
                    fg_color=COLORS['bg_darkest'],
                    height=min(150, 15 * len(rec.fallback_code.split('\n'))),
                    wrap="none"
                )
                code_text.pack(fill="x", padx=SPACING['xs'], pady=SPACING['xs'])
                code_text.insert("1.0", rec.fallback_code)
                code_text.configure(state="disabled")

                copy_code_btn = ctk.CTkButton(
                    code_frame,
                    text="Copy CSS",
                    width=80,
                    height=24,
                    fg_color=COLORS['bg_light'],
                    hover_color=COLORS['hover_bg'],
                    text_color=COLORS['text_secondary'],
                    font=ctk.CTkFont(size=10),
                    command=lambda code=rec.fallback_code: self._copy_to_clipboard(code)
                )
                copy_code_btn.pack(anchor="e", padx=SPACING['xs'], pady=(0, SPACING['xs']))

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _on_generate_click(self):
        if self._on_generate_file:
            self._on_generate_file("polyfills.js")


class PolyfillEmptyCard(ctk.CTkFrame):
    """Shown when no polyfills are needed."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._init_ui()

    def _init_ui(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        icon = ctk.CTkLabel(
            content,
            text="\u2713",
            font=ctk.CTkFont(size=24),
            text_color=COLORS['success']
        )
        icon.pack()

        text = ctk.CTkLabel(
            content,
            text="No polyfills needed",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary']
        )
        text.pack(pady=(SPACING['xs'], 0))

        subtext = ctk.CTkLabel(
            content,
            text="All detected features are fully supported in your target browsers,\nor no polyfills are available for the unsupported features.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
            wraplength=400,
            justify="center"
        )
        subtext.pack(pady=(SPACING['xs'], 0))
