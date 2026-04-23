"""Main window -- sidebar nav, file table, results, history, and settings."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import customtkinter as ctk

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
    BuildBadge,
    CollapsibleSection,
    IssuesSummary,
    QuickStatsBar,
    BrowserSelector,
    get_available_browsers,
    HistoryCard,
    StatisticsPanel,
    CompactStatsBar,
    BookmarkButton,
    TagManagerDialog,
    PolyfillCard,
    AIFixCard,
)
from .widgets.rules_manager import show_rules_manager

from .export_manager import ExportManager


class MainWindow(ctk.CTkFrame):

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
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self._current_view = view_id

        if view_id == "files":
            self._build_files_view()
        elif view_id == "results":
            self._build_results_view()
        elif view_id == "history":
            self._build_history_view()
        elif view_id == "settings":
            self._build_settings_view()

        titles = {
            "files": "File Selection",
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

    def _build_results_view(self):
        if not self.current_report:
            self._build_results_empty_state()
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

        self._build_results_score_section(scroll_frame, report)
        self._build_results_issues_section(scroll_frame, report)
        self._build_results_recommendations_section(scroll_frame, report)
        self._build_results_browsers_section(scroll_frame, report)
        self._build_results_features_section(scroll_frame, report)
        self._build_results_viz_section(scroll_frame, report)
        self._build_results_actions_section(scroll_frame, report)

    def _build_results_empty_state(self):
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

    def _build_results_score_section(self, scroll_frame, report):
        scores = report.get('scores', {})
        summary = report.get('summary', {})
        browsers = report.get('browsers', {})

        weighted_score = scores.get('weighted_score', 0)
        grade = scores.get('grade', 'N/A')
        total_features = summary.get('total_features', 0)
        browsers_count = len(browsers)

        issues_count = self._count_issues(browsers)

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

    def _build_results_issues_section(self, scroll_frame, report):
        browsers = report.get('browsers', {})
        issues = self._extract_issues(browsers)
        if issues:
            issues_section = CollapsibleSection(
                scroll_frame,
                title="Issues & Fixes",
                badge_text=f"{len(issues)} issues",
                badge_color=COLORS['danger'],
                expanded=True,
            )
            issues_section.pack(fill="x", pady=(0, SPACING['lg']))
            issues_content = issues_section.get_content_frame()

            issues_summary = IssuesSummary(issues_content, issues=issues)
            issues_summary.pack(fill="x")

            ai_key = self._analyzer_service.get_setting('ai_api_key', '')
            if ai_key:
                ctk.CTkFrame(issues_content, fg_color=COLORS['border'], height=1).pack(
                    fill="x", pady=SPACING['md']
                )
                self._ai_placeholder = ctk.CTkFrame(issues_content, fg_color="transparent")
                self._ai_placeholder.pack(fill="x")

                ai_row = ctk.CTkFrame(self._ai_placeholder, fg_color="transparent")
                ai_row.pack(fill="x")

                ctk.CTkLabel(
                    ai_row,
                    text="Need help fixing these issues?",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS['text_muted'],
                ).pack(side="left")

                ctk.CTkButton(
                    ai_row, text="Get AI Suggestions",
                    font=ctk.CTkFont(size=11),
                    width=150, height=30,
                    fg_color=COLORS['accent'],
                    hover_color=COLORS['accent_dim'],
                    command=lambda e=None: self._on_ai_suggestions_click(browsers, scroll_frame),
                ).pack(side="right")

    def _build_results_recommendations_section(self, scroll_frame, report):
        browsers = report.get('browsers', {})
        polyfill_data = self._get_polyfill_recommendations(browsers)
        recommendations = report.get('recommendations', [])
        has_recs = polyfill_data['has_recommendations'] or recommendations

        if has_recs:
            rec_count = polyfill_data.get('count', 0) + len(recommendations)
            rec_section = CollapsibleSection(
                scroll_frame,
                title="Recommendations",
                badge_text=str(rec_count),
                badge_color=COLORS['info'],
                expanded=False,
            )
            rec_section.pack(fill="x", pady=(0, SPACING['lg']))
            rec_content = rec_section.get_content_frame()

            if polyfill_data['has_recommendations']:
                polyfill_card = PolyfillCard(
                    rec_content,
                    install_command=polyfill_data['install_command'],
                    import_statements=polyfill_data['imports'],
                    npm_recommendations=polyfill_data['npm'],
                    css_fallbacks=polyfill_data['css'],
                    total_size_kb=polyfill_data['total_size_kb'],
                    on_generate_file=self._generate_polyfills_file,
                )
                polyfill_card.pack(fill="x")

            if recommendations:
                if polyfill_data['has_recommendations']:
                    ctk.CTkFrame(rec_content, fg_color=COLORS['border'], height=1).pack(
                        fill="x", pady=SPACING['sm']
                    )
                for i, rec in enumerate(recommendations, 1):
                    rec_row = ctk.CTkFrame(rec_content, fg_color=COLORS['bg_dark'], corner_radius=4, height=28)
                    rec_row.pack(fill="x", pady=(0, 1))
                    rec_row.pack_propagate(False)
                    ctk.CTkLabel(
                        rec_row, text=f"{i}. {rec}",
                        font=ctk.CTkFont(size=11),
                        text_color=COLORS['text_secondary'],
                        anchor="w",
                    ).pack(side="left", padx=SPACING['sm'])

    def _build_results_browsers_section(self, scroll_frame, report):
        browsers = report.get('browsers', {})
        browsers_count = len(browsers)
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
            from .widgets.browser_card import StackedBarWidget

            for browser_name, details in browsers.items():
                supported = details.get('supported', 0)
                partial_count = details.get('partial', 0)
                unsupported = details.get('unsupported', 0)
                pct = details.get('compatibility_percentage', 0)
                version = details.get('version', '')
                unsupported_list = details.get('unsupported_features', [])
                partial_list = details.get('partial_features', [])

                card = ctk.CTkFrame(browser_content, fg_color=COLORS['bg_dark'], corner_radius=6,
                                    border_width=1, border_color=COLORS['border'])
                card.pack(fill="x", pady=(0, SPACING['sm']))

                header_row = ctk.CTkFrame(card, fg_color="transparent")
                header_row.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['xs']))

                ctk.CTkLabel(
                    header_row,
                    text=f"{browser_name.title()} {version}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS['text_primary'],
                    width=120, anchor="w",
                ).pack(side="left")

                bar = StackedBarWidget(header_row, height=12, bg_color=COLORS['bg_dark'])
                bar.pack(side="left", fill="x", expand=True, padx=SPACING['sm'])
                bar.set_values(supported, partial_count, unsupported, animate=False)

                pct_color = COLORS['success'] if pct >= 80 else (COLORS['warning'] if pct >= 50 else COLORS['danger'])
                ctk.CTkLabel(
                    header_row,
                    text=f"{pct:.0f}%",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=pct_color,
                    width=45, anchor="e",
                ).pack(side="right")

                tab_row = ctk.CTkFrame(card, fg_color="transparent")
                tab_row.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['xs']))

                tab_content = ctk.CTkFrame(card, fg_color="transparent")
                tab_content.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

                active_tab = [None]
                tab_buttons = {}
                tab_frames = {}

                def build_overview(parent, s, p, u):
                    frame = ctk.CTkFrame(parent, fg_color="transparent")
                    row = ctk.CTkFrame(frame, fg_color="transparent")
                    row.pack(fill="x")
                    for label, count, color in [("Supported", s, COLORS['success']), ("Partial", p, COLORS['warning']), ("Unsupported", u, COLORS['danger'])]:
                        block = ctk.CTkFrame(row, fg_color=COLORS['bg_medium'], corner_radius=4)
                        block.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
                        ctk.CTkLabel(block, text=str(count), font=ctk.CTkFont(size=16, weight="bold"),
                                     text_color=color).pack(pady=(SPACING['xs'], 0))
                        ctk.CTkLabel(block, text=label, font=ctk.CTkFont(size=9),
                                     text_color=COLORS['text_muted']).pack(pady=(0, SPACING['xs']))
                    return frame

                def build_issues(parent, u_list, p_list):
                    frame = ctk.CTkFrame(parent, fg_color="transparent")
                    if u_list:
                        ctk.CTkLabel(frame, text="Not Supported", font=ctk.CTkFont(size=10, weight="bold"),
                                     text_color=COLORS['danger']).pack(anchor="w", pady=(0, 2))
                        for feat in u_list:
                            r = ctk.CTkFrame(frame, fg_color=COLORS['bg_medium'], corner_radius=3, height=22)
                            r.pack(fill="x", pady=(0, 1))
                            r.pack_propagate(False)
                            ctk.CTkFrame(r, fg_color=COLORS['danger'], width=3, corner_radius=0).place(x=0, y=0, relheight=1)
                            ctk.CTkLabel(r, text=self._analyzer_service.get_feature_display_name(feat),
                                         font=ctk.CTkFont(size=9), text_color=COLORS['text_primary']).pack(side="left", padx=(SPACING['sm'], 0))
                    if p_list:
                        ctk.CTkLabel(frame, text="Partial Support", font=ctk.CTkFont(size=10, weight="bold"),
                                     text_color=COLORS['warning']).pack(anchor="w", pady=(SPACING['xs'], 2))
                        for feat in p_list:
                            r = ctk.CTkFrame(frame, fg_color=COLORS['bg_medium'], corner_radius=3, height=22)
                            r.pack(fill="x", pady=(0, 1))
                            r.pack_propagate(False)
                            ctk.CTkFrame(r, fg_color=COLORS['warning'], width=3, corner_radius=0).place(x=0, y=0, relheight=1)
                            ctk.CTkLabel(r, text=self._analyzer_service.get_feature_display_name(feat),
                                         font=ctk.CTkFont(size=9), text_color=COLORS['text_primary']).pack(side="left", padx=(SPACING['sm'], 0))
                    if not u_list and not p_list:
                        ctk.CTkLabel(frame, text="All features fully supported.",
                                     font=ctk.CTkFont(size=10), text_color=COLORS['text_muted']).pack(anchor="w")
                    return frame

                def build_versions(parent, u_list, p_list, b_name):
                    frame = ctk.CTkFrame(parent, fg_color="transparent")
                    problem_feats = list(u_list) + list(p_list)
                    if not problem_feats:
                        ctk.CTkLabel(frame, text="No version history needed.",
                                     font=ctk.CTkFont(size=10), text_color=COLORS['text_muted']).pack(anchor="w")
                        return frame
                    for fid in problem_feats[:8]:
                        ranges = self._analyzer_service.get_version_ranges(fid, b_name)
                        if not ranges:
                            continue
                        r = ctk.CTkFrame(frame, fg_color=COLORS['bg_medium'], corner_radius=3, height=24)
                        r.pack(fill="x", pady=(0, 1))
                        r.pack_propagate(False)
                        ctk.CTkLabel(r, text=self._analyzer_service.get_feature_display_name(fid),
                                     font=ctk.CTkFont(size=9, weight="bold"), text_color=COLORS['text_primary'],
                                     width=170, anchor="w").pack(side="left", padx=(SPACING['sm'], 0))
                        for rng in ranges[-4:]:
                            v = rng['start'] if rng['start'] == rng['end'] else f"{rng['start']}-{rng['end']}"
                            c = COLORS['success'] if rng['status'] == 'y' else (
                                COLORS['warning'] if rng['status'] in ('a', 'p') else COLORS['danger'])
                            ctk.CTkLabel(r, text=f" {v} ", font=ctk.CTkFont(size=8),
                                         text_color="#FFFFFF", fg_color=c, corner_radius=3).pack(side="left", padx=(2, 0))
                    return frame

                overview_frame = build_overview(tab_content, supported, partial_count, unsupported)
                issues_frame = build_issues(tab_content, unsupported_list, partial_list)
                versions_frame = build_versions(tab_content, unsupported_list, partial_list, browser_name)

                _frames = {"overview": overview_frame, "issues": issues_frame, "versions": versions_frame}
                _buttons = {}

                def make_switcher(frames_ref, buttons_ref):
                    def switch(tab_name):
                        for f in frames_ref.values():
                            f.pack_forget()
                        frames_ref[tab_name].pack(fill="x")
                        for n, b in buttons_ref.items():
                            if n == tab_name:
                                b.configure(fg_color=COLORS['accent'], text_color="#FFFFFF")
                            else:
                                b.configure(fg_color=COLORS['bg_light'], text_color=COLORS['text_muted'])
                    return switch

                switcher = make_switcher(_frames, _buttons)

                for tab_name, tab_label in [("overview", "Overview"), ("issues", "Issues"), ("versions", "Versions")]:
                    btn = ctk.CTkButton(
                        tab_row, text=tab_label,
                        font=ctk.CTkFont(size=10), width=80, height=24,
                        corner_radius=4,
                        fg_color=COLORS['bg_light'],
                        hover_color=COLORS['hover_bg'],
                        text_color=COLORS['text_muted'],
                    )
                    btn.configure(command=lambda t=tab_name, s=switcher: s(t))
                    btn.pack(side="left", padx=(0, SPACING['xs']))
                    _buttons[tab_name] = btn

                switcher("overview")

    def _build_results_features_section(self, scroll_frame, report):
        summary = report.get('summary', {})
        browsers = report.get('browsers', {})
        features = report.get('features', {})
        total_features = summary.get('total_features', 0)
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

            feature_support = {}  # feature_id -> {browser: status}
            browser_names_ordered = list(browsers.keys())
            for b_name, b_data in browsers.items():
                for fid in b_data.get('unsupported_features', []):
                    feature_support.setdefault(fid, {})[b_name] = 'unsupported'
                for fid in b_data.get('partial_features', []):
                    feature_support.setdefault(fid, {})[b_name] = 'partial'

            legend_row = ctk.CTkFrame(features_content, fg_color="transparent")
            legend_row.pack(fill="x", pady=(0, SPACING['sm']))

            browser_labels = {}
            used_labels = set()
            for b_name in browser_names_ordered:
                label = b_name[0].upper()
                if label in used_labels:
                    label = b_name[:2].upper()
                used_labels.add(label)
                browser_labels[b_name] = label

            for b_name in browser_names_ordered:
                ctk.CTkLabel(
                    legend_row, text=browser_labels[b_name],
                    font=ctk.CTkFont(size=8, weight="bold"),
                    text_color=COLORS['success'], width=14,
                ).pack(side="left")
                ctk.CTkLabel(legend_row, text=b_name.title(), font=ctk.CTkFont(size=8),
                             text_color=COLORS['text_muted']).pack(side="left", padx=(1, SPACING['md']))

            for label, color in [("Supported", COLORS['success']), ("Partial", COLORS['warning']), ("Unsupported", COLORS['danger'])]:
                ctk.CTkLabel(
                    legend_row, text=label,
                    font=ctk.CTkFont(size=8),
                    text_color=color,
                ).pack(side="right", padx=(SPACING['sm'], 0))

            search_var = ctk.StringVar()
            search_entry = ctk.CTkEntry(
                features_content,
                placeholder_text="Search features...",
                textvariable=search_var,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['bg_medium'],
                border_color=COLORS['border'],
                text_color=COLORS['text_primary'],
            )
            search_entry.pack(fill="x", pady=(0, SPACING['sm']))

            all_feature_frames = []
            detail_maps = {}
            for lang in ('html', 'css', 'js'):
                detail_maps[lang] = {}
                for detail in feature_details.get(lang, []):
                    fid = detail.get('feature')
                    if fid:
                        detail_maps[lang][fid] = detail

            feature_types = [
                ("HTML", features.get('html', []), COLORS['html_color'], detail_maps['html']),
                ("CSS", features.get('css', []), COLORS['css_color'], detail_maps['css']),
                ("JavaScript", features.get('js', []), COLORS['js_color'], detail_maps['js']),
            ]

            for type_name, feature_list, type_color, details_map in feature_types:
                if not feature_list:
                    continue

                type_header = ctk.CTkFrame(features_content, fg_color="transparent", cursor="hand2")
                type_header.pack(fill="x", pady=(SPACING['sm'], SPACING['xs']))

                type_toggle = ctk.CTkLabel(
                    type_header, text="\u25BC",
                    font=ctk.CTkFont(size=8), text_color=COLORS['text_muted'], width=12,
                )
                type_toggle.pack(side="left", padx=(0, SPACING['xs']))

                ctk.CTkLabel(
                    type_header,
                    text=f" {type_name} ({len(feature_list)}) ",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=COLORS['text_primary'],
                    fg_color=type_color,
                    corner_radius=4,
                ).pack(side="left")

                ctk.CTkLabel(
                    type_header, text="Collapse",
                    font=ctk.CTkFont(size=8), text_color=COLORS['text_muted'],
                ).pack(side="right")

                type_container = ctk.CTkFrame(features_content, fg_color="transparent")
                type_container.pack(fill="x")
                type_expanded = [True]

                def make_type_toggle(container, toggle_lbl, expanded, hint_parent):
                    hint = [w for w in hint_parent.winfo_children() if hasattr(w, 'cget') and w.cget("text") in ("Collapse", "Expand")]
                    def toggle():
                        expanded[0] = not expanded[0]
                        if expanded[0]:
                            container.pack(fill="x")
                            toggle_lbl.configure(text="\u25BC")
                            if hint:
                                hint[0].configure(text="Collapse")
                        else:
                            container.pack_forget()
                            toggle_lbl.configure(text="\u25B6")
                            if hint:
                                hint[0].configure(text="Expand")
                    return toggle

                toggler = make_type_toggle(type_container, type_toggle, type_expanded, type_header)
                type_header.bind("<Button-1>", lambda e=None, t=toggler: t())
                for child in type_header.winfo_children():
                    child.bind("<Button-1>", lambda e=None, t=toggler: t())

                for feature_id in feature_list:
                    detail = details_map.get(feature_id, {})
                    matched = (
                        detail.get('matched_properties', []) or
                        detail.get('matched_apis', []) or
                        detail.get('matched_items', [])
                    )
                    name = detail.get('description', self._analyzer_service.get_feature_display_name(feature_id))
                    match_text = ", ".join(matched[:3]) if matched else ""
                    search_text = f"{name} {feature_id} {match_text}".lower()

                    row = ctk.CTkFrame(type_container, fg_color=COLORS['bg_dark'], corner_radius=3, height=26)
                    row.pack(fill="x", pady=(0, 1))
                    row.pack_propagate(False)

                    ctk.CTkLabel(
                        row, text=name,
                        font=ctk.CTkFont(size=10, weight="bold"),
                        text_color=COLORS['text_primary'],
                        anchor="w",
                    ).pack(side="left", padx=(SPACING['sm'], 0))

                    if match_text:
                        ctk.CTkLabel(
                            row, text=match_text,
                            font=ctk.CTkFont(size=9),
                            text_color=COLORS['text_muted'],
                            anchor="w",
                        ).pack(side="left", padx=(SPACING['sm'], 0))

                    badges_frame = ctk.CTkFrame(row, fg_color="transparent")
                    badges_frame.pack(side="right", padx=SPACING['sm'])

                    support_info = feature_support.get(feature_id, {})
                    for b_name in browser_names_ordered:
                        status = support_info.get(b_name, 'supported')
                        badge_color = COLORS['success'] if status == 'supported' else (
                            COLORS['warning'] if status == 'partial' else COLORS['danger'])
                        ctk.CTkLabel(
                            badges_frame,
                            text=browser_labels[b_name],
                            font=ctk.CTkFont(size=8, weight="bold"),
                            text_color=badge_color,
                            width=16,
                        ).pack(side="left", padx=(1, 0))

                    def on_enter(e, r=row):
                        r.configure(fg_color=COLORS['bg_medium'])
                    def on_leave(e, r=row):
                        r.configure(fg_color=COLORS['bg_dark'])
                    row.bind("<Enter>", on_enter)
                    row.bind("<Leave>", on_leave)

                    all_feature_frames.append((row, search_text))

            def filter_features(*args):
                query = search_var.get().lower().strip()
                for frame, text in all_feature_frames:
                    if query == "" or query in text:
                        frame.pack(fill="x", pady=(0, 1))
                    else:
                        frame.pack_forget()

            search_var.trace_add("write", filter_features)

            unrecognized = report.get('unrecognized', {})
            if unrecognized and unrecognized.get('total', 0) > 0:
                ctk.CTkFrame(features_content, fg_color=COLORS['border'], height=1).pack(fill="x", pady=SPACING['sm'])

                ctk.CTkLabel(
                    features_content,
                    text=f" Unrecognized ({unrecognized.get('total', 0)}) ",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=COLORS['text_primary'],
                    fg_color=COLORS['bg_light'],
                    corner_radius=4,
                ).pack(anchor="w", pady=(0, SPACING['xs']))

                unrec_types = [
                    ("HTML", unrecognized.get('html', []), COLORS['html_color']),
                    ("CSS", unrecognized.get('css', []), COLORS['css_color']),
                    ("JavaScript", unrecognized.get('js', []), COLORS['js_color']),
                ]

                for type_name, pattern_list, color in unrec_types:
                    for pattern in pattern_list:
                        row = ctk.CTkFrame(features_content, fg_color=COLORS['bg_dark'], corner_radius=3, height=26)
                        row.pack(fill="x", pady=(0, 1))
                        row.pack_propagate(False)

                        ctk.CTkLabel(
                            row, text=pattern,
                            font=ctk.CTkFont(size=10, weight="bold"),
                            text_color=COLORS['text_muted'],
                        ).pack(side="left", padx=(SPACING['sm'], 0))

                        ctk.CTkLabel(
                            row, text=type_name,
                            font=ctk.CTkFont(size=8),
                            text_color=COLORS['text_muted'],
                        ).pack(side="right", padx=SPACING['sm'])

    def _build_results_viz_section(self, scroll_frame, report):
        summary = report.get('summary', {})
        browsers = report.get('browsers', {})
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

    def _build_results_actions_section(self, scroll_frame, report):
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
            ctk.CTkLabel(
                self._history_list_frame, text="No analysis history yet.",
                font=ctk.CTkFont(size=12), text_color=COLORS['text_muted'],
            ).pack(fill="x", pady=SPACING['md'])
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
        issues = set()
        for browser_data in browsers.values():
            for feature in browser_data.get('unsupported_features', []):
                issues.add(feature)
            for feature in browser_data.get('partial_features', []):
                issues.add(feature)
        return len(issues)

    def _extract_issues(self, browsers: Dict) -> List[dict]:
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
            baseline = self._analyzer_service.get_baseline_status(feature_id)
            issues.append({
                'feature_name': self._analyzer_service.get_feature_display_name(feature_id),
                'feature_id': feature_id,
                'severity': 'critical',
                'browsers': affected_browsers,
                'fix_suggestion': self._analyzer_service.get_fix_suggestion(feature_id),
                'baseline_status': baseline.get('status') if baseline else None,
            })

        # Only add partial issues if the feature isn't already listed as unsupported
        for feature_id, affected_browsers in partial_map.items():
            if feature_id not in unsupported_map:
                baseline = self._analyzer_service.get_baseline_status(feature_id)
                issues.append({
                    'feature_name': self._analyzer_service.get_feature_display_name(feature_id),
                    'feature_id': feature_id,
                    'severity': 'warning',
                    'browsers': affected_browsers,
                    'fix_suggestion': self._analyzer_service.get_fix_suggestion(feature_id),
                    'baseline_status': baseline.get('status') if baseline else None,
                })

        return issues

    def _get_polyfill_recommendations(self, browsers: Dict) -> dict:
        if not browsers:
            return {'has_recommendations': False}

        unsupported = set()
        partial = set()
        browser_versions = {}

        for browser_name, data in browsers.items():
            browser_versions[browser_name] = data.get('version', '')
            unsupported.update(data.get('unsupported_features', []))
            partial.update(data.get('partial_features', []))

        recommendations = self._analyzer_service.get_polyfill_recommendations(
            list(unsupported), list(partial), browser_versions)

        if not recommendations:
            return {'has_recommendations': False}

        categorized = self._analyzer_service.categorize_polyfill_recommendations(recommendations)
        npm_recs = categorized['npm']
        css_recs = categorized['fallback']

        return {
            'has_recommendations': True,
            'count': len(recommendations),
            'install_command': self._analyzer_service.get_polyfill_install_command(recommendations),
            'imports': self._analyzer_service.get_polyfill_imports(recommendations),
            'npm': npm_recs,
            'css': css_recs,
            'total_size_kb': self._analyzer_service.get_polyfill_total_size_kb(recommendations),
        }

    def _get_ai_fix_suggestions(self, browsers: Dict) -> dict:
        if not browsers:
            return {'has_suggestions': False, 'count': 0, 'suggestions': []}

        unsupported = set()
        partial = set()
        browser_versions = {}

        for browser_name, data in browsers.items():
            browser_versions[browser_name] = data.get('version', '')
            unsupported.update(data.get('unsupported_features', []))
            partial.update(data.get('partial_features', []))

        if not unsupported and not partial:
            return {'has_suggestions': False, 'count': 0, 'suggestions': []}

        ai_key = self._analyzer_service.get_setting('ai_api_key', '')
        ai_provider = self._analyzer_service.get_setting('ai_provider', 'anthropic')

        suggestions = self._analyzer_service.get_ai_fix_suggestions(
            unsupported_features=list(unsupported),
            partial_features=list(partial),
            file_type='css',  # default; could detect from last analysis
            browsers=browser_versions,
            api_key=ai_key,
            provider=ai_provider,
        )

        return {
            'has_suggestions': bool(suggestions),
            'count': len(suggestions),
            'suggestions': suggestions,
        }

    def _on_ai_suggestions_click(self, browsers: Dict, scroll_frame):
        import threading

        for w in self._ai_placeholder.winfo_children():
            w.destroy()

        loading_frame = ctk.CTkFrame(self._ai_placeholder, fg_color="transparent")
        loading_frame.pack(fill="x")

        loading_label = ctk.CTkLabel(
            loading_frame,
            text="Generating AI suggestions...",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
        )
        loading_label.pack(side="left")

        # Animate dots while waiting
        self._ai_loading = True
        dot_count = [0]

        def animate_dots():
            if not self._ai_loading:
                return
            dot_count[0] = (dot_count[0] % 3) + 1
            try:
                loading_label.configure(text="Generating AI suggestions" + "." * dot_count[0])
                self.after(500, animate_dots)
            except Exception:
                pass

        animate_dots()

        def fetch():
            ai_data = self._get_ai_fix_suggestions(browsers)
            # Schedule UI update back on main thread
            self.after(0, lambda: self._show_ai_results(ai_data))

        threading.Thread(target=fetch, daemon=True).start()

    def _show_ai_results(self, ai_data: dict):
        self._ai_loading = False

        for w in self._ai_placeholder.winfo_children():
            w.destroy()

        if ai_data['has_suggestions']:
            ai_section = CollapsibleSection(
                self._ai_placeholder,
                title="AI Fix Suggestions",
                badge_text=str(ai_data['count']),
                badge_color=COLORS['accent'],
                expanded=True,
            )
            ai_section.pack(fill="x")
            ai_card = AIFixCard(ai_section.get_content_frame(), suggestions=ai_data['suggestions'])
            ai_card.pack(fill="x")
        else:
            ctk.CTkLabel(
                self._ai_placeholder,
                text="Could not generate suggestions. Check your API key and internet connection, then try again.",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_muted'],
            ).pack(anchor="w")

    def _generate_polyfills_file(self, filename: str):
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


    def _build_settings_view(self):
        container = ctk.CTkScrollableFrame(
            self.content_frame, fg_color="transparent",
            scrollbar_button_color=COLORS['bg_light'],
            scrollbar_button_hover_color=COLORS['accent'],
        )
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])

        ctk.CTkLabel(
            container,
            text="Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, SPACING['xl']))

        self._build_settings_database_section(container)
        self._build_settings_rules_section(container)
        self._build_settings_ai_section(container)
        self._build_settings_preferences_section(container)
        self._build_settings_about_section(container)

    def _build_settings_database_section(self, container):
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

    def _build_settings_rules_section(self, container):
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

    def _build_settings_ai_section(self, container):
        OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        ANTHROPIC_MODELS = ["claude-sonnet-4-20250514", "claude-haiku-4-5-20251001", "claude-opus-4-20250514"]

        ai_section = ctk.CTkFrame(
            container, fg_color=COLORS['bg_medium'], corner_radius=8,
            border_width=1, border_color=COLORS['border'],
        )
        ai_section.pack(fill="x", pady=(0, SPACING['lg']))

        ai_inner = ctk.CTkFrame(ai_section, fg_color="transparent")
        ai_inner.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])

        ctk.CTkLabel(
            ai_inner, text="AI Fix Suggestions",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS['text_primary'],
        ).pack(anchor="w", pady=(0, SPACING['xs']))

        ctk.CTkLabel(
            ai_inner, text="Configure AI-powered code fix suggestions for unsupported browser features",
            font=ctk.CTkFont(size=11), text_color=COLORS['text_muted'],
        ).pack(anchor="w", pady=(0, SPACING['md']))

        lbl_width = 100

        def make_row(parent):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=(0, SPACING['sm']))
            return row

        r = make_row(ai_inner)
        ctk.CTkLabel(r, text="API Key", font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary'], width=lbl_width).pack(side="left")
        current_key = self._analyzer_service.get_setting('ai_api_key', '')
        self._ai_key_var = ctk.StringVar(value=current_key)
        ctk.CTkEntry(r, textvariable=self._ai_key_var, show="*", placeholder_text="sk-...", height=30).pack(side="left", fill="x", expand=True, padx=(SPACING['sm'], 0))

        r = make_row(ai_inner)
        ctk.CTkLabel(r, text="Provider", font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary'], width=lbl_width).pack(side="left")
        current_provider = self._analyzer_service.get_setting('ai_provider', 'anthropic')
        self._ai_provider_var = ctk.StringVar(value=current_provider)

        model_r = make_row(ai_inner)
        ctk.CTkLabel(model_r, text="Model", font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary'], width=lbl_width).pack(side="left")
        current_model = self._analyzer_service.get_setting('ai_model', '')
        models_for_provider = OPENAI_MODELS if current_provider == "openai" else ANTHROPIC_MODELS
        self._ai_model_var = ctk.StringVar(value=current_model if current_model else models_for_provider[0])
        self._model_menu = ctk.CTkOptionMenu(
            model_r, values=models_for_provider, variable=self._ai_model_var,
            width=250, height=30, fg_color=COLORS['bg_light'],
            button_color=COLORS['bg_light'], button_hover_color=COLORS['hover_bg'],
        )
        self._model_menu.pack(side="left", padx=(SPACING['sm'], 0))

        def on_provider_change(val):
            new_models = OPENAI_MODELS if val == "openai" else ANTHROPIC_MODELS
            self._model_menu.configure(values=new_models)
            self._ai_model_var.set(new_models[0])

        ctk.CTkOptionMenu(
            r, values=["anthropic", "openai"], variable=self._ai_provider_var,
            width=140, height=30, fg_color=COLORS['bg_light'],
            button_color=COLORS['bg_light'], button_hover_color=COLORS['hover_bg'],
            command=on_provider_change,
        ).pack(side="left", padx=(SPACING['sm'], 0))

        r = make_row(ai_inner)
        ctk.CTkLabel(r, text="Max Features", font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary'], width=lbl_width).pack(side="left")
        current_limit = self._analyzer_service.get_setting('ai_max_features', '10')
        limit_display = "All" if current_limit == "0" else current_limit
        self._ai_limit_var = ctk.StringVar(value=limit_display)
        ctk.CTkOptionMenu(
            r, values=["5", "10", "15", "20", "All"], variable=self._ai_limit_var,
            width=100, height=30, fg_color=COLORS['bg_light'],
            button_color=COLORS['bg_light'], button_hover_color=COLORS['hover_bg'],
        ).pack(side="left", padx=(SPACING['sm'], 0))
        ctk.CTkLabel(r, text="features sent per API request", font=ctk.CTkFont(size=9), text_color=COLORS['text_muted']).pack(side="left", padx=(SPACING['sm'], 0))

        r = make_row(ai_inner)
        ctk.CTkLabel(r, text="Priority", font=ctk.CTkFont(size=11), text_color=COLORS['text_secondary'], width=lbl_width).pack(side="left")
        current_priority = self._analyzer_service.get_setting('ai_priority', 'unsupported_first')
        self._ai_priority_var = ctk.StringVar(value=current_priority)
        ctk.CTkOptionMenu(
            r, values=["unsupported_first", "all_equal"], variable=self._ai_priority_var,
            width=170, height=30, fg_color=COLORS['bg_light'],
            button_color=COLORS['bg_light'], button_hover_color=COLORS['hover_bg'],
        ).pack(side="left", padx=(SPACING['sm'], 0))
        ctk.CTkLabel(r, text="which features to send first", font=ctk.CTkFont(size=9), text_color=COLORS['text_muted']).pack(side="left", padx=(SPACING['sm'], 0))

        btn_row = ctk.CTkFrame(ai_inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(SPACING['sm'], 0))

        def save_all_ai():
            self._analyzer_service.set_setting('ai_api_key', self._ai_key_var.get().strip())
            self._analyzer_service.set_setting('ai_provider', self._ai_provider_var.get())
            self._analyzer_service.set_setting('ai_model', self._ai_model_var.get())
            limit_val = self._ai_limit_var.get()
            self._analyzer_service.set_setting('ai_max_features', '0' if limit_val == 'All' else limit_val)
            self._analyzer_service.set_setting('ai_priority', self._ai_priority_var.get())
            show_info(self, "Saved", "AI settings saved successfully.")

        ctk.CTkButton(
            btn_row, text="Save Settings", width=120, height=32,
            fg_color=COLORS['accent'], hover_color=COLORS['accent_dim'],
            font=ctk.CTkFont(size=11),
            command=save_all_ai,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="Clear API Key", width=110, height=32,
            fg_color=COLORS['bg_light'], hover_color=COLORS['hover_bg'],
            text_color=COLORS['text_muted'], font=ctk.CTkFont(size=11),
            command=lambda e=None: [self._ai_key_var.set(""), self._analyzer_service.set_setting('ai_api_key', ''), show_info(self, "Cleared", "API key removed.")],
        ).pack(side="left", padx=(SPACING['sm'], 0))

    def _build_settings_preferences_section(self, container):
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

    def _build_settings_about_section(self, container):
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
