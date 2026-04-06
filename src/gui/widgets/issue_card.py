"""Issue cards showing compatibility problems."""

from typing import List, Optional
import customtkinter as ctk

from ..theme import COLORS, SPACING


class IssueCard(ctk.CTkFrame):
    """Compact issue row with colored left border, feature name, and browser pills."""

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
        super().__init__(master, fg_color=COLORS['bg_dark'], corner_radius=4,
                         height=36, **kwargs)
        self.pack_propagate(False)

        border_color = COLORS['danger'] if severity == 'critical' else COLORS['warning']

        # Colored left strip
        ctk.CTkFrame(self, fg_color=border_color, width=4, corner_radius=0).pack(
            side="left", fill="y"
        )

        # Feature name
        ctk.CTkLabel(
            self, text=feature_name,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_primary'],
        ).pack(side="left", padx=(SPACING['sm'], 0))

        # Browser pills (right side)
        for browser in reversed(browsers):
            ctk.CTkLabel(
                self,
                text=f" {browser} ",
                font=ctk.CTkFont(size=9),
                text_color=COLORS['text_muted'],
                fg_color=COLORS['bg_light'],
                corner_radius=3,
                height=20,
            ).pack(side="right", padx=(0, 3))


class IssuesSummary(ctk.CTkFrame):
    """Compact list of issue rows, sorted by severity."""

    def __init__(self, master, issues: List[dict], expanded: bool = False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._issues = issues
        self._init_ui()

    def _init_ui(self):
        sorted_issues = sorted(
            self._issues,
            key=lambda x: (0 if x.get('severity') == 'critical' else 1, x.get('feature_name', ''))
        )

        critical = [i for i in sorted_issues if i.get('severity') == 'critical']
        warnings = [i for i in sorted_issues if i.get('severity') != 'critical']

        for issue in critical:
            IssueCard(
                self,
                feature_name=issue.get('feature_name', issue.get('feature_id', 'Unknown')),
                feature_id=issue.get('feature_id', ''),
                severity='critical',
                browsers=issue.get('browsers', []),
            ).pack(fill="x", pady=(0, 2))

        if critical and warnings:
            ctk.CTkFrame(self, fg_color=COLORS['border'], height=1).pack(
                fill="x", pady=SPACING['xs']
            )

        for issue in warnings:
            IssueCard(
                self,
                feature_name=issue.get('feature_name', issue.get('feature_id', 'Unknown')),
                feature_id=issue.get('feature_id', ''),
                severity='warning',
                browsers=issue.get('browsers', []),
            ).pack(fill="x", pady=(0, 2))

    def has_issues(self) -> bool:
        return len(self._issues) > 0
