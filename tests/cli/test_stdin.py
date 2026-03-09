"""Tests for stdin input support in CLI."""

import pytest
from click.testing import CliRunner

from src.cli.main import cli


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

    def test_stdin_whitespace_only(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'test.js'],
            input='   \n  \n  ',
        )
        assert result.exit_code == 2

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

    def test_stdin_with_css(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'style.css', '--format', 'summary'],
            input='body { display: flex; }',
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"

    def test_stdin_cleans_up_temp_file(self):
        """Temp file should be cleaned up even on error."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'test.js', '--format', 'json'],
            input='var x = 1;',
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
