"""White-box tests for analyzer internals -- database loading, web features, NPM updater.

Tests internal state, mocked I/O paths, singleton management, and data parsing
logic that is not exposed through the public analysis API.
"""

import json
import os
import tarfile
import tempfile
from unittest.mock import patch, mock_open, MagicMock

import pytest

from src.analyzer.database import (
    CanIUseDatabase,
    get_database,
    reload_database,
)
import src.analyzer.database as db_module
from src.analyzer.web_features import WebFeaturesManager, BaselineInfo
from src.analyzer.database_updater import DatabaseUpdater


# ============================================================================
# SECTION 1: Database Loading
# ============================================================================

class TestDatabaseLoading:
    """Tests for load(), _load_feature_files(), _build_index()."""

    @pytest.mark.whitebox
    def test_load_returns_true_and_has_features(self, caniuse_db):
        assert caniuse_db.loaded is True
        assert len(caniuse_db.features) > 500
        assert len(caniuse_db.feature_index) > 0

    @pytest.mark.whitebox
    def test_features_have_stats(self, caniuse_db):
        flexbox = caniuse_db.features.get('flexbox')
        assert flexbox is not None and 'stats' in flexbox

    @pytest.mark.whitebox
    def test_fresh_db_not_loaded(self, fresh_db):
        assert fresh_db.loaded is False
        assert fresh_db.features == {}

    @pytest.mark.whitebox
    def test_auto_load_on_get_feature(self):
        db = CanIUseDatabase()
        assert db.loaded is False
        assert db.get_feature('flexbox') is not None
        assert db.loaded is True


# ============================================================================
# SECTION 2: Load Error Handling (mocked)
# ============================================================================

class TestLoadErrors:
    """Tests for error paths in load() using mocks."""

    @pytest.mark.whitebox
    @pytest.mark.parametrize("side_effect", [
        FileNotFoundError("not found"),
        PermissionError("denied"),
    ])
    def test_open_error_returns_false(self, side_effect):
        db = CanIUseDatabase()
        with patch('builtins.open', side_effect=side_effect):
            assert db.load() is False

    @pytest.mark.whitebox
    def test_corrupt_json_returns_false(self):
        db = CanIUseDatabase()
        with patch('builtins.open', mock_open(read_data='{invalid json')):
            assert db.load() is False


# ============================================================================
# SECTION 3: Singleton Pattern
# ============================================================================

class TestSingleton:
    """Tests for get_database() and reload_database()."""

    @pytest.mark.whitebox
    def test_get_database_returns_same_loaded_instance(self, reset_singleton):
        db = get_database()
        assert isinstance(db, CanIUseDatabase) and db.loaded is True
        assert get_database() is db

    @pytest.mark.whitebox
    def test_reload_database_replaces_singleton(self, reset_singleton):
        db1 = get_database()
        db2 = reload_database()
        assert db2 is not db1 and db2.loaded is True
        assert get_database() is db2


# ============================================================================
# SECTION 4: check_support() and internal parsing
# ============================================================================

class TestCheckSupport:
    """Tests for check_support() and internal parsing helpers."""

    @pytest.mark.whitebox
    @pytest.mark.parametrize("feature,browser,version,expected", [
        ('flexbox', 'chrome', '120', 'y'),
        ('arrow-functions', 'ie', '11', 'n'),
        ('css-grid', 'chrome', '120', 'y'),
    ])
    def test_known_feature_exact_status(self, caniuse_db, feature, browser, version, expected):
        assert caniuse_db.check_support(feature, browser, version) == expected

    @pytest.mark.whitebox
    def test_unknown_feature_and_browser_return_u(self, caniuse_db):
        assert caniuse_db.check_support('totally-fake-feature-xyz', 'chrome', '120') == 'u'
        assert caniuse_db.check_support('flexbox', 'netscape', '4') == 'u'

    @pytest.mark.whitebox
    @pytest.mark.parametrize("raw,expected", [
        ('y', 'y'), ('a x #2', 'a'), ('', 'u'), (None, 'u'),
    ])
    def test_parse_support_status(self, caniuse_db, raw, expected):
        assert caniuse_db._parse_support_status(raw) == expected

    @pytest.mark.whitebox
    def test_closest_version_for_fractional(self, caniuse_db):
        assert caniuse_db.check_support('flexbox', 'chrome', '119.5') == 'y'

    @pytest.mark.whitebox
    def test_non_numeric_and_empty_stats_return_u(self, caniuse_db):
        feature = caniuse_db.get_feature('flexbox')
        assert caniuse_db._find_closest_version_support(feature['stats']['chrome'], 'abc') == 'u'
        assert caniuse_db._find_closest_version_support({}, '120') == 'u'


# ============================================================================
# SECTION 5: check_multiple_browsers() and search_features()
# ============================================================================

class TestQueryMethods:
    """Tests for check_multiple_browsers() and search_features()."""

    @pytest.mark.whitebox
    def test_check_multiple_returns_all_browsers(self, caniuse_db, modern_browsers):
        results = caniuse_db.check_multiple_browsers('flexbox', modern_browsers)
        assert set(results.keys()) == set(modern_browsers.keys())

    @pytest.mark.whitebox
    def test_search_by_keyword_case_insensitive(self, caniuse_db):
        assert 'css-grid' in caniuse_db.search_features('grid')
        assert set(caniuse_db.search_features('flexbox')) == set(caniuse_db.search_features('FLEXBOX'))

    @pytest.mark.whitebox
    def test_search_nonsense_returns_empty(self, caniuse_db):
        assert len(caniuse_db.search_features('zzzznonexistentfeaturexxxx')) == 0


# ============================================================================
# SECTION 6: get_feature_info() and Metadata
# ============================================================================

class TestFeatureInfoAndMetadata:
    """Tests for get_feature_info(), get_all_features(), get_statistics()."""

    @pytest.mark.whitebox
    def test_known_feature_info(self, caniuse_db):
        info = caniuse_db.get_feature_info('flexbox')
        assert info is not None
        assert {'id', 'title', 'description', 'spec', 'status', 'categories', 'keywords', 'bugs'} == set(info.keys())

    @pytest.mark.whitebox
    def test_unknown_feature_returns_none(self, caniuse_db):
        assert caniuse_db.get_feature_info('totally-fake-xyz') is None

    @pytest.mark.whitebox
    def test_metadata_with_loaded_db(self, caniuse_db):
        assert len(caniuse_db.get_all_features()) > 500
        assert 'CSS' in caniuse_db.get_feature_categories()
        stats = caniuse_db.get_statistics()
        assert stats['loaded'] is True and stats['total_features'] > 500

    @pytest.mark.whitebox
    def test_statistics_unloaded(self):
        assert CanIUseDatabase().get_statistics() == {'loaded': False}

    @pytest.mark.whitebox
    def test_chrome_versions_cached(self, caniuse_db):
        versions = caniuse_db.get_browser_versions('chrome')
        assert len(versions) > 100
        assert caniuse_db.get_browser_versions('chrome') is versions


# ============================================================================
# SECTION 7: WebFeaturesManager
# ============================================================================

@pytest.fixture
def sample_web_features_data():
    return {
        "css-grid": {
            "caniuse": ["css-grid"],
            "status": {"baseline": "high", "baseline_low_date": "2017-10-17", "baseline_high_date": "2020-04-17"}
        },
        "container-queries": {
            "caniuse": ["css-container-queries"],
            "status": {"baseline": "low", "baseline_low_date": "2023-02-14"}
        },
        "has-selector": {
            "caniuse": ["css-has"],
            "status": {"baseline": False}
        },
        "multi-caniuse": {
            "caniuse": ["feat-a", "feat-b"],
            "status": {"baseline": "high", "baseline_low_date": "2020-01-01", "baseline_high_date": "2022-07-01"}
        },
    }


@pytest.fixture
def manager_with_data(tmp_path, sample_web_features_data):
    cache_path = tmp_path / "web_features.json"
    cache_path.write_text(json.dumps(sample_web_features_data))
    with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
        yield WebFeaturesManager()


@pytest.fixture
def empty_manager(tmp_path):
    cache_path = tmp_path / "web_features.json"
    with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
        yield WebFeaturesManager()


class TestBaselineInfo:
    @pytest.mark.whitebox
    def test_to_dict(self):
        info = BaselineInfo(status='high', low_date='2020-01-01', high_date='2022-06-01')
        assert info.to_dict() == {'status': 'high', 'low_date': '2020-01-01', 'high_date': '2022-06-01'}

    @pytest.mark.whitebox
    def test_to_dict_no_dates(self):
        assert BaselineInfo(status='limited').to_dict()['low_date'] is None


class TestReverseMapAndSummary:
    @pytest.mark.whitebox
    def test_baseline_status_levels(self, manager_with_data):
        """high, low, and limited (false) baseline statuses resolve correctly."""
        assert manager_with_data.get_baseline_status('css-grid').status == 'high'
        assert manager_with_data.get_baseline_status('css-container-queries').status == 'low'
        assert manager_with_data.get_baseline_status('css-has').status == 'limited'

    @pytest.mark.whitebox
    def test_multi_caniuse_ids(self, manager_with_data):
        a = manager_with_data.get_baseline_status('feat-a')
        b = manager_with_data.get_baseline_status('feat-b')
        assert a is not None and b is not None and a.status == 'high'

    @pytest.mark.whitebox
    def test_unknown_feature(self, manager_with_data):
        assert manager_with_data.get_baseline_status('nonexistent') is None

    @pytest.mark.whitebox
    def test_mixed_summary(self, manager_with_data):
        summary = manager_with_data.get_baseline_summary([
            'css-grid', 'css-container-queries', 'css-has', 'nonexistent',
        ])
        assert summary['widely_available'] == 1
        assert summary['newly_available'] == 1
        assert summary['limited'] == 1
        assert summary['unknown'] == 1


class TestWebFeaturesDataAndDownload:
    @pytest.mark.whitebox
    def test_with_data(self, manager_with_data):
        assert manager_with_data.has_data() is True

    @pytest.mark.whitebox
    def test_without_data(self, empty_manager):
        assert empty_manager.has_data() is False

    @pytest.mark.whitebox
    @patch('src.analyzer.web_features.urlopen')
    def test_successful_download(self, mock_urlopen, tmp_path):
        cache_path = tmp_path / "web_features.json"
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"test": {"status": {"baseline": "high"}}}).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path), \
             patch('src.analyzer.web_features.WEB_FEATURES_CACHE_DIR', tmp_path):
            assert WebFeaturesManager().download() is True

    @pytest.mark.whitebox
    @patch('src.analyzer.web_features.urlopen')
    def test_network_failure(self, mock_urlopen, tmp_path):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("timeout")
        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', tmp_path / "wf.json"):
            assert WebFeaturesManager().download() is False


class TestWebFeaturesEdgeCases:
    @pytest.mark.whitebox
    def test_corrupt_cache_file(self, tmp_path):
        cache_path = tmp_path / "web_features.json"
        cache_path.write_text("{{bad json")
        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
            mgr = WebFeaturesManager()
            assert mgr.get_baseline_status('anything') is None
            assert mgr.get_feature_count() == 0

    @pytest.mark.whitebox
    def test_feature_with_string_caniuse(self, tmp_path):
        data = {"string-feat": {"caniuse": "single-id", "status": {"baseline": "low", "baseline_low_date": "2024-01-01"}}}
        cache_path = tmp_path / "web_features.json"
        cache_path.write_text(json.dumps(data))
        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
            assert WebFeaturesManager().get_baseline_status('single-id').status == 'low'


# ============================================================================
# SECTION 8: NPM Database Updater
# ============================================================================

@pytest.fixture
def tmp_caniuse(tmp_path):
    caniuse_dir = tmp_path / "caniuse"
    caniuse_dir.mkdir()
    (caniuse_dir / "data.json").write_text(json.dumps({"updated": 1700000000, "data": {"feature1": {}, "feature2": {}}}))
    return caniuse_dir


@pytest.fixture
def updater(tmp_caniuse):
    return DatabaseUpdater(tmp_caniuse)


class TestNpmVersion:
    @pytest.mark.whitebox
    def test_no_package_json(self, updater):
        assert updater.get_local_npm_version() is None

    @pytest.mark.whitebox
    def test_with_package_json(self, updater):
        (updater.caniuse_dir / "package.json").write_text(json.dumps({"version": "1.0.1234"}))
        assert updater.get_local_npm_version() == "1.0.1234"


class TestCheckNpmUpdate:
    @pytest.mark.whitebox
    @patch('src.analyzer.database_updater.urlopen')
    def test_update_available(self, mock_urlopen, updater):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "version": "1.0.9999",
            "dist": {"tarball": "https://registry.npmjs.org/caniuse-db/-/caniuse-db-1.0.9999.tgz"}
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        result = updater.check_npm_update()
        assert result['success'] is True and result['update_available'] is True

    @pytest.mark.whitebox
    @patch('src.analyzer.database_updater.urlopen')
    def test_network_failure(self, mock_urlopen, updater):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("connection refused")
        assert updater.check_npm_update()['success'] is False


class TestDownloadNpmUpdate:
    @pytest.mark.whitebox
    @patch.object(DatabaseUpdater, 'check_npm_update')
    def test_no_update_available(self, mock_check, updater):
        mock_check.return_value = {'success': True, 'update_available': False, 'latest_version': '1.0.5000'}
        result = updater.download_npm_update()
        assert result['success'] is True and result['no_changes'] is True

    @pytest.mark.whitebox
    @patch('src.analyzer.database_updater.urlopen')
    @patch.object(DatabaseUpdater, 'check_npm_update')
    def test_successful_download(self, mock_check, mock_urlopen, updater):
        mock_check.return_value = {
            'success': True, 'update_available': True,
            'latest_version': '1.0.9999', 'tarball_url': 'https://example.com/t.tgz',
        }
        tmp = tempfile.mkdtemp()
        pkg_dir = os.path.join(tmp, 'package')
        os.makedirs(pkg_dir)
        with open(os.path.join(pkg_dir, 'data.json'), 'w') as f:
            json.dump({"updated": 1700001000, "data": {"f1": {}}}, f)
        with open(os.path.join(pkg_dir, 'package.json'), 'w') as f:
            json.dump({"version": "1.0.9999"}, f)
        tar_path = os.path.join(tmp, 'test.tgz')
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(pkg_dir, arcname='package')
        with open(tar_path, 'rb') as f:
            tar_bytes = f.read()
        mock_resp = MagicMock()
        mock_resp.read.return_value = tar_bytes
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        assert updater.download_npm_update()['success'] is True
        assert updater.get_local_npm_version() == '1.0.9999'


class TestUpdateFallback:
    @pytest.mark.whitebox
    @patch.object(DatabaseUpdater, 'download_npm_update')
    @patch.object(DatabaseUpdater, 'update_via_git')
    def test_npm_success_skips_git(self, mock_git, mock_npm, updater):
        mock_npm.return_value = {'success': True, 'message': 'Updated via npm'}
        assert updater.update_database()['success'] is True
        mock_git.assert_not_called()

    @pytest.mark.whitebox
    @patch.object(DatabaseUpdater, 'download_npm_update')
    @patch.object(DatabaseUpdater, 'update_via_git')
    def test_npm_failure_falls_back_to_git(self, mock_git, mock_npm, updater):
        mock_npm.return_value = {'success': False, 'message': 'npm failed'}
        mock_git.return_value = {'success': True, 'message': 'Updated via git'}
        assert updater.update_database()['success'] is True
        mock_git.assert_called_once()

    @pytest.mark.whitebox
    @patch.object(DatabaseUpdater, 'download_npm_update')
    @patch.object(DatabaseUpdater, 'update_via_git')
    def test_both_fail(self, mock_git, mock_npm, updater):
        mock_npm.return_value = {'success': False, 'message': 'npm failed'}
        mock_git.return_value = {'success': False, 'message': 'git failed'}
        assert updater.update_database()['success'] is False


class TestDatabaseInfo:
    @pytest.mark.whitebox
    def test_includes_npm_version(self, updater):
        (updater.caniuse_dir / "package.json").write_text(json.dumps({"version": "1.0.4242"}))
        info = updater.get_database_info()
        assert info['npm_version'] == '1.0.4242' and info['features_count'] == 2
