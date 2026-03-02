"""Tests for polyfill map CRUD — load, save, add, edit, delete entries (used by rules manager)."""

import json
import copy
import pytest
from pathlib import Path
from unittest.mock import patch

from src.polyfill.polyfill_loader import (
    load_polyfill_map,
    save_polyfill_map,
    get_polyfill_loader,
    POLYFILL_MAP_PATH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def restore_singleton_after_test():
    """Ensure the polyfill loader singleton is restored to real data after each test."""
    yield
    # Reload from the real polyfill_map.json to undo any singleton corruption
    get_polyfill_loader().reload()


@pytest.fixture
def polyfill_data():
    """A fresh copy of the real polyfill_map.json for mutation tests."""
    return load_polyfill_map()


@pytest.fixture
def tmp_polyfill_file(tmp_path):
    """A temporary polyfill_map.json for save/load tests."""
    data = {
        'metadata': {'version': '1.0.0', 'description': 'Test'},
        'javascript': {
            'fetch': {
                'name': 'Fetch API',
                'polyfillable': True,
                'packages': [{'name': 'whatwg-fetch', 'npm': 'whatwg-fetch', 'import': "import 'whatwg-fetch';", 'size_kb': 3.2}]
            }
        },
        'css': {
            'css-grid': {
                'name': 'CSS Grid',
                'polyfillable': False,
                'fallback': {'type': 'css', 'description': 'Use flexbox', 'code': '/* flexbox fallback */'}
            }
        },
        'html': {
            'dialog': {
                'name': 'Dialog Element',
                'polyfillable': True,
                'packages': [{'name': 'dialog-polyfill', 'npm': 'dialog-polyfill', 'import': "import 'dialog-polyfill';", 'size_kb': 3.5}]
            }
        },
    }
    file_path = tmp_path / 'polyfill_map.json'
    file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return file_path, data


# ---------------------------------------------------------------------------
# Add entry
# ---------------------------------------------------------------------------

class TestAddEntry:
    def test_add_javascript_polyfill(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['new-feature'] = {
            'name': 'New Feature',
            'polyfillable': True,
            'packages': [{'name': 'new-pkg', 'npm': 'new-pkg', 'import': "import 'new-pkg';"}]
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            assert save_polyfill_map(data) is True

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert 'new-feature' in reloaded['javascript']
        assert reloaded['javascript']['new-feature']['name'] == 'New Feature'

    def test_add_css_fallback(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['css']['css-new'] = {
            'name': 'New CSS Feature',
            'polyfillable': False,
            'fallback': {'type': 'css', 'description': 'A fallback', 'code': '.new { display: block; }'}
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            assert save_polyfill_map(data) is True

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert 'css-new' in reloaded['css']
        assert reloaded['css']['css-new']['fallback']['code'] == '.new { display: block; }'

    def test_add_html_polyfill(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['html']['new-element'] = {
            'name': 'New HTML Element',
            'polyfillable': True,
            'packages': [{'name': 'new-el-polyfill', 'npm': 'new-el-polyfill', 'import': "import 'new-el-polyfill';"}]
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            assert save_polyfill_map(data) is True

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert 'new-element' in reloaded['html']

    def test_add_polyfill_with_all_package_fields(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['full-pkg'] = {
            'name': 'Full Package',
            'polyfillable': True,
            'packages': [{
                'name': 'full-pkg',
                'npm': 'full-pkg',
                'import': "import 'full-pkg';",
                'cdn': 'https://cdn.example.com/full-pkg.js',
                'size_kb': 5.5,
                'note': 'Complete polyfill',
            }]
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        pkg = reloaded['javascript']['full-pkg']['packages'][0]
        assert pkg['cdn'] == 'https://cdn.example.com/full-pkg.js'
        assert pkg['size_kb'] == 5.5
        assert pkg['note'] == 'Complete polyfill'


# ---------------------------------------------------------------------------
# Edit entry
# ---------------------------------------------------------------------------

class TestEditEntry:
    def test_edit_name(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['fetch']['name'] = 'Fetch API (Updated)'
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['javascript']['fetch']['name'] == 'Fetch API (Updated)'

    def test_edit_polyfillable_flag(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['fetch']['polyfillable'] = False
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['javascript']['fetch']['polyfillable'] is False

    def test_edit_package_npm_name(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['fetch']['packages'][0]['npm'] = 'new-fetch-pkg'
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['javascript']['fetch']['packages'][0]['npm'] == 'new-fetch-pkg'

    def test_edit_fallback_code(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['css']['css-grid']['fallback']['code'] = '/* new fallback code */'
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['css']['css-grid']['fallback']['code'] == '/* new fallback code */'

    def test_add_packages_to_fallback_entry(self, tmp_polyfill_file):
        """Convert a fallback-only entry to also have packages."""
        file_path, data = tmp_polyfill_file
        data['css']['css-grid']['polyfillable'] = True
        data['css']['css-grid']['packages'] = [
            {'name': 'grid-polyfill', 'npm': 'grid-polyfill', 'import': "import 'grid-polyfill';"}
        ]
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['css']['css-grid']['polyfillable'] is True
        assert len(reloaded['css']['css-grid']['packages']) == 1
        # Fallback should still be there too
        assert 'fallback' in reloaded['css']['css-grid']

    def test_rename_feature_id(self, tmp_polyfill_file):
        """Simulate renaming by deleting old key and adding new one."""
        file_path, data = tmp_polyfill_file
        old_data = data['javascript'].pop('fetch')
        data['javascript']['fetch-api'] = old_data
        data['javascript']['fetch-api']['name'] = 'Fetch API (Renamed)'
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert 'fetch' not in reloaded['javascript']
        assert 'fetch-api' in reloaded['javascript']


# ---------------------------------------------------------------------------
# Delete entry
# ---------------------------------------------------------------------------

class TestDeleteEntry:
    def test_delete_javascript_entry(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        del data['javascript']['fetch']
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert 'fetch' not in reloaded['javascript']

    def test_delete_css_entry(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        del data['css']['css-grid']
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert 'css-grid' not in reloaded['css']

    def test_delete_html_entry(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        del data['html']['dialog']
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert 'dialog' not in reloaded['html']

    def test_delete_preserves_other_entries(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        del data['javascript']['fetch']
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        # Other sections should be untouched
        assert 'css-grid' in reloaded['css']
        assert 'dialog' in reloaded['html']
        assert 'metadata' in reloaded

    def test_delete_all_in_section(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript'] = {}
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['javascript'] == {}
        assert len(reloaded['css']) > 0  # other sections preserved


# ---------------------------------------------------------------------------
# Round-trip: load → modify → save → load
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_add_reload_verify(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['round-trip-test'] = {
            'name': 'Round Trip Test',
            'polyfillable': True,
            'packages': [{'name': 'rt', 'npm': 'rt', 'import': "import 'rt';", 'size_kb': 1.0}]
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)
            reloaded = load_polyfill_map()

        # Note: load_polyfill_map reads from POLYFILL_MAP_PATH, which is patched
        # So reload from file directly
        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['javascript']['round-trip-test']['packages'][0]['size_kb'] == 1.0

    def test_multiple_modifications(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file

        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            # Add
            data['javascript']['new1'] = {'name': 'New 1', 'polyfillable': True, 'packages': []}
            save_polyfill_map(data)

            # Edit
            data['javascript']['new1']['name'] = 'New 1 Updated'
            save_polyfill_map(data)

            # Add another
            data['javascript']['new2'] = {'name': 'New 2', 'polyfillable': False}
            save_polyfill_map(data)

            # Delete first
            del data['javascript']['new1']
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert 'new1' not in reloaded['javascript']
        assert 'new2' in reloaded['javascript']
        assert reloaded['javascript']['new2']['name'] == 'New 2'

    def test_metadata_preserved_through_edits(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        original_meta = copy.deepcopy(data['metadata'])

        data['javascript']['temp'] = {'name': 'Temp', 'polyfillable': True, 'packages': []}
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['metadata'] == original_meta


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_packages_list(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['empty-pkg'] = {
            'name': 'Empty Packages',
            'polyfillable': True,
            'packages': [],
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['javascript']['empty-pkg']['packages'] == []

    def test_unicode_in_name(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['unicode'] = {
            'name': 'Feature with émojis 🎉',
            'polyfillable': True,
            'packages': [{'name': 'test', 'npm': 'test', 'import': "import 'test';"}]
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert '🎉' in reloaded['javascript']['unicode']['name']

    def test_multiline_import_statement(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        data['javascript']['multi-import'] = {
            'name': 'Multi Import',
            'polyfillable': True,
            'packages': [{
                'name': 'multi',
                'npm': 'multi',
                'import': "import { A } from 'multi';\nwindow.A = window.A || A;",
            }]
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert '\n' in reloaded['javascript']['multi-import']['packages'][0]['import']

    def test_multiline_fallback_code(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        code = "/* fallback */\n.container {\n  display: block;\n}\n@supports (display: grid) {\n  .container { display: grid; }\n}"
        data['css']['multi-fallback'] = {
            'name': 'Multi Fallback',
            'polyfillable': False,
            'fallback': {'type': 'css', 'description': 'test', 'code': code}
        }
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        reloaded = json.loads(file_path.read_text(encoding='utf-8'))
        assert reloaded['css']['multi-fallback']['fallback']['code'] == code

    def test_saved_json_is_formatted(self, tmp_polyfill_file):
        """Saved JSON should be human-readable (indented)."""
        file_path, data = tmp_polyfill_file
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        raw = file_path.read_text(encoding='utf-8')
        # Indented JSON should have lines starting with spaces
        lines = raw.strip().split('\n')
        assert any(line.startswith('  ') for line in lines)

    def test_saved_json_ends_with_newline(self, tmp_polyfill_file):
        file_path, data = tmp_polyfill_file
        with patch('src.polyfill.polyfill_loader.POLYFILL_MAP_PATH', file_path):
            save_polyfill_map(data)

        raw = file_path.read_text(encoding='utf-8')
        assert raw.endswith('\n')
