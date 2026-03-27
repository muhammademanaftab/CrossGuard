"""Blackbox tests for CLI commands, exit codes, browser validation, and stdin.

Tests the public CLI interface via CliRunner without testing internal
implementation details.
"""

import json
import os
import pytest
import click
from click.testing import CliRunner

from src.cli.main import cli, _parse_browsers


# --- Browser validation ---


@pytest.mark.blackbox
class TestParseBrowsers:
    def test_valid_input(self):
        assert _parse_browsers('chrome:120,firefox:121') == {'chrome': '120', 'firefox': '121'}

    def test_none_returns_none(self):
        assert _parse_browsers(None) is None

    def test_invalid_input_raises(self):
        with pytest.raises(click.BadParameter, match="Unknown browser 'netscape'"):
            _parse_browsers('netscape:5')


# --- Analyze command ---


@pytest.mark.blackbox
class TestAnalyzeCommand:
    def test_nonexistent_target(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '/nonexistent/file.js'])
        assert result.exit_code == 2

    def test_analyze_single_file_json(self, tmp_path):
        js_file = tmp_path / "test.js"
        js_file.write_text("const x = 1; let y = 2;")
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'json'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        data = json.loads(result.output)
        assert data['success'] is True

    def test_unsupported_file_type(self, tmp_path):
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("hello")
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', str(txt_file)])
        assert result.exit_code == 2


# --- Misc commands ---


@pytest.mark.blackbox
class TestMiscCommands:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output


# --- Stdin support ---


@pytest.mark.blackbox
class TestStdinSupport:
    def test_stdin_requires_filename(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '--stdin'], input='const x = 1;')
        assert result.exit_code == 2
        assert '--stdin-filename is required' in result.output

    def test_stdin_with_js(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'test.js', '--format', 'json'],
            input='const x = Promise.resolve();',
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
