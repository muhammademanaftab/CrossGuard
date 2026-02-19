"""Configuration settings for Cross Guard."""
import os
import logging
import sys
from pathlib import Path
from typing import Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CANIUSE_DIR = PROJECT_ROOT / "caniuse"
CANIUSE_DB_PATH = CANIUSE_DIR / "data.json"
CANIUSE_FEATURES_PATH = CANIUSE_DIR / "features-json"

# Database configuration
DATABASE_PATH = PROJECT_ROOT / 'crossguard.db'
DATABASE_HISTORY_LIMIT = 100  # Max history items to display

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
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Feature flags
ML_ENABLED = False  # Disable ML features for now (will enable after testing)

# =============================================================================
# Logging Configuration
# =============================================================================

# Logging levels
LOG_LEVEL = os.environ.get('CROSSGUARD_LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Log file settings
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "crossguard.log"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3


class CrossGuardLogger:
    """Centralized logging manager for Cross Guard.

    Provides consistent logging across all modules with support for
    both console and file output.
    """

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
        """Set up the root logger with console handler."""
        root_logger = logging.getLogger('crossguard')
        root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

        # Prevent duplicate handlers
        if root_logger.handlers:
            return

        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    def _setup_file_handler(self):
        """Set up file handler for persistent logging."""
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)

            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=LOG_MAX_SIZE,
                backupCount=LOG_BACKUP_COUNT
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
            file_handler.setFormatter(file_formatter)

            root_logger = logging.getLogger('crossguard')
            root_logger.addHandler(file_handler)
        except Exception:
            # Silently fail if file logging cannot be set up
            pass

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger for a specific module.

        Args:
            name: Logger name (typically module name)

        Returns:
            Configured logger instance
        """
        full_name = f'crossguard.{name}'
        if full_name not in self._loggers:
            self._loggers[full_name] = logging.getLogger(full_name)
        return self._loggers[full_name]

    def set_level(self, level: str):
        """Set logging level for all loggers.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger('crossguard').setLevel(log_level)

    def enable_file_logging(self):
        """Enable persistent file logging."""
        self._setup_file_handler()

    def disable_console_output(self):
        """Disable console output (useful for GUI mode)."""
        root_logger = logging.getLogger('crossguard')
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)


# Global logger manager instance
_logger_manager = CrossGuardLogger()


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    This is the main entry point for getting loggers throughout the application.

    Args:
        name: Module name (e.g., 'parser.css', 'analyzer.main')

    Returns:
        Configured logger instance

    Example:
        >>> from src.utils.config import get_logger
        >>> logger = get_logger('analyzer.main')
        >>> logger.info('Starting analysis...')
    """
    return _logger_manager.get_logger(name)


def set_log_level(level: str):
    """Set the global logging level.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    _logger_manager.set_level(level)


def enable_file_logging():
    """Enable file-based logging."""
    _logger_manager.enable_file_logging()


def disable_console_logging():
    """Disable console output for logging."""
    _logger_manager.disable_console_output()
