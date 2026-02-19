"""Tests for package.json config fallback."""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from src.config.config_manager import ConfigManager, _load_from_package_json


class TestLoadFromPackageJson:
    def test_reads_crossguard_key(self, tmp_path):
        pkg = tmp_path / 'package.json'
        pkg.write_text(json.dumps({
            'name': 'my-app',
            'crossguard': {
                'browsers': {'chrome': '120'},
                'output': 'json',
            }
        }))
        result = _load_from_package_json(tmp_path)
        assert result is not None
        assert result['browsers'] == {'chrome': '120'}
        assert result['output'] == 'json'

    def test_returns_none_when_no_crossguard_key(self, tmp_path):
        pkg = tmp_path / 'package.json'
        pkg.write_text(json.dumps({'name': 'my-app', 'version': '1.0.0'}))
        result = _load_from_package_json(tmp_path)
        assert result is None

    def test_returns_none_when_no_package_json(self, tmp_path):
        result = _load_from_package_json(tmp_path)
        assert result is None

    def test_returns_none_when_crossguard_is_not_dict(self, tmp_path):
        pkg = tmp_path / 'package.json'
        pkg.write_text(json.dumps({'crossguard': 'not a dict'}))
        result = _load_from_package_json(tmp_path)
        assert result is None

    def test_returns_none_on_invalid_json(self, tmp_path):
        pkg = tmp_path / 'package.json'
        pkg.write_text('not valid json {{{')
        result = _load_from_package_json(tmp_path)
        assert result is None

    def test_walks_up_to_parent(self, tmp_path):
        pkg = tmp_path / 'package.json'
        pkg.write_text(json.dumps({
            'crossguard': {'output': 'summary'}
        }))
        child = tmp_path / 'src'
        child.mkdir()
        result = _load_from_package_json(child)
        assert result is not None
        assert result['output'] == 'summary'


class TestConfigManagerPackageJsonFallback:
    def test_package_json_used_when_no_config_file(self, tmp_path):
        pkg = tmp_path / 'package.json'
        pkg.write_text(json.dumps({
            'crossguard': {'output': 'summary'}
        }))
        with patch('src.config.config_manager._find_config_file', return_value=None):
            with patch('src.config.config_manager._load_from_package_json', return_value={'output': 'summary'}):
                cm = ConfigManager()
                assert cm.output_format == 'summary'

    def test_config_file_takes_precedence(self, tmp_path):
        # If crossguard.config.json exists, package.json is ignored
        cfg = tmp_path / 'crossguard.config.json'
        cfg.write_text(json.dumps({'output': 'json'}))
        pkg = tmp_path / 'package.json'
        pkg.write_text(json.dumps({
            'crossguard': {'output': 'summary'}
        }))
        cm = ConfigManager(config_path=str(cfg))
        assert cm.output_format == 'json'

    def test_overrides_beat_package_json(self, tmp_path):
        with patch('src.config.config_manager._find_config_file', return_value=None):
            with patch('src.config.config_manager._load_from_package_json', return_value={'output': 'summary'}):
                cm = ConfigManager(overrides={'output': 'table'})
                assert cm.output_format == 'table'
