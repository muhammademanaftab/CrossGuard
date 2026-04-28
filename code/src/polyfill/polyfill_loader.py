"""Singleton polyfill map loader."""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from ..utils.config import get_logger

logger = get_logger('polyfill.loader')

POLYFILL_MAP_PATH = Path(__file__).parent / "polyfill_map.json"


class PolyfillLoader:
    """Reads polyfill_map.json once and keeps the data in memory for fast lookups."""

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
        if feature_id in self._data.get('javascript', {}):
            return self._data['javascript'][feature_id]

        if feature_id in self._data.get('css', {}):
            return self._data['css'][feature_id]

        if feature_id in self._data.get('html', {}):
            return self._data['html'][feature_id]

        return None

    def reload(self):
        self._load_data()


_loader: Optional[PolyfillLoader] = None


def get_polyfill_loader() -> PolyfillLoader:
    global _loader
    if _loader is None:
        _loader = PolyfillLoader()
    return _loader


def load_polyfill_map() -> Dict:
    try:
        with open(POLYFILL_MAP_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'metadata': {}, 'javascript': {}, 'css': {}, 'html': {}}


def save_polyfill_map(data: Dict) -> bool:
    try:
        with open(POLYFILL_MAP_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        get_polyfill_loader().reload()
        return True
    except Exception as e:
        logger.error(f"Error saving polyfill map: {e}")
        return False
