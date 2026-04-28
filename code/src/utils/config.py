"""App-wide constants, paths, and logging setup."""
import os
import logging
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
CANIUSE_DIR = PROJECT_ROOT / "data" / "caniuse"
CANIUSE_DB_PATH = CANIUSE_DIR / "data.json"
CANIUSE_FEATURES_PATH = CANIUSE_DIR / "features-json"

NPM_REGISTRY_URL = "https://registry.npmjs.org/caniuse-db/latest"

WEB_FEATURES_URL = "https://unpkg.com/web-features/data.json"
WEB_FEATURES_CACHE_DIR = Path.home() / ".crossguard"
WEB_FEATURES_CACHE_PATH = WEB_FEATURES_CACHE_DIR / "web_features.json"

LATEST_VERSIONS = {
    'chrome': '144',
    'firefox': '146',
    'safari': '18.4',
    'edge': '141',
    'ie': '11',
    'opera': '122'
}

LOG_LEVEL = os.environ.get('CROSSGUARD_LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class CrossGuardLogger:
    """Singleton logger. All log messages go to stderr so piped CLI output stays clean."""

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

        # Must use stderr — stdout is reserved for piped CLI output
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        root_logger.addHandler(console_handler)

    def get_logger(self, name: str) -> logging.Logger:
        full_name = f'crossguard.{name}'
        if full_name not in self._loggers:
            self._loggers[full_name] = logging.getLogger(full_name)
        return self._loggers[full_name]

    def set_level(self, level: str):
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger('crossguard').setLevel(log_level)


_logger_manager = CrossGuardLogger()


def get_logger(name: str) -> logging.Logger:
    return _logger_manager.get_logger(name)


def set_log_level(level: str):
    _logger_manager.set_level(level)
