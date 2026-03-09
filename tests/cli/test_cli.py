"""Tests for Cross Guard CLI commands and helper functions."""

import json
import os
import pytest
from click.testing import CliRunner

from src.cli.main import cli, _parse_browsers, _classify_files, _collect_files


# --- Helper parsing tests ---


class TestParseBrowsers:
    @pytest.mark.parametrize("input_str, expected", [
        ('chrome:120,firefox:121', {'chrome': '120', 'firefox': '121'}),
        ('chrome : 120 , safari : 17', {'chrome': '120', 'safari': '17'}),
    ])
    def test_valid_strings(self, input_str, expected):
        assert _parse_browsers(input_str) == expected

    @pytest.mark.parametrize("input_str", [None, ''])
    def test_none_or_empty_returns_none(self, input_str):
        assert _parse_browsers(input_str) is None


class TestClassifyFiles:
    @pytest.mark.parametrize("files, expected_counts", [
        (['index.html', 'page.htm'], (2, 0, 0)),
        (['style.css'], (0, 1, 0)),
        (['app.js', 'mod.mjs', 'comp.tsx'], (0, 0, 3)),
        (['a.html', 'b.css', 'c.js'], (1, 1, 1)),
        (['readme.md', 'photo.png'], (0, 0, 0)),
    ])
    def test_classification(self, files, expected_counts):
        html, css, js = _classify_files(files)
        assert (len(html), len(css), len(js)) == expected_counts


class TestCollectFiles:
    def test_single_file(self, tmp_path):
        f = tmp_path / "test.js"
        f.write_text("const x = 1;")
        assert len(_collect_files(str(f))) == 1

    def test_directory_collects_supported_only(self, tmp_path):
        (tmp_path / "a.html").write_text("<div></div>")
        (tmp_path / "b.css").write_text("body {}")
        (tmp_path / "c.js").write_text("var x;")
        (tmp_path / "d.txt").write_text("ignored")
        assert len(_collect_files(str(tmp_path))) == 3

    def test_ignores_node_modules(self, tmp_path):
        nm = tmp_path / "node_modules"
        nm.mkdir()
        (nm / "lib.js").write_text("module.exports = {};")
        (tmp_path / "app.js").write_text("import x;")
        assert len(_collect_files(str(tmp_path))) == 1

    def test_nonexistent_returns_empty(self):
        assert _collect_files("/nonexistent/path") == []


# --- CLI command tests ---


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
