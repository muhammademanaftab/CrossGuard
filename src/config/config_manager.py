"""Configuration manager for Cross Guard.

Loads settings from a crossguard.config.json file (project-level)
with fallback to sensible defaults. Designed for CLI and programmatic use.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.config import LATEST_VERSIONS

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    'browsers': {
        'chrome': LATEST_VERSIONS['chrome'],
        'firefox': LATEST_VERSIONS['firefox'],
        'safari': LATEST_VERSIONS['safari'],
        'edge': LATEST_VERSIONS['edge'],
    },
    'output': 'table',
    'ignore': [
        'node_modules', 'dist', 'build', '.git',
        '__pycache__', '.next', '.nuxt', 'vendor',
    ],
    'rules': None,  # Path to custom_rules.json (None = use built-in path)
}

CONFIG_FILENAME = 'crossguard.config.json'


class ConfigManager:
    """Manages Cross Guard configuration from file and defaults."""

    def __init__(self, config_path: Optional[str] = None, overrides: Optional[Dict] = None):
        """Initialize configuration manager.

        Args:
            config_path: Explicit path to config file. If None, searches
                         current directory and parents for crossguard.config.json.
            overrides: Dict of values to override file/default config.
        """
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._load(config_path, overrides)

    def _load(self, config_path: Optional[str], overrides: Optional[Dict]):
        """Load configuration with precedence: overrides > file > defaults."""
        # Start with defaults
        self._config = _deep_copy(DEFAULT_CONFIG)

        # Layer file config
        file_config = self._load_from_file(config_path)
        if file_config:
            _deep_merge(self._config, file_config)

        # Layer overrides
        if overrides:
            _deep_merge(self._config, overrides)

    def _load_from_file(self, config_path: Optional[str]) -> Optional[Dict]:
        """Load config from file.

        Args:
            config_path: Explicit path, or None to search.

        Returns:
            Config dict from file, or None if not found.
        """
        if config_path:
            path = Path(config_path)
            if path.is_file():
                self._config_path = path
                return _read_json(path)
            return None

        # Search current directory and parents
        found = _find_config_file(Path.cwd())
        if found:
            self._config_path = found
            return _read_json(found)
        return None

    @property
    def config_path(self) -> Optional[Path]:
        """Path to the loaded config file, or None."""
        return self._config_path

    @property
    def browsers(self) -> Dict[str, str]:
        """Target browsers configuration."""
        return dict(self._config.get('browsers', DEFAULT_CONFIG['browsers']))

    @property
    def output_format(self) -> str:
        """Default output format."""
        return self._config.get('output', 'table')

    @property
    def ignore_patterns(self) -> List[str]:
        """Directory/file patterns to ignore during scanning."""
        return list(self._config.get('ignore', DEFAULT_CONFIG['ignore']))

    @property
    def rules_path(self) -> Optional[str]:
        """Path to custom rules file, or None for built-in."""
        return self._config.get('rules')

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by key."""
        return self._config.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Return a copy of the full config."""
        return _deep_copy(self._config)

    @staticmethod
    def create_default_config(directory: str = '.') -> str:
        """Create a default crossguard.config.json in the given directory.

        Args:
            directory: Directory to create the file in.

        Returns:
            Path to the created file.
        """
        path = Path(directory) / CONFIG_FILENAME
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return str(path)


# ── Module-level convenience functions ────────────────────────────────


def load_config(
    config_path: Optional[str] = None,
    overrides: Optional[Dict] = None,
) -> ConfigManager:
    """Load configuration.

    Args:
        config_path: Explicit path to config file.
        overrides: Dict of values to override.

    Returns:
        ConfigManager instance.
    """
    return ConfigManager(config_path=config_path, overrides=overrides)


def get_default_config() -> Dict[str, Any]:
    """Get the default configuration as a dict."""
    return _deep_copy(DEFAULT_CONFIG)


# ── Helpers ───────────────────────────────────────────────────────────


def _find_config_file(start: Path) -> Optional[Path]:
    """Search start directory and parents for crossguard.config.json."""
    current = start.resolve()
    for _ in range(10):  # Limit depth to avoid infinite loop
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _read_json(path: Path) -> Optional[Dict]:
    """Read and parse a JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _deep_copy(d: Dict) -> Dict:
    """Simple deep copy for JSON-serializable dicts."""
    return json.loads(json.dumps(d))


def _deep_merge(base: Dict, override: Dict):
    """Recursively merge override into base (in-place)."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
