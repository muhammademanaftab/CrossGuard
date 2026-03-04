"""Tests for the web-features (Baseline) integration."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.analyzer.web_features import WebFeaturesManager, BaselineInfo


@pytest.fixture
def sample_web_features_data():
    """Minimal web-features data structure."""
    return {
        "css-grid": {
            "caniuse": ["css-grid"],
            "status": {
                "baseline": "high",
                "baseline_low_date": "2017-10-17",
                "baseline_high_date": "2020-04-17",
            }
        },
        "container-queries": {
            "caniuse": ["css-container-queries"],
            "status": {
                "baseline": "low",
                "baseline_low_date": "2023-02-14",
            }
        },
        "has-selector": {
            "caniuse": ["css-has"],
            "status": {
                "baseline": False,
            }
        },
        "multi-caniuse": {
            "caniuse": ["feat-a", "feat-b"],
            "status": {
                "baseline": "high",
                "baseline_low_date": "2020-01-01",
                "baseline_high_date": "2022-07-01",
            }
        },
        "no-caniuse-mapping": {
            "status": {"baseline": "high"}
        },
    }


@pytest.fixture
def manager_with_data(tmp_path, sample_web_features_data):
    """WebFeaturesManager with cached data."""
    cache_path = tmp_path / "web_features.json"
    cache_path.write_text(json.dumps(sample_web_features_data))

    with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
        mgr = WebFeaturesManager()
        yield mgr


@pytest.fixture
def empty_manager(tmp_path):
    """WebFeaturesManager with no cached data."""
    cache_path = tmp_path / "web_features.json"
    with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
        mgr = WebFeaturesManager()
        yield mgr


class TestBaselineInfo:
    def test_to_dict(self):
        info = BaselineInfo(status='high', low_date='2020-01-01', high_date='2022-06-01')
        d = info.to_dict()
        assert d == {'status': 'high', 'low_date': '2020-01-01', 'high_date': '2022-06-01'}

    def test_to_dict_no_dates(self):
        info = BaselineInfo(status='limited')
        d = info.to_dict()
        assert d['status'] == 'limited'
        assert d['low_date'] is None


class TestReverseMap:
    def test_single_caniuse_mapping(self, manager_with_data):
        info = manager_with_data.get_baseline_status('css-grid')
        assert info is not None
        assert info.status == 'high'
        assert info.low_date == '2017-10-17'
        assert info.high_date == '2020-04-17'

    def test_low_baseline(self, manager_with_data):
        info = manager_with_data.get_baseline_status('css-container-queries')
        assert info is not None
        assert info.status == 'low'

    def test_false_baseline_maps_to_limited(self, manager_with_data):
        info = manager_with_data.get_baseline_status('css-has')
        assert info is not None
        assert info.status == 'limited'

    def test_multi_caniuse_ids(self, manager_with_data):
        a = manager_with_data.get_baseline_status('feat-a')
        b = manager_with_data.get_baseline_status('feat-b')
        assert a is not None and b is not None
        assert a.status == 'high'
        assert b.status == 'high'

    def test_unknown_feature(self, manager_with_data):
        info = manager_with_data.get_baseline_status('nonexistent')
        assert info is None

    def test_feature_count(self, manager_with_data):
        # css-grid, css-container-queries, css-has, feat-a, feat-b = 5
        assert manager_with_data.get_feature_count() == 5


class TestBaselineSummary:
    def test_mixed_features(self, manager_with_data):
        summary = manager_with_data.get_baseline_summary([
            'css-grid',             # high
            'css-container-queries', # low
            'css-has',              # limited
            'nonexistent',          # unknown
        ])
        assert summary['widely_available'] == 1
        assert summary['newly_available'] == 1
        assert summary['limited'] == 1
        assert summary['unknown'] == 1

    def test_empty_list(self, manager_with_data):
        summary = manager_with_data.get_baseline_summary([])
        assert summary['widely_available'] == 0
        assert summary['newly_available'] == 0
        assert summary['limited'] == 0
        assert summary['unknown'] == 0

    def test_all_unknown(self, manager_with_data):
        summary = manager_with_data.get_baseline_summary(['x', 'y', 'z'])
        assert summary['unknown'] == 3
        assert summary['widely_available'] == 0

    def test_all_high(self, manager_with_data):
        summary = manager_with_data.get_baseline_summary(['css-grid', 'feat-a', 'feat-b'])
        assert summary['widely_available'] == 3
        assert summary['unknown'] == 0


class TestHasData:
    def test_with_data(self, manager_with_data):
        assert manager_with_data.has_data() is True

    def test_without_data(self, empty_manager):
        assert empty_manager.has_data() is False


class TestDownload:
    @patch('src.analyzer.web_features.urlopen')
    def test_successful_download(self, mock_urlopen, tmp_path):
        cache_path = tmp_path / "web_features.json"
        cache_dir = tmp_path

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"test": {"status": {"baseline": "high"}}}).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path), \
             patch('src.analyzer.web_features.WEB_FEATURES_CACHE_DIR', cache_dir):
            mgr = WebFeaturesManager()
            assert mgr.download() is True
            assert cache_path.exists()

    @patch('src.analyzer.web_features.urlopen')
    def test_network_failure(self, mock_urlopen, tmp_path):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("timeout")

        cache_path = tmp_path / "web_features.json"
        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
            mgr = WebFeaturesManager()
            assert mgr.download() is False
            assert not cache_path.exists()

    @patch('src.analyzer.web_features.urlopen')
    def test_invalid_json_response(self, mock_urlopen, tmp_path):
        cache_path = tmp_path / "web_features.json"
        cache_dir = tmp_path

        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not valid json"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path), \
             patch('src.analyzer.web_features.WEB_FEATURES_CACHE_DIR', cache_dir):
            mgr = WebFeaturesManager()
            assert mgr.download() is False


class TestEdgeCases:
    def test_corrupt_cache_file(self, tmp_path):
        cache_path = tmp_path / "web_features.json"
        cache_path.write_text("{{bad json")

        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
            mgr = WebFeaturesManager()
            # Should not crash, returns empty map
            assert mgr.get_baseline_status('anything') is None
            assert mgr.get_feature_count() == 0

    def test_feature_with_string_caniuse(self, tmp_path):
        """Some entries have caniuse as a string instead of a list."""
        data = {
            "string-feat": {
                "caniuse": "single-id",
                "status": {"baseline": "low", "baseline_low_date": "2024-01-01"}
            }
        }
        cache_path = tmp_path / "web_features.json"
        cache_path.write_text(json.dumps(data))

        with patch('src.analyzer.web_features.WEB_FEATURES_CACHE_PATH', cache_path):
            mgr = WebFeaturesManager()
            info = mgr.get_baseline_status('single-id')
            assert info is not None
            assert info.status == 'low'
