"""
Configuration module for Cross Guard.

Loads project-level settings from crossguard.config.json
with sensible defaults for CLI and programmatic use.
"""

from .config_manager import ConfigManager, load_config, get_default_config

__all__ = [
    'ConfigManager',
    'load_config',
    'get_default_config',
]
