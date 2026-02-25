"""App-wide constants, paths, and logging setup."""
import os
import logging
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
CANIUSE_DIR = PROJECT_ROOT / "caniuse"
CANIUSE_DB_PATH = CANIUSE_DIR / "data.json"
CANIUSE_FEATURES_PATH = CANIUSE_DIR / "features-json"

DATABASE_PATH = PROJECT_ROOT / 'crossguard.db'
DATABASE_HISTORY_LIMIT = 100

DEFAULT_BROWSERS = {
    'chrome': 'Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'edge': 'Edge',
    'ie': 'Internet Explorer',
    'opera': 'Opera'
}

LATEST_VERSIONS = {
    'chrome': '144',
    'firefox': '146',
    'safari': '18.4',
    'edge': '141',
    'ie': '11',
    'opera': '122'
}

SUPPORT_STATUS = {
    'y': 'Fully Supported',
    'a': 'Partially Supported',
    'n': 'Not Supported',
    'p': 'Polyfill Available',
    'u': 'Unknown',
    'x': 'Requires Prefix',
    'd': 'Disabled by Default'
}

STATUS_COLORS = {
    'y': '#4CAF50',
    'a': '#FFC107',
    'n': '#F44336',
    'p': '#2196F3',
    'u': '#9E9E9E',
    'x': '#FF9800',
    'd': '#795548'
}

SEVERITY_LEVELS = {
    'critical': 'Feature not supported in any target browser',
    'high': 'Feature not supported in 50%+ of target browsers',
    'medium': 'Feature partially supported or requires prefix',
    'low': 'Feature fully supported with minor issues'
}

APP_NAME = "Cross Guard"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

ML_ENABLED = False  # Not ready yet — enable after testing

# --- Logging ---

LOG_LEVEL = os.environ.get('CROSSGUARD_LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "crossguard.log"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3


class CrossGuardLogger:
    """Singleton that manages all logging for the app."""

    _instance: Optional['CrossGuardLogger'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if CrossGuardLogger._initialized:
            return
        CrossGuardLogger._initialized = True
        self._loggers: dict = {}
        self._setup_root_logger()

    def _setup_root_logger(self):
        root_logger = logging.getLogger('crossguard')
        root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

        if root_logger.handlers:
            return

        # stderr so we don't pollute piped CLI output
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        root_logger.addHandler(console_handler)

    def _setup_file_handler(self):
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)

            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=LOG_MAX_SIZE,
                backupCount=LOG_BACKUP_COUNT
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

            logging.getLogger('crossguard').addHandler(file_handler)
        except Exception:
            pass  # Not critical — file logging is best-effort

    def get_logger(self, name: str) -> logging.Logger:
        """Get a namespaced logger (e.g. 'parser.css')."""
        full_name = f'crossguard.{name}'
        if full_name not in self._loggers:
            self._loggers[full_name] = logging.getLogger(full_name)
        return self._loggers[full_name]

    def set_level(self, level: str):
        """Change log level for all loggers at once."""
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger('crossguard').setLevel(log_level)

    def enable_file_logging(self):
        self._setup_file_handler()

    def disable_console_output(self):
        """Kill console output (useful in GUI mode)."""
        root_logger = logging.getLogger('crossguard')
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)


_logger_manager = CrossGuardLogger()


def get_logger(name: str) -> logging.Logger:
    """Main way to grab a logger anywhere in the app."""
    return _logger_manager.get_logger(name)


def set_log_level(level: str):
    """Set global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""
    _logger_manager.set_level(level)


def enable_file_logging():
    """Turn on rotating file logging."""
    _logger_manager.enable_file_logging()


def disable_console_logging():
    """Silence console log output."""
    _logger_manager.disable_console_output()
