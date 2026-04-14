"""Data contracts shared between the frontend and backend."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class AnalysisStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    NO_FILES = "no_files"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnalysisRequest:
    html_files: List[str] = field(default_factory=list)
    css_files: List[str] = field(default_factory=list)
    js_files: List[str] = field(default_factory=list)
    target_browsers: Dict[str, str] = field(default_factory=dict)

    def has_files(self) -> bool:
        return bool(self.html_files or self.css_files or self.js_files)

    def total_files(self) -> int:
        return len(self.html_files) + len(self.css_files) + len(self.js_files)


@dataclass
class BrowserCompatibility:
    name: str
    version: str
    supported: int = 0
    partial: int = 0
    unsupported: int = 0
    compatibility_percentage: float = 0.0
    unsupported_features: List[str] = field(default_factory=list)
    partial_features: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    success: bool
    summary: Optional[Dict[str, Any]] = None
    scores: Optional[Dict[str, Any]] = None
    browsers: Dict[str, BrowserCompatibility] = field(default_factory=dict)
    detected_features: Optional[Dict[str, Any]] = None
    feature_details: Optional[Dict[str, Any]] = None
    unrecognized_patterns: Optional[Dict[str, Any]] = None
    recommendations: List[str] = field(default_factory=list)
    baseline_summary: Optional[Dict[str, Any]] = None
    ai_suggestions: Optional[List] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisResult':
        """Build an AnalysisResult from a raw backend report dict."""
        if not data.get('success', False):
            return cls(
                success=False,
                error=data.get('error', 'Unknown error')
            )

        summary_data = data.get('summary', {})
        summary = {
            'total_features': summary_data.get('total_features', 0),
            'html_features': summary_data.get('html_features', 0),
            'css_features': summary_data.get('css_features', 0),
            'js_features': summary_data.get('js_features', 0),
            'critical_issues': summary_data.get('critical_issues', 0),
        }

        scores_data = data.get('scores', {})
        scores = {
            'grade': scores_data.get('grade', 'N/A'),
            'risk_level': scores_data.get('risk_level', 'unknown'),
            'simple_score': scores_data.get('simple_score', 0.0),
            'weighted_score': scores_data.get('weighted_score', 0.0),
        }

        browsers = {}
        for browser_name, browser_data in data.get('browsers', {}).items():
            browsers[browser_name] = BrowserCompatibility(
                name=browser_name,
                version=browser_data.get('version', ''),
                supported=browser_data.get('supported', 0),
                partial=browser_data.get('partial', 0),
                unsupported=browser_data.get('unsupported', 0),
                compatibility_percentage=browser_data.get('compatibility_percentage', 0.0),
                unsupported_features=browser_data.get('unsupported_features', []),
                partial_features=browser_data.get('partial_features', []),
            )

        features_data = data.get('features', {})
        detected_features = {
            'html': features_data.get('html', []),
            'css': features_data.get('css', []),
            'js': features_data.get('js', []),
            'all': features_data.get('all', []),
        }

        details_data = data.get('feature_details', {})
        feature_details = {
            'css': details_data.get('css', []),
            'js': details_data.get('js', []),
            'html': details_data.get('html', []),
        }

        unrecognized_data = data.get('unrecognized', {})
        unrecognized_patterns = {
            'html': unrecognized_data.get('html', []),
            'css': unrecognized_data.get('css', []),
            'js': unrecognized_data.get('js', []),
            'total': unrecognized_data.get('total', 0),
        }

        baseline_summary = None
        baseline_data = data.get('baseline_summary')
        if baseline_data:
            baseline_summary = {
                'widely_available': baseline_data.get('widely_available', 0),
                'newly_available': baseline_data.get('newly_available', 0),
                'limited': baseline_data.get('limited', 0),
                'unknown': baseline_data.get('unknown', 0),
            }

        return cls(
            success=True,
            summary=summary,
            scores=scores,
            browsers=browsers,
            detected_features=detected_features,
            feature_details=feature_details,
            unrecognized_patterns=unrecognized_patterns,
            recommendations=data.get('recommendations', []),
            baseline_summary=baseline_summary,
        )

    def to_dict(self) -> Dict:
        """Serialize to a plain dict for export."""
        if not self.success:
            return {'success': False, 'error': self.error}

        return {
            'success': True,
            'summary': self.summary or {
                'total_features': 0, 'html_features': 0,
                'css_features': 0, 'js_features': 0, 'critical_issues': 0,
            },
            'scores': self.scores or {
                'grade': 'N/A', 'risk_level': 'unknown',
                'simple_score': 0.0, 'weighted_score': 0.0,
            },
            'browsers': {
                name: {
                    'version': browser.version,
                    'supported': browser.supported,
                    'partial': browser.partial,
                    'unsupported': browser.unsupported,
                    'compatibility_percentage': browser.compatibility_percentage,
                    'unsupported_features': browser.unsupported_features,
                    'partial_features': browser.partial_features,
                }
                for name, browser in self.browsers.items()
            },
            'features': self.detected_features or {
                'html': [], 'css': [], 'js': [], 'all': [],
            },
            'feature_details': self.feature_details or {
                'css': [], 'js': [], 'html': [],
            },
            'unrecognized': self.unrecognized_patterns or {
                'html': [], 'css': [], 'js': [], 'total': 0,
            },
            'recommendations': self.recommendations,
            'baseline_summary': self.baseline_summary,
            'ai_suggestions': [
                {
                    'feature_id': s.feature_id,
                    'feature_name': s.feature_name,
                    'suggestion': s.suggestion,
                    'code_example': s.code_example,
                    'browsers_affected': s.browsers_affected,
                }
                for s in self.ai_suggestions
            ] if self.ai_suggestions else None,
        }


@dataclass
class DatabaseInfo:
    features_count: int = 0
    last_updated: str = "Unknown"
    is_git_repo: bool = False
    npm_version: Optional[str] = None
    npm_latest: Optional[str] = None
    update_available: bool = False


@dataclass
class DatabaseUpdateResult:
    success: bool
    message: str = ""
    no_changes: bool = False
    error: Optional[str] = None


ProgressCallback = Optional[callable]


@dataclass
class ExportRequest:
    format: str  # "json" or "pdf"
    analysis_id: Optional[int] = None
    result: Optional[AnalysisResult] = None
    output_path: Optional[str] = None

    def __post_init__(self):
        if self.format not in ('json', 'pdf'):
            raise ValueError(f"Unsupported export format: {self.format}")
        if self.analysis_id is None and self.result is None:
            raise ValueError("Either analysis_id or result must be provided")
