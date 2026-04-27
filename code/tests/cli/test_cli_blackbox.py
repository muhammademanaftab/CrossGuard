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
            runner = CliRunner()
            result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'json', '--ai'])
            assert result.exit_code == 0, result.output
            # Old Click folds stderr into output; new Click (8.3+) splits them.
            # Try stderr first; if it raises (not separately captured) or is empty, fall back to output.
            try:
                stderr = result.stderr or ''
            except ValueError:
                stderr = ''
            combined = result.output + stderr
            assert '--ai requires an API key' in combined
            mock_ai.assert_not_called()


# --- Quality gate combinations (--fail-on-errors / --fail-on-warnings) ---


@pytest.mark.blackbox
class TestQualityGateCombinations:
    """`--fail-on-score` is covered elsewhere; this pins the error/warning
    gates and their AND-composition (any breached gate => exit 1)."""

    def _clean_js(self, tmp_path):
        f = tmp_path / "ok.js"
        f.write_text("const x = 1;")
        return f

    def _problem_css(self, tmp_path):
        # Modern CSS that is unsupported / partially supported in IE 11.
        f = tmp_path / "bad.css"
        f.write_text(".a { display: grid; gap: 10px; container-type: inline-size; }")
        return f

    def test_fail_on_errors_passes_when_threshold_high(self, tmp_path):
        f = self._clean_js(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, [
            'analyze', str(f), '--format', 'summary',
            '--fail-on-errors', '100',
        ])
        assert result.exit_code == 0, result.output

    @staticmethod
    def _combined(result):
        # Click 8.3+ separates stderr; older Click folds it into output.
        try:
            stderr = result.stderr or ''
        except ValueError:
            stderr = ''
        return result.output + stderr

    def test_fail_on_warnings_fails_when_threshold_zero(self, tmp_path):
        f = self._problem_css(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, [
            'analyze', str(f), '--format', 'summary',
            '--browsers', 'ie:11',
            '--fail-on-warnings', '0',
        ])
        # Either errors or warnings will trip; we only care that it failed.
        assert result.exit_code == 1
        assert 'GATE FAILED' in self._combined(result)

    def test_combined_gates_fail_if_any_breached(self, tmp_path):
        f = self._problem_css(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, [
            'analyze', str(f), '--format', 'summary',
            '--browsers', 'ie:11',
            '--fail-on-score', '0',     # 0% min: passes alone
            '--fail-on-errors', '0',    # any error trips this
        ])
        assert result.exit_code == 1
        # The error-count failure must be the one reported, not the score one.
        assert 'Error count' in self._combined(result)


