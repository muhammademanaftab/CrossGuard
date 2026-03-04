"""Web Features (Baseline) integration — maps Can I Use IDs to W3C Baseline status."""

import json
import os
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

from src.utils.config import WEB_FEATURES_URL, WEB_FEATURES_CACHE_PATH, WEB_FEATURES_CACHE_DIR, get_logger

logger = get_logger('analyzer.web_features')


class BaselineInfo:
    """Baseline status for a single feature."""
    __slots__ = ('status', 'low_date', 'high_date')

    def __init__(self, status: str, low_date: Optional[str] = None, high_date: Optional[str] = None):
        self.status = status       # "high", "low", "limited"
        self.low_date = low_date
        self.high_date = high_date

    def to_dict(self) -> dict:
        return {'status': self.status, 'low_date': self.low_date, 'high_date': self.high_date}


class WebFeaturesManager:
    """Downloads, caches, and queries the web-features dataset."""

    def __init__(self):
        self._reverse_map: Optional[Dict[str, BaselineInfo]] = None

    def download(self) -> bool:
        """Fetch the latest web-features data.json from unpkg and cache it."""
        try:
            req = Request(WEB_FEATURES_URL, headers={'Accept': 'application/json'})
            with urlopen(req, timeout=30) as resp:
                data = resp.read()

            # Validate it's valid JSON
            json.loads(data)

            WEB_FEATURES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(WEB_FEATURES_CACHE_PATH, 'wb') as f:
                f.write(data)

            self._reverse_map = None  # force rebuild
            logger.info("Web features data downloaded successfully")
            return True

        except (URLError, OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to download web features data: {e}")
            return False

    def _load_cache(self) -> Optional[dict]:
        """Load the cached web-features data."""
        try:
            if WEB_FEATURES_CACHE_PATH.exists():
                with open(WEB_FEATURES_CACHE_PATH, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load web features cache: {e}")
        return None

    def _build_reverse_map(self) -> Dict[str, BaselineInfo]:
        """Build {caniuse_id: BaselineInfo} from the web-features data."""
        data = self._load_cache()
        if not data:
            return {}

        reverse_map: Dict[str, BaselineInfo] = {}

        # web-features structure: top-level keys are feature names, each has caniuse + status
        for _feature_name, feature_data in data.items():
            if not isinstance(feature_data, dict):
                continue

            caniuse_ids = feature_data.get('caniuse')
            if not caniuse_ids:
                continue

            status_data = feature_data.get('status', {})
            if not isinstance(status_data, dict):
                continue

            baseline = status_data.get('baseline')
            if baseline == 'high':
                status = 'high'
            elif baseline == 'low':
                status = 'low'
            elif baseline is False or baseline is None:
                status = 'limited'
            else:
                status = 'limited'

            info = BaselineInfo(
                status=status,
                low_date=status_data.get('baseline_low_date'),
                high_date=status_data.get('baseline_high_date'),
            )

            if isinstance(caniuse_ids, list):
                for cid in caniuse_ids:
                    reverse_map[cid] = info
            elif isinstance(caniuse_ids, str):
                reverse_map[caniuse_ids] = info

        return reverse_map

    def _ensure_loaded(self):
        if self._reverse_map is None:
            self._reverse_map = self._build_reverse_map()

    def get_baseline_status(self, caniuse_id: str) -> Optional[BaselineInfo]:
        """Look up the Baseline status for a single Can I Use feature ID."""
        self._ensure_loaded()
        return self._reverse_map.get(caniuse_id)

    def get_baseline_summary(self, feature_ids: List[str]) -> dict:
        """Compute Baseline summary counts for a list of Can I Use feature IDs."""
        self._ensure_loaded()

        widely = 0
        newly = 0
        limited = 0
        unknown = 0

        for fid in feature_ids:
            info = self._reverse_map.get(fid)
            if info is None:
                unknown += 1
            elif info.status == 'high':
                widely += 1
            elif info.status == 'low':
                newly += 1
            else:
                limited += 1

        return {
            'widely_available': widely,
            'newly_available': newly,
            'limited': limited,
            'unknown': unknown,
        }

    def has_data(self) -> bool:
        """Check if cached web-features data exists."""
        return WEB_FEATURES_CACHE_PATH.exists()

    def get_feature_count(self) -> int:
        """Number of Can I Use IDs with Baseline mappings."""
        self._ensure_loaded()
        return len(self._reverse_map)
