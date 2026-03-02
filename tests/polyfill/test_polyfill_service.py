"""Tests for PolyfillService — recommendations, aggregation, categorization, edge cases."""

import pytest

from src.polyfill.polyfill_service import (
    PolyfillService,
    PolyfillRecommendation,
    PolyfillPackage,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    return PolyfillService()


@pytest.fixture
def npm_recommendation():
    return PolyfillRecommendation(
        feature_id='fetch',
        feature_name='Fetch API',
        polyfill_type='npm',
        packages=[PolyfillPackage(
            name='whatwg-fetch',
            npm_package='whatwg-fetch',
            import_statement="import 'whatwg-fetch';",
            size_kb=3.2,
            cdn_url='https://unpkg.com/whatwg-fetch@3.6/dist/fetch.umd.js',
            note='Full Fetch API polyfill',
        )],
        browsers_affected=['ie'],
    )


@pytest.fixture
def fallback_recommendation():
    return PolyfillRecommendation(
        feature_id='css-grid',
        feature_name='CSS Grid Layout',
        polyfill_type='fallback',
        packages=[],
        fallback_code='/* Flexbox fallback */',
        fallback_description='Use Flexbox as fallback',
        browsers_affected=['ie'],
    )


# ---------------------------------------------------------------------------
# Dataclass construction
# ---------------------------------------------------------------------------

class TestPolyfillPackageDataclass:
    def test_required_fields_only(self):
        pkg = PolyfillPackage(name='test', npm_package='test-pkg', import_statement="import 'test';")
        assert pkg.cdn_url is None
        assert pkg.size_kb is None
        assert pkg.note is None

    def test_all_fields(self):
        pkg = PolyfillPackage(
            name='test', npm_package='test-pkg', import_statement="import 'test';",
            cdn_url='https://cdn.example.com/test.js', size_kb=1.5, note='A note',
        )
        assert pkg.cdn_url == 'https://cdn.example.com/test.js'
        assert pkg.size_kb == 1.5
        assert pkg.note == 'A note'

    def test_zero_size(self):
        pkg = PolyfillPackage(name='t', npm_package='t', import_statement='', size_kb=0.0)
        assert pkg.size_kb == 0.0


class TestPolyfillRecommendationDataclass:
    def test_npm_type(self, npm_recommendation):
        assert npm_recommendation.polyfill_type == 'npm'
        assert len(npm_recommendation.packages) == 1
        assert npm_recommendation.fallback_code is None

    def test_fallback_type(self, fallback_recommendation):
        assert fallback_recommendation.polyfill_type == 'fallback'
        assert len(fallback_recommendation.packages) == 0
        assert fallback_recommendation.fallback_code is not None

    def test_default_empty_lists(self):
        rec = PolyfillRecommendation(
            feature_id='x', feature_name='X', polyfill_type='npm',
        )
        assert rec.packages == []
        assert rec.browsers_affected == []


# ---------------------------------------------------------------------------
# get_recommendations — basic
# ---------------------------------------------------------------------------

class TestGetRecommendations:
    def test_single_unsupported_npm_feature(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'},
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) == 1
        assert recs[0].feature_id == 'fetch'
        assert recs[0].polyfill_type == 'npm'

    def test_single_unsupported_css_fallback(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'},
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) == 1
        assert recs[0].polyfill_type == 'fallback'
        assert recs[0].fallback_code is not None

    def test_partial_features_produce_recommendations(self, service):
        recs = service.get_recommendations(
            unsupported_features=set(),
            partial_features={'fetch'},
            browsers={'safari': '10'},
        )
        assert len(recs) == 1
        assert recs[0].feature_id == 'fetch'

    def test_mixed_unsupported_and_partial(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'},
            partial_features={'css-grid'},
            browsers={'ie': '11'},
        )
        ids = {r.feature_id for r in recs}
        assert 'fetch' in ids
        assert 'css-grid' in ids

    def test_no_duplicates_when_feature_in_both_sets(self, service):
        """If same feature is in both unsupported and partial, only one recommendation."""
        recs = service.get_recommendations(
            unsupported_features={'fetch'},
            partial_features={'fetch'},
            browsers={'ie': '11'},
        )
        assert len(recs) == 1

    def test_results_sorted_by_feature_id(self, service):
        recs = service.get_recommendations(
            unsupported_features={'promises', 'fetch', 'array-includes'},
            partial_features=set(),
            browsers={'ie': '11'},
        )
        ids = [r.feature_id for r in recs]
        assert ids == sorted(ids)

    def test_browsers_affected_matches_input(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'},
            partial_features=set(),
            browsers={'chrome': '40', 'firefox': '30'},
        )
        assert len(recs) == 1
        assert set(recs[0].browsers_affected) == {'chrome', 'firefox'}


# ---------------------------------------------------------------------------
# get_recommendations — empty / nonexistent
# ---------------------------------------------------------------------------

class TestGetRecommendationsEmpty:
    def test_empty_feature_sets(self, service):
        recs = service.get_recommendations(
            unsupported_features=set(),
            partial_features=set(),
            browsers={'chrome': '120'},
        )
        assert recs == []

    def test_nonexistent_features(self, service):
        recs = service.get_recommendations(
            unsupported_features={'totally-fake-feature', 'another-fake'},
            partial_features=set(),
            browsers={'chrome': '120'},
        )
        assert recs == []

    def test_mix_of_real_and_fake(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'totally-fake-feature'},
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) == 1
        assert recs[0].feature_id == 'fetch'

    def test_empty_browsers_dict(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'},
            partial_features=set(),
            browsers={},
        )
        assert len(recs) == 1
        assert recs[0].browsers_affected == []


# ---------------------------------------------------------------------------
# get_recommendations — all JS polyfills
# ---------------------------------------------------------------------------

class TestAllJSPolyfills:
    """Verify every JS entry in polyfill_map produces a recommendation."""

    ALL_JS = [
        'fetch', 'promises', 'async-functions', 'array-includes', 'array-flat',
        'object-entries', 'object-values', 'object-assign', 'object-fromentries',
        'pad-start-end', 'es6-string-includes', 'es6-number',
        'es6-map', 'es6-set', 'es6-weakmap', 'es6-weakset', 'es6-symbol', 'proxy',
        'intersectionobserver', 'resizeobserver', 'mutationobserver',
        'requestanimationframe', 'classlist', 'url', 'urlsearchparams',
        'customevent', 'abortcontroller', 'textencoder', 'matchmedia',
        'requestidlecallback', 'structuredclone', 'broadcastchannel', 'globalthis',
        'array-findindex', 'array-find', 'array-from', 'array-of', 'es6-array-fill',
        'pointer', 'focuswithin', 'focusvisible',
    ]

    @pytest.mark.parametrize("feature_id", ALL_JS)
    def test_js_feature_produces_npm_recommendation(self, service, feature_id):
        recs = service.get_recommendations(
            unsupported_features={feature_id},
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) == 1, f"{feature_id} should produce a recommendation"
        assert recs[0].polyfill_type == 'npm'
        assert len(recs[0].packages) > 0


# ---------------------------------------------------------------------------
# get_recommendations — all CSS polyfills
# ---------------------------------------------------------------------------

class TestAllCSSPolyfills:
    CSS_NPM = ['css-variables', 'css-sticky', 'object-fit', 'css-scroll-snap', 'css-scroll-behavior']
    CSS_FALLBACK = ['css-grid', 'flexbox', 'css-backdrop-filter', 'css-filters']

    @pytest.mark.parametrize("feature_id", CSS_NPM)
    def test_css_npm_feature(self, service, feature_id):
        recs = service.get_recommendations(
            unsupported_features={feature_id},
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) == 1
        assert recs[0].polyfill_type == 'npm'

    @pytest.mark.parametrize("feature_id", CSS_FALLBACK)
    def test_css_fallback_feature(self, service, feature_id):
        recs = service.get_recommendations(
            unsupported_features={feature_id},
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) == 1
        assert recs[0].polyfill_type == 'fallback'
        assert recs[0].fallback_code is not None
        assert len(recs[0].fallback_code) > 0


# ---------------------------------------------------------------------------
# get_recommendations — all HTML polyfills
# ---------------------------------------------------------------------------

class TestAllHTMLPolyfills:
    HTML = ['dialog', 'details', 'datalist', 'picture', 'template', 'input-color', 'input-date']

    @pytest.mark.parametrize("feature_id", HTML)
    def test_html_feature(self, service, feature_id):
        recs = service.get_recommendations(
            unsupported_features={feature_id},
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) == 1
        assert recs[0].polyfill_type == 'npm'
        assert len(recs[0].packages) > 0


# ---------------------------------------------------------------------------
# get_aggregate_install_command
# ---------------------------------------------------------------------------

class TestAggregateInstallCommand:
    def test_single_package(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        cmd = service.get_aggregate_install_command(recs)
        assert cmd == 'npm install whatwg-fetch'

    def test_multiple_packages_sorted(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'requestidlecallback', 'abortcontroller'},
            partial_features=set(), browsers={'ie': '11'},
        )
        cmd = service.get_aggregate_install_command(recs)
        assert cmd.startswith('npm install ')
        packages = cmd.replace('npm install ', '').split()
        assert packages == sorted(packages)

    def test_deduplication_of_core_js(self, service):
        """Multiple features using core-js should produce one core-js in the command."""
        recs = service.get_recommendations(
            unsupported_features={'array-includes', 'object-entries', 'globalthis'},
            partial_features=set(), browsers={'ie': '11'},
        )
        cmd = service.get_aggregate_install_command(recs)
        assert cmd.count('core-js') == 1

    def test_empty_recommendations(self, service):
        cmd = service.get_aggregate_install_command([])
        assert cmd == ''

    def test_fallback_only_returns_empty(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        cmd = service.get_aggregate_install_command(recs)
        assert cmd == ''


# ---------------------------------------------------------------------------
# get_aggregate_imports
# ---------------------------------------------------------------------------

class TestAggregateImports:
    def test_single_import(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        imports = service.get_aggregate_imports(recs)
        assert len(imports) == 1
        assert "import 'whatwg-fetch';" in imports[0]

    def test_multiple_imports(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'abortcontroller'},
            partial_features=set(), browsers={'ie': '11'},
        )
        imports = service.get_aggregate_imports(recs)
        assert len(imports) == 2

    def test_fallback_only_no_imports(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        imports = service.get_aggregate_imports(recs)
        assert imports == []

    def test_empty_recs(self, service):
        assert service.get_aggregate_imports([]) == []


# ---------------------------------------------------------------------------
# get_total_size_kb
# ---------------------------------------------------------------------------

class TestTotalSize:
    def test_single_package_size(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        size = service.get_total_size_kb(recs)
        assert size == 3.2  # whatwg-fetch

    def test_multiple_packages_sum(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'intersectionobserver'},
            partial_features=set(), browsers={'ie': '11'},
        )
        size = service.get_total_size_kb(recs)
        assert size == pytest.approx(3.2 + 4.8, rel=0.01)

    def test_fallback_only_zero_size(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        assert service.get_total_size_kb(recs) == 0.0

    def test_empty_zero_size(self, service):
        assert service.get_total_size_kb([]) == 0.0


# ---------------------------------------------------------------------------
# categorize_recommendations
# ---------------------------------------------------------------------------

class TestCategorize:
    def test_npm_only(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch'}, partial_features=set(), browsers={'ie': '11'},
        )
        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) == 1
        assert len(cat['fallback']) == 0

    def test_fallback_only(self, service):
        recs = service.get_recommendations(
            unsupported_features={'css-grid'}, partial_features=set(), browsers={'ie': '11'},
        )
        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) == 0
        assert len(cat['fallback']) == 1

    def test_mixed(self, service):
        recs = service.get_recommendations(
            unsupported_features={'fetch', 'css-grid', 'promises'},
            partial_features=set(), browsers={'ie': '11'},
        )
        cat = service.categorize_recommendations(recs)
        assert len(cat['npm']) == 2  # fetch + promises
        assert len(cat['fallback']) == 1  # css-grid

    def test_empty(self, service):
        cat = service.categorize_recommendations([])
        assert cat == {'npm': [], 'fallback': []}

    def test_all_keys_present(self, service):
        cat = service.categorize_recommendations([])
        assert 'npm' in cat
        assert 'fallback' in cat


# ---------------------------------------------------------------------------
# Large batch — all 53 features at once
# ---------------------------------------------------------------------------

class TestLargeBatch:
    ALL_FEATURES = {
        'fetch', 'promises', 'async-functions', 'array-includes', 'array-flat',
        'object-entries', 'object-values', 'object-assign', 'object-fromentries',
        'pad-start-end', 'es6-string-includes', 'es6-number',
        'es6-map', 'es6-set', 'es6-weakmap', 'es6-weakset', 'es6-symbol', 'proxy',
        'intersectionobserver', 'resizeobserver', 'mutationobserver',
        'requestanimationframe', 'classlist', 'url', 'urlsearchparams',
        'customevent', 'abortcontroller', 'textencoder', 'matchmedia',
        'requestidlecallback', 'structuredclone', 'broadcastchannel', 'globalthis',
        'array-findindex', 'array-find', 'array-from', 'array-of', 'es6-array-fill',
        'pointer', 'focuswithin', 'focusvisible',
        # CSS
        'css-grid', 'flexbox', 'css-backdrop-filter', 'css-filters',
        'css-variables', 'css-sticky', 'object-fit', 'css-scroll-snap', 'css-scroll-behavior',
        # HTML
        'dialog', 'details', 'datalist', 'picture', 'template', 'input-color', 'input-date',
    }

    def test_all_features_produce_recommendations(self, service):
        recs = service.get_recommendations(
            unsupported_features=self.ALL_FEATURES,
            partial_features=set(),
            browsers={'ie': '11'},
        )
        assert len(recs) >= 53

    def test_all_feature_ids_unique(self, service):
        recs = service.get_recommendations(
            unsupported_features=self.ALL_FEATURES,
            partial_features=set(),
            browsers={'ie': '11'},
        )
        ids = [r.feature_id for r in recs]
        assert len(ids) == len(set(ids))

    def test_install_command_not_empty(self, service):
        recs = service.get_recommendations(
            unsupported_features=self.ALL_FEATURES,
            partial_features=set(),
            browsers={'ie': '11'},
        )
        cmd = service.get_aggregate_install_command(recs)
        assert len(cmd) > len('npm install ')

    def test_total_size_is_sum_of_first_packages(self, service):
        recs = service.get_recommendations(
            unsupported_features=self.ALL_FEATURES,
            partial_features=set(),
            browsers={'ie': '11'},
        )
        manual_sum = 0.0
        for rec in recs:
            if rec.polyfill_type == 'npm' and rec.packages and rec.packages[0].size_kb:
                manual_sum += rec.packages[0].size_kb
        assert service.get_total_size_kb(recs) == pytest.approx(manual_sum)
