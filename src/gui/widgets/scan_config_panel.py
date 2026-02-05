"""
ScanConfigPanel - Configuration panel for project scanning options.

Provides checkboxes for exclude patterns, file types, and other scanning options.
"""

from typing import Callable, List, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING
from src.scanner import ScanConfig


class ScanConfigPanel(ctk.CTkFrame):
    """Configuration panel for project scanning."""

    # Default exclude patterns with display names
    EXCLUDE_OPTIONS = [
        ('node_modules', 'node_modules'),
        ('dist', 'dist'),
        ('build', 'build'),
        ('.git', '.git'),
        ('.next', '.next'),
        ('.nuxt', '.nuxt'),
        ('coverage', 'coverage'),
        ('vendor', 'vendor'),
    ]

    # File type options (HTML, CSS, JS only)
    FILE_TYPE_OPTIONS = [
        ('html', 'HTML', COLORS['html_color']),
        ('css', 'CSS', COLORS['css_color']),
        ('javascript', 'JavaScript', COLORS['js_color']),
    ]

    def __init__(
        self,
        master,
        on_config_change: Optional[Callable[[ScanConfig], None]] = None,
        **kwargs
    ):
        """Initialize the scan config panel.

        Args:
            master: Parent widget
            on_config_change: Callback when configuration changes
        """
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._on_config_change = on_config_change
        self._exclude_vars = {}  # pattern -> BooleanVar
        self._file_type_vars = {}  # type -> BooleanVar
        self._skip_minified_var = None
        self._config = ScanConfig()

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Scan Configuration",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))

        # Separator
        sep = ctk.CTkFrame(self, fg_color=COLORS['border'], height=1)
        sep.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

        # Content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))

        # === Exclude Patterns Section ===
        exclude_label = ctk.CTkLabel(
            content,
            text="Exclude Directories:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        )
        exclude_label.pack(anchor="w", pady=(0, SPACING['xs']))

        # Grid of checkboxes for exclude patterns
        exclude_frame = ctk.CTkFrame(content, fg_color="transparent")
        exclude_frame.pack(fill="x", pady=(0, SPACING['md']))

        # Create 4-column grid
        for i, (pattern, display_name) in enumerate(self.EXCLUDE_OPTIONS):
            row = i // 4
            col = i % 4

            var = ctk.BooleanVar(value=pattern in self._config.exclude_patterns)
            self._exclude_vars[pattern] = var

            checkbox = ctk.CTkCheckBox(
                exclude_frame,
                text=display_name,
                variable=var,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_bright'],
                border_color=COLORS['border_light'],
                text_color=COLORS['text_secondary'],
                checkbox_width=16,
                checkbox_height=16,
                command=self._on_change,
            )
            checkbox.grid(row=row, column=col, sticky="w", padx=(0, 16), pady=2)

        # === File Types Section ===
        file_type_label = ctk.CTkLabel(
            content,
            text="File Types:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        )
        file_type_label.pack(anchor="w", pady=(SPACING['sm'], SPACING['xs']))

        file_type_frame = ctk.CTkFrame(content, fg_color="transparent")
        file_type_frame.pack(fill="x", pady=(0, SPACING['md']))

        for i, (type_key, display_name, color) in enumerate(self.FILE_TYPE_OPTIONS):
            var = ctk.BooleanVar(value=True)
            self._file_type_vars[type_key] = var

            checkbox = ctk.CTkCheckBox(
                file_type_frame,
                text=display_name,
                variable=var,
                font=ctk.CTkFont(size=11),
                fg_color=color,
                hover_color=color,
                border_color=COLORS['border_light'],
                text_color=COLORS['text_secondary'],
                checkbox_width=16,
                checkbox_height=16,
                command=self._on_change,
            )
            checkbox.grid(row=0, column=i, sticky="w", padx=(0, 16), pady=2)

        # === Additional Options Section ===
        options_label = ctk.CTkLabel(
            content,
            text="Options:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        )
        options_label.pack(anchor="w", pady=(SPACING['sm'], SPACING['xs']))

        options_frame = ctk.CTkFrame(content, fg_color="transparent")
        options_frame.pack(fill="x")

        # Skip minified files
        self._skip_minified_var = ctk.BooleanVar(value=False)
        skip_minified_cb = ctk.CTkCheckBox(
            options_frame,
            text="Skip minified files (.min.js, .min.css)",
            variable=self._skip_minified_var,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_bright'],
            border_color=COLORS['border_light'],
            text_color=COLORS['text_secondary'],
            checkbox_width=16,
            checkbox_height=16,
            command=self._on_change,
        )
        skip_minified_cb.pack(anchor="w", pady=2)

    def _on_change(self):
        """Handle configuration change."""
        self._update_config()
        if self._on_config_change:
            self._on_config_change(self._config)

    def _update_config(self):
        """Update the internal config from UI state."""
        # Build exclude patterns list
        exclude_patterns = []
        for pattern, var in self._exclude_vars.items():
            if var.get():
                exclude_patterns.append(pattern)

        # Add some common patterns that are always excluded
        always_exclude = ['__pycache__', '.cache']
        exclude_patterns.extend(always_exclude)

        self._config.exclude_patterns = exclude_patterns

        # File types
        self._config.include_html = self._file_type_vars.get('html', ctk.BooleanVar(value=True)).get()
        self._config.include_css = self._file_type_vars.get('css', ctk.BooleanVar(value=True)).get()
        self._config.include_javascript = self._file_type_vars.get('javascript', ctk.BooleanVar(value=True)).get()

        # Options
        self._config.skip_minified = self._skip_minified_var.get() if self._skip_minified_var else False

    def get_config(self) -> ScanConfig:
        """Get the current scan configuration.

        Returns:
            ScanConfig with current settings
        """
        self._update_config()
        return self._config

    def set_config(self, config: ScanConfig):
        """Set the configuration from a ScanConfig object.

        Args:
            config: ScanConfig to apply
        """
        self._config = config

        # Update exclude checkboxes
        for pattern, var in self._exclude_vars.items():
            var.set(pattern in config.exclude_patterns)

        # Update file type checkboxes
        if 'html' in self._file_type_vars:
            self._file_type_vars['html'].set(config.include_html)
        if 'css' in self._file_type_vars:
            self._file_type_vars['css'].set(config.include_css)
        if 'javascript' in self._file_type_vars:
            self._file_type_vars['javascript'].set(config.include_javascript)

        # Update options
        if self._skip_minified_var:
            self._skip_minified_var.set(config.skip_minified)

    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.set_config(ScanConfig())

    def get_active_file_types(self) -> List[str]:
        """Get list of currently enabled file types.

        Returns:
            List of enabled file type names
        """
        types = []
        for type_key, var in self._file_type_vars.items():
            if var.get():
                types.append(type_key)
        return types

    def has_any_file_type(self) -> bool:
        """Check if at least one file type is enabled.

        Returns:
            True if at least one file type is enabled
        """
        return any(var.get() for var in self._file_type_vars.values())

    def set_exclude(self, pattern: str, excluded: bool):
        """Set the exclusion state for a specific pattern.

        Args:
            pattern: The pattern name (e.g., 'build', 'dist', 'node_modules')
            excluded: True to exclude, False to include
        """
        if pattern in self._exclude_vars:
            self._exclude_vars[pattern].set(excluded)
            self._on_change()

    def is_excluded(self, pattern: str) -> bool:
        """Check if a pattern is currently excluded.

        Args:
            pattern: The pattern name to check

        Returns:
            True if the pattern is excluded
        """
        if pattern in self._exclude_vars:
            return self._exclude_vars[pattern].get()
        return False
