"""Integration tests for CLI commands via CliRunner.

Tests the complete analyze pipeline including format outputs,
quality gates, flags, and init-ci/init-hooks.
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


@pytest.mark.integration
class TestOutputFormats:
    def test_sarif_format_produces_valid_json(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'sarif'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        data = json.loads(result.output)
        assert data['version'] == '2.1.0'
        assert 'runs' in data

    def test_junit_format_produces_valid_xml(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'junit'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        root = ET.fromstring(result.output)
        assert root.tag == 'testsuites'



# --- Quality gates integration ---


@pytest.mark.integration
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


# --- Flags ---


@pytest.mark.integration
class TestFlags:
    def test_timing_shows_elapsed(self, runner, js_file):
        result = runner.invoke(cli, [
            '--timing', 'analyze', str(js_file), '--format', 'summary'
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert 'Elapsed' in result.output



# --- init-ci / init-hooks integration ---


@pytest.mark.integration
class TestInitCommands:
    @pytest.mark.parametrize("provider, expected_content", [
        ('github', 'sarif'),
    ])
    def test_init_ci(self, runner, provider, expected_content):
        result = runner.invoke(cli, ['init-ci', '-p', provider])
        assert result.exit_code == 0
        assert expected_content in result.output

