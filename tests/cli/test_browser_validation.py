"""Tests for browser validation in CLI."""

import pytest
import click

from src.cli.main import _parse_browsers


class TestParseBrowsersValidation:
    @pytest.mark.parametrize("input_str, expected", [
        ('chrome:120', {'chrome': '120'}),
        ('chrome:120,firefox:121', {'chrome': '120', 'firefox': '121'}),
        ('chrome : 120 , safari : 18.4', {'chrome': '120', 'safari': '18.4'}),
        ('safari:18.4', {'safari': '18.4'}),
        ('Chrome:120', {'chrome': '120'}),   # case insensitive
        ('chrome:120,,firefox:121', {'chrome': '120', 'firefox': '121'}),  # empty pair ignored
    ])
    def test_valid_inputs(self, input_str, expected):
        assert _parse_browsers(input_str) == expected

    @pytest.mark.parametrize("input_str", [None, ''])
    def test_none_or_empty_returns_none(self, input_str):
        assert _parse_browsers(input_str) is None

    @pytest.mark.parametrize("input_str, error_match", [
        ('netscape:5', "Unknown browser 'netscape'"),
        ('chrom:120', "Did you mean 'chrome'"),
        ('chrome120', "Invalid format"),
        ('chrome:latest', "Version must be numeric"),
    ])
    def test_invalid_inputs_raise(self, input_str, error_match):
        with pytest.raises(click.BadParameter, match=error_match):
            _parse_browsers(input_str)

    def test_all_known_browsers_accepted(self):
        from src.utils.config import LATEST_VERSIONS
        for browser in LATEST_VERSIONS:
            result = _parse_browsers(f'{browser}:1')
            assert browser in result
