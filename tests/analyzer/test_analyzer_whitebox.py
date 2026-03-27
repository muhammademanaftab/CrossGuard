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
    def test_auto_load_on_get_feature(self):
        db = CanIUseDatabase()
        assert db.loaded is False
        assert db.get_feature('flexbox') is not None
        assert db.loaded is True


# ============================================================================
# SECTION 2: Singleton Pattern
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
# SECTION 3: check_support() and internal parsing
# ============================================================================

class TestCheckSupport:
    """Tests for check_support() and internal parsing helpers."""

    @pytest.mark.whitebox
    @pytest.mark.parametrize("feature,browser,version,expected", [
        ('flexbox', 'chrome', '120', 'y'),
        ('arrow-functions', 'ie', '11', 'n'),
    ])
    def test_known_feature_exact_status(self, caniuse_db, feature, browser, version, expected):
        assert caniuse_db.check_support(feature, browser, version) == expected

    @pytest.mark.whitebox
    def test_unknown_feature_and_browser_return_u(self, caniuse_db):
        assert caniuse_db.check_support('totally-fake-feature-xyz', 'chrome', '120') == 'u'
        assert caniuse_db.check_support('flexbox', 'netscape', '4') == 'u'


# ============================================================================
# SECTION 4: WebFeaturesManager
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


# ============================================================================
# SECTION 5: NPM Database Updater
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


class TestUpdateFallback:
    @pytest.mark.whitebox
    @patch.object(DatabaseUpdater, 'download_npm_update')
    @patch.object(DatabaseUpdater, 'update_via_git')
    def test_npm_failure_falls_back_to_git(self, mock_git, mock_npm, updater):
        mock_npm.return_value = {'success': False, 'message': 'npm failed'}
        mock_git.return_value = {'success': True, 'message': 'Updated via git'}
        assert updater.update_database()['success'] is True
        mock_git.assert_called_once()
