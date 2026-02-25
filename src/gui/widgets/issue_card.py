"""Issue cards showing compatibility problems in plain English."""

from typing import List, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING, ICONS


class IssueCard(ctk.CTkFrame):
    """Single compatibility issue with severity, affected browsers, and fix suggestion."""

    def __init__(
        self,
        master,
        feature_name: str,
        feature_id: str,
        severity: str,  # 'critical' or 'warning'
        browsers: List[str],
        fix_suggestion: Optional[str] = None,
        **kwargs
    ):
        if severity == 'critical':
            bg_color = COLORS['danger_muted']
            border_color = COLORS['danger']
            icon = ICONS['error']
            icon_color = COLORS['danger']
            status_text = "won't work in"
        else:
            bg_color = COLORS['warning_muted']
            border_color = COLORS['warning']
            icon = ICONS['warning']
            icon_color = COLORS['warning']
            status_text = "has limited support in"

        super().__init__(
            master,
            fg_color=bg_color,
            corner_radius=8,
            border_width=1,
            border_color=border_color,
            **kwargs
        )

        self._feature_name = feature_name
        self._feature_id = feature_id
        self._severity = severity
        self._browsers = browsers
        self._fix_suggestion = fix_suggestion
        self._icon = icon
        self._icon_color = icon_color
        self._status_text = status_text

        self._init_ui()

    def _init_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=SPACING['md'], pady=SPACING['md'])

        top_row = ctk.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x")

        icon_label = ctk.CTkLabel(
            top_row,
            text=self._icon,
            font=ctk.CTkFont(size=16),
            text_color=self._icon_color,
        )
        icon_label.pack(side="left", padx=(0, SPACING['sm']))

        # e.g. "CSS Grid won't work in Safari 15"
        browsers_text = self._format_browsers()
        message = f"{self._feature_name} {self._status_text} {browsers_text}"

        message_label = ctk.CTkLabel(
            top_row,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_primary'],
            wraplength=600,
            justify="left",
        )
        message_label.pack(side="left", fill="x", expand=True)

        if self._fix_suggestion:
            suggestion_row = ctk.CTkFrame(container, fg_color="transparent")
            suggestion_row.pack(fill="x", pady=(SPACING['xs'], 0))

            arrow_label = ctk.CTkLabel(
                suggestion_row,
                text="\u203A",
                font=ctk.CTkFont(size=14),
                text_color=COLORS['text_muted'],
            )
            arrow_label.pack(side="left", padx=(SPACING['lg'], SPACING['xs']))

            suggestion_label = ctk.CTkLabel(
                suggestion_row,
                text=self._fix_suggestion,
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_muted'],
                wraplength=580,
                justify="left",
            )
            suggestion_label.pack(side="left", fill="x", expand=True)

    def _format_browsers(self) -> str:
        if not self._browsers:
            return "some browsers"

        if len(self._browsers) == 1:
            return self._browsers[0]
        elif len(self._browsers) == 2:
            return f"{self._browsers[0]} and {self._browsers[1]}"
        else:
            return f"{', '.join(self._browsers[:-1])}, and {self._browsers[-1]}"


class IssuesSummary(ctk.CTkFrame):
    """Collapsible container for issue cards, sorted by severity."""

    def __init__(
        self,
        master,
        issues: List[dict],
        expanded: bool = False,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS['bg_medium'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )

        self._issues = issues
        self._expanded = expanded
        self._init_ui()

    def _init_ui(self):
        critical_count = sum(1 for i in self._issues if i.get('severity') == 'critical')
        warning_count = len(self._issues) - critical_count

        self._header = ctk.CTkFrame(self, fg_color="transparent", cursor="hand2")
        self._header.pack(fill="x", padx=SPACING['lg'], pady=SPACING['md'])

        self._toggle_indicator = ctk.CTkLabel(
            self._header,
            text="▶" if not self._expanded else "▼",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted'],
            width=16,
        )
        self._toggle_indicator.pack(side="left", padx=(0, SPACING['xs']))

        title = ctk.CTkLabel(
            self._header,
            text="WHAT NEEDS YOUR ATTENTION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_primary'],
        )
        title.pack(side="left")

        if critical_count > 0:
            critical_badge = ctk.CTkLabel(
                self._header,
                text=f" {critical_count} critical ",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
                fg_color=COLORS['danger'],
                corner_radius=4,
            )
            critical_badge.pack(side="left", padx=(SPACING['sm'], 0))

        if warning_count > 0:
            warning_badge = ctk.CTkLabel(
                self._header,
                text=f" {warning_count} warning ",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
                fg_color=COLORS['warning'],
                corner_radius=4,
            )
            warning_badge.pack(side="left", padx=(SPACING['sm'], 0))

        self._hint_label = ctk.CTkLabel(
            self._header,
            text="Click to view" if not self._expanded else "",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted'],
        )
        self._hint_label.pack(side="right")

        # Make entire header clickable
        self._header.bind("<Button-1>", lambda e=None: self._toggle())
        for child in self._header.winfo_children():
            child.bind("<Button-1>", lambda e=None: self._toggle())

        self._issues_container = ctk.CTkFrame(self, fg_color="transparent")

        # Critical issues first, then warnings
        sorted_issues = sorted(
            self._issues,
            key=lambda x: (0 if x.get('severity') == 'critical' else 1, x.get('feature_name', ''))
        )

        for issue in sorted_issues:
            card = IssueCard(
                self._issues_container,
                feature_name=issue.get('feature_name', issue.get('feature_id', 'Unknown')),
                feature_id=issue.get('feature_id', ''),
                severity=issue.get('severity', 'warning'),
                browsers=issue.get('browsers', []),
                fix_suggestion=issue.get('fix_suggestion'),
            )
            card.pack(fill="x", pady=(0, SPACING['sm']))

        if self._expanded:
            self._issues_container.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))

    def _toggle(self):
        self._expanded = not self._expanded

        if self._expanded:
            self._toggle_indicator.configure(text="▼")
            self._hint_label.configure(text="")
            self._issues_container.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        else:
            self._toggle_indicator.configure(text="▶")
            self._hint_label.configure(text="Click to view")
            self._issues_container.pack_forget()

    def expand(self):
        if not self._expanded:
            self._toggle()

    def collapse(self):
        if self._expanded:
            self._toggle()

    def has_issues(self) -> bool:
        return len(self._issues) > 0
