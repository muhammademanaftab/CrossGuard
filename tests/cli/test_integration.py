"""Integration tests for CLI commands via CliRunner.

Tests the complete analyze pipeline including format outputs,
quality gates, flags, init-ci, init-hooks, and multi-output.
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


# --- Format integration ---


class TestOutputFormats:
    def test_sarif_format_produces_valid_json(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'sarif'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        data = json.loads(result.output)
        assert data['version'] == '2.1.0'
        assert 'runs' in data

    def test_sarif_format_with_output_file(self, runner, js_file, tmp_path):
        out = tmp_path / 'report.sarif'
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'sarif', '-o', str(out)
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert out.exists()
        data = json.loads(out.read_text())
        assert data['version'] == '2.1.0'

    def test_junit_format_produces_valid_xml(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'junit'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        root = ET.fromstring(result.output)
        assert root.tag == 'testsuites'

    def test_checkstyle_format(self, runner, css_file):
        result = runner.invoke(cli, ['analyze', str(css_file), '--format', 'checkstyle'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        root = ET.fromstring(result.output)
        assert root.tag == 'checkstyle'

    def test_csv_format(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'csv'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert 'feature_id' in result.output


# --- Quality gates integration ---


class TestQualityGates:
    def test_fail_on_score_passes_when_above(self, runner, js_file):
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary', '--fail-on-score', '0'
        ])
        assert result.exit_code == 0

    def test_fail_on_score_fails_when_below(self, runner, js_file):
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary', '--fail-on-score', '100.1'
        ])
        assert result.exit_code == 1

    def test_fail_on_errors_with_high_threshold_passes(self, runner, css_file):
        result = runner.invoke(cli, [
            'analyze', str(css_file), '--format', 'summary',
            '--fail-on-errors', '9999'
        ])
        assert result.exit_code == 0

    def test_no_gates_default_behavior(self, runner, js_file):
        """Without gates, exit 0 for successful analysis."""
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary'
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"


# --- Flags ---


class TestFlags:
    def test_timing_shows_elapsed(self, runner, js_file):
        result = runner.invoke(cli, [
            '--timing', 'analyze', str(js_file), '--format', 'summary'
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert 'Elapsed' in result.output

    def test_no_color_flag_strips_ansi(self, runner, js_file):
        result = runner.invoke(cli, [
            '--no-color', 'analyze', str(js_file), '--format', 'table'
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert '\x1b[' not in result.output

    def test_quiet_flag(self, runner, js_file):
        result = runner.invoke(cli, [
            '-q', 'analyze', str(js_file), '--format', 'summary'
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"


# --- init-ci / init-hooks integration ---


class TestInitCommands:
    @pytest.mark.parametrize("provider, expected_content", [
        ('github', 'sarif'),
        ('gitlab', 'junit'),
    ])
    def test_init_ci(self, runner, provider, expected_content):
        result = runner.invoke(cli, ['init-ci', '-p', provider])
        assert result.exit_code == 0
        assert 'crossguard analyze' in result.output
        assert expected_content in result.output

    def test_init_ci_missing_provider(self, runner):
        result = runner.invoke(cli, ['init-ci'])
        assert result.exit_code != 0

    def test_init_hooks_pre_commit(self, runner):
        result = runner.invoke(cli, ['init-hooks', '-t', 'pre-commit'])
        assert result.exit_code == 0
        assert 'crossguard' in result.output.lower()

    def test_init_hooks_missing_type(self, runner):
        result = runner.invoke(cli, ['init-hooks'])
        assert result.exit_code != 0


# --- Multi-output integration ---


class TestMultiOutput:
    def test_table_stdout_with_sarif_file(self, runner, js_file, tmp_path):
        sarif_out = tmp_path / 'report.sarif'
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'table',
            '--output-sarif', str(sarif_out)
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert sarif_out.exists()
        data = json.loads(sarif_out.read_text())
        assert data['version'] == '2.1.0'
        assert 'CROSS GUARD' in result.output

    def test_multiple_file_outputs(self, runner, js_file, tmp_path):
        sarif_out = tmp_path / 'r.sarif'
        junit_out = tmp_path / 'r.xml'
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary',
            '--output-sarif', str(sarif_out),
            '--output-junit', str(junit_out),
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert sarif_out.exists()
        assert junit_out.exists()
