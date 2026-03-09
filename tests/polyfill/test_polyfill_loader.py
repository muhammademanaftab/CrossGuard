"""Tests for PolyfillLoader — singleton, lookups, predicates, categories, metadata, reload, load/save."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

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
    def test_same_instance_via_factory(self):
        a = get_polyfill_loader()
        b = get_polyfill_loader()
        assert a is b

    def test_same_instance_via_constructor(self):
        a = PolyfillLoader()
        b = PolyfillLoader()
        assert a is b


# ---------------------------------------------------------------------------
# Lookups — JavaScript (batch test + specific detail tests)
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

    def test_all_js_features_exist_polyfillable_with_packages(self, loader):
        """Every JS feature exists, is polyfillable, and has packages."""
        for fid in self.JS_FEATURES:
            info = loader.get_polyfill(fid)
            assert info is not None, f"JS feature '{fid}' not found"
            assert info['polyfillable'] is True, f"'{fid}' should be polyfillable"
            assert len(info.get('packages', [])) > 0, f"'{fid}' missing packages"

    def test_fetch_package_details(self, loader):
        pkg = loader.get_polyfill('fetch')['packages'][0]
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
# Lookups — CSS (batch tests + specific detail tests)
# ---------------------------------------------------------------------------

class TestCSSLookups:
    CSS_POLYFILLABLE = ['css-variables', 'css-sticky', 'object-fit', 'css-scroll-snap', 'css-scroll-behavior']
    CSS_FALLBACK_ONLY = ['css-grid', 'flexbox', 'css-backdrop-filter', 'css-filters']

    def test_all_css_polyfillable_entries(self, loader):
        """All CSS polyfillable entries exist and are marked polyfillable."""
        for fid in self.CSS_POLYFILLABLE:
            info = loader.get_polyfill(fid)
            assert info is not None, f"CSS feature '{fid}' not found"
            assert info['polyfillable'] is True, f"'{fid}' should be polyfillable"

    def test_all_css_fallback_entries(self, loader):
        """All CSS fallback entries exist, are not polyfillable, and have code."""
        for fid in self.CSS_FALLBACK_ONLY:
            info = loader.get_polyfill(fid)
            assert info is not None, f"CSS feature '{fid}' not found"
            assert info['polyfillable'] is False, f"'{fid}' should not be polyfillable"
            fb = info['fallback']
            assert 'code' in fb and len(fb['code']) > 0, f"'{fid}' missing fallback code"
            assert 'description' in fb and len(fb['description']) > 0, f"'{fid}' missing fallback description"

    def test_css_grid_fallback_mentions_flexbox(self, loader):
        fb = loader.get_polyfill('css-grid')['fallback']
        assert 'flex' in fb['code'].lower()

    def test_css_backdrop_filter_fallback_uses_supports(self, loader):
        fb = loader.get_polyfill('css-backdrop-filter')['fallback']
        assert '@supports' in fb['code']


# ---------------------------------------------------------------------------
# Lookups — HTML (batch test + specific detail tests)
# ---------------------------------------------------------------------------

class TestHTMLLookups:
    HTML_FEATURES = ['dialog', 'details', 'datalist', 'picture', 'template', 'input-color', 'input-date']

    def test_all_html_features_exist_and_polyfillable(self, loader):
        """All HTML features exist and are polyfillable."""
        for fid in self.HTML_FEATURES:
            info = loader.get_polyfill(fid)
            assert info is not None, f"HTML feature '{fid}' not found"
            assert info['polyfillable'] is True, f"'{fid}' should be polyfillable"

    def test_dialog_polyfill_package(self, loader):
        info = loader.get_polyfill('dialog')
        assert info['packages'][0]['npm'] == 'dialog-polyfill'

    def test_input_date_uses_flatpickr(self, loader):
        info = loader.get_polyfill('input-date')
        assert info['packages'][0]['npm'] == 'flatpickr'


# ---------------------------------------------------------------------------
# Named feature lookups (merged from root test_polyfill_module.py)
# ---------------------------------------------------------------------------

class TestNamedFeatureLookups:
    """Verify specific features return expected names and types."""

    def test_fetch_details(self, loader):
        info = loader.get_polyfill('fetch')
        assert info['name'] == 'Fetch API'
        assert info['polyfillable'] is True
        assert len(info['packages']) > 0

    def test_css_grid_details(self, loader):
        info = loader.get_polyfill('css-grid')
        assert info['name'] == 'CSS Grid Layout'
        assert info['polyfillable'] is False
        assert 'fallback' in info

    def test_dialog_details(self, loader):
        info = loader.get_polyfill('dialog')
        assert info['name'] == 'HTML <dialog> Element'
        assert info['polyfillable'] is True


# ---------------------------------------------------------------------------
# Negative / missing lookups (collapsed from 3 tests per ID to 1)
# ---------------------------------------------------------------------------

class TestMissingFeatures:
    NONEXISTENT = [
        'completely-fake', 'css-supergrid', 'js-teleporter',
        '', 'FETCH', 'Fetch',
    ]

    def test_nonexistent_features_return_none(self, loader):
        """Nonexistent features return None and both predicates are False."""
        for fid in self.NONEXISTENT:
            assert loader.get_polyfill(fid) is None, f"'{fid}' should return None"
            assert loader.has_polyfill(fid) is False, f"has_polyfill('{fid}') should be False"
            assert loader.is_polyfillable(fid) is False, f"is_polyfillable('{fid}') should be False"


# ---------------------------------------------------------------------------
# has_polyfill vs is_polyfillable distinction
# ---------------------------------------------------------------------------

class TestPolyfillPredicates:
    def test_fallback_has_polyfill_but_not_polyfillable(self, loader):
        """css-grid has a fallback (has_polyfill True) but is NOT polyfillable."""
        assert loader.has_polyfill('css-grid') is True
        assert loader.is_polyfillable('css-grid') is False

    def test_npm_feature_both_true(self, loader):
        assert loader.has_polyfill('fetch') is True
        assert loader.is_polyfillable('fetch') is True


# ---------------------------------------------------------------------------
# Category getters
# ---------------------------------------------------------------------------

class TestCategoryGetters:
    def test_javascript_polyfills_count(self, loader):
        assert len(loader.get_all_javascript_polyfills()) >= 37

    def test_css_polyfills_count(self, loader):
        assert len(loader.get_all_css_polyfills()) >= 9

    def test_html_polyfills_count(self, loader):
        assert len(loader.get_all_html_polyfills()) >= 7

    def test_category_getters_return_copies(self, loader):
        js = loader.get_all_javascript_polyfills()
        js['FAKE'] = {}
        assert 'FAKE' not in loader.get_all_javascript_polyfills()


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

class TestMetadata:
    def test_metadata_fields(self, loader):
        meta = loader.get_metadata()
        assert 'version' in meta
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
        loader.reload()
        loader.reload()
        assert loader.get_polyfill('fetch') is not None


# ---------------------------------------------------------------------------
# load_polyfill_map / save_polyfill_map
# ---------------------------------------------------------------------------

class TestLoadSave:
    def test_load_returns_complete_dict(self):
        data = load_polyfill_map()
        assert isinstance(data, dict)
        for key in ('javascript', 'css', 'html', 'metadata'):
            assert key in data

    def test_save_and_reload_round_trip(self, tmp_path):
        original = load_polyfill_map()
        js_count_before = len(original.get('javascript', {}))

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
        fake_path = tmp_path / 'nonexistent_dir' / 'sub' / 'polyfill_map.json'
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', fake_path):
            result = save_polyfill_map({'metadata': {}})
        assert result is False


# ---------------------------------------------------------------------------
# Data integrity — validate every polyfill_map.json entry
# ---------------------------------------------------------------------------

class TestDataIntegrity:
    """Validate structure/consistency of the real polyfill_map.json."""

    def test_every_entry_has_name_and_polyfillable(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                assert 'name' in info and len(info['name']) > 0, f"{section}/{fid} missing/empty name"
                assert 'polyfillable' in info, f"{section}/{fid} missing polyfillable"
                assert isinstance(info['polyfillable'], bool), f"{section}/{fid} polyfillable not bool"

    def test_polyfillable_entries_have_packages(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                if info.get('polyfillable'):
                    assert len(info.get('packages', [])) > 0, f"{section}/{fid} polyfillable but no packages"

    def test_packages_have_required_fields(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                for i, pkg in enumerate(info.get('packages', [])):
                    assert 'name' in pkg, f"{section}/{fid} package[{i}] missing 'name'"
                    assert 'npm' in pkg and len(pkg['npm'].strip()) > 0, f"{section}/{fid} empty npm"
                    assert 'import' in pkg and len(pkg['import'].strip()) > 0, f"{section}/{fid} empty import"

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
                    assert 'code' in fb and len(fb['code']) > 0, f"{section}/{fid} fallback missing code"
                    assert 'description' in fb and len(fb['description']) > 0, f"{section}/{fid} fallback missing description"

    def test_no_duplicate_npm_within_entry(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                npm_names = [p['npm'] for p in info.get('packages', [])]
                assert len(npm_names) == len(set(npm_names)), f"{section}/{fid} duplicate npm: {npm_names}"

    def test_feature_ids_are_lowercase(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid in raw_data.get(section, {}):
                assert fid == fid.lower(), f"{section}/{fid} should be lowercase"

    def test_cdn_urls_start_with_https(self, raw_data):
        for section in ('javascript', 'css', 'html'):
            for fid, info in raw_data.get(section, {}).items():
                for pkg in info.get('packages', []):
                    if 'cdn' in pkg:
                        assert pkg['cdn'].startswith('https://'), f"{section}/{fid} CDN not HTTPS"

    def test_total_entry_count(self, raw_data):
        total = sum(len(raw_data.get(s, {})) for s in ('javascript', 'css', 'html'))
        assert total >= 53, f"Expected at least 53 polyfill entries, got {total}"
