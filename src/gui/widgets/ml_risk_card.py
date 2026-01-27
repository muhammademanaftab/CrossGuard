"""
ML Risk Assessment Card widget for displaying ML-based compatibility predictions.
Shows risk level, confidence, and contributing factors from the ML module.
"""

from typing import List, Optional, Dict, Any

import customtkinter as ctk

from ..theme import COLORS, SPACING


# Risk level colors
RISK_COLORS = {
    'low': COLORS.get('success', '#22c55e'),
    'medium': COLORS.get('warning', '#f59e0b'),
    'high': COLORS.get('danger', '#ef4444'),
}

# Risk level icons
RISK_ICONS = {
    'low': '\u2713',     # Checkmark
    'medium': '\u26A0',  # Warning
    'high': '\u2717',    # X mark
}


class MLRiskCard(ctk.CTkFrame):
    """Card displaying ML-based risk assessment for detected features.

    Shows:
    - Overall ML risk prediction
    - Confidence score
    - Top contributing factors
    - Feature importance insights
    """

    def __init__(
        self,
        master,
        title: str = "ML Risk Assessment",
        **kwargs
    ):
        """Initialize the ML risk card.

        Args:
            master: Parent widget
            title: Card title
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            master,
            fg_color=COLORS.get('bg_medium', '#1e293b'),
            corner_radius=8,
            border_width=1,
            border_color=COLORS.get('border', '#334155'),
            **kwargs
        )

        self._title = title
        self._risk_data: Dict[str, Any] = {}

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING.get('lg', 16), pady=(SPACING.get('lg', 16), SPACING.get('sm', 8)))

        # ML badge
        ml_badge = ctk.CTkLabel(
            header_frame,
            text=" ML ",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS.get('text_primary', '#f1f5f9'),
            fg_color=COLORS.get('accent', '#3b82f6'),
            corner_radius=4,
        )
        ml_badge.pack(side="left")

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=self._title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS.get('text_primary', '#f1f5f9'),
        )
        title_label.pack(side="left", padx=(SPACING.get('sm', 8), 0))

        # Status indicator (will be updated with risk level)
        self.status_indicator = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get('text_muted', '#94a3b8'),
        )
        self.status_indicator.pack(side="right")

        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=SPACING.get('lg', 16), pady=(0, SPACING.get('lg', 16)))

        # Risk summary row
        self.summary_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.summary_frame.pack(fill="x", pady=(0, SPACING.get('md', 12)))

        # Risk level indicator
        self.risk_level_frame = ctk.CTkFrame(
            self.summary_frame,
            fg_color=COLORS.get('bg_light', '#334155'),
            corner_radius=6,
        )
        self.risk_level_frame.pack(side="left", padx=(0, SPACING.get('md', 12)))

        self.risk_icon = ctk.CTkLabel(
            self.risk_level_frame,
            text="?",
            font=ctk.CTkFont(size=16),
            text_color=COLORS.get('text_muted', '#94a3b8'),
            width=32,
            height=32,
        )
        self.risk_icon.pack(side="left", padx=SPACING.get('xs', 4))

        self.risk_label = ctk.CTkLabel(
            self.risk_level_frame,
            text="No Data",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS.get('text_muted', '#94a3b8'),
        )
        self.risk_label.pack(side="left", padx=(0, SPACING.get('sm', 8)), pady=SPACING.get('xs', 4))

        # Confidence meter
        confidence_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        confidence_frame.pack(side="left", fill="x", expand=True)

        conf_label = ctk.CTkLabel(
            confidence_frame,
            text="Confidence:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get('text_secondary', '#cbd5e1'),
        )
        conf_label.pack(anchor="w")

        self.confidence_bar = ctk.CTkProgressBar(
            confidence_frame,
            height=6,
            corner_radius=3,
            fg_color=COLORS.get('bg_light', '#334155'),
            progress_color=COLORS.get('accent', '#3b82f6'),
        )
        self.confidence_bar.pack(fill="x", pady=(2, 0))
        self.confidence_bar.set(0)

        self.confidence_label = ctk.CTkLabel(
            confidence_frame,
            text="0%",
            font=ctk.CTkFont(size=10),
            text_color=COLORS.get('text_muted', '#94a3b8'),
        )
        self.confidence_label.pack(anchor="e")

        # Factors list
        factors_header = ctk.CTkLabel(
            self.content_frame,
            text="Contributing Factors:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS.get('text_secondary', '#cbd5e1'),
        )
        factors_header.pack(anchor="w", pady=(SPACING.get('sm', 8), SPACING.get('xs', 4)))

        self.factors_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS.get('bg_light', '#334155'),
            corner_radius=6,
        )
        self.factors_frame.pack(fill="x")

        # Placeholder for factors
        self.factors_placeholder = ctk.CTkLabel(
            self.factors_frame,
            text="Analyze files to see ML risk factors",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get('text_muted', '#94a3b8'),
        )
        self.factors_placeholder.pack(padx=SPACING.get('sm', 8), pady=SPACING.get('sm', 8))

    def set_risk_data(
        self,
        risk_level: str,
        confidence: float,
        factors: List[str],
        high_risk_count: int = 0,
        total_features: int = 0,
    ):
        """Update the risk assessment display.

        Args:
            risk_level: Risk level ('low', 'medium', 'high')
            confidence: Confidence score (0.0 - 1.0)
            factors: List of contributing factor strings
            high_risk_count: Number of high-risk features
            total_features: Total features analyzed
        """
        # Update risk level display
        risk_level = risk_level.lower()
        color = RISK_COLORS.get(risk_level, COLORS.get('text_muted', '#94a3b8'))
        icon = RISK_ICONS.get(risk_level, '?')

        self.risk_icon.configure(text=icon, text_color=color)
        self.risk_label.configure(
            text=risk_level.upper() + " RISK",
            text_color=color
        )
        self.risk_level_frame.configure(border_width=1, border_color=color)

        # Update status indicator
        if total_features > 0:
            self.status_indicator.configure(
                text=f"{high_risk_count}/{total_features} features flagged"
            )

        # Update confidence
        self.confidence_bar.set(confidence)
        self.confidence_label.configure(text=f"{confidence * 100:.0f}%")

        # Update factors
        for widget in self.factors_frame.winfo_children():
            widget.destroy()

        if factors:
            for i, factor in enumerate(factors[:5]):  # Show top 5 factors
                factor_row = ctk.CTkFrame(self.factors_frame, fg_color="transparent")
                factor_row.pack(fill="x", padx=SPACING.get('sm', 8), pady=(SPACING.get('xs', 4) if i == 0 else 0, SPACING.get('xs', 4)))

                bullet = ctk.CTkLabel(
                    factor_row,
                    text="\u2022",
                    font=ctk.CTkFont(size=11),
                    text_color=color,
                    width=12,
                )
                bullet.pack(side="left")

                factor_label = ctk.CTkLabel(
                    factor_row,
                    text=factor,
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS.get('text_secondary', '#cbd5e1'),
                    anchor="w",
                    wraplength=300,
                )
                factor_label.pack(side="left", fill="x", expand=True)
        else:
            no_factors = ctk.CTkLabel(
                self.factors_frame,
                text="No significant risk factors detected",
                font=ctk.CTkFont(size=11),
                text_color=COLORS.get('text_muted', '#94a3b8'),
            )
            no_factors.pack(padx=SPACING.get('sm', 8), pady=SPACING.get('sm', 8))

    def set_loading(self, loading: bool = True):
        """Show loading state.

        Args:
            loading: Whether to show loading state
        """
        if loading:
            self.risk_icon.configure(text="\u23F3")  # Hourglass
            self.risk_label.configure(text="Analyzing...")
            self.status_indicator.configure(text="Processing")
        else:
            self.status_indicator.configure(text="")

    def set_error(self, error_message: str):
        """Show error state.

        Args:
            error_message: Error message to display
        """
        self.risk_icon.configure(text="\u26A0", text_color=COLORS.get('warning', '#f59e0b'))
        self.risk_label.configure(text="ML Unavailable", text_color=COLORS.get('warning', '#f59e0b'))
        self.status_indicator.configure(text="Using rule-based analysis")

        for widget in self.factors_frame.winfo_children():
            widget.destroy()

        error_label = ctk.CTkLabel(
            self.factors_frame,
            text=error_message,
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get('text_muted', '#94a3b8'),
            wraplength=280,
        )
        error_label.pack(padx=SPACING.get('sm', 8), pady=SPACING.get('sm', 8))


class MLFeatureImportanceCard(ctk.CTkFrame):
    """Card displaying top feature importance from ML model.

    Shows which characteristics most strongly predict compatibility risk.
    """

    def __init__(self, master, **kwargs):
        """Initialize the feature importance card.

        Args:
            master: Parent widget
            **kwargs: Additional arguments
        """
        super().__init__(
            master,
            fg_color=COLORS.get('bg_medium', '#1e293b'),
            corner_radius=8,
            border_width=1,
            border_color=COLORS.get('border', '#334155'),
            **kwargs
        )

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING.get('lg', 16), pady=(SPACING.get('lg', 16), SPACING.get('sm', 8)))

        ctk.CTkLabel(
            header_frame,
            text="Feature Importance",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS.get('text_primary', '#f1f5f9'),
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text="What predicts risk?",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get('text_muted', '#94a3b8'),
        ).pack(side="right")

        # Content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=SPACING.get('lg', 16), pady=(0, SPACING.get('lg', 16)))

        # Placeholder
        self.placeholder = ctk.CTkLabel(
            self.content_frame,
            text="Train ML model to see feature importance",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get('text_muted', '#94a3b8'),
        )
        self.placeholder.pack(pady=SPACING.get('md', 12))

    def set_importances(self, importances: List[tuple]):
        """Update feature importance display.

        Args:
            importances: List of (feature_name, importance) tuples
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if not importances:
            ctk.CTkLabel(
                self.content_frame,
                text="No importance data available",
                font=ctk.CTkFont(size=11),
                text_color=COLORS.get('text_muted', '#94a3b8'),
            ).pack(pady=SPACING.get('md', 12))
            return

        # Show top features with bars
        max_importance = max(imp for _, imp in importances[:5]) if importances else 1

        for name, importance in importances[:5]:
            row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            row.pack(fill="x", pady=(0, SPACING.get('xs', 4)))

            # Feature name (formatted)
            display_name = name.replace('_', ' ').title()
            if len(display_name) > 18:
                display_name = display_name[:16] + "..."

            name_label = ctk.CTkLabel(
                row,
                text=display_name,
                font=ctk.CTkFont(size=10),
                text_color=COLORS.get('text_secondary', '#cbd5e1'),
                width=120,
                anchor="w",
            )
            name_label.pack(side="left")

            # Importance bar
            bar_frame = ctk.CTkFrame(
                row,
                fg_color=COLORS.get('bg_light', '#334155'),
                height=8,
                corner_radius=4,
            )
            bar_frame.pack(side="left", fill="x", expand=True, padx=(SPACING.get('xs', 4), 0))
            bar_frame.pack_propagate(False)

            bar_width = (importance / max_importance) if max_importance > 0 else 0
            bar = ctk.CTkFrame(
                bar_frame,
                fg_color=COLORS.get('accent', '#3b82f6'),
                corner_radius=4,
            )
            bar.place(relx=0, rely=0, relwidth=bar_width, relheight=1)

            # Value
            val_label = ctk.CTkLabel(
                row,
                text=f"{importance:.3f}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS.get('text_muted', '#94a3b8'),
                width=45,
            )
            val_label.pack(side="right")
