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
from .sidebar import Sidebar
from .header_bar import HeaderBar
from .status_bar import StatusBar
from .file_table import FileTable

from .build_badge import BuildBadge
from .collapsible import CollapsibleSection
from .issue_card import IssueCard, IssuesSummary
from .quick_stats import QuickStatsBar

from .browser_selector import BrowserSelector, get_available_browsers

from .version_range_card import VersionRangeCard, VersionRangeBar, VersionRangePopup

from .history_card import HistoryCard
from .statistics_panel import StatisticsPanel, CompactStatsBar

from .bookmark_button import BookmarkButton
from .tag_widget import TagChip, TagList, TagSelector, TagManagerDialog

from .polyfill_card import PolyfillCard
from .ai_fix_card import AIFixCard

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
    'HeaderBar',
    'StatusBar',
    'FileTable',
    'BuildBadge',
    'CollapsibleSection',
    'IssueCard',
    'IssuesSummary',
    'QuickStatsBar',
    'BrowserSelector',
    'get_available_browsers',
    'VersionRangeCard',
    'VersionRangeBar',
    'VersionRangePopup',
    'HistoryCard',
    'StatisticsPanel',
    'CompactStatsBar',
    'BookmarkButton',
    'TagChip',
    'TagList',
    'TagSelector',
    'TagManagerDialog',
    'PolyfillCard',
    'AIFixCard',
]
