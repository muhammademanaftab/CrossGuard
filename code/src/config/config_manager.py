"""Loads settings from crossguard.config.json with fallback to defaults."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.config import LATEST_VERSIONS

DEFAULT_CONFIG: Dict[str, Any] = {
    'browsers': {
        'chrome': LATEST_VERSIONS['chrome'],
        'firefox': LATEST_VERSIONS['firefox'],
        'safari': LATEST_VERSIONS['safari'],
        'edge': LATEST_VERSIONS['edge'],
    },
    'output': 'table',
    'ai': {
        'api_key': '',
        'provider': '',
        'model': '',
    },
}

CONFIG_FILENAME = 'crossguard.config.json'


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None, overrides: Optional[Dict] = None):
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._load(config_path, overrides)

    def _load(self, config_path: Optional[str], overrides: Optional[Dict]):
        # Precedence: overrides > file > defaults
        self._config = _deep_copy(DEFAULT_CONFIG)

        file_config = self._load_from_file(config_path)
        if file_config:
            _deep_merge(self._config, file_config)

        if overrides:
            _deep_merge(self._config, overrides)

    def _load_from_file(self, config_path: Optional[str]) -> Optional[Dict]:
        if config_path:
            path = Path(config_path)
            if path.is_file():
                self._config_path = path
                return _read_json(path)
            return None

        found = _find_config_file(Path.cwd())
        if found:
            self._config_path = found
            return _read_json(found)

        pkg_config = _load_from_package_json(Path.cwd())
        if pkg_config is not None:
            return pkg_config

        return None

    @property
    def config_path(self) -> Optional[Path]:
        return self._config_path

    @property
    def browsers(self) -> Dict[str, str]:
        return dict(self._config.get('browsers', DEFAULT_CONFIG['browsers']))

    @property
    def output_format(self) -> str:
        return self._config.get('output', 'table')

    @property
    def ai_config(self) -> Dict[str, str]:
        return dict(self._config.get('ai', {}))

    def to_dict(self) -> Dict[str, Any]:
        return _deep_copy(self._config)

    @staticmethod
    def create_default_config(directory: str = '.') -> str:
        path = Path(directory) / CONFIG_FILENAME
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return str(path)


def load_config(
    config_path: Optional[str] = None,
    overrides: Optional[Dict] = None,
) -> ConfigManager:
    return ConfigManager(config_path=config_path, overrides=overrides)


def _find_config_file(start: Path) -> Optional[Path]:
    """Walk up from the start directory looking for crossguard.config.json."""
    current = start.resolve()
    for _ in range(10):  # cap depth so we don't crawl forever
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _read_json(path: Path) -> Optional[Dict]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _load_from_package_json(start: Path) -> Optional[Dict]:
    """Walk up looking for a package.json that has a "crossguard" key."""
    current = start.resolve()
    for _ in range(10):
        candidate = current / 'package.json'
        if candidate.is_file():
            data = _read_json(candidate)
            if data and isinstance(data.get('crossguard'), dict):
                return data['crossguard']
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _deep_copy(d: Dict) -> Dict:
    return json.loads(json.dumps(d))


def _deep_merge(base: Dict, override: Dict):
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
