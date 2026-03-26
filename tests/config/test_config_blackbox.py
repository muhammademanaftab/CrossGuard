"""Blackbox tests for config loading, merging, defaults, and package.json fallback."""

import json
import os
import pytest
from unittest.mock import patch

from src.config.config_manager import (
    ConfigManager,
    load_config,
    get_default_config,
    CONFIG_FILENAME,
    _load_from_package_json,
)


# --- Defaults ---

@pytest.mark.blackbox
def test_default_config_has_all_browsers_and_output():
    cfg = get_default_config()
    assert set(cfg['browsers']) == {'chrome', 'firefox', 'safari', 'edge'}
    assert cfg['output'] == 'table'
    assert cfg['rules'] is None


@pytest.mark.blackbox
def test_default_config_returns_independent_copies():
    a = get_default_config()
    b = get_default_config()
    a['output'] = 'json'
    assert b['output'] == 'table'


@pytest.mark.blackbox
def test_defaults_when_no_config_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mgr = ConfigManager()
    assert mgr.config_path is None
    assert mgr.output_format == 'table'
    assert 'chrome' in mgr.browsers


# --- Config file loading ---

@pytest.mark.blackbox
def test_loads_from_explicit_path(tmp_path):
    config_data = {'browsers': {'chrome': '100'}, 'output': 'json'}
    config_file = tmp_path / CONFIG_FILENAME
    config_file.write_text(json.dumps(config_data))

    mgr = ConfigManager(config_path=str(config_file))
    assert mgr.config_path == config_file
    assert mgr.browsers['chrome'] == '100'
    assert mgr.output_format == 'json'


@pytest.mark.blackbox
def test_merges_file_config_with_defaults(tmp_path):
    """File config overrides defaults, but defaults fill gaps."""
    config_data = {'output': 'summary'}
    config_file = tmp_path / CONFIG_FILENAME
    config_file.write_text(json.dumps(config_data))

    mgr = ConfigManager(config_path=str(config_file))
    assert mgr.output_format == 'summary'
    assert 'chrome' in mgr.browsers


@pytest.mark.blackbox
def test_searches_parent_directories(tmp_path, monkeypatch):
    config_data = {'output': 'json'}
    (tmp_path / CONFIG_FILENAME).write_text(json.dumps(config_data))

    subdir = tmp_path / 'a' / 'b' / 'c'
    subdir.mkdir(parents=True)
    monkeypatch.chdir(subdir)

    mgr = ConfigManager()
    assert mgr.output_format == 'json'


# --- Overrides / precedence ---

@pytest.mark.blackbox
def test_overrides_take_precedence_over_file(tmp_path):
    config_data = {'output': 'json'}
    config_file = tmp_path / CONFIG_FILENAME
    config_file.write_text(json.dumps(config_data))

    mgr = ConfigManager(config_path=str(config_file), overrides={'output': 'summary'})
    assert mgr.output_format == 'summary'


# --- API methods ---

@pytest.mark.blackbox
def test_get_returns_value_or_default():
    mgr = ConfigManager(overrides={'custom_key': 42})
    assert mgr.get('custom_key') == 42
    assert mgr.get('missing', 'fallback') == 'fallback'


@pytest.mark.blackbox
def test_to_dict_returns_independent_copy():
    mgr = ConfigManager()
    d = mgr.to_dict()
    d['output'] = 'changed'
    assert mgr.output_format == 'table'


# --- create_default_config ---

@pytest.mark.blackbox
def test_create_default_config_writes_valid_json(tmp_path):
    path = ConfigManager.create_default_config(str(tmp_path))
    assert os.path.isfile(path)
    assert path.endswith(CONFIG_FILENAME)
    with open(path) as f:
        data = json.load(f)
    assert 'browsers' in data
    assert 'output' in data


# --- load_config convenience ---

@pytest.mark.blackbox
def test_load_config_returns_config_manager_with_overrides():
    mgr = load_config(overrides={'output': 'summary'})
    assert isinstance(mgr, ConfigManager)
    assert mgr.output_format == 'summary'


# --- package.json: _load_from_package_json ---

@pytest.mark.blackbox
def test_package_json_reads_crossguard_key(tmp_path):
    pkg = tmp_path / 'package.json'
    pkg.write_text(json.dumps({
        'name': 'my-app',
        'crossguard': {'browsers': {'chrome': '120'}, 'output': 'json'},
    }))
    result = _load_from_package_json(tmp_path)
    assert result is not None
    assert result['browsers'] == {'chrome': '120'}
    assert result['output'] == 'json'


@pytest.mark.blackbox
@pytest.mark.parametrize("pkg_content, description", [
    ('{"name": "my-app", "version": "1.0.0"}', "no crossguard key"),
    ('{"crossguard": "not a dict"}', "crossguard is not a dict"),
], ids=["no-key", "non-dict"])
def test_package_json_returns_none_when_unusable(tmp_path, pkg_content, description):
    pkg = tmp_path / 'package.json'
    pkg.write_text(pkg_content)
    assert _load_from_package_json(tmp_path) is None


@pytest.mark.blackbox
def test_package_json_returns_none_when_missing(tmp_path):
    assert _load_from_package_json(tmp_path) is None


@pytest.mark.blackbox
def test_package_json_returns_none_on_invalid_json(tmp_path):
    pkg = tmp_path / 'package.json'
    pkg.write_text('not valid json {{{')
    assert _load_from_package_json(tmp_path) is None


# --- package.json: ConfigManager integration ---

@pytest.mark.blackbox
def test_package_json_used_as_fallback(tmp_path):
    with patch('src.config.config_manager._find_config_file', return_value=None):
        with patch('src.config.config_manager._load_from_package_json', return_value={'output': 'summary'}):
            cm = ConfigManager()
            assert cm.output_format == 'summary'


@pytest.mark.blackbox
def test_config_file_takes_precedence_over_package_json(tmp_path):
    cfg = tmp_path / CONFIG_FILENAME
    cfg.write_text(json.dumps({'output': 'json'}))
    pkg = tmp_path / 'package.json'
    pkg.write_text(json.dumps({'crossguard': {'output': 'summary'}}))

    cm = ConfigManager(config_path=str(cfg))
    assert cm.output_format == 'json'


@pytest.mark.blackbox
def test_overrides_beat_package_json():
    with patch('src.config.config_manager._find_config_file', return_value=None):
        with patch('src.config.config_manager._load_from_package_json', return_value={'output': 'summary'}):
            cm = ConfigManager(overrides={'output': 'table'})
            assert cm.output_format == 'table'
