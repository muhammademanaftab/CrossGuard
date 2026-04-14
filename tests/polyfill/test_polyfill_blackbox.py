"""Blackbox tests for polyfill public API -- recommendations, lookups, aggregation."""

import pytest

from src.polyfill.polyfill_service import PolyfillService
from src.polyfill.polyfill_loader import get_polyfill_loader


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return PolyfillService()


@pytest.fixture
def loader():
    return get_polyfill_loader()


# ---------------------------------------------------------------------------
# Recommendation generation -- core behaviour
# ---------------------------------------------------------------------------

class TestGetRecommendations:
    @pytest.mark.blackbox
    def test_npm_feature_returns_npm_recommendation(self, service):
        recs = service.get_recommendations({'fetch'}, set(), {'ie': '11'})
        assert len(recs) == 1
        assert recs[0]['feature_id'] == 'fetch'
        assert recs[0]['polyfill_type'] == 'npm'
        assert len(recs[0]['packages']) > 0

    @pytest.mark.blackbox
    def test_css_fallback_feature_returns_fallback_with_code(self, service):
        recs = service.get_recommendations({'css-grid'}, set(), {'ie': '11'})
        assert len(recs) == 1
        assert recs[0]['polyfill_type'] == 'fallback'
        assert recs[0]['fallback_code'] is not None



# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

class TestAggregation:
    @pytest.mark.blackbox
    def test_install_command_single_package(self, service):
        recs = service.get_recommendations({'fetch'}, set(), {'ie': '11'})
        assert service.get_aggregate_install_command(recs) == 'npm install whatwg-fetch'


# ---------------------------------------------------------------------------
# Loader lookups -- representative features
# ---------------------------------------------------------------------------

class TestLoaderLookups:
    @pytest.mark.blackbox
    def test_named_feature_lookups(self, loader):
        cases = [
            ('fetch', 'Fetch API'),
            ('css-grid', 'CSS Grid Layout'),
            ('dialog', 'HTML <dialog> Element'),
        ]
        for fid, expected_name in cases:
            info = loader.get_polyfill(fid)
            assert info is not None and info['name'] == expected_name, f"{fid} name mismatch"

    @pytest.mark.blackbox
    def test_predicate_distinction(self, loader):
        assert loader.has_polyfill('css-grid') is True
        assert loader.is_polyfillable('css-grid') is False
        assert loader.has_polyfill('fetch') is True
        assert loader.is_polyfillable('fetch') is True

