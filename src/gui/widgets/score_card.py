"""
ScoreCard widget for displaying compatibility scores with circular progress.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class CircularProgress(QWidget):
    """Circular progress indicator with animated fill."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self._animation = None
        self.setMinimumSize(120, 120)
        self.setMaximumSize(120, 120)

    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, value: float):
        self._progress = max(0.0, min(100.0, value))
        self.update()

    progress = pyqtProperty(float, get_progress, set_progress)

    def animate_to(self, target_value: float, duration: int = 800):
        """Animate the progress to a target value."""
        if self._animation:
            self._animation.stop()

        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(target_value)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()

    def _get_color_for_score(self, score: float) -> QColor:
        """Get color based on score (red -> yellow -> green gradient)."""
        if score >= 90:
            return QColor("#4CAF50")  # Green
        elif score >= 70:
            return QColor("#8BC34A")  # Light green
        elif score >= 50:
            return QColor("#FF9800")  # Orange
        elif score >= 30:
            return QColor("#FF5722")  # Deep orange
        else:
            return QColor("#F44336")  # Red

    def paintEvent(self, event):
        """Paint the circular progress."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate dimensions
        width = self.width()
        height = self.height()
        size = min(width, height) - 10
        x = (width - size) / 2
        y = (height - size) / 2
        rect = QRectF(x, y, size, size)

        # Draw background circle
        pen = QPen(QColor("#e0e0e0"))
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Draw progress arc
        if self._progress > 0:
            color = self._get_color_for_score(self._progress)
            pen = QPen(color)
            pen.setWidth(8)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            # Start from top (90 degrees) and go clockwise
            start_angle = 90 * 16
            span_angle = -int((self._progress / 100.0) * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)


class ScoreCard(QWidget):
    """Card displaying a compatibility score with circular progress."""

    def __init__(self, score: float = 0.0, grade: str = "N/A",
                 label: str = "Compatibility", parent=None):
        """
        Initialize the score card.

        Args:
            score: The score percentage (0-100)
            grade: The grade letter (A, B, C, D, F)
            label: Label text for the score
            parent: Parent widget
        """
        super().__init__(parent)
        self._score = score
        self._grade = grade
        self._label = label
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setObjectName("scoreCard")
        self.setStyleSheet("""
            QWidget#scoreCard {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        # Circular progress
        self.progress_widget = CircularProgress()
        layout.addWidget(self.progress_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Grade label (centered over progress)
        self.grade_label = QLabel(self._grade)
        self.grade_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.grade_label.setFont(font)
        self.grade_label.setStyleSheet("color: #2196F3;")

        # Create overlay layout for grade
        self.progress_widget.setLayout(QVBoxLayout())
        self.progress_widget.layout().addWidget(self.grade_label)
        self.progress_widget.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Score percentage
        self.score_label = QLabel(f"{self._score:.1f}%")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(self.score_label)

        # Label
        self.label_widget = QLabel(self._label)
        self.label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_widget.setStyleSheet("font-size: 13px; color: #666;")
        layout.addWidget(self.label_widget)

    def set_score(self, score: float, grade: str = None, animate: bool = True):
        """
        Update the score display.

        Args:
            score: New score percentage
            grade: New grade letter (optional)
            animate: Whether to animate the change
        """
        self._score = score
        self.score_label.setText(f"{score:.1f}%")

        if grade:
            self._grade = grade
            self.grade_label.setText(grade)

        if animate:
            self.progress_widget.animate_to(score)
        else:
            self.progress_widget.set_progress(score)

    def set_label(self, label: str):
        """Update the label text."""
        self._label = label
        self.label_widget.setText(label)
