"""Singleton loader for polyfill mappings.

This module loads and caches polyfill mappings from the polyfill_map.json file.
It follows the same singleton pattern as CustomRulesLoader.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from ..utils.config import get_logger

logger = get_logger('polyfill.loader')

# Path to the polyfill map file
POLYFILL_MAP_PATH = Path(__file__).parent / "polyfill_map.json"


class PolyfillLoader:
    """Loads and caches polyfill mappings from JSON."""

    _instance: Optional['PolyfillLoader'] = None
    _loaded: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if PolyfillLoader._loaded:
            return
        PolyfillLoader._loaded = True

        self._data: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self):
        """Load polyfill mappings from JSON file."""
        if not POLYFILL_MAP_PATH.exists():
            logger.warning(f"Polyfill map not found at {POLYFILL_MAP_PATH}")
            self._data = {'javascript': {}, 'css': {}, 'html': {}}
            return

        try:
            with open(POLYFILL_MAP_PATH, 'r', encoding='utf-8') as f:
                self._data = json.load(f)

            # Count loaded polyfills
            js_count = len(self._data.get('javascript', {}))
            css_count = len(self._data.get('css', {}))
            html_count = len(self._data.get('html', {}))
            total = js_count + css_count + html_count

            logger.info(f"Loaded {total} polyfill mappings (JS: {js_count}, CSS: {css_count}, HTML: {html_count})")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in polyfill_map.json: {e}")
            self._data = {'javascript': {}, 'css': {}, 'html': {}}
        except Exception as e:
            logger.error(f"Error loading polyfill mappings: {e}")
            self._data = {'javascript': {}, 'css': {}, 'html': {}}

    def get_polyfill(self, feature_id: str) -> Optional[Dict]:
        """Get polyfill info for a feature ID.

        Args:
            feature_id: Can I Use feature ID (e.g., 'fetch', 'promises', 'css-grid')

        Returns:
            Polyfill info dict or None if not found
        """
        # Check JavaScript features
        if feature_id in self._data.get('javascript', {}):
            return self._data['javascript'][feature_id]

        # Check CSS features
        if feature_id in self._data.get('css', {}):
            return self._data['css'][feature_id]

        # Check HTML features
        if feature_id in self._data.get('html', {}):
            return self._data['html'][feature_id]

        return None

    def has_polyfill(self, feature_id: str) -> bool:
        """Check if a polyfill exists for a feature.

        Args:
            feature_id: Can I Use feature ID

        Returns:
            True if a polyfillable solution exists
        """
        polyfill = self.get_polyfill(feature_id)
        if polyfill is None:
            return False

        # Check if it's polyfillable or has a fallback
        return polyfill.get('polyfillable', False) or 'fallback' in polyfill

    def is_polyfillable(self, feature_id: str) -> bool:
        """Check if a feature can be truly polyfilled (not just fallback).

        Args:
            feature_id: Can I Use feature ID

        Returns:
            True if the feature can be polyfilled with JavaScript
        """
        polyfill = self.get_polyfill(feature_id)
        return polyfill is not None and polyfill.get('polyfillable', False)

    def get_all_javascript_polyfills(self) -> Dict[str, Dict]:
        """Get all JavaScript polyfills."""
        return self._data.get('javascript', {}).copy()

    def get_all_css_polyfills(self) -> Dict[str, Dict]:
        """Get all CSS polyfills/fallbacks."""
        return self._data.get('css', {}).copy()

    def get_all_html_polyfills(self) -> Dict[str, Dict]:
        """Get all HTML polyfills."""
        return self._data.get('html', {}).copy()

    def get_metadata(self) -> Dict[str, Any]:
        """Get polyfill database metadata."""
        return self._data.get('metadata', {}).copy()

    def reload(self):
        """Reload data from disk."""
        self._load_data()


# Singleton instance
_loader: Optional[PolyfillLoader] = None


def get_polyfill_loader() -> PolyfillLoader:
    """Get the singleton PolyfillLoader instance."""
    global _loader
    if _loader is None:
        _loader = PolyfillLoader()
    return _loader
