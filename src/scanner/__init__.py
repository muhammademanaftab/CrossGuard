"""
Project Scanner Module for Cross Guard.

This module provides functionality to scan entire project directories
for browser compatibility analysis.
"""

from .project_scanner import (
    ProjectScanner,
    ScanConfig,
    ScanResult,
    FileTreeNode,
)
from .framework_detector import (
    FrameworkDetector,
    FrameworkInfo,
    BuildToolInfo,
    ProjectInfo,
)

__all__ = [
    # Scanner
    'ProjectScanner',
    'ScanConfig',
    'ScanResult',
    'FileTreeNode',

    # Framework detection
    'FrameworkDetector',
    'FrameworkInfo',
    'BuildToolInfo',
    'ProjectInfo',
]
