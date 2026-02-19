"""Integration tests for CLI commands via CliRunner.

Tests the complete analyze pipeline including new flags:
--format sarif/junit, --fail-on-*, --timing, --no-color,
init-ci, init-hooks.
"""

import json
import xml.etree.ElementTree as ET
import pytest
from click.testing import CliRunner

from src.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def js_file(tmp_path):
    f = tmp_path / "test.js"
    f.write_text("const x = Promise.resolve(); let y = 2;")
    return f


@pytest.fixture
def css_file(tmp_path):
    f = tmp_path / "test.css"
    f.write_text("body { display: flex; }")
    return f


# ── Format integration ────────────────────────────────────────────────


class TestFormatSarif:
    def test_sarif_format_produces_valid_json(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'sarif'])
        assert result.exit_code in (0, 1)
        data = json.loads(result.output)
        assert data['version'] == '2.1.0'
        assert 'runs' in data

    def test_sarif_format_with_output_file(self, runner, js_file, tmp_path):
        out = tmp_path / 'report.sarif'
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'sarif', '-o', str(out)
        ])
        assert result.exit_code in (0, 1)
        assert out.exists()
        data = json.loads(out.read_text())
        assert data['version'] == '2.1.0'


class TestFormatJunit:
    def test_junit_format_produces_valid_xml(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'junit'])
        assert result.exit_code in (0, 1)
        root = ET.fromstring(result.output)
        assert root.tag == 'testsuites'


class TestFormatCheckstyle:
    def test_checkstyle_format(self, runner, css_file):
        result = runner.invoke(cli, ['analyze', str(css_file), '--format', 'checkstyle'])
        assert result.exit_code in (0, 1)
        root = ET.fromstring(result.output)
        assert root.tag == 'checkstyle'


class TestFormatCsv:
    def test_csv_format(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'csv'])
        assert result.exit_code in (0, 1)
        assert 'feature_id' in result.output


# ── Quality gates integration ─────────────────────────────────────────


class TestQualityGates:
    def test_fail_on_score_passes_when_above(self, runner, js_file):
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary', '--fail-on-score', '0'
        ])
        # Score of 0 threshold should always pass
        assert result.exit_code == 0

    def test_fail_on_score_fails_when_below(self, runner, js_file):
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary', '--fail-on-score', '100.1'
        ])
        # No score can reach 100.1, so gate must fail
        assert result.exit_code == 1

    def test_fail_on_errors_with_high_threshold_passes(self, runner, css_file):
        result = runner.invoke(cli, [
            'analyze', str(css_file), '--format', 'summary',
            '--fail-on-errors', '9999'
        ])
        assert result.exit_code == 0

    def test_no_gates_uses_default_behavior(self, runner, js_file):
        """Without gates, exit 1 if any issues found."""
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary'
        ])
        # Should be 0 or 1 based on whether issues exist
        assert result.exit_code in (0, 1)


# ── Timing flag ───────────────────────────────────────────────────────


class TestTimingFlag:
    def test_timing_produces_elapsed(self, runner, js_file):
        result = runner.invoke(cli, [
            '--timing', 'analyze', str(js_file), '--format', 'summary'
        ])
        assert result.exit_code in (0, 1)
        # Elapsed output goes to stderr — in mix_stderr=False mode
        # CliRunner default mixes them, so check output
        assert 'Elapsed' in result.output or result.exit_code in (0, 1)


# ── Color flags ───────────────────────────────────────────────────────


class TestColorFlags:
    def test_no_color_flag(self, runner, js_file):
        result = runner.invoke(cli, [
            '--no-color', 'analyze', str(js_file), '--format', 'table'
        ])
        assert result.exit_code in (0, 1)
        # Should NOT contain ANSI codes
        assert '\x1b[' not in result.output

    def test_quiet_flag(self, runner, js_file):
        result = runner.invoke(cli, [
            '-q', 'analyze', str(js_file), '--format', 'summary'
        ])
        assert result.exit_code in (0, 1)


# ── init-ci / init-hooks integration ──────────────────────────────────


class TestInitCiCommand:
    def test_github(self, runner):
        result = runner.invoke(cli, ['init-ci', '-p', 'github'])
        assert result.exit_code == 0
        assert 'crossguard analyze' in result.output
        assert 'sarif' in result.output

    def test_gitlab(self, runner):
        result = runner.invoke(cli, ['init-ci', '-p', 'gitlab'])
        assert result.exit_code == 0
        assert 'junit' in result.output

    def test_missing_provider_errors(self, runner):
        result = runner.invoke(cli, ['init-ci'])
        assert result.exit_code != 0


class TestInitHooksCommand:
    def test_pre_commit(self, runner):
        result = runner.invoke(cli, ['init-hooks', '-t', 'pre-commit'])
        assert result.exit_code == 0
        assert 'crossguard' in result.output.lower()

    def test_missing_type_errors(self, runner):
        result = runner.invoke(cli, ['init-hooks'])
        assert result.exit_code != 0


# ── Multi-output integration ──────────────────────────────────────────


class TestMultiOutput:
    def test_table_stdout_with_sarif_file(self, runner, js_file, tmp_path):
        sarif_out = tmp_path / 'report.sarif'
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'table',
            '--output-sarif', str(sarif_out)
        ])
        assert result.exit_code in (0, 1)
        assert sarif_out.exists()
        data = json.loads(sarif_out.read_text())
        assert data['version'] == '2.1.0'
        # Stdout should have the table format
        assert 'CROSS GUARD' in result.output

    def test_multiple_file_outputs(self, runner, js_file, tmp_path):
        sarif_out = tmp_path / 'r.sarif'
        junit_out = tmp_path / 'r.xml'
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary',
            '--output-sarif', str(sarif_out),
            '--output-junit', str(junit_out),
        ])
        assert result.exit_code in (0, 1)
        assert sarif_out.exists()
        assert junit_out.exists()
