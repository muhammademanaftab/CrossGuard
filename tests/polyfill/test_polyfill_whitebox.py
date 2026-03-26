"""Whitebox tests for polyfill internals -- singleton, reload, load/save, generator."""

import json
import re
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
from src.polyfill.polyfill_service import PolyfillService
from src.polyfill.polyfill_generator import generate_polyfills_content


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def loader():
    return get_polyfill_loader()


@pytest.fixture
def service():
    return PolyfillService()


@pytest.fixture
def npm_recs(service):
    return service.get_recommendations({'fetch', 'promises'}, set(), {'ie': '11'})


# ---------------------------------------------------------------------------
# Singleton pattern
# ---------------------------------------------------------------------------

class TestSingleton:
    @pytest.mark.whitebox
    def test_factory_returns_same_instance(self):
        assert get_polyfill_loader() is get_polyfill_loader()

    @pytest.mark.whitebox
    def test_constructor_returns_same_instance(self):
        assert PolyfillLoader() is PolyfillLoader()


# ---------------------------------------------------------------------------
# Reload
# ---------------------------------------------------------------------------

class TestReload:
    @pytest.mark.whitebox
    def test_reload_preserves_data(self, loader):
        loader.reload()
        loader.reload()
        assert loader.get_polyfill('fetch') is not None


# ---------------------------------------------------------------------------
# Category getters
# ---------------------------------------------------------------------------

class TestCategoryGetters:
    @pytest.mark.whitebox
    def test_category_counts(self, loader):
        assert len(loader.get_all_javascript_polyfills()) >= 37
        assert len(loader.get_all_css_polyfills()) >= 9
        assert len(loader.get_all_html_polyfills()) >= 7

    @pytest.mark.whitebox
    def test_category_getters_return_copies(self, loader):
        js = loader.get_all_javascript_polyfills()
        js['FAKE'] = {}
        assert 'FAKE' not in loader.get_all_javascript_polyfills()


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

class TestMetadata:
    @pytest.mark.whitebox
    def test_metadata_fields_and_isolation(self, loader):
        meta = loader.get_metadata()
        assert 'version' in meta and 'description' in meta
        meta['FAKE'] = True
        assert 'FAKE' not in loader.get_metadata()


# ---------------------------------------------------------------------------
# load_polyfill_map / save_polyfill_map
# ---------------------------------------------------------------------------

class TestLoadSave:
    @pytest.mark.whitebox
    def test_load_returns_all_sections(self):
        data = load_polyfill_map()
        assert isinstance(data, dict)
        for key in ('javascript', 'css', 'html', 'metadata'):
            assert key in data

    @pytest.mark.whitebox
    def test_load_missing_file_returns_defaults(self, tmp_path):
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', tmp_path / 'nope.json'):
            data = load_polyfill_map()
        assert data == {'metadata': {}, 'javascript': {}, 'css': {}, 'html': {}}

    @pytest.mark.whitebox
    def test_load_invalid_json_returns_defaults(self, tmp_path):
        bad = tmp_path / 'bad.json'
        bad.write_text('NOT JSON!!!', encoding='utf-8')
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', bad):
            data = load_polyfill_map()
        assert data == {'metadata': {}, 'javascript': {}, 'css': {}, 'html': {}}

    @pytest.mark.whitebox
    def test_save_creates_valid_json(self, tmp_path):
        out = tmp_path / 'polyfill_map.json'
        test_data = {
            'metadata': {'version': '1.0.0'},
            'javascript': {'test': {'name': 'Test', 'polyfillable': True, 'packages': []}},
            'css': {}, 'html': {},
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', out):
            assert save_polyfill_map(test_data) is True
        loaded = json.loads(out.read_text(encoding='utf-8'))
        assert loaded['javascript']['test']['name'] == 'Test'

    @pytest.mark.whitebox
    def test_save_returns_false_on_write_error(self, tmp_path):
        fake = tmp_path / 'no' / 'such' / 'dir' / 'file.json'
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', fake):
            assert save_polyfill_map({'metadata': {}}) is False


# ---------------------------------------------------------------------------
# Content generation internals
# ---------------------------------------------------------------------------

class TestGenerateContent:
    @pytest.mark.whitebox
    def test_header_imports_and_timestamp(self, npm_recs):
        content = generate_polyfills_content(npm_recs)
        assert 'Auto-generated by Cross Guard' in content
        assert "import './polyfills';" in content
        assert "import 'whatwg-fetch';" in content
        assert re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', content)

    @pytest.mark.whitebox
    def test_empty_recs_still_valid(self):
        content = generate_polyfills_content([])
        assert 'Auto-generated by Cross Guard' in content

    @pytest.mark.whitebox
    def test_feature_names_as_comments(self, npm_recs):
        content = generate_polyfills_content(npm_recs)
        assert '// Fetch API' in content
        assert '// JavaScript Promises' in content


# ---------------------------------------------------------------------------
# Data integrity -- validate polyfill_map.json structure
# ---------------------------------------------------------------------------

class TestDataIntegrity:
    @pytest.mark.whitebox
    def test_all_entries_have_name_polyfillable_and_valid_packages(self):
        """Condensed data integrity: every entry has name, polyfillable bool,
        and polyfillable entries have packages with required fields."""
        data = load_polyfill_map()
        total = 0
        for section in ('javascript', 'css', 'html'):
            for fid, info in data.get(section, {}).items():
                total += 1
                assert 'name' in info and len(info['name']) > 0, f"{section}/{fid} bad name"
                assert isinstance(info.get('polyfillable'), bool), f"{section}/{fid} bad polyfillable"
                assert fid == fid.lower(), f"{section}/{fid} not lowercase"
                if info['polyfillable']:
                    assert len(info.get('packages', [])) > 0, f"{section}/{fid} polyfillable but no packages"
                for pkg in info.get('packages', []):
                    assert pkg.get('npm', '').strip(), f"{section}/{fid} empty npm"
                    assert pkg.get('import', '').strip(), f"{section}/{fid} empty import"
                if 'fallback' in info:
                    fb = info['fallback']
                    assert fb.get('code', '').strip(), f"{section}/{fid} fallback missing code"
                    assert fb.get('description', '').strip(), f"{section}/{fid} fallback missing desc"
        assert total >= 53
