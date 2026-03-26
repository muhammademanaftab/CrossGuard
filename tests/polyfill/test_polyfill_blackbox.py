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
        assert recs[0].feature_id == 'fetch'
        assert recs[0].polyfill_type == 'npm'
        assert len(recs[0].packages) > 0

    @pytest.mark.blackbox
    def test_css_fallback_feature_returns_fallback_with_code(self, service):
        recs = service.get_recommendations({'css-grid'}, set(), {'ie': '11'})
        assert len(recs) == 1
        assert recs[0].polyfill_type == 'fallback'
        assert recs[0].fallback_code is not None

    @pytest.mark.blackbox
    def test_partial_features_produce_recommendations(self, service):
        recs = service.get_recommendations(set(), {'fetch'}, {'safari': '10'})
        assert len(recs) == 1 and recs[0].feature_id == 'fetch'

    @pytest.mark.blackbox
    def test_mixed_unsupported_and_partial_no_duplicates(self, service):
        """Both sets contribute; overlap is deduplicated."""
        recs = service.get_recommendations({'fetch'}, {'css-grid', 'fetch'}, {'ie': '11'})
        ids = {r.feature_id for r in recs}
        assert ids == {'fetch', 'css-grid'}
        # fetch appears once despite being in both sets
        assert sum(1 for r in recs if r.feature_id == 'fetch') == 1

    @pytest.mark.blackbox
    def test_results_sorted_by_feature_id(self, service):
        recs = service.get_recommendations(
            {'promises', 'fetch', 'array-includes'}, set(), {'ie': '11'},
        )
        ids = [r.feature_id for r in recs]
        assert ids == sorted(ids)

    @pytest.mark.blackbox
    def test_browsers_affected_matches_input(self, service):
        recs = service.get_recommendations(
            {'fetch'}, set(), {'chrome': '40', 'firefox': '30'},
        )
        assert set(recs[0].browsers_affected) == {'chrome', 'firefox'}

    @pytest.mark.blackbox
    def test_empty_and_nonexistent_return_empty(self, service):
        assert service.get_recommendations(set(), set(), {'chrome': '120'}) == []
        assert service.get_recommendations({'totally-fake'}, set(), {'chrome': '120'}) == []

    @pytest.mark.blackbox
    def test_mix_of_real_and_fake(self, service):
        recs = service.get_recommendations({'fetch', 'totally-fake'}, set(), {'ie': '11'})
        assert len(recs) == 1 and recs[0].feature_id == 'fetch'

    @pytest.mark.blackbox
    def test_representative_features_produce_correct_type(self, service):
        """Representative features from JS, CSS npm, CSS fallback, HTML all produce the right type."""
        npm_features = ['fetch', 'promises', 'intersectionobserver', 'dialog', 'css-variables']
        fallback_features = ['css-grid', 'flexbox', 'css-filters']
        for fid in npm_features:
            recs = service.get_recommendations({fid}, set(), {'ie': '11'})
            assert len(recs) == 1 and recs[0].polyfill_type == 'npm', f"{fid} should be npm"
        for fid in fallback_features:
            recs = service.get_recommendations({fid}, set(), {'ie': '11'})
            assert len(recs) == 1 and recs[0].polyfill_type == 'fallback', f"{fid} should be fallback"


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

class TestAggregation:
    @pytest.mark.blackbox
    def test_install_command_single_package(self, service):
        recs = service.get_recommendations({'fetch'}, set(), {'ie': '11'})
        assert service.get_aggregate_install_command(recs) == 'npm install whatwg-fetch'

    @pytest.mark.blackbox
    def test_install_command_sorted_and_deduped(self, service):
        recs = service.get_recommendations(
            {'array-includes', 'object-entries', 'globalthis'}, set(), {'ie': '11'},
        )
        cmd = service.get_aggregate_install_command(recs)
        packages = cmd.replace('npm install ', '').split()
        assert packages == sorted(packages)
        assert cmd.count('core-js') == 1

    @pytest.mark.blackbox
    def test_install_command_empty_and_fallback_only(self, service):
        assert service.get_aggregate_install_command([]) == ''
        recs = service.get_recommendations({'css-grid'}, set(), {'ie': '11'})
        assert service.get_aggregate_install_command(recs) == ''

    @pytest.mark.blackbox
    def test_imports_for_npm_and_empty(self, service):
        recs = service.get_recommendations({'fetch'}, set(), {'ie': '11'})
        imports = service.get_aggregate_imports(recs)
        assert len(imports) == 1 and "import 'whatwg-fetch';" in imports[0]
        assert service.get_aggregate_imports([]) == []

    @pytest.mark.blackbox
    def test_size_calculation(self, service):
        recs = service.get_recommendations({'fetch'}, set(), {'ie': '11'})
        assert service.get_total_size_kb(recs) == 3.2
        assert service.get_total_size_kb([]) == 0.0

    @pytest.mark.blackbox
    def test_categorize_mixed_and_empty(self, service):
        recs = service.get_recommendations(
            {'fetch', 'css-grid', 'promises'}, set(), {'ie': '11'},
        )
        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) == 2 and len(cat['fallback']) == 1
        assert service.categorize_recommendations([]) == {'npm': [], 'fallback': []}


# ---------------------------------------------------------------------------
# Loader lookups -- representative features
# ---------------------------------------------------------------------------

class TestLoaderLookups:
    @pytest.mark.blackbox
    def test_named_feature_lookups(self, loader):
        """Representative features from each category have correct names."""
        cases = [
            ('fetch', 'Fetch API'),
            ('css-grid', 'CSS Grid Layout'),
            ('dialog', 'HTML <dialog> Element'),
        ]
        for fid, expected_name in cases:
            info = loader.get_polyfill(fid)
            assert info is not None and info['name'] == expected_name, f"{fid} name mismatch"

    @pytest.mark.blackbox
    def test_fetch_package_details(self, loader):
        pkg = loader.get_polyfill('fetch')['packages'][0]
        assert pkg['npm'] == 'whatwg-fetch'
        assert pkg['size_kb'] == 3.2

    @pytest.mark.blackbox
    def test_promises_has_multiple_packages(self, loader):
        info = loader.get_polyfill('promises')
        assert len(info['packages']) == 2
        npm_names = {p['npm'] for p in info['packages']}
        assert {'core-js', 'es6-promise'} == npm_names

    @pytest.mark.blackbox
    def test_predicate_distinction(self, loader):
        """has_polyfill vs is_polyfillable: fallback features differ."""
        # css-grid: has entry but not polyfillable (fallback only)
        assert loader.has_polyfill('css-grid') is True
        assert loader.is_polyfillable('css-grid') is False
        # fetch: both true (npm polyfill)
        assert loader.has_polyfill('fetch') is True
        assert loader.is_polyfillable('fetch') is True

    @pytest.mark.blackbox
    def test_nonexistent_features_return_none(self, loader):
        for fid in ['completely-fake', '', 'FETCH', 'Fetch']:
            assert loader.get_polyfill(fid) is None, f"'{fid}' should return None"
            assert loader.has_polyfill(fid) is False
            assert loader.is_polyfillable(fid) is False


# ---------------------------------------------------------------------------
# Large batch -- all features at once
# ---------------------------------------------------------------------------

class TestLargeBatch:
    ALL_FEATURES = {
        'fetch', 'promises', 'async-functions', 'array-includes', 'array-flat',
        'object-entries', 'object-values', 'object-assign', 'object-fromentries',
        'pad-start-end', 'es6-string-includes', 'es6-number',
        'intersectionobserver', 'resizeobserver', 'mutationobserver',
        'requestanimationframe', 'classlist', 'url', 'urlsearchparams',
        'customevent', 'abortcontroller', 'textencoder',
        'css-grid', 'flexbox', 'css-backdrop-filter', 'css-filters',
        'css-variables', 'css-sticky', 'object-fit',
        'dialog', 'details', 'datalist', 'picture', 'template',
    }

    @pytest.mark.blackbox
    def test_all_produce_unique_sorted_recommendations(self, service):
        recs = service.get_recommendations(self.ALL_FEATURES, set(), {'ie': '11'})
        assert len(recs) >= 30
        ids = [r.feature_id for r in recs]
        assert len(ids) == len(set(ids)), "duplicate recommendations"
        assert ids == sorted(ids), "not sorted"

    @pytest.mark.blackbox
    def test_batch_install_and_size(self, service):
        recs = service.get_recommendations(self.ALL_FEATURES, set(), {'ie': '11'})
        cmd = service.get_aggregate_install_command(recs)
        assert len(cmd) > len('npm install ')
        size = service.get_total_size_kb(recs)
        manual = sum(
            r.packages[0].size_kb for r in recs
            if r.polyfill_type == 'npm' and r.packages and r.packages[0].size_kb
        )
        assert size == pytest.approx(manual)

    @pytest.mark.blackbox
    def test_empty_browsers_dict(self, service):
        recs = service.get_recommendations({'fetch'}, set(), {})
        assert len(recs) == 1 and recs[0].browsers_affected == []
