"""App-level settings."""

from pathlib import Path

APP_NAME = "Cross Guard"
APP_VERSION = "1.0.0"

GUI_DIR = Path(__file__).parent
ASSETS_DIR = GUI_DIR / "assets"
LOGO_PATH = GUI_DIR / "logo.png"

EXPORT_FORMATS = ['PDF', 'JSON']
DEFAULT_EXPORT_FORMAT = 'PDF'
