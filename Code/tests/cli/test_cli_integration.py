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
