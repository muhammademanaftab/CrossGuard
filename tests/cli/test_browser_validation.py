"""Tests for browser validation in CLI."""

import pytest
import click

from src.cli.main import _parse_browsers


class TestParseBrowsersValidation:
    def test_valid_single(self):
        result = _parse_browsers('chrome:120')
        assert result == {'chrome': '120'}

    def test_valid_multiple(self):
        result = _parse_browsers('chrome:120,firefox:121')
        assert result == {'chrome': '120', 'firefox': '121'}

    def test_valid_with_spaces(self):
        result = _parse_browsers('chrome : 120 , safari : 18.4')
        assert result == {'chrome': '120', 'safari': '18.4'}

    def test_valid_decimal_version(self):
        result = _parse_browsers('safari:18.4')
        assert result == {'safari': '18.4'}

    def test_none_returns_none(self):
        assert _parse_browsers(None) is None

    def test_empty_returns_none(self):
        assert _parse_browsers('') is None

    def test_unknown_browser_raises(self):
        with pytest.raises(click.BadParameter, match="Unknown browser 'netscape'"):
            _parse_browsers('netscape:5')

    def test_unknown_browser_with_suggestion(self):
        with pytest.raises(click.BadParameter, match="Did you mean 'chrome'"):
            _parse_browsers('chrom:120')

    def test_missing_colon_raises(self):
        with pytest.raises(click.BadParameter, match="Invalid format"):
            _parse_browsers('chrome120')

    def test_non_numeric_version_raises(self):
        with pytest.raises(click.BadParameter, match="Version must be numeric"):
            _parse_browsers('chrome:latest')

    def test_all_known_browsers_accepted(self):
        from src.utils.config import LATEST_VERSIONS
        for browser in LATEST_VERSIONS:
            result = _parse_browsers(f'{browser}:1')
            assert browser in result

    def test_case_insensitive(self):
        result = _parse_browsers('Chrome:120')
        assert result == {'chrome': '120'}

    def test_empty_pair_ignored(self):
        result = _parse_browsers('chrome:120,,firefox:121')
        assert result == {'chrome': '120', 'firefox': '121'}
