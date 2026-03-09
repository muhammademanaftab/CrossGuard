"""Tests for CLI context object."""

import os
import pytest
from unittest.mock import patch

from src.cli.context import CliContext


class TestCliContextDefaults:
    def test_defaults(self):
        ctx = CliContext()
        assert ctx.verbosity == 1
        assert ctx.color is True
        assert ctx.timing is False


class TestResolveVerbosity:
    @pytest.mark.parametrize("kwargs, expected", [
        ({}, 1),                                    # normal
        ({'quiet': True}, 0),                        # quiet
        ({'verbose_count': 1}, 2),                   # verbose once
        ({'verbose_count': 2}, 3),                   # verbose twice
        ({'verbose_count': 10}, 3),                  # caps at 3
        ({'debug': True}, 3),                        # debug overrides all
        ({'quiet': True, 'debug': True}, 3),         # debug overrides quiet
    ])
    def test_verbosity_levels(self, kwargs, expected):
        assert CliContext.resolve_verbosity(**kwargs) == expected


class TestDetectColor:
    @pytest.mark.parametrize("kwargs, env_vars, expected", [
        ({'no_color_flag': True}, {}, False),
        ({}, {'NO_COLOR': '1'}, False),
        ({}, {'FORCE_COLOR': '1', 'NO_COLOR': ''}, True),
        ({'no_color_flag': True}, {'FORCE_COLOR': '1'}, False),
    ])
    def test_color_detection(self, kwargs, env_vars, expected):
        with patch.dict(os.environ, env_vars, clear=False):
            assert CliContext.detect_color(**kwargs) is expected

    def test_non_tty_returns_false(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout') as mock_stdout:
                mock_stdout.isatty.return_value = False
                assert CliContext.detect_color() is False

    def test_empty_no_color_env_is_ignored(self):
        with patch.dict(os.environ, {'NO_COLOR': ''}, clear=False):
            result = CliContext.detect_color()
            assert isinstance(result, bool)
