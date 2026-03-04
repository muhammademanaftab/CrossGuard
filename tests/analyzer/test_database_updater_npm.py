"""Tests for npm-based database update functionality."""

import json
import os
import tarfile
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.analyzer.database_updater import DatabaseUpdater


@pytest.fixture
def tmp_caniuse(tmp_path):
    """Create a temporary caniuse directory with a data.json."""
    caniuse_dir = tmp_path / "caniuse"
    caniuse_dir.mkdir()
    data = {"updated": 1700000000, "data": {"feature1": {}, "feature2": {}}}
    (caniuse_dir / "data.json").write_text(json.dumps(data))
    return caniuse_dir


@pytest.fixture
def updater(tmp_caniuse):
    return DatabaseUpdater(tmp_caniuse)


class TestGetLocalNpmVersion:
    def test_no_package_json(self, updater):
        assert updater.get_local_npm_version() is None

    def test_with_package_json(self, updater):
        (updater.caniuse_dir / "package.json").write_text(
            json.dumps({"version": "1.0.1234"})
        )
        assert updater.get_local_npm_version() == "1.0.1234"

    def test_invalid_json(self, updater):
        (updater.caniuse_dir / "package.json").write_text("not json")
        assert updater.get_local_npm_version() is None


class TestCheckNpmUpdate:
    @patch('src.analyzer.database_updater.urlopen')
    def test_success_update_available(self, mock_urlopen, updater):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "version": "1.0.9999",
            "dist": {"tarball": "https://registry.npmjs.org/caniuse-db/-/caniuse-db-1.0.9999.tgz"}
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = updater.check_npm_update()
        assert result['success'] is True
        assert result['latest_version'] == '1.0.9999'
        assert result['update_available'] is True
        assert result['tarball_url'].startswith('https://')

    @patch('src.analyzer.database_updater.urlopen')
    def test_success_up_to_date(self, mock_urlopen, updater):
        # Write matching local version
        (updater.caniuse_dir / "package.json").write_text(
            json.dumps({"version": "1.0.5000"})
        )

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "version": "1.0.5000",
            "dist": {"tarball": "https://example.com/t.tgz"}
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = updater.check_npm_update()
        assert result['success'] is True
        assert result['update_available'] is False

    @patch('src.analyzer.database_updater.urlopen')
    def test_network_failure(self, mock_urlopen, updater):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("connection refused")

        result = updater.check_npm_update()
        assert result['success'] is False
        assert 'error' in result


class TestDownloadNpmUpdate:
    @patch.object(DatabaseUpdater, 'check_npm_update')
    def test_no_update_available(self, mock_check, updater):
        mock_check.return_value = {
            'success': True,
            'update_available': False,
            'latest_version': '1.0.5000',
        }
        result = updater.download_npm_update()
        assert result['success'] is True
        assert result['no_changes'] is True

    @patch.object(DatabaseUpdater, 'check_npm_update')
    def test_registry_unreachable(self, mock_check, updater):
        mock_check.return_value = {'success': False, 'error': 'timeout'}
        result = updater.download_npm_update()
        assert result['success'] is False

    @patch('src.analyzer.database_updater.urlopen')
    @patch.object(DatabaseUpdater, 'check_npm_update')
    def test_successful_download(self, mock_check, mock_urlopen, updater):
        mock_check.return_value = {
            'success': True,
            'update_available': True,
            'latest_version': '1.0.9999',
            'tarball_url': 'https://example.com/t.tgz',
        }

        # Create a tarball in memory
        tmp = tempfile.mkdtemp()
        pkg_dir = os.path.join(tmp, 'package')
        os.makedirs(pkg_dir)

        data = {"updated": 1700001000, "data": {"f1": {}, "f2": {}, "f3": {}}}
        with open(os.path.join(pkg_dir, 'data.json'), 'w') as f:
            json.dump(data, f)
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

        result = updater.download_npm_update()
        assert result['success'] is True
        assert '1.0.9999' in result['message']
        assert updater.data_json_path.exists()
        assert updater.package_json_path.exists()

        # Verify version written
        assert updater.get_local_npm_version() == '1.0.9999'


class TestUpdateDatabaseFallback:
    @patch.object(DatabaseUpdater, 'download_npm_update')
    @patch.object(DatabaseUpdater, 'update_via_git')
    def test_npm_success_skips_git(self, mock_git, mock_npm, updater):
        mock_npm.return_value = {'success': True, 'message': 'Updated via npm'}
        result = updater.update_database()
        assert result['success'] is True
        mock_git.assert_not_called()

    @patch.object(DatabaseUpdater, 'download_npm_update')
    @patch.object(DatabaseUpdater, 'update_via_git')
    def test_npm_failure_falls_back_to_git(self, mock_git, mock_npm, updater):
        mock_npm.return_value = {'success': False, 'message': 'npm failed'}
        mock_git.return_value = {'success': True, 'message': 'Updated via git'}
        result = updater.update_database()
        assert result['success'] is True
        assert result['message'] == 'Updated via git'
        mock_git.assert_called_once()

    @patch.object(DatabaseUpdater, 'download_npm_update')
    @patch.object(DatabaseUpdater, 'update_via_git')
    def test_both_fail(self, mock_git, mock_npm, updater):
        mock_npm.return_value = {'success': False, 'message': 'npm failed'}
        mock_git.return_value = {'success': False, 'message': 'git failed'}
        result = updater.update_database()
        assert result['success'] is False


class TestDatabaseInfo:
    def test_includes_npm_version(self, updater):
        (updater.caniuse_dir / "package.json").write_text(
            json.dumps({"version": "1.0.4242"})
        )
        info = updater.get_database_info()
        assert info['npm_version'] == '1.0.4242'
        assert info['features_count'] == 2

    def test_no_npm_version(self, updater):
        info = updater.get_database_info()
        assert info['npm_version'] is None
