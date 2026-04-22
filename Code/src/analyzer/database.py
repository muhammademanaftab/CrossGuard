"""Loads and queries the Can I Use database for feature support lookups."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

from ..utils.config import CANIUSE_DB_PATH, CANIUSE_FEATURES_PATH, get_logger

logger = get_logger('analyzer.database')


class CanIUseDatabase:

    def __init__(self):
        self.data = None
        self.features = {}
        self.feature_index = {}  # keyword -> feature ID(s)
        self.loaded = False
        
    def load(self) -> bool:
        try:
            logger.info(f"Loading Can I Use database from {CANIUSE_DB_PATH}...")
            with open(CANIUSE_DB_PATH, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            self._load_feature_files()
            self._build_index()

            self.loaded = True
            logger.info(f"Loaded {len(self.features)} features successfully")
            return True

        except FileNotFoundError:
            logger.error(f"Database file not found at {CANIUSE_DB_PATH}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in database file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return False
    
    def _load_feature_files(self):
        features_path = Path(CANIUSE_FEATURES_PATH)

        if not features_path.exists():
            logger.warning(f"Features directory not found at {features_path}")
            return

        feature_files = list(features_path.glob('*.json'))
        logger.debug(f"Loading {len(feature_files)} feature files...")

        for feature_file in feature_files:
            try:
                with open(feature_file, 'r', encoding='utf-8') as f:
                    feature_data = json.load(f)
                    feature_id = feature_file.stem
                    self.features[feature_id] = feature_data
            except Exception as e:
                logger.warning(f"Could not load {feature_file.name}: {e}")
    
    def _build_index(self):
        logger.debug("Building search index...")

        for feature_id, feature_data in self.features.items():
            self.feature_index[feature_id] = feature_id

            if 'keywords' in feature_data:
                keywords = feature_data['keywords'].split(',')
                for keyword in keywords:
                    keyword = keyword.strip().lower()
                    if keyword not in self.feature_index:
                        self.feature_index[keyword] = []
                    if isinstance(self.feature_index[keyword], list):
                        self.feature_index[keyword].append(feature_id)
                    else:
                        self.feature_index[keyword] = [self.feature_index[keyword], feature_id]
            
            if 'title' in feature_data:
                title_words = feature_data['title'].lower().split()
                for word in title_words:
                    if word not in ['the', 'a', 'an', 'and', 'or', 'for', 'of', 'in']:
                        if word not in self.feature_index:
                            self.feature_index[word] = []
                        if isinstance(self.feature_index[word], list):
                            if feature_id not in self.feature_index[word]:
                                self.feature_index[word].append(feature_id)
        
        logger.debug(f"Index built with {len(self.feature_index)} entries")
    
    def _ensure_loaded(self):
        if not self.loaded:
            self.load()

    def get_feature(self, feature_id: str) -> Optional[Dict]:
        self._ensure_loaded()
        
        return self.features.get(feature_id)
    
    def check_support(self, feature_id: str, browser: str, version: str) -> str:
        """Returns a single status char: y/a/n/p/u/x/d"""
        feature = self.get_feature(feature_id)
        
        if not feature or 'stats' not in feature:
            return 'u'
        
        stats = feature['stats']
        
        if browser not in stats:
            return 'u'
        
        browser_stats = stats[browser]
        
        if version in browser_stats:
            return self._parse_support_status(browser_stats[version])

        # exact version not in DB — fall back to nearest
        return self._find_closest_version_support(browser_stats, version)
    
    def _parse_support_status(self, status: str) -> str:
        """Strips note flags like 'a x #2' down to the primary char"""
        if not status:
            return 'u'
        
        return status.strip()[0]
    
    def _find_closest_version_support(self, browser_stats: Dict, target_version: str) -> str:
        try:
            target_num = float(target_version)
        except ValueError:
            return 'u'

        closest_version = None
        min_diff = float('inf')
        
        for version in browser_stats.keys():
            try:
                version_num = float(version.split('-')[0])  # ranges like "15.2-15.3"
                diff = abs(version_num - target_num)
                
                if diff < min_diff:
                    min_diff = diff
                    closest_version = version
            except ValueError:
                continue
        
        if closest_version:
            return self._parse_support_status(browser_stats[closest_version])
        
        return 'u'
    
    def get_all_features(self) -> List[str]:
        self._ensure_loaded()

        return list(self.features.keys())
    
    def get_feature_info(self, feature_id: str) -> Optional[Dict]:
        feature = self.get_feature(feature_id)
        
        if not feature:
            return None
        
        return {
            'id': feature_id,
            'title': feature.get('title', 'Unknown'),
            'description': feature.get('description', 'No description available'),
            'spec': feature.get('spec', ''),
            'status': feature.get('status', 'unknown'),
            'categories': feature.get('categories', []),
            'keywords': feature.get('keywords', ''),
            'bugs': feature.get('bugs', [])
        }
    
    @lru_cache(maxsize=1000)
    def get_browser_versions(self, browser: str) -> List[str]:
        if not self.features:
            return []

        # all features share the same browser version list in the caniuse schema
        first_feature = next(iter(self.features.values()))
        
        if 'stats' not in first_feature or browser not in first_feature['stats']:
            return []
        
        return list(first_feature['stats'][browser].keys())
    

_database_instance = None


def get_database() -> CanIUseDatabase:
    global _database_instance
    
    if _database_instance is None:
        _database_instance = CanIUseDatabase()
        _database_instance.load()
    
    return _database_instance


def reload_database() -> CanIUseDatabase:
    """Discards the cached instance and reloads from disk — call after an update"""
    global _database_instance
    
    logger.info("Reloading database from disk...")
    _database_instance = None
    return get_database()
