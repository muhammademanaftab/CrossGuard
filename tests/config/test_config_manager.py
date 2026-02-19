"""Tests for configuration manager."""

import json
import os
import pytest

from src.config.config_manager import (
    ConfigManager,
    load_config,
    get_default_config,
    DEFAULT_CONFIG,
    CONFIG_FILENAME,
)


class TestDefaultConfig:
    """Default configuration values."""

    def test_has_browsers(self):
        cfg = get_default_config()
        assert 'browsers' in cfg
        assert 'chrome' in cfg['browsers']
        assert 'firefox' in cfg['browsers']
        assert 'safari' in cfg['browsers']
        assert 'edge' in cfg['browsers']

    def test_has_output_format(self):
        cfg = get_default_config()
        assert cfg['output'] == 'table'

    def test_has_ignore_patterns(self):
        cfg = get_default_config()
        assert 'node_modules' in cfg['ignore']
        assert '.git' in cfg['ignore']

    def test_returns_copy(self):
        a = get_default_config()
        b = get_default_config()
        a['output'] = 'json'
        assert b['output'] == 'table'


class TestConfigManager:
    """ConfigManager loading and property access."""

    def test_defaults_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mgr = ConfigManager()
        assert mgr.config_path is None
        assert mgr.output_format == 'table'
        assert 'chrome' in mgr.browsers

    def test_loads_from_explicit_path(self, tmp_path):
        config_data = {'browsers': {'chrome': '100'}, 'output': 'json'}
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text(json.dumps(config_data))

        mgr = ConfigManager(config_path=str(config_file))
        assert mgr.config_path == config_file
        assert mgr.browsers['chrome'] == '100'
        assert mgr.output_format == 'json'

    def test_merges_with_defaults(self, tmp_path):
        """File config overrides defaults, but defaults fill gaps."""
        config_data = {'output': 'summary'}
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text(json.dumps(config_data))

        mgr = ConfigManager(config_path=str(config_file))
        assert mgr.output_format == 'summary'
        # Browsers from defaults still present
        assert 'chrome' in mgr.browsers

    def test_overrides_take_precedence(self, tmp_path):
        config_data = {'output': 'json'}
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text(json.dumps(config_data))

        mgr = ConfigManager(
            config_path=str(config_file),
            overrides={'output': 'summary'},
        )
        assert mgr.output_format == 'summary'

    def test_searches_parent_dirs(self, tmp_path, monkeypatch):
        config_data = {'output': 'json'}
        (tmp_path / CONFIG_FILENAME).write_text(json.dumps(config_data))

        subdir = tmp_path / 'a' / 'b' / 'c'
        subdir.mkdir(parents=True)
        monkeypatch.chdir(subdir)

        mgr = ConfigManager()
        assert mgr.output_format == 'json'

    def test_ignore_patterns_property(self):
        mgr = ConfigManager()
        assert isinstance(mgr.ignore_patterns, list)
        assert 'node_modules' in mgr.ignore_patterns

    def test_rules_path_default_none(self):
        mgr = ConfigManager()
        assert mgr.rules_path is None

    def test_get_arbitrary_key(self):
        mgr = ConfigManager(overrides={'custom_key': 42})
        assert mgr.get('custom_key') == 42
        assert mgr.get('missing', 'default') == 'default'

    def test_to_dict_returns_copy(self):
        mgr = ConfigManager()
        d = mgr.to_dict()
        d['output'] = 'changed'
        assert mgr.output_format == 'table'


class TestCreateDefaultConfig:
    """ConfigManager.create_default_config() creates a config file."""

    def test_creates_file(self, tmp_path):
        path = ConfigManager.create_default_config(str(tmp_path))
        assert os.path.isfile(path)

    def test_file_is_valid_json(self, tmp_path):
        path = ConfigManager.create_default_config(str(tmp_path))
        with open(path) as f:
            data = json.load(f)
        assert 'browsers' in data
        assert 'output' in data

    def test_correct_filename(self, tmp_path):
        path = ConfigManager.create_default_config(str(tmp_path))
        assert path.endswith(CONFIG_FILENAME)


class TestLoadConfigConvenience:
    """Module-level load_config() function."""

    def test_returns_config_manager(self):
        mgr = load_config()
        assert isinstance(mgr, ConfigManager)

    def test_accepts_overrides(self):
        mgr = load_config(overrides={'output': 'summary'})
        assert mgr.output_format == 'summary'
