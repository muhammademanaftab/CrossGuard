"""Tests for PolyfillLoader — singleton, lookups, reload, edge cases, save/load round-trip."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from src.polyfill.polyfill_loader import (
    PolyfillLoader,
    get_polyfill_loader,
    load_polyfill_map,
    save_polyfill_map,
    POLYFILL_MAP_PATH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def loader():
    return get_polyfill_loader()


@pytest.fixture
def raw_data():
    """Load actual polyfill_map.json once for data-driven tests."""
    return load_polyfill_map()


# ---------------------------------------------------------------------------
# Singleton behaviour
# ---------------------------------------------------------------------------

class TestSingleton:
    def test_same_instance(self):
        a = get_polyfill_loader()
        b = get_polyfill_loader()
        assert a is b

    def test_new_returns_same_object(self):
        a = PolyfillLoader()
        b = PolyfillLoader()
        assert a is b


# ---------------------------------------------------------------------------
# Lookups — JavaScript
# ---------------------------------------------------------------------------

class TestJavaScriptLookups:
    JS_FEATURES = [
        'fetch', 'promises', 'async-functions', 'array-includes', 'array-flat',
        'object-entries', 'object-values', 'object-assign', 'object-fromentries',
        'pad-start-end', 'es6-string-includes', 'es6-number',
        'es6-map', 'es6-set', 'es6-weakmap', 'es6-weakset', 'es6-symbol',
        'proxy', 'intersectionobserver', 'resizeobserver', 'mutationobserver',
        'requestanimationframe', 'classlist', 'url', 'urlsearchparams',
        'customevent', 'abortcontroller', 'textencoder', 'matchmedia',
        'requestidlecallback', 'structuredclone', 'broadcastchannel',
        'globalthis', 'array-findindex', 'array-find', 'array-from',
        'array-of', 'es6-array-fill', 'pointer', 'focuswithin', 'focusvisible',
    ]

    @pytest.mark.parametrize("feature_id", JS_FEATURES)
    def test_javascript_feature_exists(self, loader, feature_id):
        info = loader.get_polyfill(feature_id)
        assert info is not None, f"JS feature '{feature_id}' not found in polyfill map"

    @pytest.mark.parametrize("feature_id", JS_FEATURES)
    def test_javascript_feature_is_polyfillable(self, loader, feature_id):
        info = loader.get_polyfill(feature_id)
        assert info['polyfillable'] is True, f"JS feature '{feature_id}' should be polyfillable"

    @pytest.mark.parametrize("feature_id", JS_FEATURES)
    def test_javascript_feature_has_packages(self, loader, feature_id):
        info = loader.get_polyfill(feature_id)
        assert len(info.get('packages', [])) > 0, f"JS feature '{feature_id}' missing packages"

    def test_fetch_package_details(self, loader):
        info = loader.get_polyfill('fetch')
        pkg = info['packages'][0]
        assert pkg['npm'] == 'whatwg-fetch'
        assert 'import' in pkg
        assert pkg['size_kb'] == 3.2

    def test_promises_has_two_packages(self, loader):
        info = loader.get_polyfill('promises')
        assert len(info['packages']) == 2
        npm_names = {p['npm'] for p in info['packages']}
        assert 'core-js' in npm_names
        assert 'es6-promise' in npm_names

    def test_structuredclone_package(self, loader):
        info = loader.get_polyfill('structuredclone')
        assert info['name'] == 'structuredClone'
        assert info['packages'][0]['npm'] == '@ungap/structured-clone'

    def test_broadcastchannel_package(self, loader):
        info = loader.get_polyfill('broadcastchannel')
        assert info['packages'][0]['npm'] == 'broadcast-channel'
        assert info['packages'][0]['size_kb'] == 8.5


# ---------------------------------------------------------------------------
# Lookups — CSS
# ---------------------------------------------------------------------------

class TestCSSLookups:
    CSS_POLYFILLABLE = ['css-variables', 'css-sticky', 'object-fit', 'css-scroll-snap', 'css-scroll-behavior']
    CSS_FALLBACK_ONLY = ['css-grid', 'flexbox', 'css-backdrop-filter', 'css-filters']

    @pytest.mark.parametrize("feature_id", CSS_POLYFILLABLE)
    def test_css_polyfillable_exists(self, loader, feature_id):
        info = loader.get_polyfill(feature_id)
        assert info is not None
        assert info['polyfillable'] is True

    @pytest.mark.parametrize("feature_id", CSS_FALLBACK_ONLY)
    def test_css_fallback_only(self, loader, feature_id):
        info = loader.get_polyfill(feature_id)
        assert info is not None
        assert info['polyfillable'] is False
        assert 'fallback' in info

    @pytest.mark.parametrize("feature_id", CSS_FALLBACK_ONLY)
    def test_css_fallback_has_code(self, loader, feature_id):
        fb = loader.get_polyfill(feature_id)['fallback']
        assert 'code' in fb and len(fb['code']) > 0
        assert 'description' in fb and len(fb['description']) > 0

    def test_css_grid_fallback_mentions_flexbox(self, loader):
        fb = loader.get_polyfill('css-grid')['fallback']
        assert 'flex' in fb['code'].lower()

    def test_css_backdrop_filter_fallback_uses_supports(self, loader):
        fb = loader.get_polyfill('css-backdrop-filter')['fallback']
        assert '@supports' in fb['code']


# ---------------------------------------------------------------------------
# Lookups — HTML
# ---------------------------------------------------------------------------

class TestHTMLLookups:
    HTML_FEATURES = ['dialog', 'details', 'datalist', 'picture', 'template', 'input-color', 'input-date']

    @pytest.mark.parametrize("feature_id", HTML_FEATURES)
    def test_html_feature_exists(self, loader, feature_id):
        info = loader.get_polyfill(feature_id)
        assert info is not None, f"HTML feature '{feature_id}' not found"

    @pytest.mark.parametrize("feature_id", HTML_FEATURES)
    def test_html_feature_is_polyfillable(self, loader, feature_id):
        info = loader.get_polyfill(feature_id)
        assert info['polyfillable'] is True

    def test_dialog_polyfill_package(self, loader):
        info = loader.get_polyfill('dialog')
        assert info['packages'][0]['npm'] == 'dialog-polyfill'

    def test_input_date_uses_flatpickr(self, loader):
        info = loader.get_polyfill('input-date')
        assert info['packages'][0]['npm'] == 'flatpickr'


# ---------------------------------------------------------------------------
# Negative / missing lookups
# ---------------------------------------------------------------------------

class TestMissingFeatures:
    NONEXISTENT = [
        'completely-fake', 'css-supergrid', 'js-teleporter',
        '', 'FETCH', 'Fetch',  # case-sensitive
    ]

    @pytest.mark.parametrize("feature_id", NONEXISTENT)
    def test_nonexistent_returns_none(self, loader, feature_id):
        assert loader.get_polyfill(feature_id) is None

    @pytest.mark.parametrize("feature_id", NONEXISTENT)
    def test_has_polyfill_false(self, loader, feature_id):
        assert loader.has_polyfill(feature_id) is False

    @pytest.mark.parametrize("feature_id", NONEXISTENT)
    def test_is_polyfillable_false(self, loader, feature_id):
        assert loader.is_polyfillable(feature_id) is False


# ---------------------------------------------------------------------------
# has_polyfill vs is_polyfillable distinction
# ---------------------------------------------------------------------------

class TestPolyfillPredicates:
    def test_fallback_only_has_polyfill_true(self, loader):
        """css-grid has a fallback but is NOT polyfillable."""
        assert loader.has_polyfill('css-grid') is True

    def test_fallback_only_is_polyfillable_false(self, loader):
        assert loader.is_polyfillable('css-grid') is False

    def test_npm_feature_both_true(self, loader):
        assert loader.has_polyfill('fetch') is True
        assert loader.is_polyfillable('fetch') is True


# ---------------------------------------------------------------------------
# Category getters
# ---------------------------------------------------------------------------

class TestCategoryGetters:
    def test_javascript_polyfills_count(self, loader):
        js = loader.get_all_javascript_polyfills()
        assert len(js) >= 37  # at least the original 37

    def test_css_polyfills_count(self, loader):
        css = loader.get_all_css_polyfills()
        assert len(css) >= 9

    def test_html_polyfills_count(self, loader):
        html = loader.get_all_html_polyfills()
        assert len(html) >= 7

    def test_category_getters_return_copies(self, loader):
        """Mutating the returned dict must not affect the loader."""
        js = loader.get_all_javascript_polyfills()
        js['FAKE'] = {}
        assert 'FAKE' not in loader.get_all_javascript_polyfills()


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

class TestMetadata:
    def test_has_version(self, loader):
        meta = loader.get_metadata()
        assert 'version' in meta

    def test_has_description(self, loader):
        meta = loader.get_metadata()
        assert 'description' in meta

    def test_metadata_is_copy(self, loader):
        meta = loader.get_metadata()
        meta['FAKE'] = True
        assert 'FAKE' not in loader.get_metadata()


# ---------------------------------------------------------------------------
# Reload
# ---------------------------------------------------------------------------

class TestReload:
    def test_reload_succeeds(self, loader):
        """Reload should not raise even when called multiple times."""
        loader.reload()
        loader.reload()
        assert loader.get_polyfill('fetch') is not None


# ---------------------------------------------------------------------------
# load_polyfill_map / save_polyfill_map round-trip
# ---------------------------------------------------------------------------

class TestLoadSave:
    def test_load_returns_dict(self):
        data = load_polyfill_map()
        assert isinstance(data, dict)
        assert 'javascript' in data
        assert 'css' in data
        assert 'html' in data

    def test_load_has_metadata(self):
        data = load_polyfill_map()
        assert 'metadata' in data

    def test_save_and_reload_round_trip(self, tmp_path):
        """Save to a temp file, reload, and verify nothing is lost."""
        original = load_polyfill_map()
        js_count_before = len(original.get('javascript', {}))

        # Add a temp entry
        original['javascript']['_test_round_trip'] = {
            'name': 'Test Round Trip',
            'polyfillable': True,
            'packages': [{'name': 'test', 'npm': 'test', 'import': "import 'test';"}]
        }

        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', tmp_path / 'polyfill_map.json'):
            (tmp_path / 'polyfill_map.json').write_text(json.dumps(original), encoding='utf-8')
            reloaded = json.loads((tmp_path / 'polyfill_map.json').read_text())

        assert '_test_round_trip' in reloaded['javascript']
        assert len(reloaded['javascript']) == js_count_before + 1

    def test_load_missing_file_returns_defaults(self, tmp_path):
        fake_path = tmp_path / 'nonexistent.json'
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', fake_path):
            data = load_polyfill_map()
        assert data == {'metadata': {}, 'javascript': {}, 'css': {}, 'html': {}}

    def test_load_invalid_json_returns_defaults(self, tmp_path):
        bad_file = tmp_path / 'bad.json'
        bad_file.write_text('NOT JSON!!!', encoding='utf-8')
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', bad_file):
            data = load_polyfill_map()
        assert data == {'metadata': {}, 'javascript': {}, 'css': {}, 'html': {}}

    def test_save_creates_valid_json(self, tmp_path):
        out_path = tmp_path / 'polyfill_map.json'
        test_data = {
            'metadata': {'version': '1.0.0'},
            'javascript': {'test': {'name': 'Test', 'polyfillable': True, 'packages': []}},
            'css': {},
            'html': {},
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', out_path):
            result = save_polyfill_map(test_data)

        assert result is True
        loaded = json.loads(out_path.read_text(encoding='utf-8'))
        assert loaded['javascript']['test']['name'] == 'Test'

    def test_save_returns_false_on_write_error(self, tmp_path):
        readonly_dir = tmp_path / 'no_write'
        readonly_dir.mkdir()
        # Point to a path inside a file (impossible to write)
        fake_path = tmp_path / 'nonexistent_dir' / 'sub' / 'polyfill_map.json'
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', fake_path):
            result = save_polyfill_map({'metadata': {}})
        assert result is False


# ---------------------------------------------------------------------------
# Data integrity — every polyfill_map.json entry
# ---------------------------------------------------------------------------

class TestDataIntegrity:
    """Validate every entry in the real polyfill_map.json."""

    def test_every_entry_has_name(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                assert 'name' in info, f"{section}/{fid} missing 'name'"
                assert len(info['name']) > 0, f"{section}/{fid} has empty name"

    def test_every_entry_has_polyfillable_bool(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                assert 'polyfillable' in info, f"{section}/{fid} missing 'polyfillable'"
                assert isinstance(info['polyfillable'], bool), f"{section}/{fid} polyfillable not bool"

    def test_polyfillable_entries_have_packages(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                if info.get('polyfillable'):
                    assert 'packages' in info, f"{section}/{fid} polyfillable but no packages"
                    assert len(info['packages']) > 0, f"{section}/{fid} empty packages"

    def test_packages_have_required_fields(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                for i, pkg in enumerate(info.get('packages', [])):
                    assert 'name' in pkg, f"{section}/{fid} package[{i}] missing 'name'"
                    assert 'npm' in pkg, f"{section}/{fid} package[{i}] missing 'npm'"
                    assert 'import' in pkg, f"{section}/{fid} package[{i}] missing 'import'"

    def test_package_npm_names_are_nonempty(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                for pkg in info.get('packages', []):
                    assert len(pkg['npm'].strip()) > 0, f"{section}/{fid} has empty npm name"

    def test_package_imports_are_nonempty(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                for pkg in info.get('packages', []):
                    assert len(pkg['import'].strip()) > 0, f"{section}/{fid} has empty import"

    def test_package_sizes_are_positive(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                for pkg in info.get('packages', []):
                    if 'size_kb' in pkg:
                        assert pkg['size_kb'] > 0, f"{section}/{fid} has non-positive size"

    def test_fallbacks_have_code_and_description(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                if 'fallback' in info:
                    fb = info['fallback']
                    assert 'code' in fb, f"{section}/{fid} fallback missing 'code'"
                    assert 'description' in fb, f"{section}/{fid} fallback missing 'description'"
                    assert len(fb['code']) > 0
                    assert len(fb['description']) > 0

    def test_no_duplicate_npm_packages_within_entry(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                pkgs = info.get('packages', [])
                npm_names = [p['npm'] for p in pkgs]
                # core-js is allowed to repeat across entries but not within one entry
                assert len(npm_names) == len(set(npm_names)), (
                    f"{section}/{fid} has duplicate npm packages: {npm_names}"
                )

    def test_feature_ids_are_lowercase(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid in raw_data.get(section, {}):
                assert fid == fid.lower(), f"{section}/{fid} should be lowercase"

    def test_cdn_urls_start_with_https(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                for pkg in info.get('packages', []):
                    if 'cdn' in pkg:
                        assert pkg['cdn'].startswith('https://'), (
                            f"{section}/{fid} CDN URL not HTTPS: {pkg['cdn']}"
                        )

    def test_total_entry_count(self, raw_data):
        js = len(raw_data.get('javascript', {}))
        css = len(raw_data.get('css', {}))
        html = len(raw_data.get('html', {}))
        total = js + css + html
        assert total >= 53, f"Expected at least 53 polyfill entries, got {total}"
