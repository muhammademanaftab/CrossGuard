"""
BrowserCard widget for displaying browser compatibility with visual bar chart.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont
from typing import List, Optional


class StackedBarWidget(QWidget):
    """Horizontal stacked bar showing support breakdown."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._supported = 0
        self._partial = 0
        self._unsupported = 0
        self._total = 0
        self._animation_progress = 0.0
        self._animation = None
        self.setMinimumHeight(20)
        self.setMaximumHeight(20)

    def set_values(self, supported: int, partial: int, unsupported: int, animate: bool = True):
        """Set the bar values."""
        self._supported = supported
        self._partial = partial
        self._unsupported = unsupported
        self._total = supported + partial + unsupported

        if animate and self._total > 0:
            self._animate_fill()
        else:
            self._animation_progress = 1.0
            self.update()

    def get_animation_progress(self) -> float:
        return self._animation_progress

    def set_animation_progress(self, value: float):
        self._animation_progress = value
        self.update()

    animation_progress = pyqtProperty(float, get_animation_progress, set_animation_progress)

    def _animate_fill(self):
        """Animate the bar filling."""
        if self._animation:
            self._animation.stop()

        self._animation_progress = 0.0
        self._animation = QPropertyAnimation(self, b"animation_progress")
        self._animation.setDuration(600)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()

    def paintEvent(self, event):
        """Paint the stacked bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        radius = 4

        # Draw background
        painter.setBrush(QColor("#e0e0e0"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, width, height, radius, radius)

        if self._total == 0:
            return

        # Calculate widths with animation
        animated_width = width * self._animation_progress
        supported_width = (self._supported / self._total) * animated_width
        partial_width = (self._partial / self._total) * animated_width
        unsupported_width = (self._unsupported / self._total) * animated_width

        x = 0

        # Draw supported (green)
        if supported_width > 0:
            painter.setBrush(QColor("#4CAF50"))
            rect = QRectF(x, 0, supported_width, height)
            if x == 0:
                painter.drawRoundedRect(rect, radius, radius)
            else:
                painter.drawRect(rect)
            x += supported_width

        # Draw partial (orange)
        if partial_width > 0:
            painter.setBrush(QColor("#FF9800"))
            painter.drawRect(QRectF(x, 0, partial_width, height))
            x += partial_width

        # Draw unsupported (red)
        if unsupported_width > 0:
            painter.setBrush(QColor("#F44336"))
            rect = QRectF(x, 0, unsupported_width, height)
            if x + unsupported_width >= animated_width - 1:
                painter.drawRoundedRect(rect, radius, radius)
            else:
                painter.drawRect(rect)


class BrowserCard(QFrame):
    """Card displaying browser compatibility with mini bar chart."""

    def __init__(self, browser_name: str, version: str,
                 supported: int, partial: int, unsupported: int,
                 compatibility_pct: float,
                 unsupported_features: Optional[List[str]] = None,
                 partial_features: Optional[List[str]] = None,
                 parent=None):
        """
        Initialize the browser card.

        Args:
            browser_name: Name of the browser
            version: Browser version
            supported: Number of supported features
            partial: Number of partially supported features
            unsupported: Number of unsupported features
            compatibility_pct: Compatibility percentage
            unsupported_features: List of unsupported feature names
            partial_features: List of partially supported feature names
            parent: Parent widget
        """
        super().__init__(parent)
        self.browser_name = browser_name
        self.version = version
        self.supported = supported
        self.partial = partial
        self.unsupported = unsupported
        self.compatibility_pct = compatibility_pct
        self.unsupported_features = unsupported_features or []
        self.partial_features = partial_features or []
        self._details_visible = False
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setObjectName("enhancedBrowserCard")
        self.setStyleSheet("""
            QFrame#enhancedBrowserCard {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QFrame#enhancedBrowserCard:hover {
                border-color: #2196F3;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 10, 12, 10)

        # Header row
        header = QHBoxLayout()

        # Browser name and version
        name_label = QLabel(f"{self.browser_name.upper()} {self.version}")
        name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        header.addWidget(name_label)

        header.addStretch()

        # Compatibility percentage
        pct_label = QLabel(f"{self.compatibility_pct:.1f}%")
        color = self._get_color_for_score(self.compatibility_pct)
        pct_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")
        header.addWidget(pct_label)

        layout.addLayout(header)

        # Stacked bar chart
        self.bar_widget = StackedBarWidget()
        self.bar_widget.set_values(self.supported, self.partial, self.unsupported)
        layout.addWidget(self.bar_widget)

        # Stats row
        stats = QHBoxLayout()
        stats.setSpacing(16)

        supported_label = QLabel(f"Supported: {self.supported}")
        supported_label.setStyleSheet("font-size: 12px; color: #4CAF50; font-weight: bold;")
        stats.addWidget(supported_label)

        partial_label = QLabel(f"Partial: {self.partial}")
        partial_label.setStyleSheet("font-size: 12px; color: #FF9800; font-weight: bold;")
        stats.addWidget(partial_label)

        unsupported_label = QLabel(f"Unsupported: {self.unsupported}")
        unsupported_label.setStyleSheet("font-size: 12px; color: #F44336; font-weight: bold;")
        stats.addWidget(unsupported_label)

        stats.addStretch()

        # Toggle details button (only if there are issues)
        if self.unsupported_features or self.partial_features:
            self.toggle_btn = QPushButton("Show Details")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    color: #666;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                    border-color: #2196F3;
                    color: #2196F3;
                }
            """)
            self.toggle_btn.clicked.connect(self._toggle_details)
            stats.addWidget(self.toggle_btn)

        layout.addLayout(stats)

        # Details section (hidden by default)
        self.details_widget = QWidget()
        self.details_widget.setVisible(False)
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(0, 8, 0, 0)
        details_layout.setSpacing(4)

        if self.unsupported_features:
            unsup_text = QLabel(f"Not supported: {', '.join(self.unsupported_features[:8])}")
            if len(self.unsupported_features) > 8:
                unsup_text.setText(unsup_text.text() + f" (+{len(self.unsupported_features) - 8} more)")
            unsup_text.setWordWrap(True)
            unsup_text.setStyleSheet("font-size: 11px; color: #d32f2f; background-color: #ffebee; padding: 6px; border-radius: 4px;")
            details_layout.addWidget(unsup_text)

        if self.partial_features:
            part_text = QLabel(f"Partial support: {', '.join(self.partial_features[:8])}")
            if len(self.partial_features) > 8:
                part_text.setText(part_text.text() + f" (+{len(self.partial_features) - 8} more)")
            part_text.setWordWrap(True)
            part_text.setStyleSheet("font-size: 11px; color: #e65100; background-color: #fff3e0; padding: 6px; border-radius: 4px;")
            details_layout.addWidget(part_text)

        layout.addWidget(self.details_widget)

    def _get_color_for_score(self, score: float) -> str:
        """Get color hex based on score."""
        if score >= 90:
            return "#4CAF50"
        elif score >= 70:
            return "#8BC34A"
        elif score >= 50:
            return "#FF9800"
        else:
            return "#F44336"

    def _toggle_details(self):
        """Toggle the details section visibility."""
        self._details_visible = not self._details_visible
        self.details_widget.setVisible(self._details_visible)
        self.toggle_btn.setText("Hide Details" if self._details_visible else "Show Details")
