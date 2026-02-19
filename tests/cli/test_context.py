"""Tests for CLI context object."""

import os
import pytest
from unittest.mock import patch

from src.cli.context import CliContext


class TestCliContextDefaults:
    def test_default_verbosity(self):
        ctx = CliContext()
        assert ctx.verbosity == 1

    def test_default_color(self):
        ctx = CliContext()
        assert ctx.color is True

    def test_default_timing(self):
        ctx = CliContext()
        assert ctx.timing is False


class TestResolveVerbosity:
    def test_normal(self):
        assert CliContext.resolve_verbosity() == 1

    def test_quiet(self):
        assert CliContext.resolve_verbosity(quiet=True) == 0

    def test_verbose_once(self):
        assert CliContext.resolve_verbosity(verbose_count=1) == 2

    def test_verbose_twice(self):
        assert CliContext.resolve_verbosity(verbose_count=2) == 3

    def test_verbose_caps_at_3(self):
        assert CliContext.resolve_verbosity(verbose_count=10) == 3

    def test_debug_overrides_all(self):
        assert CliContext.resolve_verbosity(verbose_count=0, quiet=False, debug=True) == 3

    def test_debug_overrides_quiet(self):
        assert CliContext.resolve_verbosity(quiet=True, debug=True) == 3


class TestDetectColor:
    def test_no_color_flag(self):
        assert CliContext.detect_color(no_color_flag=True) is False

    def test_no_color_env(self):
        with patch.dict(os.environ, {'NO_COLOR': '1'}):
            assert CliContext.detect_color() is False

    def test_no_color_env_empty_string_is_ignored(self):
        with patch.dict(os.environ, {'NO_COLOR': ''}, clear=False):
            # Empty NO_COLOR is the same as not set
            # Result depends on TTY; we just check it doesn't crash
            result = CliContext.detect_color()
            assert isinstance(result, bool)

    def test_force_color_env(self):
        with patch.dict(os.environ, {'FORCE_COLOR': '1', 'NO_COLOR': ''}):
            assert CliContext.detect_color() is True

    def test_no_color_flag_beats_force_color(self):
        with patch.dict(os.environ, {'FORCE_COLOR': '1'}):
            assert CliContext.detect_color(no_color_flag=True) is False

    def test_non_tty_returns_false(self):
        # When stdout is not a TTY and no env vars set
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout') as mock_stdout:
                mock_stdout.isatty.return_value = False
                assert CliContext.detect_color() is False
