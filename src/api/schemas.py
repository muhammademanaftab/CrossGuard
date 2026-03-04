"""Data contracts shared between the frontend and backend."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
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
class BrowserTarget:
    name: str
    version: str


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
class FeatureSummary:
    total_features: int = 0
    html_features: int = 0
    css_features: int = 0
    js_features: int = 0
    critical_issues: int = 0


@dataclass
class DetectedFeatures:
    html: List[str] = field(default_factory=list)
    css: List[str] = field(default_factory=list)
    js: List[str] = field(default_factory=list)
    all: List[str] = field(default_factory=list)


@dataclass
class FeatureDetails:
    """Which properties/patterns matched which Can I Use features."""
    css: List[Dict] = field(default_factory=list)  # [{feature, description, matched_properties}]
    js: List[Dict] = field(default_factory=list)
    html: List[Dict] = field(default_factory=list)


@dataclass
class UnrecognizedPatterns:
    """Patterns not matched by any detection rule."""
    html: List[str] = field(default_factory=list)
    css: List[str] = field(default_factory=list)
    js: List[str] = field(default_factory=list)
    total: int = 0


@dataclass
class CompatibilityScore:
    grade: str = "N/A"
    risk_level: str = "unknown"
    simple_score: float = 0.0
    weighted_score: float = 0.0


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
class BaselineInfo:
    status: str  # "high", "low", "limited"
    low_date: Optional[str] = None
    high_date: Optional[str] = None


@dataclass
class BaselineSummary:
    widely_available: int = 0   # baseline "high"
    newly_available: int = 0    # baseline "low"
    limited: int = 0            # baseline False
    unknown: int = 0            # no web-features mapping


@dataclass
class AnalysisResult:
    success: bool
    summary: Optional[FeatureSummary] = None
    scores: Optional[CompatibilityScore] = None
    browsers: Dict[str, BrowserCompatibility] = field(default_factory=dict)
    detected_features: Optional[DetectedFeatures] = None
    feature_details: Optional[FeatureDetails] = None
    unrecognized_patterns: Optional[UnrecognizedPatterns] = None
    recommendations: List[str] = field(default_factory=list)
    baseline_summary: Optional[BaselineSummary] = None
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
        summary = FeatureSummary(
            total_features=summary_data.get('total_features', 0),
            html_features=summary_data.get('html_features', 0),
            css_features=summary_data.get('css_features', 0),
            js_features=summary_data.get('js_features', 0),
            critical_issues=summary_data.get('critical_issues', 0),
        )

        scores_data = data.get('scores', {})
        scores = CompatibilityScore(
            grade=scores_data.get('grade', 'N/A'),
            risk_level=scores_data.get('risk_level', 'unknown'),
            simple_score=scores_data.get('simple_score', 0.0),
            weighted_score=scores_data.get('weighted_score', 0.0),
        )

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
        detected_features = DetectedFeatures(
            html=features_data.get('html', []),
            css=features_data.get('css', []),
            js=features_data.get('js', []),
            all=features_data.get('all', []),
        )

        details_data = data.get('feature_details', {})
        feature_details = FeatureDetails(
            css=details_data.get('css', []),
            js=details_data.get('js', []),
            html=details_data.get('html', []),
        )

        unrecognized_data = data.get('unrecognized', {})
        unrecognized_patterns = UnrecognizedPatterns(
            html=unrecognized_data.get('html', []),
            css=unrecognized_data.get('css', []),
            js=unrecognized_data.get('js', []),
            total=unrecognized_data.get('total', 0),
        )

        baseline_summary = None
        baseline_data = data.get('baseline_summary')
        if baseline_data:
            baseline_summary = BaselineSummary(
                widely_available=baseline_data.get('widely_available', 0),
                newly_available=baseline_data.get('newly_available', 0),
                limited=baseline_data.get('limited', 0),
                unknown=baseline_data.get('unknown', 0),
            )

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
            'summary': {
                'total_features': self.summary.total_features if self.summary else 0,
                'html_features': self.summary.html_features if self.summary else 0,
                'css_features': self.summary.css_features if self.summary else 0,
                'js_features': self.summary.js_features if self.summary else 0,
                'critical_issues': self.summary.critical_issues if self.summary else 0,
            },
            'scores': {
                'grade': self.scores.grade if self.scores else 'N/A',
                'risk_level': self.scores.risk_level if self.scores else 'unknown',
                'simple_score': self.scores.simple_score if self.scores else 0.0,
                'weighted_score': self.scores.weighted_score if self.scores else 0.0,
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
            'features': {
                'html': self.detected_features.html if self.detected_features else [],
                'css': self.detected_features.css if self.detected_features else [],
                'js': self.detected_features.js if self.detected_features else [],
                'all': self.detected_features.all if self.detected_features else [],
            },
            'feature_details': {
                'css': self.feature_details.css if self.feature_details else [],
                'js': self.feature_details.js if self.feature_details else [],
                'html': self.feature_details.html if self.feature_details else [],
            },
            'unrecognized': {
                'html': self.unrecognized_patterns.html if self.unrecognized_patterns else [],
                'css': self.unrecognized_patterns.css if self.unrecognized_patterns else [],
                'js': self.unrecognized_patterns.js if self.unrecognized_patterns else [],
                'total': self.unrecognized_patterns.total if self.unrecognized_patterns else 0,
            },
            'recommendations': self.recommendations,
            'baseline_summary': {
                'widely_available': self.baseline_summary.widely_available,
                'newly_available': self.baseline_summary.newly_available,
                'limited': self.baseline_summary.limited,
                'unknown': self.baseline_summary.unknown,
            } if self.baseline_summary else None,
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


@dataclass
class PolyfillPackageInfo:
    name: str
    npm_package: str
    import_statement: str
    cdn_url: Optional[str] = None
    size_kb: Optional[float] = None
    note: Optional[str] = None


@dataclass
class PolyfillRecommendationSchema:
    """API-layer version of a polyfill recommendation."""
    feature_id: str
    feature_name: str
    polyfill_type: str  # 'npm' or 'fallback'
    packages: List[PolyfillPackageInfo] = field(default_factory=list)
    fallback_code: Optional[str] = None
    fallback_description: Optional[str] = None
    browsers_affected: List[str] = field(default_factory=list)
