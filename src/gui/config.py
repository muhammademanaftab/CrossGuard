"""
GUI-specific configuration for Cross Guard frontend.

This module contains configuration settings specific to the GUI layer.
It should NOT import from backend modules.
"""

from pathlib import Path

# =============================================================================
# Application Window Settings
# =============================================================================

APP_NAME = "Cross Guard"
APP_VERSION = "1.0.0"

# Window dimensions
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 850
WINDOW_DEFAULT_WIDTH = 1100
WINDOW_DEFAULT_HEIGHT = 900

# =============================================================================
# UI Theme Colors
# =============================================================================

COLORS = {
    # Primary colors
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'primary_light': '#BBDEFB',

    # Status colors
    'success': '#4CAF50',
    'success_dark': '#45a049',
    'warning': '#FF9800',
    'warning_dark': '#e68900',
    'danger': '#F44336',
    'danger_dark': '#da190b',

    # Text colors
    'text_primary': '#333333',
    'text_secondary': '#555555',
    'text_muted': '#666666',

    # Background colors
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'surface_alt': '#f9f9f9',

    # Border colors
    'border': '#E0E0E0',
    'border_light': '#dddddd',
}

# =============================================================================
# UI Spacing
# =============================================================================

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
}

# =============================================================================
# Font Settings
# =============================================================================

FONTS = {
    'size_small': 12,
    'size_normal': 13,
    'size_medium': 14,
    'size_large': 16,
    'size_title': 20,
    'size_header': 24,
}

# =============================================================================
# Asset Paths
# =============================================================================

GUI_DIR = Path(__file__).parent
ASSETS_DIR = GUI_DIR / "assets"
LOGO_PATH = GUI_DIR / "logo.png"

# =============================================================================
# Export Settings
# =============================================================================

EXPORT_FORMATS = ['PDF', 'JSON']
DEFAULT_EXPORT_FORMAT = 'PDF'

# =============================================================================
# Animation Settings
# =============================================================================

ANIMATION = {
    'fade_duration': 300,
    'slide_duration': 200,
    'progress_duration': 600,
}
