"""Blackbox tests for config loading, merging, defaults, and package.json fallback."""

import json
import pytest

from src.config.config_manager import (
    ConfigManager,
    CONFIG_FILENAME,
    _load_from_package_json,
)


# --- Defaults ---

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
