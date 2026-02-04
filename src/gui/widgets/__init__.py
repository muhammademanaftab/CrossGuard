"""
Custom widgets for Cross Guard GUI (CustomTkinter implementation).
"""

from .drop_zone import DropZone
from .score_card import ScoreCard, CircularProgress
from .browser_card import BrowserCard, StackedBarWidget
from .charts import (
    BrowserRadarChart,
    CompatibilityBarChart,
    FeatureDistributionChart,
    ScoreGaugeChart,
    SupportStatusChart,
)
from .messagebox import (
    MessageDialog,
    ProgressDialog,
    show_info,
    show_warning,
    show_error,
    ask_question,
)
from .sidebar import Sidebar, SidebarItem
from .header_bar import HeaderBar
from .status_bar import StatusBar
from .file_table import FileTable, FileTableRow, FileTableHeader

# New progressive disclosure widgets
from .build_badge import BuildBadge
from .collapsible import CollapsibleSection
from .issue_card import IssueCard, IssuesSummary
from .quick_stats import QuickStatsBar, StatCard

# ML Risk Assessment widgets
from .ml_risk_card import MLRiskCard, MLFeatureImportanceCard

# Browser Selection
from .browser_selector import BrowserSelector, get_available_browsers

# Version Range Display (like Can I Use)
from .version_range_card import VersionRangeCard, VersionRangeBar, VersionRangePopup

# History and Statistics widgets
from .history_card import HistoryCard, EmptyHistoryCard
from .statistics_panel import StatisticsPanel, CompactStatsBar

# Bookmark and Tag widgets
from .bookmark_button import BookmarkButton, BookmarkIndicator
from .tag_widget import TagChip, TagList, TagSelector, TagManagerDialog

# Project Scanner widgets
from .project_tree import ProjectTreeWidget, TreeItemWidget
from .scan_config_panel import ScanConfigPanel
from .project_stats_card import ProjectStatsCard, ProjectSummaryBadge

__all__ = [
    # Drop zone
    'DropZone',

    # Score display
    'ScoreCard',
    'CircularProgress',

    # Browser card
    'BrowserCard',
    'StackedBarWidget',

    # Charts
    'BrowserRadarChart',
    'CompatibilityBarChart',
    'FeatureDistributionChart',
    'ScoreGaugeChart',
    'SupportStatusChart',

    # Message dialogs
    'MessageDialog',
    'ProgressDialog',
    'show_info',
    'show_warning',
    'show_error',
    'ask_question',

    # Navigation
    'Sidebar',
    'SidebarItem',
    'HeaderBar',
    'StatusBar',

    # File management
    'FileTable',
    'FileTableRow',
    'FileTableHeader',

    # Progressive disclosure widgets
    'BuildBadge',
    'CollapsibleSection',
    'IssueCard',
    'IssuesSummary',
    'QuickStatsBar',
    'StatCard',

    # ML Risk Assessment
    'MLRiskCard',
    'MLFeatureImportanceCard',

    # Browser Selection
    'BrowserSelector',
    'get_available_browsers',

    # Version Range Display
    'VersionRangeCard',
    'VersionRangeBar',
    'VersionRangePopup',

    # History and Statistics
    'HistoryCard',
    'EmptyHistoryCard',
    'StatisticsPanel',
    'CompactStatsBar',

    # Bookmarks and Tags
    'BookmarkButton',
    'BookmarkIndicator',
    'TagChip',
    'TagList',
    'TagSelector',
    'TagManagerDialog',

    # Project Scanner
    'ProjectTreeWidget',
    'TreeItemWidget',
    'ScanConfigPanel',
    'ProjectStatsCard',
    'ProjectSummaryBadge',
]
