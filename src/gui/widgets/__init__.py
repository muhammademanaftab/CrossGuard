"""
Custom widgets for Cross Guard GUI (CustomTkinter implementation).
"""

from .drop_zone import DropZone
from .score_card import ScoreCard, CircularProgress
from .browser_card import BrowserCard, StackedBarWidget
from .charts import CompatibilityBarChart, FeatureDistributionChart
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
    'CompatibilityBarChart',
    'FeatureDistributionChart',

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
]
