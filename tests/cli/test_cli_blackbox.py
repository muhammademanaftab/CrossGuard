"""Blackbox tests for CLI commands, exit codes, browser validation, and stdin.

Tests the public CLI interface via CliRunner without testing internal
implementation details. Each test invokes a CLI command and asserts on
exit codes, stdout content, or side effects (file creation).
"""

import json
import os
import pytest
import click
from click.testing import CliRunner

from src.cli.main import cli, _parse_browsers, _classify_files, _collect_files


# --- Browser validation ---


@pytest.mark.blackbox
class TestParseBrowsers:
    @pytest.mark.parametrize("input_str, expected", [
        ('chrome:120', {'chrome': '120'}),
        ('chrome:120,firefox:121', {'chrome': '120', 'firefox': '121'}),
        ('chrome : 120 , safari : 18.4', {'chrome': '120', 'safari': '18.4'}),
        ('Chrome:120', {'chrome': '120'}),
    ])
    def test_valid_inputs(self, input_str, expected):
        assert _parse_browsers(input_str) == expected

    @pytest.mark.parametrize("input_str", [None, ''])
    def test_none_or_empty_returns_none(self, input_str):
        assert _parse_browsers(input_str) is None

    @pytest.mark.parametrize("input_str, error_match", [
        ('netscape:5', "Unknown browser 'netscape'"),
        ('chrom:120', "Did you mean 'chrome'"),
        ('chrome120', "Invalid format"),
        ('chrome:latest', "Version must be numeric"),
    ])
    def test_invalid_inputs_raise(self, input_str, error_match):
        with pytest.raises(click.BadParameter, match=error_match):
            _parse_browsers(input_str)

    def test_all_known_browsers_accepted(self):
        from src.utils.config import LATEST_VERSIONS
        for browser in LATEST_VERSIONS:
            result = _parse_browsers(f'{browser}:1')
            assert browser in result


# --- File classification and collection ---


@pytest.mark.blackbox
class TestClassifyFiles:
    @pytest.mark.parametrize("files, expected_counts", [
        (['index.html', 'page.htm'], (2, 0, 0)),
        (['style.css'], (0, 1, 0)),
        (['app.js', 'mod.mjs', 'comp.tsx'], (0, 0, 3)),
        (['readme.md', 'photo.png'], (0, 0, 0)),
    ])
    def test_classification(self, files, expected_counts):
        html, css, js = _classify_files(files)
        assert (len(html), len(css), len(js)) == expected_counts


@pytest.mark.blackbox
class TestCollectFiles:
    def test_single_file(self, tmp_path):
        f = tmp_path / "test.js"
        f.write_text("const x = 1;")
        assert len(_collect_files(str(f))) == 1

    def test_nonexistent_returns_empty(self):
        assert _collect_files("/nonexistent/path") == []


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

    def test_analyze_summary_format(self, tmp_path):
        css_file = tmp_path / "test.css"
        css_file.write_text("body { display: flex; }")
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', str(css_file), '--format', 'summary'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert 'Grade' in result.output

    def test_unsupported_file_type(self, tmp_path):
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("hello")
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', str(txt_file)])
        assert result.exit_code == 2


# --- Misc commands ---


@pytest.mark.blackbox
class TestMiscCommands:
    def test_history_runs(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['history'])
        assert result.exit_code == 0

    def test_stats_runs(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['stats'])
        assert result.exit_code == 0
        assert 'Statistics' in result.output or 'Total' in result.output

    def test_config_show(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['config'])
        assert result.exit_code == 0
        assert 'browsers' in result.output

    def test_config_init(self, tmp_path):
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ['config', '--init'])
            assert result.exit_code == 0
            assert os.path.isfile('crossguard.config.json')

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

    def test_stdin_empty_input(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'test.js'],
            input='',
        )
        assert result.exit_code == 2
        assert 'empty' in result.output.lower()

    def test_stdin_no_extension(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'test'],
            input='const x = 1;',
        )
        assert result.exit_code == 2
        assert 'Cannot detect file type' in result.output

    def test_stdin_with_js(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'test.js', '--format', 'json'],
            input='const x = Promise.resolve();',
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
