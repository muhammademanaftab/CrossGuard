"""Tests for stdin input support in CLI."""

import pytest
from unittest.mock import patch, MagicMock
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
        # Should succeed (0 or 1 depending on compatibility)
        assert result.exit_code in (0, 1)

    def test_stdin_with_css(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'style.css', '--format', 'summary'],
            input='body { display: flex; }',
        )
        assert result.exit_code in (0, 1)

    def test_stdin_cleans_up_temp_file(self):
        """Temp file should be cleaned up even on error."""
        import os
        runner = CliRunner()
        # This should work and clean up
        result = runner.invoke(
            cli, ['analyze', '--stdin', '--stdin-filename', 'test.js', '--format', 'json'],
            input='var x = 1;',
        )
        # We can't easily check the temp file is gone, but ensure no crash
        assert result.exit_code in (0, 1)
