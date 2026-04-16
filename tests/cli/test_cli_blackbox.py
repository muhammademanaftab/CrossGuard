"""Blackbox tests for CLI commands, exit codes, browser validation, and stdin.

Tests the public CLI interface via CliRunner without testing internal
implementation details.
"""

import json
import pytest
from click.testing import CliRunner

from src.cli.main import cli, _parse_browsers


# --- Browser validation ---


@pytest.mark.blackbox
class TestParseBrowsers:
    def test_valid_input(self):
        assert _parse_browsers('chrome:120,firefox:121') == {'chrome': '120', 'firefox': '121'}


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


# --- Stdin support ---


@pytest.mark.blackbox
class TestStdinSupport:
    def test_stdin_with_js(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'test.js', '--format', 'json'],
            input='const x = Promise.resolve();',
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
