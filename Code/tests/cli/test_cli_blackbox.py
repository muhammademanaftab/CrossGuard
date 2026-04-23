"""Blackbox tests for CLI commands, exit codes, browser validation, and stdin.

Tests the public CLI interface via CliRunner without testing internal
implementation details.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
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


# --- AI gating (--ai flag and config key management) ---


@pytest.mark.blackbox
class TestAnalyzeAIFlag:
    def test_analyze_without_ai_flag_skips_ai(self, tmp_path, monkeypatch):
        """Even with env var set, no AI call happens unless --ai is passed."""
        monkeypatch.setenv('CROSSGUARD_AI_KEY', 'sk-fake')
        js_file = tmp_path / "t.js"
        js_file.write_text("const x = Promise.resolve();")
        with patch('src.cli.main.AnalyzerService.get_ai_fix_suggestions') as mock_ai:
            runner = CliRunner()
            result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'json'])
            assert result.exit_code == 0, result.output
            mock_ai.assert_not_called()

    def test_analyze_with_ai_flag_runs_ai(self, tmp_path):
        """--ai with an explicit --api-key triggers the AI call when issues exist."""
        css_file = tmp_path / "t.css"
        # Force unsupported features by targeting old IE; exit code may be 1
        # because issues exist, but that's orthogonal to whether AI was called.
        css_file.write_text(".a { display: grid; gap: 10px; container-type: inline-size; }")
        with patch('src.cli.main.AnalyzerService.get_ai_fix_suggestions', return_value=[]) as mock_ai:
            runner = CliRunner()
            result = runner.invoke(cli, [
                'analyze', str(css_file), '--format', 'json',
                '--browsers', 'ie:11',
                '--ai', '--api-key', 'sk-fake', '--ai-provider', 'anthropic',
            ])
            assert result.exit_code in (0, 1), result.output
            mock_ai.assert_called_once()

    def test_analyze_ai_flag_no_key_warns(self, tmp_path, monkeypatch):
        """Passing --ai without any key prints a warning and skips AI cleanly."""
        monkeypatch.delenv('CROSSGUARD_AI_KEY', raising=False)
        js_file = tmp_path / "t.js"
        js_file.write_text("const x = 1;")
        with patch('src.cli.main.AnalyzerService.get_setting', return_value=''), \
             patch('src.cli.main.AnalyzerService.get_ai_fix_suggestions') as mock_ai:
            runner = CliRunner(mix_stderr=False)
            result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'json', '--ai'])
            assert result.exit_code == 0, result.output
            assert '--ai requires an API key' in result.stderr
            mock_ai.assert_not_called()


@pytest.mark.blackbox
class TestConfigKeyManagement:
    def test_config_set_api_key_direct(self):
        """`config --set-api-key sk-...` saves the key via set_setting."""
        with patch('src.cli.main.AnalyzerService.set_setting') as mock_set:
            runner = CliRunner()
            result = runner.invoke(cli, ['config', '--set-api-key', 'sk-12345678'])
            assert result.exit_code == 0, result.output
            mock_set.assert_any_call('ai_api_key', 'sk-12345678')
            assert 'API key saved' in result.output

    def test_config_clear_api_key(self):
        """`config --clear-api-key` removes the saved key by setting to empty."""
        with patch('src.cli.main.AnalyzerService.set_setting') as mock_set:
            runner = CliRunner()
            result = runner.invoke(cli, ['config', '--clear-api-key'])
            assert result.exit_code == 0, result.output
            mock_set.assert_any_call('ai_api_key', '')
            assert 'API key cleared' in result.output
