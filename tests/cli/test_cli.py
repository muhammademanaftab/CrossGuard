"""Tests for Cross Guard CLI."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.cli.main import cli, _parse_browsers, _classify_files, _collect_files


# ─── Helper parsing tests ─────────────────────────────────────────────

class TestParseBrowsers:
    def test_valid_string(self):
        result = _parse_browsers('chrome:120,firefox:121')
        assert result == {'chrome': '120', 'firefox': '121'}

    def test_with_spaces(self):
        result = _parse_browsers('chrome : 120 , safari : 17')
        assert result == {'chrome': '120', 'safari': '17'}

    def test_none_returns_none(self):
        assert _parse_browsers(None) is None

    def test_empty_returns_none(self):
        assert _parse_browsers('') is None


class TestClassifyFiles:
    def test_html_files(self):
        html, css, js = _classify_files(['index.html', 'page.htm'])
        assert len(html) == 2
        assert len(css) == 0

    def test_css_files(self):
        html, css, js = _classify_files(['style.css'])
        assert len(css) == 1

    def test_js_files(self):
        html, css, js = _classify_files(['app.js', 'mod.mjs', 'comp.tsx'])
        assert len(js) == 3

    def test_mixed(self):
        html, css, js = _classify_files(['a.html', 'b.css', 'c.js'])
        assert len(html) == 1
        assert len(css) == 1
        assert len(js) == 1

    def test_unknown_ignored(self):
        html, css, js = _classify_files(['readme.md', 'photo.png'])
        assert len(html) == 0
        assert len(css) == 0
        assert len(js) == 0


class TestCollectFiles:
    def test_single_file(self, tmp_path):
        f = tmp_path / "test.js"
        f.write_text("const x = 1;")
        files = _collect_files(str(f))
        assert len(files) == 1

    def test_directory(self, tmp_path):
        (tmp_path / "a.html").write_text("<div></div>")
        (tmp_path / "b.css").write_text("body {}")
        (tmp_path / "c.js").write_text("var x;")
        (tmp_path / "d.txt").write_text("ignored")
        files = _collect_files(str(tmp_path))
        assert len(files) == 3

    def test_ignores_node_modules(self, tmp_path):
        nm = tmp_path / "node_modules"
        nm.mkdir()
        (nm / "lib.js").write_text("module.exports = {};")
        (tmp_path / "app.js").write_text("import x;")
        files = _collect_files(str(tmp_path))
        assert len(files) == 1

    def test_nonexistent_returns_empty(self):
        files = _collect_files("/nonexistent/path")
        assert files == []


# ─── CLI command tests ────────────────────────────────────────────────

class TestAnalyzeCommand:
    def test_nonexistent_target(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', '/nonexistent/file.js'])
        assert result.exit_code == 2
        assert 'not found' in result.output.lower() or 'not found' in (result.stderr_bytes or b'').decode().lower()

    def test_analyze_single_file(self, tmp_path):
        js_file = tmp_path / "test.js"
        js_file.write_text("const x = 1; let y = 2;")
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'json'])
        # Should succeed (exit 0 or 1 depending on compatibility)
        assert result.exit_code in (0, 1)

    def test_analyze_with_summary_format(self, tmp_path):
        css_file = tmp_path / "test.css"
        css_file.write_text("body { display: flex; }")
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', str(css_file), '--format', 'summary'])
        assert result.exit_code in (0, 1)
        assert 'Grade' in result.output or 'Error' in result.output

    def test_unsupported_file_type(self, tmp_path):
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("hello")
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', str(txt_file)])
        assert result.exit_code == 2


class TestHistoryCommand:
    def test_history_runs(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['history'])
        assert result.exit_code == 0


class TestStatsCommand:
    def test_stats_runs(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['stats'])
        assert result.exit_code == 0
        assert 'Statistics' in result.output or 'Total' in result.output


class TestConfigCommand:
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


class TestVersionFlag:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output
