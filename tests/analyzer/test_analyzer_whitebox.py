"""White-box tests for analyzer internals -- database loading, web features, NPM updater.

Tests internal state, mocked I/O paths, singleton management, and data parsing
logic that is not exposed through the public analysis API.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from src.analyzer.database import (
    CanIUseDatabase,
    get_database,
)
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


# ============================================================================
# SECTION 3: check_support() and internal parsing
# ============================================================================

class TestCheckSupport:
    """Tests for check_support() and internal parsing helpers."""

    @pytest.mark.whitebox
    @pytest.mark.parametrize("feature,browser,version,expected", [
        ('flexbox', 'chrome', '120', 'y'),
    ])
    def test_known_feature_exact_status(self, caniuse_db, feature, browser, version, expected):
        assert caniuse_db.check_support(feature, browser, version) == expected


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
