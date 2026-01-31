"""
Data models for Cross Guard database.

Defines dataclasses that map to database tables:
- Analysis: Main analysis record
- AnalysisFeature: Detected features per analysis
- BrowserResult: Browser support status per feature
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import json


@dataclass
class BrowserResult:
    """Browser support result for a specific feature.

    Maps to the browser_results table.

    Attributes:
        id: Primary key (auto-generated)
        analysis_feature_id: Foreign key to analysis_features
        browser: Browser name (e.g., 'chrome', 'firefox')
        version: Browser version tested
        support_status: Support status code ('y', 'n', 'a', 'x', 'p')
    """
    browser: str
    support_status: str
    version: str = ''
    id: Optional[int] = None
    analysis_feature_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'analysis_feature_id': self.analysis_feature_id,
            'browser': self.browser,
            'version': self.version,
            'support_status': self.support_status,
        }

    @classmethod
    def from_row(cls, row) -> 'BrowserResult':
        """Create from database row.

        Args:
            row: sqlite3.Row object

        Returns:
            BrowserResult instance
        """
        return cls(
            id=row['id'],
            analysis_feature_id=row['analysis_feature_id'],
            browser=row['browser'],
            version=row['version'] or '',
            support_status=row['support_status'],
        )


@dataclass
class AnalysisFeature:
    """Detected feature in an analysis.

    Maps to the analysis_features table.

    Attributes:
        id: Primary key (auto-generated)
        analysis_id: Foreign key to analyses
        feature_id: Can I Use feature ID
        feature_name: Human-readable feature name
        category: Feature category ('html', 'css', 'js')
        browser_results: List of browser support results
    """
    feature_id: str
    category: str
    feature_name: str = ''
    id: Optional[int] = None
    analysis_id: Optional[int] = None
    browser_results: List[BrowserResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'feature_id': self.feature_id,
            'feature_name': self.feature_name,
            'category': self.category,
            'browser_results': [br.to_dict() for br in self.browser_results],
        }

    @classmethod
    def from_row(cls, row) -> 'AnalysisFeature':
        """Create from database row.

        Args:
            row: sqlite3.Row object

        Returns:
            AnalysisFeature instance
        """
        return cls(
            id=row['id'],
            analysis_id=row['analysis_id'],
            feature_id=row['feature_id'],
            feature_name=row['feature_name'] or '',
            category=row['category'],
        )


@dataclass
class Analysis:
    """Analysis record for a file.

    Maps to the analyses table.

    Attributes:
        id: Primary key (auto-generated)
        file_name: Name of the analyzed file
        file_path: Full path to the file
        file_type: Type of file ('html', 'css', 'js')
        overall_score: Compatibility score (0-100)
        grade: Letter grade (A+, A, B, etc.)
        total_features: Number of features detected
        analyzed_at: Timestamp of analysis
        browsers_json: JSON string of target browsers
        features: List of detected features
    """
    file_name: str
    file_type: str
    overall_score: float
    grade: str
    total_features: int
    file_path: str = ''
    analyzed_at: Optional[datetime] = None
    browsers_json: str = '{}'
    id: Optional[int] = None
    features: List[AnalysisFeature] = field(default_factory=list)

    def __post_init__(self):
        """Initialize defaults after dataclass initialization."""
        if self.analyzed_at is None:
            self.analyzed_at = datetime.now()

    @property
    def browsers(self) -> Dict[str, str]:
        """Get browsers dict from JSON string."""
        try:
            return json.loads(self.browsers_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    @browsers.setter
    def browsers(self, value: Dict[str, str]):
        """Set browsers JSON from dict."""
        self.browsers_json = json.dumps(value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'overall_score': self.overall_score,
            'grade': self.grade,
            'total_features': self.total_features,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
            'browsers': self.browsers,
            'features': [f.to_dict() for f in self.features],
        }

    @classmethod
    def from_row(cls, row) -> 'Analysis':
        """Create from database row.

        Args:
            row: sqlite3.Row object

        Returns:
            Analysis instance
        """
        # Parse analyzed_at timestamp
        analyzed_at = None
        if row['analyzed_at']:
            try:
                analyzed_at = datetime.fromisoformat(row['analyzed_at'])
            except (ValueError, TypeError):
                # Try parsing as SQLite datetime format
                try:
                    analyzed_at = datetime.strptime(
                        row['analyzed_at'],
                        '%Y-%m-%d %H:%M:%S'
                    )
                except (ValueError, TypeError):
                    analyzed_at = datetime.now()

        return cls(
            id=row['id'],
            file_name=row['file_name'],
            file_path=row['file_path'] or '',
            file_type=row['file_type'],
            overall_score=row['overall_score'],
            grade=row['grade'],
            total_features=row['total_features'],
            analyzed_at=analyzed_at,
            browsers_json=row['browsers_json'] or '{}',
        )

    def get_formatted_date(self) -> str:
        """Get a human-readable formatted date string.

        Returns:
            Formatted date string (e.g., 'Today 2:30 PM', 'Yesterday', 'Jan 15')
        """
        if not self.analyzed_at:
            return 'Unknown'

        now = datetime.now()
        diff = now - self.analyzed_at

        if diff.days == 0:
            return f"Today {self.analyzed_at.strftime('%I:%M %p')}"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return self.analyzed_at.strftime('%b %d, %Y')

    def get_file_type_icon(self) -> str:
        """Get icon character for file type.

        Returns:
            Unicode icon character
        """
        icons = {
            'html': '\u25B6',  # Play triangle
            'htm': '\u25B6',
            'css': '\u25C6',   # Diamond
            'js': '\u2605',    # Star
        }
        return icons.get(self.file_type.lower(), '\u25A0')  # Square default
