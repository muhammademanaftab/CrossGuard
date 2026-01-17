"""
Type definitions for Cross Guard.

This module provides TypedDict definitions for structured data types
used throughout the application, improving type safety and IDE support.
"""

from typing import TypedDict, List, Dict, Optional, Set, Union, Any
from typing_extensions import NotRequired


# =============================================================================
# Browser Types
# =============================================================================

class BrowserInfo(TypedDict):
    """Information about a browser."""
    name: str
    version: str
    display_name: str


class BrowserSupport(TypedDict):
    """Support status for a feature in a browser."""
    status: str  # 'y', 'a', 'n', 'p', 'x', 'u', 'd'
    status_text: str
    version: str
    notes: NotRequired[str]


class BrowserScore(TypedDict):
    """Compatibility score for a browser."""
    browser: str
    version: str
    score: float
    supported_count: int
    partial_count: int
    unsupported_count: int
    total_features: int


# =============================================================================
# Feature Types
# =============================================================================

class FeatureInfo(TypedDict):
    """Information about a web feature."""
    id: str
    title: str
    description: str
    categories: List[str]
    status: str
    spec: NotRequired[str]
    notes: NotRequired[str]


class DetectedFeature(TypedDict):
    """A feature detected in analyzed code."""
    feature_id: str
    feature_name: str
    file_path: NotRequired[str]
    line_number: NotRequired[int]
    pattern: NotRequired[str]


class FeatureCompatibility(TypedDict):
    """Compatibility information for a feature."""
    feature_id: str
    feature_name: str
    support_status: Dict[str, str]
    browsers_affected: List[str]
    severity: str
    description: str
    category: str
    workaround: NotRequired[str]


# =============================================================================
# Analysis Report Types
# =============================================================================

class AnalysisSummary(TypedDict):
    """Summary of analysis results."""
    total_features: int
    html_features: int
    css_features: int
    js_features: int
    critical_issues: int
    overall_grade: str
    risk_level: str


class FilesAnalyzed(TypedDict):
    """Count of files analyzed by type."""
    html: int
    css: int
    javascript: int
    total: int


class FeaturesDetected(TypedDict):
    """Features detected by type."""
    html: List[str]
    css: List[str]
    javascript: List[str]


class ScoreBreakdown(TypedDict):
    """Detailed score breakdown."""
    simple_score: float
    weighted_score: float
    compatibility_index: float
    grade: str
    risk_level: str


class CompatibilityScores(TypedDict):
    """Compatibility scores section of report."""
    overall: float
    by_browser: Dict[str, float]
    breakdown: ScoreBreakdown


class IssueDetail(TypedDict):
    """Detailed information about a compatibility issue."""
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
    """Summary of compatibility issues."""
    critical: int
    high: int
    medium: int
    low: int
    total: int
    details: List[IssueDetail]


class BrowserResult(TypedDict):
    """Result for a single browser."""
    browser: str
    version: str
    score: float
    supported: int
    partial: int
    unsupported: int
    grade: str


class Recommendation(TypedDict):
    """A recommendation for improving compatibility."""
    type: str  # 'polyfill', 'fallback', 'prefix', 'alternative'
    feature: str
    message: str
    priority: str  # 'high', 'medium', 'low'
    url: NotRequired[str]


class AnalysisReport(TypedDict):
    """Complete analysis report structure."""
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
    """Error report when analysis fails."""
    success: bool
    error: str
    timestamp: str
    details: NotRequired[Dict[str, Any]]


# =============================================================================
# Parser Types
# =============================================================================

class ParserResult(TypedDict):
    """Result from a parser."""
    features: Set[str]
    feature_details: List[DetectedFeature]
    errors: List[str]
    warnings: List[str]


class ParserStatistics(TypedDict):
    """Statistics from parsing."""
    total_features: int
    features_by_category: Dict[str, int]
    features_list: List[str]


class CSSParserStats(TypedDict):
    """CSS parser specific statistics."""
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
    """JavaScript parser specific statistics."""
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


# =============================================================================
# Database Types
# =============================================================================

class DatabaseStats(TypedDict):
    """Statistics about the Can I Use database."""
    total_features: int
    total_categories: int
    index_size: int
    last_updated: NotRequired[str]


class SupportData(TypedDict):
    """Support data for a feature from Can I Use."""
    stats: Dict[str, str]
    notes: NotRequired[str]


class CanIUseFeature(TypedDict):
    """Feature data from Can I Use database."""
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


# =============================================================================
# Export Types
# =============================================================================

class ExportOptions(TypedDict):
    """Options for exporting reports."""
    format: str  # 'json', 'html', 'pdf', 'txt'
    output_path: str
    include_details: NotRequired[bool]
    include_recommendations: NotRequired[bool]
    theme: NotRequired[str]


class ExportResult(TypedDict):
    """Result of export operation."""
    success: bool
    output_path: str
    format: str
    size_bytes: NotRequired[int]
    error: NotRequired[str]


# =============================================================================
# Configuration Types
# =============================================================================

class TargetBrowsers(TypedDict, total=False):
    """Target browsers configuration."""
    chrome: str
    firefox: str
    safari: str
    edge: str
    opera: str
    ie: str


class AnalysisConfig(TypedDict):
    """Configuration for analysis."""
    target_browsers: TargetBrowsers
    ignore_features: NotRequired[List[str]]
    severity_threshold: NotRequired[str]
    include_polyfills: NotRequired[bool]


# =============================================================================
# Scoring Types
# =============================================================================

class WeightedScoreResult(TypedDict):
    """Result of weighted score calculation."""
    total_score: float
    weighted_score: float
    breakdown: Dict[str, float]
    weights: Dict[str, float]


class CompatibilityIndex(TypedDict):
    """Compatibility index calculation result."""
    score: float
    grade: str
    supported_count: int
    partial_count: int
    unsupported_count: int
    total_browsers: int
    support_percentage: float
    risk_level: str


class FeatureComparison(TypedDict):
    """Feature comparison result."""
    best_features: List[Dict[str, Union[str, float]]]
    worst_features: List[Dict[str, Union[str, float]]]
    average_score: float
    score_variance: float
    total_features: int


class TrendAnalysis(TypedDict):
    """Trend analysis result."""
    trend: str  # 'improving', 'stable', 'declining', 'unknown'
    improvement: float
    first_score: NotRequired[float]
    last_score: NotRequired[float]
    versions_analyzed: NotRequired[int]
