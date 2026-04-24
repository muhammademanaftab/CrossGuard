"""Integration tests for CLI commands via CliRunner.

Tests the complete analyze pipeline including format outputs and
quality gates.
"""

import json
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


# --- Format integration ---


@pytest.mark.integration
class TestOutputFormats:
    def test_sarif_format_produces_valid_json(self, runner, js_file):
        result = runner.invoke(cli, ['analyze', str(js_file), '--format', 'sarif'])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        data = json.loads(result.output)
        assert data['version'] == '2.1.0'
        assert 'runs' in data


# --- Quality gates integration ---


@pytest.mark.integration
class TestQualityGates:
    def test_fail_on_score_fails_when_below(self, runner, js_file):
        result = runner.invoke(cli, [
            'analyze', str(js_file), '--format', 'summary', '--fail-on-score', '100.1'
        ])
        assert result.exit_code == 1


# --- Config file's "output" key drives --format when neither flag nor env is set ---


@pytest.mark.integration
class TestConfigOutputFormat:
    def _write_config(self, tmp_path, output_value):
        cfg = tmp_path / "crossguard.config.json"
        cfg.write_text(json.dumps({"output": output_value}))
        return cfg

    def test_config_output_json_drives_format(self, runner, tmp_path, js_file):
        cfg = self._write_config(tmp_path, "json")
        result = runner.invoke(cli, ['-q', 'analyze', str(js_file), '-c', str(cfg)])
        assert result.exit_code in (0, 1), f"unexpected failure: {result.output}"
        data = json.loads(result.output)
        assert data['success'] is True

    def test_explicit_format_flag_overrides_config(self, runner, tmp_path, js_file):
        cfg = self._write_config(tmp_path, "json")
        result = runner.invoke(cli, [
            '-q', 'analyze', str(js_file), '-c', str(cfg), '--format', 'summary'
        ])
        assert result.exit_code in (0, 1)
        # summary output starts with "Grade:" not a JSON object
        assert result.output.lstrip().startswith('Grade:')

