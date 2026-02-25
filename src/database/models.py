"""Dataclasses that map to the database tables."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import json


@dataclass
class BrowserResult:
    """Support status for one browser on one feature."""
    browser: str
    support_status: str
    version: str = ''
    id: Optional[int] = None
    analysis_feature_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'analysis_feature_id': self.analysis_feature_id,
            'browser': self.browser,
            'version': self.version,
            'support_status': self.support_status,
        }

    @classmethod
    def from_row(cls, row) -> 'BrowserResult':
        return cls(
            id=row['id'],
            analysis_feature_id=row['analysis_feature_id'],
            browser=row['browser'],
            version=row['version'] or '',
            support_status=row['support_status'],
        )


@dataclass
class AnalysisFeature:
    """A detected Can I Use feature within an analysis."""
    feature_id: str
    category: str
    feature_name: str = ''
    id: Optional[int] = None
    analysis_id: Optional[int] = None
    browser_results: List[BrowserResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
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
        return cls(
            id=row['id'],
            analysis_id=row['analysis_id'],
            feature_id=row['feature_id'],
            feature_name=row['feature_name'] or '',
            category=row['category'],
        )


@dataclass
class Analysis:
    """A single file analysis with score, grade, and detected features."""
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
        if self.analyzed_at is None:
            self.analyzed_at = datetime.now()

    @property
    def browsers(self) -> Dict[str, str]:
        """Parse browsers_json into a dict."""
        try:
            return json.loads(self.browsers_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    @browsers.setter
    def browsers(self, value: Dict[str, str]):
        self.browsers_json = json.dumps(value)

    def to_dict(self) -> Dict[str, Any]:
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
        analyzed_at = None
        if row['analyzed_at']:
            try:
                analyzed_at = datetime.fromisoformat(row['analyzed_at'])
            except (ValueError, TypeError):
                # fallback for SQLite's default datetime format
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
        """Human-friendly relative date like 'Today 2:30 PM' or 'Jan 15, 2026'."""
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
        """Unicode icon for the file type."""
        icons = {
            'html': '\u25B6',
            'htm': '\u25B6',
            'css': '\u25C6',
            'js': '\u2605',
        }
        return icons.get(self.file_type.lower(), '\u25A0')


@dataclass
class Setting:
    """Key-value user preference."""
    key: str
    value: str
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_row(cls, row) -> 'Setting':
        updated_at = None
        if row['updated_at']:
            try:
                updated_at = datetime.fromisoformat(row['updated_at'])
            except (ValueError, TypeError):
                pass

        return cls(
            key=row['key'],
            value=row['value'],
            updated_at=updated_at,
        )

    def get_as_bool(self) -> bool:
        return self.value.lower() in ('true', '1', 'yes', 'on')

    def get_as_int(self) -> int:
        try:
            return int(self.value)
        except (ValueError, TypeError):
            return 0

    def get_as_list(self) -> List[str]:
        """Split comma-separated value into a list."""
        return [v.strip() for v in self.value.split(',') if v.strip()]


@dataclass
class Bookmark:
    """A bookmarked analysis with an optional note."""
    analysis_id: int
    note: str = ''
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    analysis: Optional[Analysis] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if self.analysis:
            result['analysis'] = self.analysis.to_dict()
        return result

    @classmethod
    def from_row(cls, row) -> 'Bookmark':
        created_at = None
        if row['created_at']:
            try:
                created_at = datetime.fromisoformat(row['created_at'])
            except (ValueError, TypeError):
                pass

        return cls(
            id=row['id'],
            analysis_id=row['analysis_id'],
            note=row['note'] or '',
            created_at=created_at,
        )


@dataclass
class Tag:
    """A named, colored label for categorizing analyses."""
    name: str
    color: str = '#58a6ff'
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_row(cls, row) -> 'Tag':
        created_at = None
        if row['created_at']:
            try:
                created_at = datetime.fromisoformat(row['created_at'])
            except (ValueError, TypeError):
                pass

        return cls(
            id=row['id'],
            name=row['name'],
            color=row['color'] or '#58a6ff',
            created_at=created_at,
        )


@dataclass
class AnalysisTag:
    """Many-to-many link between an analysis and a tag."""
    analysis_id: int
    tag_id: int
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'analysis_id': self.analysis_id,
            'tag_id': self.tag_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_row(cls, row) -> 'AnalysisTag':
        created_at = None
        if row['created_at']:
            try:
                created_at = datetime.fromisoformat(row['created_at'])
            except (ValueError, TypeError):
                pass

        return cls(
            analysis_id=row['analysis_id'],
            tag_id=row['tag_id'],
            created_at=created_at,
        )
