"""GUI widgets package."""

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

from .build_badge import BuildBadge
from .collapsible import CollapsibleSection
from .issue_card import IssueCard, IssuesSummary
from .quick_stats import QuickStatsBar, StatCard

from .ml_risk_card import MLRiskCard, MLFeatureImportanceCard

from .browser_selector import BrowserSelector, get_available_browsers

from .version_range_card import VersionRangeCard, VersionRangeBar, VersionRangePopup

from .history_card import HistoryCard, EmptyHistoryCard
from .statistics_panel import StatisticsPanel, CompactStatsBar

from .bookmark_button import BookmarkButton, BookmarkIndicator
from .tag_widget import TagChip, TagList, TagSelector, TagManagerDialog

from .polyfill_card import PolyfillCard, PolyfillEmptyCard

__all__ = [
    'DropZone',
    'ScoreCard',
    'CircularProgress',
    'BrowserCard',
    'StackedBarWidget',
    'BrowserRadarChart',
    'CompatibilityBarChart',
    'FeatureDistributionChart',
    'ScoreGaugeChart',
    'SupportStatusChart',
    'MessageDialog',
    'ProgressDialog',
    'show_info',
    'show_warning',
    'show_error',
    'ask_question',
    'Sidebar',
    'SidebarItem',
    'HeaderBar',
    'StatusBar',
    'FileTable',
    'FileTableRow',
    'FileTableHeader',
    'BuildBadge',
    'CollapsibleSection',
    'IssueCard',
    'IssuesSummary',
    'QuickStatsBar',
    'StatCard',
    'MLRiskCard',
    'MLFeatureImportanceCard',
    'BrowserSelector',
    'get_available_browsers',
    'VersionRangeCard',
    'VersionRangeBar',
    'VersionRangePopup',
    'HistoryCard',
    'EmptyHistoryCard',
    'StatisticsPanel',
    'CompactStatsBar',
    'BookmarkButton',
    'BookmarkIndicator',
    'TagChip',
    'TagList',
    'TagSelector',
    'TagManagerDialog',
    'PolyfillCard',
    'PolyfillEmptyCard',
]
