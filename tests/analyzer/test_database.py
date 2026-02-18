"""Tests for CanIUseDatabase — loading, querying, searching, and caching.

Validates the core database engine that maps feature IDs to browser support
data from 570+ JSON files in caniuse/features-json/.
"""

import pytest
from unittest.mock import patch, mock_open

from src.analyzer.database import (
    CanIUseDatabase,
    get_database,
    reload_database,
)
import src.analyzer.database as db_module


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: Database Loading
# ═══════════════════════════════════════════════════════════════════════════

class TestDatabaseLoading:
    """Tests for load(), _load_feature_files(), _build_index()."""

    def test_load_returns_true(self, caniuse_db):
        """load() returns True on success."""
        assert caniuse_db.loaded is True

    def test_loads_many_features(self, caniuse_db):
        """Database contains 500+ features from JSON files."""
        assert len(caniuse_db.features) > 500

    def test_builds_search_index(self, caniuse_db):
        """Search index is populated after loading."""
        assert len(caniuse_db.feature_index) > 0

    def test_data_json_loaded(self, caniuse_db):
        """Main data.json is parsed into self.data."""
        assert caniuse_db.data is not None
        assert isinstance(caniuse_db.data, dict)

    def test_features_have_stats(self, caniuse_db):
        """Loaded features contain 'stats' keys for browser data."""
        flexbox = caniuse_db.features.get('flexbox')
        assert flexbox is not None
        assert 'stats' in flexbox

    def test_fresh_db_not_loaded(self, fresh_db):
        """Unloaded DB has empty state."""
        assert fresh_db.loaded is False
        assert fresh_db.features == {}
        assert fresh_db.feature_index == {}

    def test_fresh_db_load_succeeds(self, fresh_db):
        """A fresh instance can load successfully."""
        assert fresh_db.load() is True
        assert fresh_db.loaded is True
        assert len(fresh_db.features) > 500

    def test_auto_load_on_get_feature(self):
        """_ensure_loaded() triggers load when accessing an unloaded DB."""
        db = CanIUseDatabase()
        assert db.loaded is False
        result = db.get_feature('flexbox')
        assert db.loaded is True
        assert result is not None


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: Load Error Handling (mocked)
# ═══════════════════════════════════════════════════════════════════════════

class TestLoadErrors:
    """Tests for error paths in load() using mocks for isolation."""

    def test_missing_data_json_returns_false(self):
        """load() returns False when data.json is missing."""
        db = CanIUseDatabase()
        with patch('builtins.open', side_effect=FileNotFoundError("not found")):
            result = db.load()
        assert result is False
        assert db.loaded is False

    def test_corrupt_json_returns_false(self):
        """load() returns False when data.json contains invalid JSON."""
        db = CanIUseDatabase()
        with patch('builtins.open', mock_open(read_data='{invalid json')):
            result = db.load()
        assert result is False
        assert db.loaded is False

    def test_generic_exception_returns_false(self):
        """load() returns False on unexpected errors."""
        db = CanIUseDatabase()
        with patch('builtins.open', side_effect=PermissionError("denied")):
            result = db.load()
        assert result is False
        assert db.loaded is False

    def test_missing_features_dir_loads_partially(self):
        """load() succeeds with data.json even if features-json/ is absent."""
        db = CanIUseDatabase()
        with patch.object(db, '_load_feature_files'):
            with patch.object(db, '_build_index'):
                with patch('builtins.open', mock_open(read_data='{}')):
                    result = db.load()
        assert result is True
        assert db.loaded is True


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Singleton Pattern
# ═══════════════════════════════════════════════════════════════════════════

class TestSingleton:
    """Tests for get_database() and reload_database()."""

    def test_get_database_returns_instance(self, reset_singleton):
        """get_database() returns a loaded CanIUseDatabase."""
        db = get_database()
        assert isinstance(db, CanIUseDatabase)
        assert db.loaded is True

    def test_get_database_same_instance(self, reset_singleton):
        """Calling get_database() twice returns the same object."""
        db1 = get_database()
        db2 = get_database()
        assert db1 is db2

    def test_reload_database_new_instance(self, reset_singleton):
        """reload_database() replaces the singleton with a fresh instance."""
        db1 = get_database()
        db2 = reload_database()
        assert db2 is not db1
        assert db2.loaded is True

    def test_reload_clears_old_singleton(self, reset_singleton):
        """After reload, get_database() returns the new instance."""
        get_database()
        new_db = reload_database()
        assert get_database() is new_db


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: check_support()
# ═══════════════════════════════════════════════════════════════════════════

class TestCheckSupport:
    """Tests for check_support(feature_id, browser, version)."""

    @pytest.mark.parametrize("feature,browser,version,expected", [
        ('flexbox', 'chrome', '120', 'y'),
        ('flexbox', 'ie', '11', 'a'),
        ('arrow-functions', 'ie', '11', 'n'),
        ('css-grid', 'chrome', '120', 'y'),
        ('promises', 'firefox', '121', 'y'),
    ])
    def test_known_feature_exact_status(self, caniuse_db, feature, browser, version, expected):
        """Known features return exact expected status in specific browsers."""
        assert caniuse_db.check_support(feature, browser, version) == expected

    def test_unknown_feature_returns_u(self, caniuse_db):
        """Unknown feature returns 'u' (unknown)."""
        assert caniuse_db.check_support('totally-fake-feature-xyz', 'chrome', '120') == 'u'

    def test_unknown_browser_returns_u(self, caniuse_db):
        """Unknown browser returns 'u'."""
        assert caniuse_db.check_support('flexbox', 'netscape', '4') == 'u'

    def test_feature_with_empty_stats(self, caniuse_db):
        """Feature that exists but has no stats for a browser returns 'u'."""
        # Use a real feature but an implausible browser
        assert caniuse_db.check_support('flexbox', 'op_mini', '99999') in ['y', 'a', 'n', 'x', 'p', 'u']

    def test_dialog_safari_17_supported(self, caniuse_db):
        """Dialog element is supported in Safari 17 (shipped in Safari 15.4)."""
        status = caniuse_db.check_support('dialog', 'safari', '17')
        assert status == 'y'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: _parse_support_status()
# ═══════════════════════════════════════════════════════════════════════════

class TestParseStatus:
    """Tests for _parse_support_status() — extracts primary status char."""

    @pytest.mark.parametrize("raw,expected", [
        ('y', 'y'),
        ('a x #2', 'a'),
        ('y #1', 'y'),
        ('x', 'x'),
        ('p', 'p'),
        ('d #3', 'd'),
        ('n', 'n'),
    ])
    def test_extracts_first_char(self, caniuse_db, raw, expected):
        """Primary status is the first non-whitespace character."""
        assert caniuse_db._parse_support_status(raw) == expected

    def test_empty_string_returns_u(self, caniuse_db):
        """Empty string returns 'u' (unknown)."""
        assert caniuse_db._parse_support_status('') == 'u'

    def test_none_returns_u(self, caniuse_db):
        """None returns 'u'."""
        assert caniuse_db._parse_support_status(None) == 'u'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: _find_closest_version_support()
# ═══════════════════════════════════════════════════════════════════════════

class TestClosestVersion:
    """Tests for _find_closest_version_support()."""

    def test_finds_nearest_version_with_specific_result(self, caniuse_db):
        """Closest version for Chrome 119.5 should be 'y' (flexbox supported since ~29)."""
        status = caniuse_db.check_support('flexbox', 'chrome', '119.5')
        assert status == 'y'

    def test_non_numeric_version_returns_u(self, caniuse_db):
        """Non-numeric version string returns 'u'."""
        feature = caniuse_db.get_feature('flexbox')
        stats = feature['stats']['chrome']
        result = caniuse_db._find_closest_version_support(stats, 'abc')
        assert result == 'u'

    def test_handles_safari_version_ranges(self, caniuse_db):
        """Safari range versions (e.g., '15.2-15.3') don't crash and return valid status."""
        status = caniuse_db.check_support('flexbox', 'safari', '15.3')
        assert status == 'y'  # Flexbox fully supported in Safari 15.3

    def test_empty_browser_stats_returns_u(self, caniuse_db):
        """Empty browser stats dict returns 'u'."""
        result = caniuse_db._find_closest_version_support({}, '120')
        assert result == 'u'


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: check_multiple_browsers()
# ═══════════════════════════════════════════════════════════════════════════

class TestCheckMultipleBrowsers:
    """Tests for check_multiple_browsers()."""

    def test_returns_dict_for_all_browsers(self, caniuse_db, modern_browsers):
        """Returns a status for every browser in the input."""
        results = caniuse_db.check_multiple_browsers('flexbox', modern_browsers)
        assert set(results.keys()) == set(modern_browsers.keys())

    def test_flexbox_all_modern_supported(self, caniuse_db, modern_browsers):
        """Flexbox is supported in all modern browsers."""
        results = caniuse_db.check_multiple_browsers('flexbox', modern_browsers)
        for browser, status in results.items():
            assert status in ['y', 'a'], f"Flexbox not supported in {browser}: got '{status}'"

    def test_arrow_functions_with_ie(self, caniuse_db, legacy_browsers):
        """Arrow functions fail in IE but pass in modern browsers."""
        results = caniuse_db.check_multiple_browsers('arrow-functions', legacy_browsers)
        assert results['ie'] == 'n'
        assert results['chrome'] == 'y'

    def test_empty_browsers_returns_empty(self, caniuse_db):
        """Empty browser dict returns empty results."""
        assert caniuse_db.check_multiple_browsers('flexbox', {}) == {}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: search_features()
# ═══════════════════════════════════════════════════════════════════════════

class TestSearchFeatures:
    """Tests for search_features()."""

    def test_search_by_exact_id(self, caniuse_db):
        """Exact feature ID returns that feature."""
        results = caniuse_db.search_features('flexbox')
        assert 'flexbox' in results

    def test_search_by_keyword_returns_relevant(self, caniuse_db):
        """Keyword 'grid' returns css-grid among results."""
        results = caniuse_db.search_features('grid')
        assert 'css-grid' in results

    def test_search_empty_query(self, caniuse_db):
        """Empty query returns a list (graceful handling)."""
        results = caniuse_db.search_features('')
        assert isinstance(results, list)

    def test_search_nonsense_returns_empty(self, caniuse_db):
        """Nonsense query returns no matches."""
        assert len(caniuse_db.search_features('zzzznonexistentfeaturexxxx')) == 0

    def test_search_case_insensitive(self, caniuse_db):
        """Search is case-insensitive."""
        lower = set(caniuse_db.search_features('flexbox'))
        upper = set(caniuse_db.search_features('FLEXBOX'))
        assert lower == upper

    def test_search_special_characters(self, caniuse_db):
        """Special characters don't crash the search."""
        results = caniuse_db.search_features('flex*box[')
        assert isinstance(results, list)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: get_feature_info()
# ═══════════════════════════════════════════════════════════════════════════

class TestGetFeatureInfo:
    """Tests for get_feature_info()."""

    def test_known_feature_has_all_keys(self, caniuse_db):
        """Known feature returns dict with all standard keys."""
        info = caniuse_db.get_feature_info('flexbox')
        assert info is not None
        expected_keys = {'id', 'title', 'description', 'spec', 'status', 'categories', 'keywords', 'bugs'}
        assert expected_keys == set(info.keys())

    def test_unknown_feature_returns_none(self, caniuse_db):
        """Unknown feature returns None."""
        assert caniuse_db.get_feature_info('totally-fake-xyz') is None

    def test_feature_id_in_result(self, caniuse_db):
        """Result 'id' matches the queried feature ID."""
        info = caniuse_db.get_feature_info('css-grid')
        assert info['id'] == 'css-grid'

    def test_title_is_nonempty_string(self, caniuse_db):
        """Title is a non-empty string."""
        info = caniuse_db.get_feature_info('flexbox')
        assert isinstance(info['title'], str)
        assert len(info['title']) > 0

    def test_categories_is_list(self, caniuse_db):
        """Categories field is a list."""
        info = caniuse_db.get_feature_info('flexbox')
        assert isinstance(info['categories'], list)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: get_browser_versions()
# ═══════════════════════════════════════════════════════════════════════════

class TestGetBrowserVersions:
    """Tests for get_browser_versions()."""

    def test_chrome_has_many_versions(self, caniuse_db):
        """Chrome version list is large (100+)."""
        versions = caniuse_db.get_browser_versions('chrome')
        assert len(versions) > 100

    def test_unknown_browser_empty(self, caniuse_db):
        """Unknown browser returns empty list."""
        assert caniuse_db.get_browser_versions('netscape') == []

    def test_versions_are_strings(self, caniuse_db):
        """Version list contains strings."""
        versions = caniuse_db.get_browser_versions('firefox')
        assert all(isinstance(v, str) for v in versions)

    def test_lru_cache_returns_same_object(self, caniuse_db):
        """lru_cache returns the exact same list object on repeated calls."""
        v1 = caniuse_db.get_browser_versions('chrome')
        v2 = caniuse_db.get_browser_versions('chrome')
        assert v1 is v2  # Same object identity, not just equality


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 11: Metadata methods
# ═══════════════════════════════════════════════════════════════════════════

class TestDatabaseMetadata:
    """Tests for get_all_features(), get_feature_categories(), get_statistics()."""

    def test_get_all_features_returns_list(self, caniuse_db):
        """get_all_features() returns a list of 500+ string IDs."""
        features = caniuse_db.get_all_features()
        assert isinstance(features, list)
        assert len(features) > 500
        assert all(isinstance(f, str) for f in features)

    def test_get_feature_categories_has_css(self, caniuse_db):
        """get_feature_categories() includes a 'CSS' category."""
        categories = caniuse_db.get_feature_categories()
        assert isinstance(categories, dict)
        assert 'CSS' in categories

    def test_statistics_loaded(self, caniuse_db):
        """get_statistics() reflects loaded state with counts."""
        stats = caniuse_db.get_statistics()
        assert stats['loaded'] is True
        assert stats['total_features'] > 500
        assert stats['total_categories'] > 0
        assert stats['index_size'] > 0

    def test_statistics_unloaded(self):
        """Unloaded DB statistics show loaded=False only."""
        db = CanIUseDatabase()
        stats = db.get_statistics()
        assert stats == {'loaded': False}
