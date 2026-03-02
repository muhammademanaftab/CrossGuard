"""Main window -- sidebar nav, file table, results, history, and settings."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import customtkinter as ctk

from src.api import get_analyzer_service, AnalysisResult
from src.api.project_schemas import ScanConfig

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
    BuildBadge,
    CollapsibleSection,
    IssuesSummary,
    QuickStatsBar,
    MLRiskCard,
    MLFeatureImportanceCard,
    BrowserSelector,
    get_available_browsers,
    HistoryCard,
    EmptyHistoryCard,
    StatisticsPanel,
    CompactStatsBar,
    BookmarkButton,
    TagManagerDialog,
    ProjectTreeWidget,
    ScanConfigPanel,
    ProjectStatsCard,
    FrameworkHintCard,
    FrameworkHint,
    PolyfillCard,
    PolyfillEmptyCard,
)
from .widgets.rules_manager import show_rules_manager

from .export_manager import ExportManager


class MainWindow(ctk.CTkFrame):
    """VS Code-style layout: sidebar + swappable content views."""

    def __init__(self, master):
        super().__init__(master, fg_color=COLORS['bg_darkest'])

        self.master = master
        self.current_report = None
        self.export_manager = ExportManager(master)
        self._analyzer_service = get_analyzer_service()
        self._current_view = "files"
        self._last_files: List[str] = []
        self._selected_browsers: Dict[str, str] = None  # None = use widget defaults
        self._init_layout()
        self._show_view("files")

    def _init_layout(self):
        """Set up the grid: sidebar (col 0), header/content/statusbar (col 1)."""
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.sidebar = Sidebar(
            self,
            on_navigate=self._on_navigate,
        )
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")

        self.header = HeaderBar(
            self,
            title="Browser Compatibility Checker",
        )
        self.header.grid(row=0, column=1, sticky="ew")

        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_dark'],
            corner_radius=0,
        )
        self.content_frame.grid(row=1, column=1, sticky="nsew")

        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=1, sticky="ew")

        self._views = {}

    def _on_navigate(self, view_id: str):
        if view_id == "help":
            self._show_help()
            return
        self._show_view(view_id)

    def _show_view(self, view_id: str):
        """Destroy current view and build the requested one."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self._current_view = view_id

        if view_id == "files":
            self._build_files_view()
        elif view_id == "project":
            self._build_project_view()
        elif view_id == "results":
            self._build_results_view()
        elif view_id == "history":
            self._build_history_view()
        elif view_id == "settings":
            self._build_settings_view()

        titles = {
            "files": "File Selection",
            "project": "Project Scanner",
            "results": "Analysis Results",
            "history": "Analysis History",
            "settings": "Settings",
        }
        self.header.set_title(titles.get(view_id, "Cross Guard"))

    def _build_files_view(self):
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        enable_smooth_scrolling(scroll_frame)

        title_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, SPACING['lg']))

        ctk.CTkLabel(
            title_frame,
            text="Select Files to Analyze",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="Drag and drop files or use the file browser",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_muted'],
        ).pack(side="left", padx=(SPACING['lg'], 0))

        self.drop_zone = DropZone(
            scroll_frame,
            allowed_extensions=['html', 'htm', 'css', 'js', 'jsx', 'ts', 'tsx', 'mjs'],
            on_files_dropped=self._on_files_dropped,
            height=160,
        )
        self.drop_zone.pack(fill="x", pady=(0, SPACING['xl']))

        table_header = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        table_header.pack(fill="x", pady=(0, SPACING['sm']))

        ctk.CTkLabel(
            table_header,
            text="Selected Files",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

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

        self.file_table = FileTable(
            scroll_frame,
            on_files_changed=self._update_status,
        )
        self.file_table.pack(fill="both", expand=True, pady=(0, SPACING['xl']))

        # Restore files from before view switch
        if self._last_files:
            existing_files = [f for f in self._last_files if Path(f).exists()]
            if existing_files:
                self.file_table.add_files(existing_files)

        browser_header = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        browser_header.pack(fill="x", pady=(SPACING['lg'], SPACING['sm']))

        ctk.CTkLabel(
            browser_header,
            text="Target Browsers",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        ctk.CTkLabel(
            browser_header,
            text="Select which browsers to check compatibility for",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        ).pack(side="left", padx=(SPACING['md'], 0))

        self.browser_selector = BrowserSelector(
            scroll_frame,
            on_selection_change=self._on_browser_selection_change,
        )
        self.browser_selector.pack(fill="x", pady=(0, SPACING['xl']))
        self._selected_browsers = self.browser_selector.get_selected_browsers()

        actions_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        actions_frame.pack(fill="x")

        ctk.CTkButton(
            actions_frame,
            text=f"{ICONS['check']} Analyze Compatibility",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=220,
            height=48,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dim'],
            command=self._analyze_files,
        ).pack(side="right")

        self._update_status()

    def _build_project_view(self):
        """Scan an entire project directory for compatibility."""
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        enable_smooth_scrolling(scroll_frame)

        title_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, SPACING['lg']))

        ctk.CTkLabel(
            title_frame,
            text="Scan Project Directory",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="Analyze all HTML, CSS, and JavaScript files in a project",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_muted'],
        ).pack(side="left", padx=(SPACING['lg'], 0))

        path_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
        )
        path_frame.pack(fill="x", pady=(0, SPACING['md']))

        path_inner = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_inner.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        ctk.CTkLabel(
            path_inner,
            text="Project Path:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        self._project_path_var = ctk.StringVar()
        self._project_path_entry = ctk.CTkEntry(
            path_inner,
            textvariable=self._project_path_var,
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            placeholder_text="Select a project directory...",
        )
        self._project_path_entry.pack(side="left", fill="x", expand=True, padx=(SPACING['md'], SPACING['sm']))

        folder_icon = ICONS.get('folder', '\U0001F4C1')
        browse_btn = ctk.CTkButton(
            path_inner,
            text=f"{folder_icon} Browse",
            width=100,
            height=36,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dim'],
            command=self._browse_project_directory,
        )
        browse_btn.pack(side="right")

        self._scan_config_panel = ScanConfigPanel(
            scroll_frame,
            on_config_change=self._on_scan_config_change,
        )
        self._scan_config_panel.pack(fill="x", pady=(0, SPACING['md']))

        # Hidden until a scan runs
        self._project_stats_card = ProjectStatsCard(scroll_frame)
        self._project_stats_card.pack(fill="x", pady=(0, SPACING['md']))
        self._project_stats_card.pack_forget()

        self._framework_hint_card = FrameworkHintCard(
            scroll_frame,
            on_include_build=self._on_include_build_folder,
            on_dismiss=self._on_dismiss_hint,
        )
        self._framework_hint_card.pack(fill="x", pady=(0, SPACING['md']))
        self._framework_hint_card.pack_forget()

        self._project_tree = ProjectTreeWidget(
            scroll_frame,
            on_selection_change=self._on_project_selection_change,
            max_height=350,
        )
        self._project_tree.pack(fill="x", pady=(0, SPACING['md']))
        self._project_tree.pack_forget()

        self._project_actions_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self._project_actions_frame.pack(fill="x", pady=(SPACING['md'], 0))

        search_icon = ICONS.get('search', '\U0001F50D')
        self._preview_btn = ctk.CTkButton(
            self._project_actions_frame,
            text=f"{search_icon} Preview Files",
            width=150,
            height=40,
            fg_color=COLORS['bg_medium'],
            hover_color=COLORS['hover_bg'],
            border_width=1,
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            command=self._preview_project,
        )
        self._preview_btn.pack(side="left")

        self._scan_project_btn = ctk.CTkButton(
            self._project_actions_frame,
            text=f"{ICONS['check']} Scan Project",
            width=180,
            height=40,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dim'],
            command=self._scan_project,
            state="disabled",
        )
        self._scan_project_btn.pack(side="right")

        self._project_status_label = ctk.CTkLabel(
            self._project_actions_frame,
            text="Select a project directory to begin",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        self._project_status_label.pack(side="right", padx=(0, SPACING['lg']))
        self._project_scroll_frame = scroll_frame

    def _browse_project_directory(self):
        from tkinter import filedialog

        directory = filedialog.askdirectory(
            title="Select Project Directory",
            mustexist=True,
        )

        if directory:
            self._project_path_var.set(directory)
            self._project_status_label.configure(
                text="Click 'Preview Files' to scan the directory",
                text_color=COLORS['text_secondary'],
            )

    def _on_scan_config_change(self, config: ScanConfig):
        pass  # Could trigger re-scan if preview is already shown

    def _on_project_selection_change(self, count: int):
        if count > 0:
            self._scan_project_btn.configure(state="normal")
            self._project_status_label.configure(
                text=f"{count} file{'s' if count != 1 else ''} selected",
                text_color=COLORS['text_secondary'],
            )
        else:
            self._scan_project_btn.configure(state="disabled")
            self._project_status_label.configure(
                text="No files selected",
                text_color=COLORS['text_muted'],
            )

    def _on_include_build_folder(self, folder_name: str):
        """Uncheck the exclusion for this folder and re-scan."""
        self._scan_config_panel.set_exclude(folder_name, False)
        self._preview_project()

    def _on_dismiss_hint(self):
        self._framework_hint_card.pack_forget()

    def _preview_project(self):
        """Scan the directory and show the file tree (no analysis yet)."""
        path = self._project_path_var.get()
        if not path:
            show_warning(self, "No Directory", "Please select a project directory first.")
            return

        import os
        if not os.path.isdir(path):
            show_error(self, "Invalid Directory", f"The path does not exist or is not a directory:\n{path}")
            return

        config = self._scan_config_panel.get_config()

        progress = ProgressDialog(
            self,
            title="Scanning Project",
            message="Scanning directory...",
        )
        progress.show()
        self.update_idletasks()

        try:
            progress.set_message("Finding files...")
            result = self._analyzer_service.scan_project_directory(path, config)

            progress.set_message("Detecting framework...")
            project_info = self._analyzer_service.detect_project_framework(path)

            progress.close()

            self._project_stats_card.update_stats(
                framework_name=project_info.framework.name if project_info.framework else None,
                framework_version=project_info.framework.version if project_info.framework else None,
                framework_color=project_info.framework.color if project_info.framework else None,
                build_tool=project_info.build_tool.name if project_info.build_tool else None,
                html_count=result.html_count,
                css_count=result.css_count,
                js_count=result.js_count,
                minified_count=result.minified_files,
                has_typescript=project_info.has_typescript,
            )
            self._project_stats_card.pack(fill="x", pady=(0, SPACING['md']))
            hint_data = detector.get_scanning_hint(project_info, path)
            build_folders = detector.check_build_folders(path)

            if hint_data and hint_data.get('hint_type') != 'ready':
                hint = FrameworkHint(
                    hint_type=hint_data['hint_type'],
                    title=hint_data['title'],
                    message=hint_data['message'],
                    build_command=hint_data.get('build_command'),
                    build_folder=hint_data.get('build_folder'),
                    icon=hint_data.get('icon', 'info'),
                )

                build_exists = build_folders.get(hint.build_folder, False) if hint.build_folder else False

                self._framework_hint_card.update_hint(hint, build_exists)
                self._framework_hint_card.pack(fill="x", pady=(0, SPACING['md']))
            else:
                self._framework_hint_card.pack_forget()

            self._project_tree.set_tree(result.file_tree)
            self._project_tree.pack(fill="x", pady=(0, SPACING['md']))

            total = result.total_files
            if total > 0:
                self._scan_project_btn.configure(state="normal")
                self._project_status_label.configure(
                    text=f"Found {total} file{'s' if total != 1 else ''}",
                    text_color=COLORS['success'],
                )
            else:
                self._scan_project_btn.configure(state="disabled")
                self._project_status_label.configure(
                    text="No analyzable files found",
                    text_color=COLORS['warning'],
                )

            self._last_scan_result = result

        except Exception as e:
            progress.close()
            show_error(self, "Scan Error", f"Failed to scan directory:\n{str(e)}")

    def _scan_project(self):
        """Run compatibility analysis on all selected project files."""
        if not hasattr(self, '_last_scan_result') or not self._last_scan_result:
            show_warning(self, "No Files", "Please preview the project first.")
            return

        selected_files = self._project_tree.get_selected_files()
        total_files = sum(len(files) for files in selected_files.values())

        if total_files == 0:
            show_warning(self, "No Files Selected", "Please select at least one file to analyze.")
            return

        progress = ProgressDialog(self, title="Analyzing Project", message=f"Analyzing {total_files} files...")
        progress.show()
        self.update_idletasks()

        try:
            def update_progress(current, total, filename):
                progress.set_progress(current, total)
                progress.set_message(f"Analyzing: {filename}")
                self.update_idletasks()

            from src.api.schemas import AnalysisRequest

            request = AnalysisRequest(
                html_files=selected_files.get('html', []),
                css_files=selected_files.get('css', []),
                js_files=selected_files.get('javascript', []),
                target_browsers=self._selected_browsers or self._analyzer_service.DEFAULT_BROWSERS,
            )

            progress.set_message(f"Analyzing {total_files} files...")
            combined_result = self._analyzer_service.analyze(request)

            if combined_result.success:
                self.current_report = combined_result.to_dict()
                self._last_files = (
                    selected_files.get('html', []) +
                    selected_files.get('css', []) +
                    selected_files.get('javascript', [])
                )

                progress.close()

                self.sidebar.set_active_view("results")
                self._show_view("results")

                score = combined_result.scores.simple_score if combined_result.scores else 0
                grade = combined_result.scores.grade if combined_result.scores else 'N/A'
                self.status_bar.set_status(
                    f"Project analysis complete: {grade} ({score:.1f}%)",
                    "success"
                )
                return  # Exit early since we closed progress
            else:
                show_error(self, "Analysis Error", combined_result.error or "Unknown error occurred")

        except Exception as e:
            show_error(self, "Analysis Error", f"Failed to analyze project:\n{str(e)}")
        finally:
            progress.close()

    def _build_results_view(self):
        """Results with progressive disclosure: badge hero, stats, issues, then collapsible details."""
        if not self.current_report:
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

        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        enable_smooth_scrolling(scroll_frame)

        scores = report.get('scores', {})
        summary = report.get('summary', {})
        browsers = report.get('browsers', {})
        features = report.get('features', {})

        weighted_score = scores.get('weighted_score', 0)
        grade = scores.get('grade', 'N/A')
        total_features = summary.get('total_features', 0)
        browsers_count = len(browsers)

        issues_count = self._count_issues(browsers)

        # Build badge hero (always visible)
        build_badge = BuildBadge(scroll_frame)
        build_badge.pack(fill="x", pady=(0, SPACING['lg']))
        build_badge.set_data(
            score=weighted_score,
            total_features=total_features,
            issues_count=issues_count,
            browsers_count=browsers_count,
            animate=True
        )

        quick_stats = QuickStatsBar(scroll_frame)
        quick_stats.pack(fill="x", pady=(0, SPACING['lg']))
        quick_stats.set_data(
            score=weighted_score,
            grade=grade,
            browsers_count=browsers_count,
            features_count=total_features
        )

        # ML risk assessment (only if ML module is available)
        if self._analyzer_service.is_ml_enabled():
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

            # Replaced with actual results when user clicks "Run ML Analysis"
            self._ml_content_frame = ctk.CTkFrame(ml_content, fg_color="transparent")
            self._ml_content_frame.pack(fill="x")

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

        # Issues summary (if any)
        issues = self._extract_issues(browsers)
        if issues:
            issues_summary = IssuesSummary(scroll_frame, issues=issues)
            issues_summary.pack(fill="x", pady=(0, SPACING['lg']))

        # Polyfill recommendations
        polyfill_data = self._get_polyfill_recommendations(browsers)
        if polyfill_data['has_recommendations']:
            polyfill_section = CollapsibleSection(
                scroll_frame,
                title="Polyfill Recommendations",
                badge_text=str(polyfill_data['count']),
                badge_color=COLORS['info'],
                expanded=True,
            )
            polyfill_section.pack(fill="x", pady=(0, SPACING['lg']))

            polyfill_content = polyfill_section.get_content_frame()
            polyfill_card = PolyfillCard(
                polyfill_content,
                install_command=polyfill_data['install_command'],
                import_statements=polyfill_data['imports'],
                npm_recommendations=polyfill_data['npm'],
                css_fallbacks=polyfill_data['css'],
                total_size_kb=polyfill_data['total_size_kb'],
                on_generate_file=self._generate_polyfills_file,
            )
            polyfill_card.pack(fill="x")

        # Browser support (collapsed)
        if browsers:
            browser_section = CollapsibleSection(
                scroll_frame,
                title="Browser Support",
                badge_text=f"{browsers_count} browsers",
                badge_color=COLORS['accent'],
                expanded=False,
            )
            browser_section.pack(fill="x", pady=(0, SPACING['lg']))

            browser_content = browser_section.get_content_frame()
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

        # Detected features
        feature_details = report.get('feature_details', {})
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

            search_frame = ctk.CTkFrame(features_content, fg_color="transparent")
            search_frame.pack(fill="x", pady=(0, SPACING['md']))

            search_icon = ctk.CTkLabel(
                search_frame,
                text="🔍",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_muted'],
            )
            search_icon.pack(side="left", padx=(0, SPACING['xs']))

            search_var = ctk.StringVar()
            search_entry = ctk.CTkEntry(
                search_frame,
                placeholder_text="Search features...",
                textvariable=search_var,
                width=250,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['bg_medium'],
                border_color=COLORS['border'],
                text_color=COLORS['text_primary'],
            )
            search_entry.pack(side="left", fill="x", expand=True)

            all_feature_frames = []  # (frame, searchable_text) tuples for filtering
            html_details_map = {}
            for detail in feature_details.get('html', []):
                fid = detail.get('feature')
                if fid:
                    html_details_map[fid] = detail

            css_details_map = {}
            for detail in feature_details.get('css', []):
                fid = detail.get('feature')
                if fid:
                    css_details_map[fid] = detail

            js_details_map = {}
            for detail in feature_details.get('js', []):
                fid = detail.get('feature')
                if fid:
                    js_details_map[fid] = detail

            feature_types = [
                ("HTML", features.get('html', []), COLORS['html_color'], html_details_map),
                ("CSS", features.get('css', []), COLORS['css_color'], css_details_map),
                ("JavaScript", features.get('js', []), COLORS['js_color'], js_details_map),
            ]

            for type_name, feature_list, color, details_map in feature_types:
                if feature_list:
                    type_container = ctk.CTkFrame(features_content, fg_color="transparent")
                    type_container.pack(fill="x", pady=(0, SPACING['md']))

                    # Header row with badge and toggle button
                    header_row = ctk.CTkFrame(type_container, fg_color="transparent")
                    header_row.pack(fill="x")

                    badge = ctk.CTkLabel(
                        header_row,
                        text=f" {type_name} ({len(feature_list)}) ",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS['text_primary'],
                        fg_color=color,
                        corner_radius=4,
                    )
                    badge.pack(side="left")

                    def create_feature_label(parent, feature_id, details_map, frame_list):
                        detail = details_map.get(feature_id, {})
                        matched_items = (
                            detail.get('matched_properties', []) or
                            detail.get('matched_apis', []) or
                            detail.get('matched_items', [])
                        )
                        description = detail.get('description', self._analyzer_service.get_feature_display_name(feature_id))

                        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
                        item_frame.pack(fill="x", pady=(2, 0), padx=(SPACING['md'], 0))

                        if matched_items:
                            items_text = ", ".join(matched_items)
                            display_text = f"{items_text}  →  {description} ({feature_id})"
                        else:
                            display_text = f"{description} ({feature_id})"

                        ctk.CTkLabel(
                            item_frame,
                            text=display_text,
                            font=ctk.CTkFont(size=11),
                            text_color=COLORS['text_secondary'],
                            wraplength=650,
                            justify="left",
                        ).pack(anchor="w")

                        frame_list.append((item_frame, display_text.lower()))

                    for feature_id in feature_list:
                        create_feature_label(type_container, feature_id, details_map, all_feature_frames)

            def filter_features(*args):
                query = search_var.get().lower().strip()
                for frame, text in all_feature_frames:
                    if query == "" or query in text:
                        frame.pack(fill="x", pady=(2, 0), padx=(SPACING['md'], 0))
                    else:
                        frame.pack_forget()

            search_var.trace_add("write", filter_features)

        # Visualizations
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

            radar_chart = BrowserRadarChart(charts_frame)
            radar_chart.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING['sm']))
            radar_chart.set_data(chart_data)

            feature_chart = FeatureDistributionChart(charts_frame)
            feature_chart.grid(row=0, column=1, sticky="nsew", padx=(SPACING['sm'], 0))
            feature_chart.set_data(
                summary.get('html_features', 0),
                summary.get('css_features', 0),
                summary.get('js_features', 0),
                summary.get('total_features', None)
            )

            breakdown_chart = CompatibilityBarChart(viz_content)
            breakdown_chart.pack(fill="x", pady=(SPACING['sm'], 0))
            breakdown_chart.set_data(chart_data)

        # Unrecognized patterns
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

                    patterns_container = ctk.CTkFrame(type_frame, fg_color="transparent")
                    patterns_container.pack(side="left", fill="x", expand=True, padx=(SPACING['sm'], 0))

                    short_text = ", ".join(pattern_list[:10])
                    full_text = ", ".join(pattern_list)
                    is_truncated = len(pattern_list) > 10

                    if is_truncated:
                        short_text += f", ... (+{len(pattern_list) - 10} more)"

                    patterns_label = ctk.CTkLabel(
                        patterns_container,
                        text=short_text,
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS['text_muted'],
                        wraplength=600,
                        justify="left",
                    )
                    patterns_label.pack(side="left")

                    if is_truncated:
                        is_expanded = [False]  # mutable closure trick

                        def toggle_expand(lbl=patterns_label, short=short_text, full=full_text, expanded=is_expanded):
                            expanded[0] = not expanded[0]
                            lbl.configure(text=full if expanded[0] else short)

                        see_all_btn = ctk.CTkButton(
                            patterns_container,
                            text="See All",
                            font=ctk.CTkFont(size=10),
                            width=50,
                            height=20,
                            fg_color=COLORS['bg_light'],
                            hover_color=COLORS['bg_medium'],
                            text_color=COLORS['accent'],
                            command=toggle_expand,
                        )
                        see_all_btn.pack(side="left", padx=(SPACING['sm'], 0))

        # Recommendations
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

        # Export actions
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
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        enable_smooth_scrolling(scroll_frame)

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

        btn_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        tag_icon = ICONS.get('tag', '\u2302')
        tags_btn = ctk.CTkButton(
            btn_frame,
            text=f"{tag_icon} Tags",
            font=ctk.CTkFont(size=12),
            width=80,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['accent_muted'],
            text_color=COLORS['text_muted'],
            command=self._show_tag_manager,
        )
        tags_btn.pack(side="left", padx=(0, SPACING['sm']))

        bookmark_icon = ICONS.get('bookmark', '\u2606')
        bookmarks_btn = ctk.CTkButton(
            btn_frame,
            text=f"{bookmark_icon} Bookmarks",
            font=ctk.CTkFont(size=12),
            width=100,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['accent_muted'],
            text_color=COLORS['text_muted'],
            command=self._show_bookmarks_only,
        )
        bookmarks_btn.pack(side="left", padx=(0, SPACING['sm']))

        clear_icon = ICONS.get('clear', '\u2718')
        clear_btn = ctk.CTkButton(
            btn_frame,
            text=f"{clear_icon} Clear All",
            font=ctk.CTkFont(size=12),
            width=100,
            height=32,
            fg_color="transparent",
            hover_color=COLORS['danger_muted'],
            text_color=COLORS['text_muted'],
            command=self._clear_all_history,
        )
        clear_btn.pack(side="left")

        stats = self._analyzer_service.get_statistics()
        if stats.get('total_analyses', 0) > 0:
            stats_panel = StatisticsPanel(scroll_frame)
            stats_panel.pack(fill="x", pady=(0, SPACING['lg']))
            stats_panel.set_statistics(stats)

        list_header = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, SPACING['sm']))

        list_title = ctk.CTkLabel(
            list_header,
            text="Recent Analyses",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_secondary'],
        )
        list_title.pack(side="left")

        history_count = self._analyzer_service.get_history_count()
        count_label = ctk.CTkLabel(
            list_header,
            text=f"{history_count} total",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
        )
        count_label.pack(side="right")

        self._history_list_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self._history_list_frame.pack(fill="both", expand=True)
        self._load_history_items()

    def _load_history_items(self):
        for widget in self._history_list_frame.winfo_children():
            widget.destroy()

        history = self._analyzer_service.get_analysis_history(limit=50)

        if not history:
            empty_card = EmptyHistoryCard(self._history_list_frame)
            empty_card.pack(fill="x", pady=SPACING['md'])
            return

        for analysis in history:
            analysis_id = analysis.get('id')
            is_bookmarked = self._analyzer_service.is_bookmarked(analysis_id) if analysis_id else False
            tags = self._analyzer_service.get_tags_for_analysis(analysis_id) if analysis_id else []

            card = HistoryCard(
                self._history_list_frame,
                analysis_data=analysis,
                on_click=self._on_history_item_click,
                on_delete=self._on_history_item_delete,
                on_bookmark_toggle=self._on_bookmark_toggle,
                is_bookmarked=is_bookmarked,
                tags=tags,
            )
            card.pack(fill="x", pady=(0, SPACING['sm']))

    def _on_bookmark_toggle(self, analysis_id: int, is_bookmarked: bool):
        if is_bookmarked:
            success = self._analyzer_service.add_bookmark(analysis_id)
            if success:
                self.status_bar.set_status("Analysis bookmarked", "success")
        else:
            success = self._analyzer_service.remove_bookmark(analysis_id)
            if success:
                self.status_bar.set_status("Bookmark removed", "info")

    def _show_tag_manager(self):
        from .widgets import TagManagerDialog
        tags = self._analyzer_service.get_all_tags()

        def on_create(name: str, color: str):
            tag_id = self._analyzer_service.create_tag(name, color)
            if tag_id:
                self.status_bar.set_status(f"Tag '{name}' created", "success")
                dialog.set_tags(self._analyzer_service.get_all_tags())

        def on_delete(tag_id: int):
            if self._analyzer_service.delete_tag(tag_id):
                self.status_bar.set_status("Tag deleted", "info")
                dialog.set_tags(self._analyzer_service.get_all_tags())

        dialog = TagManagerDialog(
            self.master,
            tags=tags,
            on_create=on_create,
            on_delete=on_delete,
        )

    def _show_bookmarks_only(self):
        for widget in self._history_list_frame.winfo_children():
            widget.destroy()

        bookmarks = self._analyzer_service.get_all_bookmarks(limit=50)

        if not bookmarks:
            empty_frame = ctk.CTkFrame(self._history_list_frame, fg_color=COLORS['bg_medium'], corner_radius=8)
            empty_frame.pack(fill="x", pady=SPACING['md'])

            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No bookmarked analyses yet",
                font=ctk.CTkFont(size=14),
                text_color=COLORS['text_muted'],
            )
            empty_label.pack(pady=SPACING['xl'])

            show_all_btn = ctk.CTkButton(
                empty_frame,
                text="Show All History",
                font=ctk.CTkFont(size=12),
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_bright'],
                command=self._load_history_items,
            )
            show_all_btn.pack(pady=(0, SPACING['xl']))
            return

        all_btn = ctk.CTkButton(
            self._history_list_frame,
            text="< Show All History",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=COLORS['bg_light'],
            text_color=COLORS['accent'],
            anchor="w",
            command=self._load_history_items,
        )
        all_btn.pack(anchor="w", pady=(0, SPACING['sm']))

        for bookmark in bookmarks:
            analysis_data = bookmark.get('analysis', {})
            analysis_data['id'] = bookmark.get('analysis_id')
            analysis_id = bookmark.get('analysis_id')
            tags = self._analyzer_service.get_tags_for_analysis(analysis_id) if analysis_id else []

            card = HistoryCard(
                self._history_list_frame,
                analysis_data=analysis_data,
                on_click=self._on_history_item_click,
                on_delete=self._on_history_item_delete,
                on_bookmark_toggle=self._on_bookmark_toggle,
                is_bookmarked=True,
                tags=tags,
            )
            card.pack(fill="x", pady=(0, SPACING['sm']))

    def _on_history_item_click(self, analysis_id: int):
        analysis = self._analyzer_service.get_analysis_by_id(analysis_id)
        if not analysis:
            show_warning(self.master, "Not Found", "Analysis record not found.")
            return

        # TODO: restore full results view instead of just showing info
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
        if ask_question(self.master, "Confirm Delete", "Delete this analysis from history?"):
            success = self._analyzer_service.delete_from_history(analysis_id)
            if success:
                self.status_bar.set_status("Analysis deleted from history", "info")
                self._build_history_view()
            else:
                show_error(self.master, "Error", "Failed to delete analysis.")

    def _clear_all_history(self):
        count = self._analyzer_service.get_history_count()
        if count == 0:
            show_info(self.master, "History Empty", "There is no history to clear.")
            return

        if ask_question(self.master, "Clear All History", f"Delete all {count} analyses from history?\n\nThis action cannot be undone."):
            success = self._analyzer_service.clear_history()
            if success:
                self.status_bar.set_status("All history cleared", "info")
                self._build_history_view()
            else:
                show_error(self.master, "Error", "Failed to clear history.")

    def _count_issues(self, browsers: Dict) -> int:
        """Count unique unsupported/partial features across all browsers."""
        issues = set()
        for browser_data in browsers.values():
            for feature in browser_data.get('unsupported_features', []):
                issues.add(feature)
            for feature in browser_data.get('partial_features', []):
                issues.add(feature)
        return len(issues)

    def _extract_issues(self, browsers: Dict) -> List[dict]:
        """Group unsupported/partial features into issue dicts for IssuesSummary."""
        unsupported_map = {}
        partial_map = {}

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

        for feature_id, affected_browsers in unsupported_map.items():
            issues.append({
                'feature_name': self._analyzer_service.get_feature_display_name(feature_id),
                'feature_id': feature_id,
                'severity': 'critical',
                'browsers': affected_browsers,
                'fix_suggestion': self._analyzer_service.get_fix_suggestion(feature_id),
            })

        # Only add partial issues if the feature isn't already listed as unsupported
        for feature_id, affected_browsers in partial_map.items():
            if feature_id not in unsupported_map:
                issues.append({
                    'feature_name': self._analyzer_service.get_feature_display_name(feature_id),
                    'feature_id': feature_id,
                    'severity': 'warning',
                    'browsers': affected_browsers,
                    'fix_suggestion': self._analyzer_service.get_fix_suggestion(feature_id),
                })

        return issues

    def _get_polyfill_recommendations(self, browsers: Dict) -> dict:
        """Build polyfill recommendations from unsupported/partial features."""
        if not browsers:
            return {'has_recommendations': False}

        from src.polyfill import PolyfillService
        polyfill_svc = PolyfillService()

        unsupported = set()
        partial = set()
        browser_versions = {}

        for browser_name, data in browsers.items():
            browser_versions[browser_name] = data.get('version', '')
            unsupported.update(data.get('unsupported_features', []))
            partial.update(data.get('partial_features', []))

        recommendations = polyfill_svc.get_recommendations(unsupported, partial, browser_versions)

        if not recommendations:
            return {'has_recommendations': False}

        categorized = polyfill_svc.categorize_recommendations(recommendations)
        npm_recs = categorized['npm']
        css_recs = categorized['fallback']

        return {
            'has_recommendations': True,
            'count': len(recommendations),
            'install_command': polyfill_svc.get_aggregate_install_command(recommendations),
            'imports': polyfill_svc.get_aggregate_imports(recommendations),
            'npm': npm_recs,
            'css': css_recs,
            'total_size_kb': polyfill_svc.get_total_size_kb(recommendations),
        }

    def _generate_polyfills_file(self, filename: str):
        """Save a polyfills.js file with all necessary imports."""
        if not self.current_report:
            show_warning(self, "No Analysis", "Please run an analysis first.")
            return

        browsers = self.current_report.get('browsers', {})
        polyfill_data = self._get_polyfill_recommendations(browsers)

        if not polyfill_data['has_recommendations']:
            show_info(self, "No Polyfills", "No polyfills are needed for your current analysis.")
            return

        from tkinter import filedialog
        output_path = filedialog.asksaveasfilename(
            defaultextension=".js",
            filetypes=[("JavaScript files", "*.js"), ("All files", "*.*")],
            initialfile=filename,
            title="Save Polyfills File"
        )

        if not output_path:
            return

        try:
            all_recs = polyfill_data['npm']
            generated_path = self._analyzer_service.generate_polyfills_file(all_recs, output_path)
            show_info(
                self,
                "File Generated",
                f"Polyfills file created:\n{generated_path}\n\n"
                f"Don't forget to install the packages:\n{polyfill_data['install_command']}"
            )
        except Exception as e:
            show_error(self, "Error", f"Failed to generate file: {e}")

    def _get_ml_risk_assessment(self, features: Dict) -> Optional[Dict]:
        """Run ML risk prediction on detected features. Returns None if unavailable."""
        try:
            from src.ml.risk_predictor import get_risk_predictor, RiskCategory

            all_features = []
            for key in ['html', 'css', 'js']:
                all_features.extend(features.get(key, []))

            if not all_features:
                return None

            all_features = all_features[:50]  # cap for performance

            predictor = get_risk_predictor()

            high_risk_count = 0
            medium_risk_count = 0
            low_risk_count = 0
            sample_factors = []

            # Sample for speed -- extrapolate results to full set later
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
                    continue

            total = high_risk_count + medium_risk_count + low_risk_count
            if total == 0:
                return None

            if high_risk_count > total * 0.3:
                overall_risk = 'high'
            elif high_risk_count > 0 or medium_risk_count > total * 0.3:
                overall_risk = 'medium'
            else:
                overall_risk = 'low'

            unique_factors = list(dict.fromkeys(sample_factors))[:5]

            feature_importance = predictor.get_feature_importance()
            if feature_importance:
                sorted_importance = sorted(
                    feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            else:
                sorted_importance = None

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
            return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None

    def _run_ml_analysis(self):
        self._run_ml_button.configure(state="disabled", text="Analyzing...")
        # Defer so the button text updates before we block the main thread
        self.after(100, self._perform_ml_analysis)

    def _perform_ml_analysis(self):
        try:
            from src.ml.risk_predictor import get_all_models_aggregate, get_risk_predictor

            all_features = []
            for key in ['html', 'css', 'js']:
                all_features.extend(self._ml_features.get(key, []))

            if not all_features:
                self._ml_button_frame.destroy()
                self._show_ml_error("No features to analyze")
                return

            # Single source of truth for all model predictions
            all_models_data = get_all_models_aggregate(all_features, full_analysis=True)

            if not all_models_data or not all_models_data.get('models'):
                self._ml_button_frame.destroy()
                self._show_ml_error("ML models not available. Make sure models are trained.")
                return

            # Gradient Boosting is the best model, use it for the main card
            gb_data = all_models_data['models'].get('gradient_boosting', {})

            if not gb_data:
                gb_data = list(all_models_data['models'].values())[0] if all_models_data['models'] else {}

            flagged_count = gb_data.get('high_count', 0) + gb_data.get('medium_count', 0)

            predictor = get_risk_predictor()
            feature_importance = predictor.get_feature_importance()
            sorted_importance = None
            if feature_importance:
                sorted_importance = sorted(
                    feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]

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

            self._ml_button_frame.destroy()

            ml_risk_card = MLRiskCard(self._ml_content_frame, title="Compatibility Risk Prediction")
            ml_risk_card.pack(fill="x", pady=(0, SPACING['sm']))

            model_confidence = gb_data.get('avg_confidence', 0.5)
            model_accuracy = gb_data.get('accuracy', 0.93)

            ml_risk_card.set_risk_data(
                risk_level=gb_data.get('overall_risk', 'low'),
                confidence=model_confidence,
                factors=factors,
                high_risk_count=flagged_count,
                total_features=self._ml_total_features,
                model_accuracy=model_accuracy,
            )

            if sorted_importance:
                importance_card = MLFeatureImportanceCard(self._ml_content_frame)
                importance_card.pack(fill="x", pady=(0, SPACING['sm']))
                importance_card.set_importances(sorted_importance)

            self._create_advanced_section(all_models_data)

        except Exception as e:
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
        error_frame = ctk.CTkFrame(self._ml_content_frame, fg_color=COLORS['bg_medium'], corner_radius=8)
        error_frame.pack(fill="x", pady=SPACING['sm'])

        ctk.CTkLabel(
            error_frame,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['warning'],
        ).pack(padx=SPACING['lg'], pady=SPACING['lg'])

    def _create_advanced_section(self, all_models_data: dict):
        """Collapsible section comparing all 3 ML models side by side."""
        advanced_frame = ctk.CTkFrame(
            self._ml_content_frame,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
        )
        advanced_frame.pack(fill="x", pady=(SPACING['sm'], 0))

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

        # Hidden until user expands
        self._advanced_content = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        self._populate_advanced_content(all_models_data)

    def _toggle_advanced_section(self, all_models_data: dict):
        self._advanced_expanded = not self._advanced_expanded

        if self._advanced_expanded:
            self._advanced_toggle_btn.configure(text="▼  View All Models")
            self._advanced_content.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        else:
            self._advanced_toggle_btn.configure(text="▶  View All Models")
            self._advanced_content.pack_forget()

    def _populate_advanced_content(self, all_models_data: dict):
        models = all_models_data.get('models', {})

        risk_colors = {
            'low': COLORS['success'],
            'medium': COLORS['warning'],
            'high': COLORS['danger'],
        }

        model_order = ['gradient_boosting', 'random_forest', 'logistic_regression']

        for model_name in model_order:
            if model_name not in models:
                continue

            model_data = models[model_name]

            model_frame = ctk.CTkFrame(self._advanced_content, fg_color=COLORS['bg_light'], corner_radius=6)
            model_frame.pack(fill="x", pady=(0, SPACING['sm']))

            header_row = ctk.CTkFrame(model_frame, fg_color="transparent")
            header_row.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])

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

            predictions = model_data.get('predictions', [])
            flagged_predictions = [p for p in predictions if p.get('risk') in ['high', 'medium']]

            if flagged_predictions:
                divider = ctk.CTkFrame(model_frame, fg_color=COLORS['border'], height=1)
                divider.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['xs']))

                header_frame = ctk.CTkFrame(model_frame, fg_color="transparent")
                header_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['xs']))

                flagged_header = ctk.CTkLabel(
                    header_frame,
                    text="Flagged Features:",
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS['text_muted'],
                )
                flagged_header.pack(side="left")

                features_container = ctk.CTkFrame(model_frame, fg_color="transparent")
                features_container.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

                initial_frame = ctk.CTkFrame(features_container, fg_color="transparent")
                initial_frame.pack(fill="x")

                # Rest are hidden until toggled
                hidden_frame = ctk.CTkFrame(features_container, fg_color="transparent")

                for idx, pred in enumerate(flagged_predictions):
                    feature_id = pred.get('feature', 'unknown')
                    feature_risk = pred.get('risk', 'unknown')
                    feature_reason = pred.get('reason', 'Risk detected by ML model')
                    feature_color = risk_colors.get(feature_risk, COLORS['text_muted'])

                    parent_frame = initial_frame if idx < 5 else hidden_frame

                    feature_row = ctk.CTkFrame(parent_frame, fg_color=COLORS['bg_medium'], corner_radius=4)
                    feature_row.pack(fill="x", pady=(0, 4))

                    feature_inner = ctk.CTkFrame(feature_row, fg_color="transparent")
                    feature_inner.pack(fill="x", padx=SPACING['sm'], pady=SPACING['xs'])

                    left_frame = ctk.CTkFrame(feature_inner, fg_color="transparent")
                    left_frame.pack(side="left", fill="x", expand=True)

                    bullet = ctk.CTkLabel(
                        left_frame,
                        text="•",
                        font=ctk.CTkFont(size=11),
                        text_color=feature_color,
                        width=15,
                    )
                    bullet.pack(side="left")

                    feature_name_label = ctk.CTkLabel(
                        left_frame,
                        text=feature_id,
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS['text_primary'],
                        anchor="w",
                    )
                    feature_name_label.pack(side="left")

                    risk_badge = ctk.CTkLabel(
                        feature_inner,
                        text=f" {feature_risk.upper()} ",
                        font=ctk.CTkFont(size=9, weight="bold"),
                        text_color=feature_color,
                    )
                    risk_badge.pack(side="right")

                    reason_label = ctk.CTkLabel(
                        feature_row,
                        text=f"    {feature_reason}",
                        font=ctk.CTkFont(size=10),
                        text_color=COLORS['text_muted'],
                        anchor="w",
                    )
                    reason_label.pack(fill="x", padx=SPACING['sm'], pady=(0, SPACING['xs']))

                if len(flagged_predictions) > 5:
                    toggle_frame = ctk.CTkFrame(features_container, fg_color="transparent")
                    toggle_frame.pack(fill="x", pady=(SPACING['xs'], 0))

                    is_expanded = [False]  # mutable closure trick

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

                    # Re-configure so the callback can update the button text
                    toggle_btn.configure(
                        command=make_toggle_callback(hidden_frame, toggle_btn, is_expanded, len(flagged_predictions))
                    )

    def _build_settings_view(self):
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])

        ctk.CTkLabel(
            container,
            text="Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, SPACING['xl']))

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

        prefs_section = ctk.CTkFrame(
            container,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
        )
        prefs_section.pack(fill="x", pady=(0, SPACING['lg']))

        prefs_header = ctk.CTkFrame(prefs_section, fg_color="transparent")
        prefs_header.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        ctk.CTkLabel(
            prefs_header,
            text="User Preferences",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        prefs_content = ctk.CTkFrame(prefs_section, fg_color="transparent")
        prefs_content.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))

        auto_save_row = ctk.CTkFrame(prefs_content, fg_color="transparent")
        auto_save_row.pack(fill="x", pady=(0, SPACING['md']))

        ctk.CTkLabel(
            auto_save_row,
            text="Auto-save to History",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(side="left")

        ctk.CTkLabel(
            auto_save_row,
            text="Automatically save analyses to history",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted'],
        ).pack(side="left", padx=(SPACING['sm'], 0))

        auto_save_current = self._analyzer_service.get_setting_as_bool('auto_save_history', True)
        self._auto_save_var = ctk.BooleanVar(value=auto_save_current)

        auto_save_switch = ctk.CTkSwitch(
            auto_save_row,
            text="",
            variable=self._auto_save_var,
            onvalue=True,
            offvalue=False,
            command=self._on_auto_save_changed,
            fg_color=COLORS['bg_light'],
            progress_color=COLORS['accent'],
        )
        auto_save_switch.pack(side="right")

        history_limit_row = ctk.CTkFrame(prefs_content, fg_color="transparent")
        history_limit_row.pack(fill="x", pady=(0, SPACING['md']))

        ctk.CTkLabel(
            history_limit_row,
            text="History Limit",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(side="left")

        ctk.CTkLabel(
            history_limit_row,
            text="Maximum analyses to keep in history",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted'],
        ).pack(side="left", padx=(SPACING['sm'], 0))

        history_limit_current = self._analyzer_service.get_setting('history_limit', '100')

        self._history_limit_var = ctk.StringVar(value=history_limit_current)
        history_limit_menu = ctk.CTkOptionMenu(
            history_limit_row,
            variable=self._history_limit_var,
            values=['25', '50', '100', '200', '500'],
            width=80,
            height=28,
            fg_color=COLORS['bg_light'],
            button_color=COLORS['bg_light'],
            button_hover_color=COLORS['hover_bg'],
            dropdown_fg_color=COLORS['bg_medium'],
            dropdown_hover_color=COLORS['hover_bg'],
            command=self._on_history_limit_changed,
        )
        history_limit_menu.pack(side="right")

        browsers_row = ctk.CTkFrame(prefs_content, fg_color="transparent")
        browsers_row.pack(fill="x", pady=(0, SPACING['sm']))

        ctk.CTkLabel(
            browsers_row,
            text="Default Browsers",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
        ).pack(side="left")

        ctk.CTkLabel(
            browsers_row,
            text="Browsers to check by default",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted'],
        ).pack(side="left", padx=(SPACING['sm'], 0))

        browsers_frame = ctk.CTkFrame(prefs_content, fg_color="transparent")
        browsers_frame.pack(fill="x", pady=(SPACING['xs'], 0))

        default_browsers = self._analyzer_service.get_setting_as_list(
            'default_browsers',
            ['chrome', 'firefox', 'safari', 'edge']
        )

        self._browser_vars = {}
        all_browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera', 'ie']

        for browser in all_browsers:
            var = ctk.BooleanVar(value=browser in default_browsers)
            self._browser_vars[browser] = var

            cb = ctk.CTkCheckBox(
                browsers_frame,
                text=browser.title(),
                variable=var,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary'],
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_bright'],
                command=self._on_default_browsers_changed,
            )
            cb.pack(side="left", padx=(0, SPACING['lg']))

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
        if hasattr(self, 'file_table'):
            self.file_table.add_files(file_paths)
            self._update_status()

    def _clear_all_files(self):
        if hasattr(self, 'file_table'):
            self.file_table.clear_files()
            self._last_files = []
            self._update_status()

    def _update_status(self):
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
        self._selected_browsers = selected_browsers
        browser_count = len(selected_browsers)
        if browser_count > 0:
            self.status_bar.set_status(f"{browser_count} browser(s) selected for analysis", "info")

    def _analyze_files(self):
        if not hasattr(self, 'file_table'):
            return

        files = self.file_table.get_files()
        if not files:
            show_warning(self.master, "No Files", "Please select at least one file.")
            return

        if not self._selected_browsers:
            show_warning(self.master, "No Browsers", "Please select at least one target browser.")
            return

        browser_count = len(self._selected_browsers)
        if ask_question(self.master, "Confirm", f"Analyze {len(files)} file(s) against {browser_count} browser(s)?"):
            self._run_analysis(files)

    def _run_analysis(self, files: List[str]):
        self._last_files = list(files)

        html_files = [f for f in files if Path(f).suffix.lower() in ['.html', '.htm']]
        css_files = [f for f in files if Path(f).suffix.lower() == '.css']
        js_files = [f for f in files if Path(f).suffix.lower() in ['.js', '.jsx', '.ts', '.tsx', '.mjs']]

        try:
            progress = ProgressDialog(self.master, "Analyzing", "Starting analysis...")
            progress.set_progress(10)
            self.master.update()

            progress.set_progress(30, message="Analyzing browser compatibility...")

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

                self._save_to_history(result, files)

                self.sidebar.set_active_view("results")
                self._show_view("results")
            else:
                show_error(self.master, "Analysis Failed", f"{result.error or 'Unknown error'}")

        except Exception as e:
            show_error(self.master, "Error", str(e))
            import traceback
            traceback.print_exc()

    def _save_to_history(self, result, files: List[str]):
        try:
            if len(files) == 1:
                file_path = files[0]
                file_name = Path(file_path).name
                file_type = Path(file_path).suffix.lower().lstrip('.')
                if file_type == 'htm':
                    file_type = 'html'
            else:
                file_names = [Path(f).name for f in files]
                file_name = f"{file_names[0]} (+{len(files)-1} more)" if len(files) > 1 else file_names[0]
                file_path = str(Path(files[0]).parent)
                file_type = 'mixed'

            self._analyzer_service.save_analysis_to_history(
                result=result,
                file_name=file_name,
                file_path=file_path,
                file_type=file_type,
            )
        except Exception as e:
            # Non-fatal -- don't let a history save failure break the analysis
            import traceback
            traceback.print_exc()

    def _recheck_files(self):
        if not self._last_files:
            show_warning(self.master, "Warning", "No files to re-check.")
            return

        missing = [f for f in self._last_files if not Path(f).exists()]
        if missing:
            missing_list = "\n".join(missing[:5])
            if len(missing) > 5:
                missing_list += f"\n... and {len(missing) - 5} more"
            show_warning(self.master, "Missing Files", f"Some files no longer exist:\n{missing_list}")
            return

        self._run_analysis(self._last_files)

    def _update_database(self):
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
                progress.set_progress(percentage, message=message)
                self.master.update()

            result = self._analyzer_service.update_database(update_progress)

            progress.set_progress(100)
            progress.close()

            if result.success:
                show_info(self.master, "Success", result.message or 'Database updated!')
                if self._current_view == "settings":
                    self._show_view("settings")
            else:
                show_error(self.master, "Failed", result.message or 'Update failed')

        except Exception as e:
            show_error(self.master, "Error", str(e))

    def _on_auto_save_changed(self):
        value = self._auto_save_var.get()
        self._analyzer_service.set_setting('auto_save_history', 'true' if value else 'false')
        status = "enabled" if value else "disabled"
        self.status_bar.set_status(f"Auto-save to history {status}", "info")

    def _on_history_limit_changed(self, value: str):
        self._analyzer_service.set_setting('history_limit', value)
        self.status_bar.set_status(f"History limit set to {value}", "info")

    def _on_default_browsers_changed(self):
        selected = [browser for browser, var in self._browser_vars.items() if var.get()]

        if not selected:
            # Always need at least one browser
            self._browser_vars['chrome'].set(True)
            selected = ['chrome']
            show_warning(self.master, "Warning", "At least one browser must be selected.")

        browsers_str = ','.join(selected)
        self._analyzer_service.set_setting('default_browsers', browsers_str)
        self.status_bar.set_status(f"Default browsers: {', '.join(b.title() for b in selected)}", "info")

    def _open_rules_manager(self):
        def on_rules_changed():
            self._analyzer_service.reload_custom_rules()

        show_rules_manager(self.master, on_rules_changed)

    def _show_help(self):
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
