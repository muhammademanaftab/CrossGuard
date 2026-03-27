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
    assert mgr.browsers['chrome'] == '100'
    assert mgr.output_format == 'json'


@pytest.mark.blackbox
def test_merges_file_config_with_defaults(tmp_path):
    config_data = {'output': 'summary'}
    config_file = tmp_path / CONFIG_FILENAME
    config_file.write_text(json.dumps(config_data))

    mgr = ConfigManager(config_path=str(config_file))
    assert mgr.output_format == 'summary'
    assert 'chrome' in mgr.browsers


# --- Overrides / precedence ---

@pytest.mark.blackbox
def test_overrides_take_precedence_over_file(tmp_path):
    config_data = {'output': 'json'}
    config_file = tmp_path / CONFIG_FILENAME
    config_file.write_text(json.dumps(config_data))

    mgr = ConfigManager(config_path=str(config_file), overrides={'output': 'summary'})
    assert mgr.output_format == 'summary'


# --- create_default_config ---

@pytest.mark.blackbox
def test_create_default_config_writes_valid_json(tmp_path):
    path = ConfigManager.create_default_config(str(tmp_path))
    assert os.path.isfile(path)
    with open(path) as f:
        data = json.load(f)
    assert 'browsers' in data


# --- load_config convenience ---


# --- package.json ---

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


@pytest.mark.blackbox
def test_package_json_returns_none_when_missing(tmp_path):
    assert _load_from_package_json(tmp_path) is None


