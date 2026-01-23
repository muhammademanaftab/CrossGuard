"""
GUI-specific configuration for Cross Guard frontend.

This module contains configuration settings specific to the GUI layer.
It should NOT import from backend modules.

Note: Most theme settings have been moved to theme.py for the CustomTkinter
implementation. This file is kept for backward compatibility and
application-level settings.
"""

from pathlib import Path

# =============================================================================
# Application Info
# =============================================================================

APP_NAME = "Cross Guard"
APP_VERSION = "1.0.0"

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
# Re-export theme settings for backward compatibility
# =============================================================================

from .theme import (
    COLORS,
    FONTS,
    SPACING,
    ANIMATION,
    WINDOW,
    get_color,
    get_score_color,
    configure_ctk_theme,
)
