"""TypedDict definitions used across the app."""

from typing import TypedDict, List, Dict, Optional, Set, Union, Any
from typing_extensions import NotRequired


# --- Browser ---

class BrowserInfo(TypedDict):
    name: str
    version: str
    display_name: str


class BrowserSupport(TypedDict):
    status: str  # 'y', 'a', 'n', 'p', 'x', 'u', 'd'
    status_text: str
    version: str
    notes: NotRequired[str]


class BrowserScore(TypedDict):
    browser: str
    version: str
    score: float
    supported_count: int
    partial_count: int
    unsupported_count: int
    total_features: int


# --- Feature ---

class FeatureInfo(TypedDict):
    id: str
    title: str
    description: str
    categories: List[str]
    status: str
    spec: NotRequired[str]
    notes: NotRequired[str]


class DetectedFeature(TypedDict):
    feature_id: str
    feature_name: str
    file_path: NotRequired[str]
    line_number: NotRequired[int]
    pattern: NotRequired[str]


class FeatureCompatibility(TypedDict):
    feature_id: str
    feature_name: str
    support_status: Dict[str, str]
    browsers_affected: List[str]
    severity: str
    description: str
    category: str
    workaround: NotRequired[str]


# --- Analysis Report ---

class AnalysisSummary(TypedDict):
    total_features: int
    html_features: int
    css_features: int
    js_features: int
    critical_issues: int
    overall_grade: str
    risk_level: str


class FilesAnalyzed(TypedDict):
    html: int
    css: int
    javascript: int
    total: int


class FeaturesDetected(TypedDict):
    html: List[str]
    css: List[str]
    javascript: List[str]


class ScoreBreakdown(TypedDict):
    simple_score: float
    weighted_score: float
    compatibility_index: float
    grade: str
    risk_level: str


class CompatibilityScores(TypedDict):
    overall: float
    by_browser: Dict[str, float]
    breakdown: ScoreBreakdown


class IssueDetail(TypedDict):
    feature_id: str
    feature_name: str
    severity: str
    browsers_affected: List[str]
    support_status: Dict[str, str]
    description: str
    category: str
    workaround: NotRequired[str]
    recommendation: NotRequired[str]


class IssuesSummary(TypedDict):
    critical: int
    high: int
    medium: int
    low: int
    total: int
    details: List[IssueDetail]


class BrowserResult(TypedDict):
    browser: str
    version: str
    score: float
    supported: int
    partial: int
    unsupported: int
    grade: str


class Recommendation(TypedDict):
    type: str  # 'polyfill', 'fallback', 'prefix', 'alternative'
    feature: str
    message: str
    priority: str  # 'high', 'medium', 'low'
    url: NotRequired[str]


class AnalysisReport(TypedDict):
    success: bool
    timestamp: str
    summary: AnalysisSummary
    scores: CompatibilityScores
    browsers: Dict[str, BrowserResult]
    features: FeaturesDetected
    issues: IssuesSummary
    recommendations: List[Recommendation]
    errors: NotRequired[List[str]]
    warnings: NotRequired[List[str]]


class ErrorReport(TypedDict):
    success: bool
    error: str
    timestamp: str
    details: NotRequired[Dict[str, Any]]


# --- Parser ---

class ParserResult(TypedDict):
    features: Set[str]
    feature_details: List[DetectedFeature]
    errors: List[str]
    warnings: List[str]


class ParserStatistics(TypedDict):
    total_features: int
    features_by_category: Dict[str, int]
    features_list: List[str]


class CSSParserStats(TypedDict):
    total_features: int
    layout_features: int
    transform_animation: int
    color_background: int
    typography: int
    selectors: int
    media_queries: int
    other_features: int
    features_list: List[str]
    categories: Dict[str, List[str]]


class JSParserStats(TypedDict):
    total_features: int
    syntax_features: int
    api_features: int
    array_methods: int
    string_methods: int
    object_methods: int
    storage_apis: int
    dom_apis: int
    features_list: List[str]
    categories: Dict[str, List[str]]


# --- Database ---

class DatabaseStats(TypedDict):
    total_features: int
    total_categories: int
    index_size: int
    last_updated: NotRequired[str]


class SupportData(TypedDict):
    stats: Dict[str, str]
    notes: NotRequired[str]


class CanIUseFeature(TypedDict):
    title: str
    description: str
    spec: NotRequired[str]
    status: str
    links: NotRequired[List[Dict[str, str]]]
    categories: List[str]
    stats: Dict[str, Dict[str, str]]
    notes: NotRequired[str]
    notes_by_num: NotRequired[Dict[str, str]]
    usage_perc_y: NotRequired[float]
    usage_perc_a: NotRequired[float]
    keywords: NotRequired[str]


# --- Export ---

class ExportOptions(TypedDict):
    format: str  # 'json', 'html', 'pdf', 'txt'
    output_path: str
    include_details: NotRequired[bool]
    include_recommendations: NotRequired[bool]
    theme: NotRequired[str]


class ExportResult(TypedDict):
    success: bool
    output_path: str
    format: str
    size_bytes: NotRequired[int]
    error: NotRequired[str]


# --- Configuration ---

class TargetBrowsers(TypedDict, total=False):
    chrome: str
    firefox: str
    safari: str
    edge: str
    opera: str
    ie: str


class AnalysisConfig(TypedDict):
    target_browsers: TargetBrowsers
    ignore_features: NotRequired[List[str]]
    severity_threshold: NotRequired[str]
    include_polyfills: NotRequired[bool]


# --- Scoring ---

class WeightedScoreResult(TypedDict):
    total_score: float
    weighted_score: float
    breakdown: Dict[str, float]
    weights: Dict[str, float]


class CompatibilityIndex(TypedDict):
    score: float
    grade: str
    supported_count: int
    partial_count: int
    unsupported_count: int
    total_browsers: int
    support_percentage: float
    risk_level: str


class FeatureComparison(TypedDict):
    best_features: List[Dict[str, Union[str, float]]]
    worst_features: List[Dict[str, Union[str, float]]]
    average_score: float
    score_variance: float
    total_features: int


class TrendAnalysis(TypedDict):
    trend: str  # 'improving', 'stable', 'declining', 'unknown'
    improvement: float
    first_score: NotRequired[float]
    last_score: NotRequired[float]
    versions_analyzed: NotRequired[int]
