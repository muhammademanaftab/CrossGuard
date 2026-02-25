"""Singleton loader for polyfill mappings from polyfill_map.json."""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from ..utils.config import get_logger

logger = get_logger('polyfill.loader')

POLYFILL_MAP_PATH = Path(__file__).parent / "polyfill_map.json"


class PolyfillLoader:
    """Loads and caches polyfill_map.json as a singleton."""

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
        """Load mappings from disk, falling back to empty dicts on error."""
        if not POLYFILL_MAP_PATH.exists():
            logger.warning(f"Polyfill map not found at {POLYFILL_MAP_PATH}")
            self._data = {'javascript': {}, 'css': {}, 'html': {}}
            return

        try:
            with open(POLYFILL_MAP_PATH, 'r', encoding='utf-8') as f:
                self._data = json.load(f)

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
        """Look up polyfill info by Can I Use feature ID, or None."""
        if feature_id in self._data.get('javascript', {}):
            return self._data['javascript'][feature_id]

        if feature_id in self._data.get('css', {}):
            return self._data['css'][feature_id]

        if feature_id in self._data.get('html', {}):
            return self._data['html'][feature_id]

        return None

    def has_polyfill(self, feature_id: str) -> bool:
        """True if the feature has a polyfill or fallback available."""
        polyfill = self.get_polyfill(feature_id)
        if polyfill is None:
            return False

        return polyfill.get('polyfillable', False) or 'fallback' in polyfill

    def is_polyfillable(self, feature_id: str) -> bool:
        """True if the feature can be truly polyfilled (not just a CSS fallback)."""
        polyfill = self.get_polyfill(feature_id)
        return polyfill is not None and polyfill.get('polyfillable', False)

    def get_all_javascript_polyfills(self) -> Dict[str, Dict]:
        return self._data.get('javascript', {}).copy()

    def get_all_css_polyfills(self) -> Dict[str, Dict]:
        return self._data.get('css', {}).copy()

    def get_all_html_polyfills(self) -> Dict[str, Dict]:
        return self._data.get('html', {}).copy()

    def get_metadata(self) -> Dict[str, Any]:
        return self._data.get('metadata', {}).copy()

    def reload(self):
        self._load_data()


_loader: Optional[PolyfillLoader] = None


def get_polyfill_loader() -> PolyfillLoader:
    global _loader
    if _loader is None:
        _loader = PolyfillLoader()
    return _loader
