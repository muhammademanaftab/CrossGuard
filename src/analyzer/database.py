"""Can I Use Database Loader and Query Engine.

This module provides efficient loading and querying of the Can I Use database.
It handles feature lookups, browser compatibility checks, and data caching.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from functools import lru_cache

from ..utils.config import CANIUSE_DB_PATH, CANIUSE_FEATURES_PATH, SUPPORT_STATUS


class CanIUseDatabase:
    """Main database loader and query interface for Can I Use data."""
    
    def __init__(self):
        """Initialize the database loader."""
        self.data = None
        self.features = {}
        self.feature_index = {}  # Fast lookup by keyword
        self.loaded = False
        
    def load(self) -> bool:
        """Load the Can I Use database into memory.
        
        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        try:
            # Load main data.json file
            print(f"Loading Can I Use database from {CANIUSE_DB_PATH}...")
            with open(CANIUSE_DB_PATH, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Load individual feature files for detailed information
            self._load_feature_files()
            
            # Build search index
            self._build_index()
            
            self.loaded = True
            print(f"✓ Loaded {len(self.features)} features successfully")
            return True
            
        except FileNotFoundError:
            print(f"✗ Error: Database file not found at {CANIUSE_DB_PATH}")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON in database file: {e}")
            return False
        except Exception as e:
            print(f"✗ Error loading database: {e}")
            return False
    
    def _load_feature_files(self):
        """Load individual feature JSON files from features-json directory."""
        features_path = Path(CANIUSE_FEATURES_PATH)
        
        if not features_path.exists():
            print(f"Warning: Features directory not found at {features_path}")
            return
        
        # Load each feature file
        feature_files = list(features_path.glob('*.json'))
        print(f"Loading {len(feature_files)} feature files...")
        
        for feature_file in feature_files:
            try:
                with open(feature_file, 'r', encoding='utf-8') as f:
                    feature_data = json.load(f)
                    feature_id = feature_file.stem  # filename without .json
                    self.features[feature_id] = feature_data
            except Exception as e:
                print(f"Warning: Could not load {feature_file.name}: {e}")
    
    def _build_index(self):
        """Build search index for fast keyword lookups."""
        print("Building search index...")
        
        for feature_id, feature_data in self.features.items():
            # Index by feature ID
            self.feature_index[feature_id] = feature_id
            
            # Index by keywords if available
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
            
            # Index by title words
            if 'title' in feature_data:
                title_words = feature_data['title'].lower().split()
                for word in title_words:
                    # Remove common words
                    if word not in ['the', 'a', 'an', 'and', 'or', 'for', 'of', 'in']:
                        if word not in self.feature_index:
                            self.feature_index[word] = []
                        if isinstance(self.feature_index[word], list):
                            if feature_id not in self.feature_index[word]:
                                self.feature_index[word].append(feature_id)
        
        print(f"✓ Index built with {len(self.feature_index)} entries")
    
    def get_feature(self, feature_id: str) -> Optional[Dict]:
        """Get detailed information about a specific feature.
        
        Args:
            feature_id: The feature identifier (e.g., 'flexbox', 'css-grid')
            
        Returns:
            Dict containing feature data, or None if not found.
        """
        if not self.loaded:
            raise RuntimeError("Database not loaded. Call load() first.")
        
        return self.features.get(feature_id)
    
    def check_support(self, feature_id: str, browser: str, version: str) -> str:
        """Check if a feature is supported in a specific browser version.
        
        Args:
            feature_id: The feature identifier
            browser: Browser name (e.g., 'chrome', 'firefox')
            version: Browser version (e.g., '144', '146')
            
        Returns:
            Support status: 'y', 'a', 'n', 'p', 'u', 'x', 'd'
            - y: Fully supported
            - a: Partially supported
            - n: Not supported
            - p: Polyfill available
            - u: Unknown
            - x: Requires prefix
            - d: Disabled by default
        """
        feature = self.get_feature(feature_id)
        
        if not feature or 'stats' not in feature:
            return 'u'  # Unknown
        
        stats = feature['stats']
        
        if browser not in stats:
            return 'u'
        
        browser_stats = stats[browser]
        
        # Try exact version match
        if version in browser_stats:
            return self._parse_support_status(browser_stats[version])
        
        # Try to find closest version
        return self._find_closest_version_support(browser_stats, version)
    
    def _parse_support_status(self, status: str) -> str:
        """Parse support status string and return primary status.
        
        Can I Use uses compound statuses like 'a x #2' meaning:
        - a: partial support
        - x: requires prefix
        - #2: see note 2
        
        Args:
            status: Raw status string from database
            
        Returns:
            Primary support status character
        """
        if not status:
            return 'u'
        
        # Take first character as primary status
        return status.strip()[0]
    
    def _find_closest_version_support(self, browser_stats: Dict, target_version: str) -> str:
        """Find support status for closest available version.
        
        Args:
            browser_stats: Browser version support data
            target_version: Target version to check
            
        Returns:
            Support status for closest version
        """
        try:
            target_num = float(target_version)
        except ValueError:
            # If version is not numeric, return unknown
            return 'u'
        
        # Find closest version
        closest_version = None
        min_diff = float('inf')
        
        for version in browser_stats.keys():
            try:
                version_num = float(version.split('-')[0])  # Handle ranges like "15.2-15.3"
                diff = abs(version_num - target_num)
                
                if diff < min_diff:
                    min_diff = diff
                    closest_version = version
            except ValueError:
                continue
        
        if closest_version:
            return self._parse_support_status(browser_stats[closest_version])
        
        return 'u'
    
    def check_multiple_browsers(self, feature_id: str, browsers: Dict[str, str]) -> Dict[str, str]:
        """Check feature support across multiple browsers.
        
        Args:
            feature_id: The feature identifier
            browsers: Dict mapping browser names to versions
                     e.g., {'chrome': '144', 'firefox': '146'}
        
        Returns:
            Dict mapping browser names to support status
        """
        results = {}
        
        for browser, version in browsers.items():
            results[browser] = self.check_support(feature_id, browser, version)
        
        return results
    
    def search_features(self, query: str) -> List[str]:
        """Search for features by keyword or title.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching feature IDs
        """
        if not self.loaded:
            raise RuntimeError("Database not loaded. Call load() first.")
        
        query = query.lower().strip()
        results = set()
        
        # Direct feature ID match
        if query in self.features:
            results.add(query)
        
        # Search in index
        if query in self.feature_index:
            indexed = self.feature_index[query]
            if isinstance(indexed, str):
                results.add(indexed)
            elif isinstance(indexed, list):
                results.update(indexed)
        
        # Partial match in feature IDs
        for feature_id in self.features.keys():
            if query in feature_id.lower():
                results.add(feature_id)
        
        # Search in titles and descriptions
        for feature_id, feature_data in self.features.items():
            if 'title' in feature_data and query in feature_data['title'].lower():
                results.add(feature_id)
            if 'description' in feature_data and query in feature_data['description'].lower():
                results.add(feature_id)
        
        return list(results)
    
    def get_all_features(self) -> List[str]:
        """Get list of all available feature IDs.
        
        Returns:
            List of feature IDs
        """
        if not self.loaded:
            raise RuntimeError("Database not loaded. Call load() first.")
        
        return list(self.features.keys())
    
    def get_feature_categories(self) -> Dict[str, List[str]]:
        """Get features grouped by category.
        
        Returns:
            Dict mapping category names to lists of feature IDs
        """
        categories = {}
        
        for feature_id, feature_data in self.features.items():
            if 'categories' in feature_data:
                for category in feature_data['categories']:
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(feature_id)
        
        return categories
    
    def get_feature_info(self, feature_id: str) -> Optional[Dict]:
        """Get human-readable information about a feature.
        
        Args:
            feature_id: The feature identifier
            
        Returns:
            Dict with title, description, spec URL, and status
        """
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
        """Get all available versions for a browser.
        
        Args:
            browser: Browser name
            
        Returns:
            List of version strings
        """
        if not self.features:
            return []
        
        # Get versions from first feature (all features have same browser versions)
        first_feature = next(iter(self.features.values()))
        
        if 'stats' not in first_feature or browser not in first_feature['stats']:
            return []
        
        return list(first_feature['stats'][browser].keys())
    
    def get_statistics(self) -> Dict:
        """Get database statistics.
        
        Returns:
            Dict with database statistics
        """
        if not self.loaded:
            return {'loaded': False}
        
        categories = self.get_feature_categories()
        
        return {
            'loaded': True,
            'total_features': len(self.features),
            'total_categories': len(categories),
            'categories': {cat: len(features) for cat, features in categories.items()},
            'index_size': len(self.feature_index)
        }


# Singleton instance
_database_instance = None


def get_database() -> CanIUseDatabase:
    """Get or create the singleton database instance.
    
    Returns:
        CanIUseDatabase instance
    """
    global _database_instance
    
    if _database_instance is None:
        _database_instance = CanIUseDatabase()
        _database_instance.load()
    
    return _database_instance
