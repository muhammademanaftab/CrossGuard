"""Configuration settings for Cross Guard."""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CANIUSE_DIR = PROJECT_ROOT / "caniuse"
CANIUSE_DB_PATH = CANIUSE_DIR / "data.json"
CANIUSE_FEATURES_PATH = CANIUSE_DIR / "features-json"

# Target browsers (can be customized by user)
DEFAULT_BROWSERS = {
    'chrome': 'Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'edge': 'Edge',
    'ie': 'Internet Explorer',
    'opera': 'Opera'
}

# Browser version mapping (latest versions as of database)
LATEST_VERSIONS = {
    'chrome': '144',
    'firefox': '146',
    'safari': '18.4',
    'edge': '141',
    'ie': '11',
    'opera': '122'
}

# Support status meanings
SUPPORT_STATUS = {
    'y': 'Fully Supported',
    'a': 'Partially Supported',
    'n': 'Not Supported',
    'p': 'Polyfill Available',
    'u': 'Unknown',
    'x': 'Requires Prefix',
    'd': 'Disabled by Default'
}

# Support status colors for UI
STATUS_COLORS = {
    'y': '#4CAF50',  # Green
    'a': '#FFC107',  # Amber
    'n': '#F44336',  # Red
    'p': '#2196F3',  # Blue
    'u': '#9E9E9E',  # Grey
    'x': '#FF9800',  # Orange
    'd': '#795548'   # Brown
}

# Severity levels
SEVERITY_LEVELS = {
    'critical': 'Feature not supported in any target browser',
    'high': 'Feature not supported in 50%+ of target browsers',
    'medium': 'Feature partially supported or requires prefix',
    'low': 'Feature fully supported with minor issues'
}

# Application settings
APP_NAME = "Cross Guard"
APP_VERSION = "0.1.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
