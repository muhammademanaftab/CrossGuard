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
    # ML Risk Assessment widgets
    MLRiskCard,
    MLFeatureImportanceCard,
    # Browser Selection
    BrowserSelector,
    get_available_browsers,
    # History and Statistics widgets
    HistoryCard,
    EmptyHistoryCard,
    StatisticsPanel,
    CompactStatsBar,
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

        # Store selected browsers for analysis (default: Chrome, Firefox, Safari, Edge)
        self._selected_browsers: Dict[str, str] = None  # Will use widget defaults

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
        elif view_id == "history":
            self._build_history_view()
        elif view_id == "settings":
            self._build_settings_view()

        # Update header
        titles = {
            "files": "File Selection",
            "results": "Analysis Results",
            "history": "Analysis History",
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

        # Browser Selector section
        browser_header = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        browser_header.pack(fill="x", pady=(SPACING['lg'], SPACING['sm']))

        browser_title = ctk.CTkLabel(
            browser_header,
            text="Target Browsers",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        browser_title.pack(side="left")

        browser_subtitle = ctk.CTkLabel(
            browser_header,
            text="Select which browsers to check compatibility for",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        )
        browser_subtitle.pack(side="left", padx=(SPACING['md'], 0))

        # Browser selector widget
        self.browser_selector = BrowserSelector(
            scroll_frame,
            on_selection_change=self._on_browser_selection_change,
        )
        self.browser_selector.pack(fill="x", pady=(0, SPACING['xl']))

        # Initialize selected browsers from widget
        self._selected_browsers = self.browser_selector.get_selected_browsers()

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

        # ===== SECTION 2.5: ML Risk Assessment (On-Demand) =====
        # Store features for later ML analysis
        self._ml_features = features
        self._ml_total_features = total_features

        ml_section = CollapsibleSection(
            scroll_frame,
            title="ML Risk Assessment",
            badge_text="AI",
            badge_color=COLORS['accent'],
            expanded=True,
        )
        ml_section.pack(fill="x", pady=(0, SPACING['lg']))

        ml_content = ml_section.get_content_frame()

        # Container for ML content (will be updated when button clicked)
        self._ml_content_frame = ctk.CTkFrame(ml_content, fg_color="transparent")
        self._ml_content_frame.pack(fill="x")

        # Initial state: Show button to run ML analysis
        self._ml_button_frame = ctk.CTkFrame(self._ml_content_frame, fg_color=COLORS['bg_medium'], corner_radius=8)
        self._ml_button_frame.pack(fill="x", pady=SPACING['sm'])

        ml_info_frame = ctk.CTkFrame(self._ml_button_frame, fg_color="transparent")
        ml_info_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        ctk.CTkLabel(
            ml_info_frame,
            text="🤖 ML-Powered Risk Analysis",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w")

        ctk.CTkLabel(
            ml_info_frame,
            text="Use machine learning to predict compatibility risks based on feature characteristics,\nspec status, browser bugs, and historical patterns.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
            justify="left",
        ).pack(anchor="w", pady=(SPACING['xs'], SPACING['md']))

        self._run_ml_button = ctk.CTkButton(
            ml_info_frame,
            text="▶  Run ML Analysis",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_bright'],
            height=40,
            width=180,
            command=self._run_ml_analysis,
        )
        self._run_ml_button.pack(anchor="w")

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

            # Collect all detected features for version range display
            all_detected_features = []
            if features:
                all_detected_features.extend(features.get('html', []))
                all_detected_features.extend(features.get('css', []))
                all_detected_features.extend(features.get('js', []))

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
                    supported_features=details.get('supported_features', []),
                    all_features=all_detected_features,
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
                    type_container = ctk.CTkFrame(features_content, fg_color="transparent")
                    type_container.pack(fill="x", pady=(0, SPACING['sm']))

                    type_frame = ctk.CTkFrame(type_container, fg_color="transparent")
                    type_frame.pack(fill="x")

                    badge = ctk.CTkLabel(
                        type_frame,
                        text=f" {type_name} ({len(feature_list)}) ",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS['text_primary'],
                        fg_color=color,
                        corner_radius=4,
                    )
                    badge.pack(side="left")

                    # Get all readable feature names
                    all_readable = [get_feature_name(f) for f in feature_list]

                    # Show first 15 features
                    short_text = ", ".join(all_readable[:15])
                    if len(feature_list) > 15:
                        short_text += f", ... (+{len(feature_list) - 15} more)"

                    # Create label for short text
                    features_label = ctk.CTkLabel(
                        type_frame,
                        text=short_text,
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS['text_secondary'],
                        wraplength=600,
                        justify="left",
                    )
                    features_label.pack(side="left", padx=(SPACING['sm'], 0))

                    # Add toggle button if more than 15 features
                    if len(feature_list) > 15:
                        full_text = ", ".join(all_readable)
                        is_expanded = [False]  # Use list for mutable closure

                        def make_toggle(label, short, full, expanded, btn):
                            def toggle():
                                expanded[0] = not expanded[0]
                                if expanded[0]:
                                    label.configure(text=full)
                                    btn.configure(text="▲ Less")
                                else:
                                    label.configure(text=short)
                                    btn.configure(text="▼ All")
                            return toggle

                        toggle_btn = ctk.CTkButton(
                            type_frame,
                            text="▼ All",
                            font=ctk.CTkFont(size=10),
                            width=50,
                            height=20,
                            fg_color="transparent",
                            hover_color=COLORS['bg_light'],
                            text_color=COLORS['accent'],
                        )
                        toggle_btn.pack(side="right", padx=(SPACING['sm'], 0))
                        toggle_btn.configure(command=make_toggle(features_label, short_text, full_text, is_expanded, toggle_btn))

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

    def _build_history_view(self):
        """Build the history view showing past analyses and statistics."""
        # Scrollable container
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        enable_smooth_scrolling(scroll_frame)

        # Title section with Clear All button
        title_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, SPACING['lg']))

        history_icon = ICONS.get('history', '\u23F3')
        title_label = ctk.CTkLabel(
            title_frame,
            text=f"{history_icon} Analysis History",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title_label.pack(side="left")

        # Clear All button
        clear_icon = ICONS.get('clear', '\u2718')
        clear_btn = ctk.CTkButton(
            title_frame,
            text=f"{clear_icon} Clear All",
            font=ctk.CTkFont(size=12),
            width=100,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['danger_muted'],
            text_color=COLORS['text_muted'],
            command=self._clear_all_history,
        )
        clear_btn.pack(side="right")

        # Statistics panel
        stats = self._analyzer_service.get_statistics()
        if stats.get('total_analyses', 0) > 0:
            stats_panel = StatisticsPanel(scroll_frame)
            stats_panel.pack(fill="x", pady=(0, SPACING['lg']))
            stats_panel.set_statistics(stats)

        # History list header
        list_header = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, SPACING['sm']))

        list_title = ctk.CTkLabel(
            list_header,
            text="Recent Analyses",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_secondary'],
        )
        list_title.pack(side="left")

        # History count
        history_count = self._analyzer_service.get_history_count()
        count_label = ctk.CTkLabel(
            list_header,
            text=f"{history_count} total",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        )
        count_label.pack(side="right")

        # History list container
        self._history_list_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self._history_list_frame.pack(fill="both", expand=True)

        # Load history items
        self._load_history_items()

    def _load_history_items(self):
        """Load and display history items."""
        # Clear existing items
        for widget in self._history_list_frame.winfo_children():
            widget.destroy()

        # Get history from service
        history = self._analyzer_service.get_analysis_history(limit=50)

        if not history:
            # Show empty state
            empty_card = EmptyHistoryCard(self._history_list_frame)
            empty_card.pack(fill="x", pady=SPACING['md'])
            return

        # Create history cards
        for analysis in history:
            card = HistoryCard(
                self._history_list_frame,
                analysis_data=analysis,
                on_click=self._on_history_item_click,
                on_delete=self._on_history_item_delete,
            )
            card.pack(fill="x", pady=(0, SPACING['sm']))

    def _on_history_item_click(self, analysis_id: int):
        """Handle click on a history item.

        Args:
            analysis_id: ID of the clicked analysis
        """
        # Get the full analysis details
        analysis = self._analyzer_service.get_analysis_by_id(analysis_id)
        if not analysis:
            show_warning(self.master, "Not Found", "Analysis record not found.")
            return

        # Show info about the analysis for now
        # In the future, this could restore the full results view
        file_name = analysis.get('file_name', 'Unknown')
        score = analysis.get('overall_score', 0)
        grade = analysis.get('grade', 'N/A')
        date = analysis.get('analyzed_at', 'Unknown')[:16]

        message = f"File: {file_name}\n"
        message += f"Score: {score:.0f}% ({grade})\n"
        message += f"Analyzed: {date}\n"
        message += f"Features: {analysis.get('total_features', 0)}"

        show_info(self.master, "Analysis Details", message)

    def _on_history_item_delete(self, analysis_id: int):
        """Handle delete button click on a history item.

        Args:
            analysis_id: ID of the analysis to delete
        """
        if ask_question(self.master, "Confirm Delete", "Delete this analysis from history?"):
            success = self._analyzer_service.delete_from_history(analysis_id)
            if success:
                self.status_bar.set_status("Analysis deleted from history", "info")
                # Refresh the history view
                self._build_history_view()
            else:
                show_error(self.master, "Error", "Failed to delete analysis.")

    def _clear_all_history(self):
        """Clear all analysis history."""
        count = self._analyzer_service.get_history_count()
        if count == 0:
            show_info(self.master, "History Empty", "There is no history to clear.")
            return

        if ask_question(self.master, "Clear All History", f"Delete all {count} analyses from history?\n\nThis action cannot be undone."):
            success = self._analyzer_service.clear_history()
            if success:
                self.status_bar.set_status("All history cleared", "info")
                # Refresh the history view
                self._build_history_view()
            else:
                show_error(self.master, "Error", "Failed to clear history.")

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

    def _get_ml_risk_assessment(self, features: Dict) -> Optional[Dict]:
        """Get ML-based risk assessment for detected features.

        Args:
            features: Dict with 'html', 'css', 'js' feature lists

        Returns:
            Dict with ML risk assessment data, or None if unavailable
        """
        try:
            # Import ML module (lazy import to avoid startup delay)
            from src.ml.risk_predictor import get_risk_predictor, RiskCategory

            # Collect all feature IDs (limit to first 50 for performance)
            all_features = []
            for key in ['html', 'css', 'js']:
                all_features.extend(features.get(key, []))

            if not all_features:
                return None

            # Limit features to prevent slow analysis
            all_features = all_features[:50]

            predictor = get_risk_predictor()

            # Quick aggregate prediction instead of individual predictions
            high_risk_count = 0
            medium_risk_count = 0
            low_risk_count = 0
            sample_factors = []

            # Only predict for a sample of features (faster)
            sample_size = min(10, len(all_features))
            sample_features = all_features[:sample_size]

            for fid in sample_features:
                try:
                    pred = predictor.predict(fid)
                    if pred.risk_level == RiskCategory.HIGH:
                        high_risk_count += 1
                    elif pred.risk_level == RiskCategory.MEDIUM:
                        medium_risk_count += 1
                    else:
                        low_risk_count += 1

                    if len(sample_factors) < 5:
                        sample_factors.extend(pred.contributing_factors[:1])
                except Exception:
                    continue  # Skip features that fail

            # Determine overall risk level from sample
            total = high_risk_count + medium_risk_count + low_risk_count
            if total == 0:
                return None

            if high_risk_count > total * 0.3:
                overall_risk = 'high'
            elif high_risk_count > 0 or medium_risk_count > total * 0.3:
                overall_risk = 'medium'
            else:
                overall_risk = 'low'

            # Deduplicate factors
            unique_factors = list(dict.fromkeys(sample_factors))[:5]

            # Get feature importance (fast - just reads from model)
            feature_importance = predictor.get_feature_importance()
            if feature_importance:
                sorted_importance = sorted(
                    feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            else:
                sorted_importance = None

            # Extrapolate counts to full feature set
            scale = len(all_features) / sample_size if sample_size > 0 else 1
            return {
                'risk_level': overall_risk,
                'confidence': 0.7 if predictor.is_model_loaded() else 0.5,
                'factors': unique_factors if unique_factors else ["Analysis based on feature characteristics"],
                'high_risk_count': int(high_risk_count * scale),
                'medium_risk_count': int(medium_risk_count * scale),
                'low_risk_count': int(low_risk_count * scale),
                'feature_importance': sorted_importance,
                'model_loaded': predictor.is_model_loaded(),
            }

        except ImportError:
            # ML module not available
            return None
        except Exception as e:
            # Log error but don't crash
            import traceback
            traceback.print_exc()
            return None

    def _run_ml_analysis(self):
        """Run ML analysis when user clicks the button."""
        # Disable button and show loading state
        self._run_ml_button.configure(state="disabled", text="Analyzing...")

        # Schedule the actual analysis (allows UI to update)
        self.after(100, self._perform_ml_analysis)

    def _perform_ml_analysis(self):
        """Perform the actual ML analysis."""
        try:
            # Collect all feature IDs
            from src.ml.risk_predictor import get_all_models_aggregate, get_risk_predictor

            all_features = []
            for key in ['html', 'css', 'js']:
                all_features.extend(self._ml_features.get(key, []))

            if not all_features:
                self._ml_button_frame.destroy()
                self._show_ml_error("No features to analyze")
                return

            # === SINGLE SOURCE OF TRUTH ===
            # Get all models data (full analysis) - this is the ONLY data source
            all_models_data = get_all_models_aggregate(all_features, full_analysis=True)

            if not all_models_data or not all_models_data.get('models'):
                self._ml_button_frame.destroy()
                self._show_ml_error("ML models not available. Make sure models are trained.")
                return

            # Extract Gradient Boosting data for main card (it's the best model)
            gb_data = all_models_data['models'].get('gradient_boosting', {})

            if not gb_data:
                # Fallback to any available model
                gb_data = list(all_models_data['models'].values())[0] if all_models_data['models'] else {}

            # Calculate flagged count from actual data
            flagged_count = gb_data.get('high_count', 0) + gb_data.get('medium_count', 0)

            # Get feature importance from the predictor
            predictor = get_risk_predictor()
            feature_importance = predictor.get_feature_importance()
            sorted_importance = None
            if feature_importance:
                sorted_importance = sorted(
                    feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]

            # Generate contributing factors from flagged features
            factors = []
            flagged_features = gb_data.get('predictions', [])
            high_risk_features = [p for p in flagged_features if p.get('risk') == 'high']
            if high_risk_features:
                factors.append(f"{len(high_risk_features)} features with HIGH risk detected")
            medium_risk_features = [p for p in flagged_features if p.get('risk') == 'medium']
            if medium_risk_features:
                factors.append(f"{len(medium_risk_features)} features with MEDIUM risk detected")
            if not factors:
                factors.append("All features have LOW risk")

            # Clear the button frame
            self._ml_button_frame.destroy()

            # Show ML Risk Card (Best Model - Gradient Boosting)
            ml_risk_card = MLRiskCard(self._ml_content_frame, title="Compatibility Risk Prediction")
            ml_risk_card.pack(fill="x", pady=(0, SPACING['sm']))

            # Use actual model confidence, not hardcoded value
            model_confidence = gb_data.get('avg_confidence', 0.5)
            model_accuracy = gb_data.get('accuracy', 0.93)  # Gradient Boosting accuracy

            ml_risk_card.set_risk_data(
                risk_level=gb_data.get('overall_risk', 'low'),
                confidence=model_confidence,
                factors=factors,
                high_risk_count=flagged_count,
                total_features=self._ml_total_features,
                model_accuracy=model_accuracy,  # Pass model accuracy for display
            )

            # Show Feature Importance Card (if available)
            if sorted_importance:
                importance_card = MLFeatureImportanceCard(self._ml_content_frame)
                importance_card.pack(fill="x", pady=(0, SPACING['sm']))
                importance_card.set_importances(sorted_importance)

            # Advanced Details Section (All 3 Models)
            self._create_advanced_section(all_models_data)

        except Exception as e:
            # Show error
            import traceback
            traceback.print_exc()

            try:
                self._ml_button_frame.destroy()
            except:
                pass

            error_frame = ctk.CTkFrame(self._ml_content_frame, fg_color=COLORS['bg_medium'], corner_radius=8)
            error_frame.pack(fill="x", pady=SPACING['sm'])

            self._show_ml_error(f"Error running ML analysis: {str(e)}")

    def _show_ml_error(self, message: str):
        """Show an error message in the ML section."""
        error_frame = ctk.CTkFrame(self._ml_content_frame, fg_color=COLORS['bg_medium'], corner_radius=8)
        error_frame.pack(fill="x", pady=SPACING['sm'])

        ctk.CTkLabel(
            error_frame,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['warning'],
        ).pack(padx=SPACING['lg'], pady=SPACING['lg'])

    def _create_advanced_section(self, all_models_data: dict):
        """Create the Advanced Details section showing all 3 models."""
        # Advanced section container
        advanced_frame = ctk.CTkFrame(
            self._ml_content_frame,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
        )
        advanced_frame.pack(fill="x", pady=(SPACING['sm'], 0))

        # Header with toggle button
        header_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['sm'])

        self._advanced_expanded = False
        self._advanced_toggle_btn = ctk.CTkButton(
            header_frame,
            text="▶  View All Models",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=COLORS['bg_light'],
            text_color=COLORS['text_secondary'],
            anchor="w",
            command=lambda: self._toggle_advanced_section(all_models_data),
        )
        self._advanced_toggle_btn.pack(side="left", fill="x", expand=True)

        # Content frame (initially hidden)
        self._advanced_content = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        # Don't pack yet - will be shown when expanded

        # Populate content
        self._populate_advanced_content(all_models_data)

    def _toggle_advanced_section(self, all_models_data: dict):
        """Toggle the advanced section visibility."""
        self._advanced_expanded = not self._advanced_expanded

        if self._advanced_expanded:
            self._advanced_toggle_btn.configure(text="▼  View All Models")
            self._advanced_content.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        else:
            self._advanced_toggle_btn.configure(text="▶  View All Models")
            self._advanced_content.pack_forget()

    def _populate_advanced_content(self, all_models_data: dict):
        """Populate the advanced content with all models comparison."""
        models = all_models_data.get('models', {})

        # Risk colors
        risk_colors = {
            'low': COLORS['success'],
            'medium': COLORS['warning'],
            'high': COLORS['danger'],
        }

        # Model order
        model_order = ['gradient_boosting', 'random_forest', 'logistic_regression']

        for model_name in model_order:
            if model_name not in models:
                continue

            model_data = models[model_name]

            # Model container
            model_frame = ctk.CTkFrame(self._advanced_content, fg_color=COLORS['bg_light'], corner_radius=6)
            model_frame.pack(fill="x", pady=(0, SPACING['sm']))

            # Model header row
            header_row = ctk.CTkFrame(model_frame, fg_color="transparent")
            header_row.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])

            # Model name
            name_text = model_data.get('display_name', model_name)
            name_label = ctk.CTkLabel(
                header_row,
                text=name_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_primary'],
                width=160,
                anchor="w",
            )
            name_label.pack(side="left")

            # Risk level badge
            risk = model_data.get('overall_risk', 'unknown')
            risk_color = risk_colors.get(risk, COLORS['text_muted'])

            risk_label = ctk.CTkLabel(
                header_row,
                text=f" {risk.upper()} RISK ",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=risk_color,
                fg_color=COLORS['bg_medium'],
                corner_radius=4,
            )
            risk_label.pack(side="left", padx=(SPACING['sm'], 0))

            # Flagged count
            high_count = model_data.get('high_count', 0)
            medium_count = model_data.get('medium_count', 0)
            flagged = high_count + medium_count
            total = self._ml_total_features

            flagged_label = ctk.CTkLabel(
                header_row,
                text=f"{flagged}/{total} flagged",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted'],
            )
            flagged_label.pack(side="right")

            # Flagged features details (get from predictions)
            predictions = model_data.get('predictions', [])
            flagged_predictions = [p for p in predictions if p.get('risk') in ['high', 'medium']]

            if flagged_predictions:
                # Divider line
                divider = ctk.CTkFrame(model_frame, fg_color=COLORS['border'], height=1)
                divider.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['xs']))

                # Flagged features header with toggle
                header_frame = ctk.CTkFrame(model_frame, fg_color="transparent")
                header_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['xs']))

                flagged_header = ctk.CTkLabel(
                    header_frame,
                    text="Flagged Features:",
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS['text_muted'],
                )
                flagged_header.pack(side="left")

                # Container for features list
                features_container = ctk.CTkFrame(model_frame, fg_color="transparent")
                features_container.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

                # Initially visible features (first 5)
                initial_frame = ctk.CTkFrame(features_container, fg_color="transparent")
                initial_frame.pack(fill="x")

                # Hidden features (rest)
                hidden_frame = ctk.CTkFrame(features_container, fg_color="transparent")
                # Don't pack yet - will show on toggle

                # Create feature rows
                for idx, pred in enumerate(flagged_predictions):
                    feature_id = pred.get('feature', 'unknown')
                    feature_risk = pred.get('risk', 'unknown')
                    feature_reason = pred.get('reason', 'Risk detected by ML model')
                    feature_color = risk_colors.get(feature_risk, COLORS['text_muted'])

                    # Decide which frame to add to
                    parent_frame = initial_frame if idx < 5 else hidden_frame

                    # Feature row container
                    feature_row = ctk.CTkFrame(parent_frame, fg_color=COLORS['bg_medium'], corner_radius=4)
                    feature_row.pack(fill="x", pady=(0, 4))

                    feature_inner = ctk.CTkFrame(feature_row, fg_color="transparent")
                    feature_inner.pack(fill="x", padx=SPACING['sm'], pady=SPACING['xs'])

                    # Left side: bullet + feature name
                    left_frame = ctk.CTkFrame(feature_inner, fg_color="transparent")
                    left_frame.pack(side="left", fill="x", expand=True)

                    # Bullet point
                    bullet = ctk.CTkLabel(
                        left_frame,
                        text="•",
                        font=ctk.CTkFont(size=11),
                        text_color=feature_color,
                        width=15,
                    )
                    bullet.pack(side="left")

                    # Feature name
                    feature_name_label = ctk.CTkLabel(
                        left_frame,
                        text=feature_id,
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS['text_primary'],
                        anchor="w",
                    )
                    feature_name_label.pack(side="left")

                    # Risk badge
                    risk_badge = ctk.CTkLabel(
                        feature_inner,
                        text=f" {feature_risk.upper()} ",
                        font=ctk.CTkFont(size=9, weight="bold"),
                        text_color=feature_color,
                    )
                    risk_badge.pack(side="right")

                    # Reason row (below feature name)
                    reason_label = ctk.CTkLabel(
                        feature_row,
                        text=f"    {feature_reason}",
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS['text_muted'],
                        anchor="w",
                    )
                    reason_label.pack(fill="x", padx=SPACING['sm'], pady=(0, SPACING['xs']))

                # Toggle button if more than 5 features
                if len(flagged_predictions) > 5:
                    toggle_frame = ctk.CTkFrame(features_container, fg_color="transparent")
                    toggle_frame.pack(fill="x", pady=(SPACING['xs'], 0))

                    # Store state for this model's toggle
                    is_expanded = [False]  # Use list to allow mutation in closure

                    def make_toggle_callback(hf, tf, exp, count):
                        def toggle():
                            exp[0] = not exp[0]
                            if exp[0]:
                                hf.pack(fill="x")
                                tf.configure(text=f"▲ Show less")
                            else:
                                hf.pack_forget()
                                tf.configure(text=f"▼ Show all {count} flagged features")
                        return toggle

                    toggle_btn = ctk.CTkButton(
                        toggle_frame,
                        text=f"▼ Show all {len(flagged_predictions)} flagged features",
                        font=ctk.CTkFont(size=10),
                        fg_color="transparent",
                        hover_color=COLORS['bg_light'],
                        text_color=COLORS['accent'],
                        height=24,
                        anchor="w",
                        command=make_toggle_callback(hidden_frame, None, is_expanded, len(flagged_predictions)),
                    )
                    toggle_btn.pack(side="left")

                    # Update the callback to reference the button
                    toggle_btn.configure(
                        command=make_toggle_callback(hidden_frame, toggle_btn, is_expanded, len(flagged_predictions))
                    )

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

    def _on_browser_selection_change(self, selected_browsers: Dict[str, str]):
        """Handle browser selection changes.

        Args:
            selected_browsers: Dict mapping browser_id to latest_version
        """
        self._selected_browsers = selected_browsers
        browser_count = len(selected_browsers)
        if browser_count > 0:
            self.status_bar.set_status(f"{browser_count} browser(s) selected for analysis", "info")

    def _analyze_files(self):
        """Analyze selected files."""
        if not hasattr(self, 'file_table'):
            return

        files = self.file_table.get_files()
        if not files:
            show_warning(self.master, "No Files", "Please select at least one file.")
            return

        # Check if browsers are selected
        if not self._selected_browsers:
            show_warning(self.master, "No Browsers", "Please select at least one target browser.")
            return

        browser_count = len(self._selected_browsers)
        if ask_question(self.master, "Confirm", f"Analyze {len(files)} file(s) against {browser_count} browser(s)?"):
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

            # Use selected browsers or fall back to service defaults
            target_browsers = self._selected_browsers if self._selected_browsers else None

            result = self._analyzer_service.analyze_files(
                html_files=html_files if html_files else None,
                css_files=css_files if css_files else None,
                js_files=js_files if js_files else None,
                target_browsers=target_browsers,
            )

            progress.set_progress(100)
            progress.close()

            if result.success:
                self.current_report = result.to_dict()
                self.status_bar.set_last_analysis()
                self.status_bar.set_status("Analysis complete", "success")

                # Auto-save to history
                self._save_to_history(result, files)

                # Navigate to results
                self.sidebar.set_active_view("results")
                self._show_view("results")
            else:
                show_error(self.master, "Analysis Failed", f"{result.error or 'Unknown error'}")

        except Exception as e:
            show_error(self.master, "Error", str(e))
            import traceback
            traceback.print_exc()

    def _save_to_history(self, result, files: List[str]):
        """Save analysis result to history database.

        Args:
            result: AnalysisResult from analysis
            files: List of analyzed file paths
        """
        try:
            # Determine primary file info
            if len(files) == 1:
                file_path = files[0]
                file_name = Path(file_path).name
                file_type = Path(file_path).suffix.lower().lstrip('.')
                if file_type == 'htm':
                    file_type = 'html'
            else:
                # Multiple files - use "mixed" type
                file_names = [Path(f).name for f in files]
                file_name = f"{file_names[0]} (+{len(files)-1} more)" if len(files) > 1 else file_names[0]
                file_path = str(Path(files[0]).parent)
                file_type = 'mixed'

            # Save to database
            self._analyzer_service.save_analysis_to_history(
                result=result,
                file_name=file_name,
                file_path=file_path,
                file_type=file_type,
            )
        except Exception as e:
            # Don't fail the analysis if history save fails
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
