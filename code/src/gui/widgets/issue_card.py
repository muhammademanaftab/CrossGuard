"""Compact issue cards with colored left border, browser badges, and optional fix suggestion."""

from typing import List, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING


class IssueCard(ctk.CTkFrame):

    BASELINE_COLORS = {
        'high': (COLORS['success'], 'Widely Available'),
        'low': (COLORS['accent'], 'Newly Available'),
        'limited': (COLORS['warning'], 'Limited'),
    }

    def __init__(
        self,
        master,
        feature_name: str,
        feature_id: str,
        severity: str,
        browsers: List[str],
        fix_suggestion: Optional[str] = None,
        baseline_status: Optional[str] = None,
        **kwargs
    ):
        border_color = COLORS['danger'] if severity == 'critical' else COLORS['warning']

        super().__init__(
            master, fg_color=COLORS['bg_dark'], corner_radius=0,
            border_width=0, **kwargs
        )

        # Colored left border spans the full card height
        ctk.CTkFrame(
            self, fg_color=border_color, width=3, corner_radius=0
        ).place(x=0, y=0, relheight=1)

        # Top row — feature name + browser badges + baseline pill
        top = ctk.CTkFrame(self, fg_color="transparent", height=32)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        ctk.CTkLabel(
            top, text=feature_name,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left", padx=(12, 0))

        right = ctk.CTkFrame(top, fg_color="transparent")
        right.pack(side="right", padx=8)

        for browser in reversed(browsers):
            ctk.CTkLabel(
                right,
                text=f" {browser} ",
                font=ctk.CTkFont(size=8),
                text_color=COLORS['text_muted'],
                fg_color=COLORS['bg_light'],
                corner_radius=3,
            ).pack(side="right", padx=(2, 0))

        if baseline_status and baseline_status in self.BASELINE_COLORS:
            badge_color, badge_text = self.BASELINE_COLORS[baseline_status]
            ctk.CTkLabel(
                right,
                text=f" {badge_text} ",
                font=ctk.CTkFont(size=8),
                text_color="#FFFFFF",
                fg_color=badge_color,
                corner_radius=3,
            ).pack(side="right", padx=(0, 4))

        # Fix suggestion row — only rendered when we actually have text to show
        if fix_suggestion:
            fix_row = ctk.CTkFrame(self, fg_color="transparent")
            fix_row.pack(fill="x", side="top", padx=(12, 8), pady=(0, 6))
            ctk.CTkLabel(
                fix_row,
                text=f"Fix: {fix_suggestion}",
                font=ctk.CTkFont(size=10, slant="italic"),
                text_color=COLORS['text_muted'],
                wraplength=600,
                justify="left",
                anchor="w",
            ).pack(anchor="w", fill="x")


class IssuesSummary(ctk.CTkFrame):

    def __init__(self, master, issues: List[dict], expanded: bool = False, **kwargs):
        super().__init__(
            master, fg_color=COLORS['bg_medium'], corner_radius=8,
            border_width=1, border_color=COLORS['border'], **kwargs
        )

        self._issues = issues
        self._expanded = expanded
        self._init_ui()

    def _init_ui(self):
        critical = [i for i in self._issues if i.get('severity') == 'critical']
        warnings = [i for i in self._issues if i.get('severity') != 'critical']

        self._header = ctk.CTkFrame(self, fg_color="transparent", cursor="hand2")
        self._header.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])

        self._toggle = ctk.CTkLabel(
            self._header,
            text="▼" if self._expanded else "▶",
            font=ctk.CTkFont(size=9),
            text_color=COLORS['text_muted'],
            width=14,
        )
        self._toggle.pack(side="left", padx=(0, SPACING['xs']))

        ctk.CTkLabel(
            self._header,
            text="WHAT NEEDS YOUR ATTENTION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left")

        if critical:
            ctk.CTkLabel(
                self._header,
                text=f" {len(critical)} critical ",
                font=ctk.CTkFont(size=9),
                text_color=COLORS['text_primary'],
                fg_color=COLORS['danger'],
                corner_radius=4,
            ).pack(side="left", padx=(SPACING['sm'], 0))

        if warnings:
            ctk.CTkLabel(
                self._header,
                text=f" {len(warnings)} warning ",
                font=ctk.CTkFont(size=9),
                text_color=COLORS['text_primary'],
                fg_color=COLORS['warning'],
                corner_radius=4,
            ).pack(side="left", padx=(SPACING['xs'], 0))

        self._hint = ctk.CTkLabel(
            self._header,
            text="Click to view" if not self._expanded else "Collapse",
            font=ctk.CTkFont(size=9),
            text_color=COLORS['text_muted'],
        )
        self._hint.pack(side="right")

        self._header.bind("<Button-1>", lambda e=None: self._toggle_view())
        for child in self._header.winfo_children():
            child.bind("<Button-1>", lambda e=None: self._toggle_view())

        self._container = ctk.CTkFrame(self, fg_color="transparent")

        sorted_issues = sorted(self._issues, key=lambda i: 0 if i.get('severity') == 'critical' else 1)

        for issue in sorted_issues:
            card = IssueCard(
                self._container,
                feature_name=issue.get('feature_name', ''),
                feature_id=issue.get('feature_id', ''),
                severity=issue.get('severity', 'warning'),
                browsers=issue.get('browsers', []),
                fix_suggestion=issue.get('fix_suggestion'),
                baseline_status=issue.get('baseline_status'),
            )
            card.pack(fill="x", pady=(0, 1))

        if self._expanded:
            self._container.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))

    def _toggle_view(self):
        self._expanded = not self._expanded
        if self._expanded:
            self._container.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
            self._toggle.configure(text="▼")
            self._hint.configure(text="Collapse")
        else:
            self._container.pack_forget()
            self._toggle.configure(text="▶")
            self._hint.configure(text="Click to view")
