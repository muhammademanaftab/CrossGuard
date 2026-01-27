"""
Cross Guard Main Window - Professional UI Redesign
VS Code-style layout with sidebar navigation, file table, and results view.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import customtkinter as ctk

# API Layer imports
from src.api import get_analyzer_service, AnalysisResult

from .theme import COLORS, SPACING, ICONS, WINDOW, LOGO_SIMPLE, enable_smooth_scrolling
from .widgets import (
    Sidebar,
    HeaderBar,
    StatusBar,
    FileTable,
    DropZone,
    ScoreCard,
    BrowserCard,
    BrowserRadarChart,
    CompatibilityBarChart,
    FeatureDistributionChart,
    show_info,
    show_warning,
    show_error,
    ask_question,
    ProgressDialog,
    # New progressive disclosure widgets
    BuildBadge,
    CollapsibleSection,
    IssuesSummary,
    QuickStatsBar,
)
from .widgets.rules_manager import show_rules_manager
from .export_manager import ExportManager

# Import feature name utilities
from src.utils.feature_names import get_feature_name, get_fix_suggestion


class MainWindow(ctk.CTkFrame):
    """Main application window with VS Code-style layout.

    Features:
    - Sidebar navigation (Files, Results, Settings)
    - File table with drag-and-drop
    - Results view with scores and browser cards
    - Settings view with database update and custom rules
    """

    def __init__(self, master):
        """Initialize the main window."""
        super().__init__(master, fg_color=COLORS['bg_darkest'])

        self.master = master
        self.current_report = None
        self.export_manager = ExportManager(master)
        self._analyzer_service = get_analyzer_service()
        self._current_view = "files"

        # Store last analyzed files for re-checking
        self._last_files: List[str] = []

        # Build the layout
        self._init_layout()
        self._show_view("files")

    def _init_layout(self):
        """Initialize the main layout structure."""
        # Configure grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(0, weight=0)     # Header
        self.grid_rowconfigure(1, weight=1)     # Main content
        self.grid_rowconfigure(2, weight=0)     # Status bar

        # Sidebar
        self.sidebar = Sidebar(
            self,
            on_navigate=self._on_navigate,
        )
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")

        # Header bar
        self.header = HeaderBar(
            self,
            title="Browser Compatibility Checker",
        )
        self.header.grid(row=0, column=1, sticky="ew")

        # Content area (will hold different views)
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_dark'],
            corner_radius=0,
        )
        self.content_frame.grid(row=1, column=1, sticky="nsew")

        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=1, sticky="ew")

        # Initialize views (but don't show yet)
        self._views = {}

    def _on_navigate(self, view_id: str):
        """Handle sidebar navigation."""
        if view_id == "help":
            self._show_help()
            return
        self._show_view(view_id)

    def _show_view(self, view_id: str):
        """Show a specific view.

        Args:
            view_id: The view identifier ('files', 'results', 'settings')
        """
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self._current_view = view_id

        # Build the requested view
        if view_id == "files":
            self._build_files_view()
        elif view_id == "results":
            self._build_results_view()
        elif view_id == "settings":
            self._build_settings_view()

        # Update header
        titles = {
            "files": "File Selection",
            "results": "Analysis Results",
            "settings": "Settings",
        }
        self.header.set_title(titles.get(view_id, "Cross Guard"))

    def _build_files_view(self):
        """Build the files view with drop zone and file table."""
        # Scrollable container
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        enable_smooth_scrolling(scroll_frame)

        # Title section
        title_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, SPACING['lg']))

        title_label = ctk.CTkLabel(
            title_frame,
            text="Select Files to Analyze",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Drag and drop files or use the file browser",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_muted'],
        )
        subtitle_label.pack(side="left", padx=(SPACING['lg'], 0))

        # Drop zone
        self.drop_zone = DropZone(
            scroll_frame,
            allowed_extensions=['html', 'htm', 'css', 'js'],
            on_files_dropped=self._on_files_dropped,
            height=160,
        )
        self.drop_zone.pack(fill="x", pady=(0, SPACING['xl']))

        # File table section
        table_header = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        table_header.pack(fill="x", pady=(0, SPACING['sm']))

        table_title = ctk.CTkLabel(
            table_header,
            text="Selected Files",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        table_title.pack(side="left")

        # Clear button
        clear_btn = ctk.CTkButton(
            table_header,
            text=f"{ICONS['delete']} Clear All",
            font=ctk.CTkFont(size=12),
            width=100,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['danger_muted'],
            text_color=COLORS['text_muted'],
            command=self._clear_all_files,
        )
        clear_btn.pack(side="right")

        # File table
        self.file_table = FileTable(
            scroll_frame,
            on_files_changed=self._update_status,
        )
        self.file_table.pack(fill="both", expand=True, pady=(0, SPACING['xl']))

        # Restore files if any were previously added
        if self._last_files:
            existing_files = [f for f in self._last_files if Path(f).exists()]
            if existing_files:
                self.file_table.add_files(existing_files)

        # Action buttons
        actions_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        actions_frame.pack(fill="x")

        # Analyze button
        analyze_btn = ctk.CTkButton(
            actions_frame,
            text=f"{ICONS['check']} Analyze Compatibility",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=220,
            height=48,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dim'],
            command=self._analyze_files,
        )
        analyze_btn.pack(side="right")

        self._update_status()

    def _build_results_view(self):
        """Build the results view with progressive disclosure design.

        Layout:
        1. Build Badge Hero (always visible)
        2. Quick Stats Bar (always visible)
        3. Issues Summary (if problems exist)
        4. Browser Support (collapsed by default)
        5. Technical Details (collapsed by default)
        6. Export Actions (bottom)
        """
        if not self.current_report:
            # No results yet
            empty_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            empty_frame.place(relx=0.5, rely=0.5, anchor="center")

            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No Analysis Results",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=COLORS['text_muted'],
            )
            empty_label.pack()

            hint_label = ctk.CTkLabel(
                empty_frame,
                text="Add files and run an analysis to see results",
                font=ctk.CTkFont(size=13),
                text_color=COLORS['text_disabled'],
            )
            hint_label.pack(pady=(SPACING['sm'], 0))

            go_btn = ctk.CTkButton(
                empty_frame,
                text="Go to Files",
                font=ctk.CTkFont(size=13),
                width=120,
                height=36,
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_dim'],
                command=lambda: self._show_view("files"),
            )
            go_btn.pack(pady=(SPACING['lg'], 0))
            return

        report = self.current_report

        # Scrollable container
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        enable_smooth_scrolling(scroll_frame)

        # Extract report data
        scores = report.get('scores', {})
        summary = report.get('summary', {})
        browsers = report.get('browsers', {})
        features = report.get('features', {})

        weighted_score = scores.get('weighted_score', 0)
        grade = scores.get('grade', 'N/A')
        total_features = summary.get('total_features', 0)
        browsers_count = len(browsers)

        # Calculate issues count
        issues_count = self._count_issues(browsers)

        # ===== SECTION 1: Build Badge Hero (Always Visible) =====
        build_badge = BuildBadge(scroll_frame)
        build_badge.pack(fill="x", pady=(0, SPACING['lg']))
        build_badge.set_data(
            score=weighted_score,
            total_features=total_features,
            issues_count=issues_count,
            browsers_count=browsers_count,
            animate=True
        )

        # ===== SECTION 2: Quick Stats Bar (Always Visible) =====
        quick_stats = QuickStatsBar(scroll_frame)
        quick_stats.pack(fill="x", pady=(0, SPACING['lg']))
        quick_stats.set_data(
            score=weighted_score,
            grade=grade,
            browsers_count=browsers_count,
            features_count=total_features
        )

        # ===== SECTION 3: Issues Summary (If Problems Exist) =====
        issues = self._extract_issues(browsers)
        if issues:
            issues_summary = IssuesSummary(scroll_frame, issues=issues)
            issues_summary.pack(fill="x", pady=(0, SPACING['lg']))

        # ===== SECTION 4: Browser Support (Collapsed by Default) =====
        if browsers:
            browser_section = CollapsibleSection(
                scroll_frame,
                title="Browser Support",
                badge_text=f"{browsers_count} browsers",
                badge_color=COLORS['accent'],
                expanded=False,
            )
            browser_section.pack(fill="x", pady=(0, SPACING['lg']))

            # Add browser cards to collapsible content
            browser_content = browser_section.get_content_frame()
            for browser_name, details in browsers.items():
                card = BrowserCard(
                    browser_content,
                    browser_name=browser_name,
                    version=details.get('version', ''),
                    supported=details.get('supported', 0),
                    partial=details.get('partial', 0),
                    unsupported=details.get('unsupported', 0),
                    compatibility_pct=details.get('compatibility_percentage', 0),
                    unsupported_features=details.get('unsupported_features', []),
                    partial_features=details.get('partial_features', []),
                )
                card.pack(fill="x", pady=(0, SPACING['sm']))

        # ===== SECTION 5: Technical Details (Collapsed by Default) =====

        # 5a. Detected Features
        if features and any([features.get('html'), features.get('css'), features.get('js')]):
            features_section = CollapsibleSection(
                scroll_frame,
                title="Detected Features",
                badge_text=str(total_features),
                badge_color=COLORS['info'],
                expanded=False,
            )
            features_section.pack(fill="x", pady=(0, SPACING['lg']))

            features_content = features_section.get_content_frame()
            feature_types = [
                ("HTML", features.get('html', []), COLORS['html_color']),
                ("CSS", features.get('css', []), COLORS['css_color']),
                ("JavaScript", features.get('js', []), COLORS['js_color']),
            ]

            for type_name, feature_list, color in feature_types:
                if feature_list:
                    type_frame = ctk.CTkFrame(features_content, fg_color="transparent")
                    type_frame.pack(fill="x", pady=(0, SPACING['sm']))

                    badge = ctk.CTkLabel(
                        type_frame,
                        text=f" {type_name} ({len(feature_list)}) ",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS['text_primary'],
                        fg_color=color,
                        corner_radius=4,
                    )
                    badge.pack(side="left")

                    # Show human-readable names
                    readable_features = [get_feature_name(f) for f in feature_list[:15]]
                    features_text = ", ".join(readable_features)
                    if len(feature_list) > 15:
                        features_text += f", ... (+{len(feature_list) - 15} more)"

                    ctk.CTkLabel(
                        type_frame,
                        text=features_text,
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS['text_secondary'],
                        wraplength=600,
                        justify="left",
                    ).pack(side="left", padx=(SPACING['sm'], 0))

        # 5b. Visualizations
        if browsers:
            viz_section = CollapsibleSection(
                scroll_frame,
                title="Visualizations",
                badge_text="Charts",
                badge_color=COLORS['accent_dim'],
                expanded=False,
            )
            viz_section.pack(fill="x", pady=(0, SPACING['lg']))

            viz_content = viz_section.get_content_frame()

            # Charts container
            charts_frame = ctk.CTkFrame(viz_content, fg_color="transparent")
            charts_frame.pack(fill="x", pady=(0, SPACING['sm']))

            charts_frame.grid_columnconfigure(0, weight=1)
            charts_frame.grid_columnconfigure(1, weight=1)

            chart_data = {
                name: {
                    'supported': d.get('supported', 0),
                    'partial': d.get('partial', 0),
                    'unsupported': d.get('unsupported', 0),
                    'compatibility_percentage': d.get('compatibility_percentage', 0)
                }
                for name, d in browsers.items()
            }

            # Radar chart (left side)
            radar_chart = BrowserRadarChart(charts_frame)
            radar_chart.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING['sm']))
            radar_chart.set_data(chart_data)

            # Feature distribution chart (right side)
            feature_chart = FeatureDistributionChart(charts_frame)
            feature_chart.grid(row=0, column=1, sticky="nsew", padx=(SPACING['sm'], 0))
            feature_chart.set_data(
                summary.get('html_features', 0),
                summary.get('css_features', 0),
                summary.get('js_features', 0),
                summary.get('total_features', None)
            )

            # Feature Support Breakdown (full width below)
            breakdown_chart = CompatibilityBarChart(viz_content)
            breakdown_chart.pack(fill="x", pady=(SPACING['sm'], 0))
            breakdown_chart.set_data(chart_data)

        # 5c. Unrecognized Patterns
        unrecognized = report.get('unrecognized', {})
        if unrecognized and unrecognized.get('total', 0) > 0:
            unrec_section = CollapsibleSection(
                scroll_frame,
                title="Unrecognized Patterns",
                badge_text=str(unrecognized.get('total', 0)),
                badge_color=COLORS['warning'],
                expanded=False,
            )
            unrec_section.pack(fill="x", pady=(0, SPACING['lg']))

            unrec_content = unrec_section.get_content_frame()

            # Info message
            ctk.CTkLabel(
                unrec_content,
                text="These patterns were found but have no detection rules. Consider adding custom rules.",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted'],
            ).pack(anchor="w", pady=(0, SPACING['sm']))

            unrec_types = [
                ("HTML", unrecognized.get('html', []), COLORS['html_color']),
                ("CSS", unrecognized.get('css', []), COLORS['css_color']),
                ("JavaScript", unrecognized.get('js', []), COLORS['js_color']),
            ]

            for type_name, pattern_list, color in unrec_types:
                if pattern_list:
                    type_frame = ctk.CTkFrame(unrec_content, fg_color="transparent")
                    type_frame.pack(fill="x", pady=(0, SPACING['sm']))

                    badge = ctk.CTkLabel(
                        type_frame,
                        text=f" {type_name} ({len(pattern_list)}) ",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS['text_primary'],
                        fg_color=color,
                        corner_radius=4,
                    )
                    badge.pack(side="left")

                    patterns_text = ", ".join(pattern_list[:10])
                    if len(pattern_list) > 10:
                        patterns_text += f", ... (+{len(pattern_list) - 10} more)"

                    ctk.CTkLabel(
                        type_frame,
                        text=patterns_text,
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS['text_muted'],
                        wraplength=600,
                        justify="left",
                    ).pack(side="left", padx=(SPACING['sm'], 0))

        # 5d. Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            rec_section = CollapsibleSection(
                scroll_frame,
                title="Recommendations",
                badge_text=str(len(recommendations)),
                badge_color=COLORS['info'],
                expanded=False,
            )
            rec_section.pack(fill="x", pady=(0, SPACING['lg']))

            rec_content = rec_section.get_content_frame()
            for i, rec in enumerate(recommendations, 1):
                rec_frame = ctk.CTkFrame(
                    rec_content,
                    fg_color=COLORS['bg_light'],
                    corner_radius=4,
                )
                rec_frame.pack(fill="x", pady=(0, SPACING['sm']))

                ctk.CTkLabel(
                    rec_frame,
                    text=f"{i}. {rec}",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS['text_secondary'],
                    wraplength=600,
                    justify="left",
                ).pack(anchor="w", padx=SPACING['sm'], pady=SPACING['sm'])

        # ===== SECTION 6: Export Actions (Bottom) =====
        actions_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
        )
        actions_frame.pack(fill="x", pady=(SPACING['md'], 0))

        actions_inner = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_inner.pack(fill="x", padx=SPACING['lg'], pady=SPACING['md'])

        recheck_btn = ctk.CTkButton(
            actions_inner,
            text=f"{ICONS['refresh']} Re-check",
            font=ctk.CTkFont(size=12),
            width=110,
            height=36,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            command=self._recheck_files,
        )
        recheck_btn.pack(side="left", padx=(0, SPACING['sm']))

        export_pdf_btn = ctk.CTkButton(
            actions_inner,
            text="Export PDF",
            font=ctk.CTkFont(size=12),
            width=110,
            height=36,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dim'],
            command=lambda: self.export_manager.export_pdf(self.current_report),
        )
        export_pdf_btn.pack(side="left", padx=(0, SPACING['sm']))

        export_json_btn = ctk.CTkButton(
            actions_inner,
            text="Export JSON",
            font=ctk.CTkFont(size=12),
            width=110,
            height=36,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            command=lambda: self.export_manager.export_json(self.current_report),
        )
        export_json_btn.pack(side="left")

    def _count_issues(self, browsers: Dict) -> int:
        """Count total issues (unsupported + partial) across all browsers."""
        issues = set()
        for browser_data in browsers.values():
            for feature in browser_data.get('unsupported_features', []):
                issues.add(feature)
            for feature in browser_data.get('partial_features', []):
                issues.add(feature)
        return len(issues)

    def _extract_issues(self, browsers: Dict) -> List[dict]:
        """Extract issues from browser data for IssuesSummary.

        Returns list of issue dicts with:
        - feature_name: Human-readable name
        - feature_id: Technical ID
        - severity: 'critical' or 'warning'
        - browsers: List of affected browsers
        - fix_suggestion: Optional fix text
        """
        # Group issues by feature
        unsupported_map = {}  # feature_id -> list of browsers
        partial_map = {}  # feature_id -> list of browsers

        for browser_name, data in browsers.items():
            browser_display = f"{browser_name.title()} {data.get('version', '')}"

            for feature in data.get('unsupported_features', []):
                if feature not in unsupported_map:
                    unsupported_map[feature] = []
                unsupported_map[feature].append(browser_display)

            for feature in data.get('partial_features', []):
                if feature not in partial_map:
                    partial_map[feature] = []
                partial_map[feature].append(browser_display)

        issues = []

        # Add critical issues (unsupported)
        for feature_id, affected_browsers in unsupported_map.items():
            issues.append({
                'feature_name': get_feature_name(feature_id),
                'feature_id': feature_id,
                'severity': 'critical',
                'browsers': affected_browsers,
                'fix_suggestion': get_fix_suggestion(feature_id),
            })

        # Add warning issues (partial) - only if not already critical
        for feature_id, affected_browsers in partial_map.items():
            if feature_id not in unsupported_map:
                issues.append({
                    'feature_name': get_feature_name(feature_id),
                    'feature_id': feature_id,
                    'severity': 'warning',
                    'browsers': affected_browsers,
                    'fix_suggestion': get_fix_suggestion(feature_id),
                })

        return issues

    def _build_settings_view(self):
        """Build the settings view."""
        # Container
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])

        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title_label.pack(anchor="w", pady=(0, SPACING['xl']))

        # Database section
        db_section = ctk.CTkFrame(
            container,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
        )
        db_section.pack(fill="x", pady=(0, SPACING['lg']))

        db_header = ctk.CTkFrame(db_section, fg_color="transparent")
        db_header.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        ctk.CTkLabel(
            db_header,
            text="Can I Use Database",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        update_btn = ctk.CTkButton(
            db_header,
            text=f"{ICONS['refresh']} Update Database",
            font=ctk.CTkFont(size=12),
            width=150,
            height=36,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dim'],
            command=self._update_database,
        )
        update_btn.pack(side="right")

        # Database info
        try:
            db_info = self._analyzer_service.get_database_info()
            info_text = f"Features: {db_info.features_count}  |  Last updated: {db_info.last_updated}"
        except Exception:
            info_text = "Unable to load database info"

        ctk.CTkLabel(
            db_section,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))

        # Custom rules section
        rules_section = ctk.CTkFrame(
            container,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
        )
        rules_section.pack(fill="x", pady=(0, SPACING['lg']))

        rules_header = ctk.CTkFrame(rules_section, fg_color="transparent")
        rules_header.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        ctk.CTkLabel(
            rules_header,
            text="Custom Detection Rules",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        rules_btn = ctk.CTkButton(
            rules_header,
            text=f"{ICONS['settings']} Manage Rules",
            font=ctk.CTkFont(size=12),
            width=140,
            height=36,
            fg_color=COLORS['bg_light'],
            hover_color=COLORS['hover_bg'],
            command=self._open_rules_manager,
        )
        rules_btn.pack(side="right")

        ctk.CTkLabel(
            rules_section,
            text="Add custom feature detection patterns without modifying source code",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))

        # About section
        about_section = ctk.CTkFrame(
            container,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
        )
        about_section.pack(fill="x")

        about_content = ctk.CTkFrame(about_section, fg_color="transparent")
        about_content.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        ctk.CTkLabel(
            about_content,
            text=LOGO_SIMPLE,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['accent'],
        ).pack(anchor="w")

        ctk.CTkLabel(
            about_content,
            text="Browser Compatibility Checker",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(anchor="w", pady=(SPACING['xs'], 0))

        ctk.CTkLabel(
            about_content,
            text="Analyzes HTML, CSS, and JavaScript for browser support issues",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(SPACING['xs'], 0))

    def _on_files_dropped(self, file_paths: List[str]):
        """Handle files dropped onto drop zone."""
        if hasattr(self, 'file_table'):
            self.file_table.add_files(file_paths)
            self._update_status()

    def _clear_all_files(self):
        """Clear all selected files."""
        if hasattr(self, 'file_table'):
            self.file_table.clear_files()
            self._last_files = []
            self._update_status()

    def _update_status(self):
        """Update status bar with file count."""
        if hasattr(self, 'file_table'):
            count = self.file_table.get_file_count()
            self._last_files = self.file_table.get_files()
        else:
            count = len(self._last_files)

        self.status_bar.set_file_count(count)

        if count > 0:
            self.status_bar.set_status(f"{count} file(s) ready for analysis", "info")
        else:
            self.status_bar.set_status("Ready", "normal")

    def _analyze_files(self):
        """Analyze selected files."""
        if not hasattr(self, 'file_table'):
            return

        files = self.file_table.get_files()
        if not files:
            show_warning(self.master, "No Files", "Please select at least one file.")
            return

        if ask_question(self.master, "Confirm", f"Analyze {len(files)} file(s)?"):
            self._run_analysis(files)

    def _run_analysis(self, files: List[str]):
        """Run the analysis."""
        self._last_files = list(files)

        # Separate files by type
        html_files = [f for f in files if Path(f).suffix.lower() in ['.html', '.htm']]
        css_files = [f for f in files if Path(f).suffix.lower() == '.css']
        js_files = [f for f in files if Path(f).suffix.lower() == '.js']

        try:
            progress = ProgressDialog(self.master, "Analyzing", "Starting analysis...")
            progress.set_progress(10)
            self.master.update()

            progress.set_progress(30, "Analyzing browser compatibility...")
            result = self._analyzer_service.analyze_files(
                html_files=html_files if html_files else None,
                css_files=css_files if css_files else None,
                js_files=js_files if js_files else None,
            )

            progress.set_progress(100)
            progress.close()

            if result.success:
                self.current_report = result.to_dict()
                self.status_bar.set_last_analysis()
                self.status_bar.set_status("Analysis complete", "success")

                # Navigate to results
                self.sidebar.set_active_view("results")
                self._show_view("results")
            else:
                show_error(self.master, "Analysis Failed", f"{result.error or 'Unknown error'}")

        except Exception as e:
            show_error(self.master, "Error", str(e))
            import traceback
            traceback.print_exc()

    def _recheck_files(self):
        """Re-analyze the previously selected files."""
        if not self._last_files:
            show_warning(self.master, "Warning", "No files to re-check.")
            return

        # Verify files still exist
        missing = [f for f in self._last_files if not Path(f).exists()]
        if missing:
            missing_list = "\n".join(missing[:5])
            if len(missing) > 5:
                missing_list += f"\n... and {len(missing) - 5} more"
            show_warning(self.master, "Missing Files", f"Some files no longer exist:\n{missing_list}")
            return

        self._run_analysis(self._last_files)

    def _update_database(self):
        """Update the Can I Use database."""
        try:
            db_info = self._analyzer_service.get_database_info()

            msg = f"Features: {db_info.features_count}\n"
            msg += f"Last updated: {db_info.last_updated}\n\n"
            msg += "Download latest database?"

            if not ask_question(self.master, "Update Database", msg):
                return

            progress = ProgressDialog(self.master, "Updating", "Connecting...")
            progress.set_progress(0)

            def update_progress(message: str, percentage: int):
                progress.set_progress(percentage, message)
                self.master.update()

            result = self._analyzer_service.update_database(update_progress)

            progress.set_progress(100)
            progress.close()

            if result.success:
                show_info(self.master, "Success", result.message or 'Database updated!')
                # Refresh settings view
                if self._current_view == "settings":
                    self._show_view("settings")
            else:
                show_error(self.master, "Failed", result.message or 'Update failed')

        except Exception as e:
            show_error(self.master, "Error", str(e))

    def _open_rules_manager(self):
        """Open the custom rules manager dialog."""
        def on_rules_changed():
            # Reload custom rules AND reset the analyzer to pick them up
            self._analyzer_service.reload_custom_rules()

        show_rules_manager(self.master, on_rules_changed)

    def _show_help(self):
        """Show help information."""
        help_text = """Cross Guard - Browser Compatibility Checker

How to use:
1. Go to Files view and add HTML, CSS, or JS files
2. Click 'Analyze Compatibility' to check browser support
3. View results in the Results tab
4. Export as PDF or JSON for reports

Features:
- Drag and drop file support
- Custom detection rules
- Multiple browser support checking
- Detailed compatibility reports"""

        show_info(self.master, "Help", help_text)
