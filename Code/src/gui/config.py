"""App-level settings. Theme constants live in theme.py -- this re-exports them for old import paths."""

from pathlib import Path

APP_NAME = "Cross Guard"
APP_VERSION = "1.0.0"

GUI_DIR = Path(__file__).parent
ASSETS_DIR = GUI_DIR / "assets"
LOGO_PATH = GUI_DIR / "logo.png"

EXPORT_FORMATS = ['PDF', 'JSON']
DEFAULT_EXPORT_FORMAT = 'PDF'


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
