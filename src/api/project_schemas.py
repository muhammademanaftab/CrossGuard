"""
Project Scanner Schemas - Data contracts for project scanning.

These dataclasses define the structure of data for project scanning
operations, separate from single-file analysis schemas.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

# Re-export scanner dataclasses for convenience
from src.scanner import (
    ScanConfig,
    ScanResult,
    FileTreeNode,
    FrameworkInfo,
    BuildToolInfo,
    ProjectInfo,
)


class ScanStatus(Enum):
    """Status of a scan operation."""
    PENDING = "pending"
    SCANNING = "scanning"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProjectScanRequest:
    """Request to scan a project directory."""
    project_path: str
    config: Optional[ScanConfig] = None
    target_browsers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.config is None:
            self.config = ScanConfig()


@dataclass
class FileAnalysisResult:
    """Result of analyzing a single file within a project."""
    file_path: str
    file_name: str
    file_type: str  # 'html', 'css', 'javascript'
    score: float = 0.0
    grade: str = "N/A"
    features_count: int = 0
    issues_count: int = 0
    unsupported_features: List[str] = field(default_factory=list)
    partial_features: List[str] = field(default_factory=list)


@dataclass
class ProjectAnalysisResult:
    """Aggregate result of analyzing an entire project."""

    # Overall metrics
    success: bool = True
    error: Optional[str] = None

    # Project info
    project_path: str = ""
    project_name: str = ""
    framework: Optional[FrameworkInfo] = None
    build_tool: Optional[BuildToolInfo] = None

    # Aggregate scores
    overall_score: float = 0.0
    overall_grade: str = "N/A"
    weighted_score: float = 0.0

    # File breakdown
    total_files: int = 0
    html_files: int = 0
    css_files: int = 0
    js_files: int = 0

    # File results
    file_results: List[FileAnalysisResult] = field(default_factory=list)

    # Worst performing files
    worst_files: List[FileAnalysisResult] = field(default_factory=list)

    # Feature aggregates
    total_features: int = 0
    unique_features: int = 0
    unsupported_count: int = 0
    partial_count: int = 0

    # Most problematic features across project
    top_issues: List[Dict[str, Any]] = field(default_factory=list)

    # Browser breakdown (same as single-file analysis)
    browsers: Dict[str, Any] = field(default_factory=dict)

    # Scan metadata
    scan_duration_ms: int = 0
    analysis_duration_ms: int = 0
    scanned_at: str = ""

    @classmethod
    def from_error(cls, error: str, project_path: str = "") -> 'ProjectAnalysisResult':
        """Create a failed result with an error message."""
        return cls(
            success=False,
            error=error,
            project_path=project_path
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary dictionary for display."""
        return {
            'project_name': self.project_name,
            'overall_score': self.overall_score,
            'overall_grade': self.overall_grade,
            'total_files': self.total_files,
            'total_features': self.total_features,
            'unsupported_count': self.unsupported_count,
            'partial_count': self.partial_count,
            'framework': str(self.framework) if self.framework else None,
            'build_tool': str(self.build_tool) if self.build_tool else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export/serialization."""
        return {
            'success': self.success,
            'error': self.error,
            'project_path': self.project_path,
            'project_name': self.project_name,
            'framework': {
                'name': self.framework.name,
                'version': self.framework.version,
            } if self.framework else None,
            'build_tool': {
                'name': self.build_tool.name,
                'version': self.build_tool.version,
            } if self.build_tool else None,
            'overall_score': self.overall_score,
            'overall_grade': self.overall_grade,
            'weighted_score': self.weighted_score,
            'total_files': self.total_files,
            'html_files': self.html_files,
            'css_files': self.css_files,
            'js_files': self.js_files,
            'file_results': [
                {
                    'file_path': f.file_path,
                    'file_name': f.file_name,
                    'file_type': f.file_type,
                    'score': f.score,
                    'grade': f.grade,
                    'features_count': f.features_count,
                    'issues_count': f.issues_count,
                }
                for f in self.file_results
            ],
            'worst_files': [
                {
                    'file_path': f.file_path,
                    'file_name': f.file_name,
                    'score': f.score,
                    'grade': f.grade,
                }
                for f in self.worst_files
            ],
            'total_features': self.total_features,
            'unique_features': self.unique_features,
            'unsupported_count': self.unsupported_count,
            'partial_count': self.partial_count,
            'top_issues': self.top_issues,
            'browsers': self.browsers,
            'scan_duration_ms': self.scan_duration_ms,
            'analysis_duration_ms': self.analysis_duration_ms,
            'scanned_at': self.scanned_at,
        }


@dataclass
class ProjectScanProgress:
    """Progress update for project scanning."""
    status: ScanStatus
    message: str = ""
    current_file: str = ""
    files_scanned: int = 0
    files_total: int = 0
    current_phase: str = ""  # "scanning", "detecting", "analyzing"

    @property
    def progress_percent(self) -> float:
        """Get progress as percentage (0-100)."""
        if self.files_total == 0:
            return 0.0
        return (self.files_scanned / self.files_total) * 100


# Convenience exports
__all__ = [
    # Re-exported from scanner
    'ScanConfig',
    'ScanResult',
    'FileTreeNode',
    'FrameworkInfo',
    'BuildToolInfo',
    'ProjectInfo',

    # New schemas
    'ScanStatus',
    'ProjectScanRequest',
    'FileAnalysisResult',
    'ProjectAnalysisResult',
    'ProjectScanProgress',
]
