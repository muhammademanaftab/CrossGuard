"""HTML parser test fixtures."""

import pytest
from src.parsers.html_parser import HTMLParser


@pytest.fixture
def html_parser():
    """Fresh HTMLParser instance for each test."""
    return HTMLParser()


@pytest.fixture
def parse_html(html_parser):
    """Helper fixture to parse HTML and return features set."""
    def _parse(html: str) -> set:
        return html_parser.parse_string(html)
    return _parse


@pytest.fixture
def parse_and_check(html_parser):
    """Helper fixture to parse HTML and check for specific feature."""
    def _check(html: str, expected_feature: str) -> bool:
        features = html_parser.parse_string(html)
        return expected_feature in features
    return _check


@pytest.fixture
def get_detailed_report(html_parser):
    """Helper fixture to parse HTML and return detailed report."""
    def _report(html: str) -> dict:
        html_parser.parse_string(html)
        return html_parser.get_detailed_report()
    return _report


@pytest.fixture
def minimal_html():
    """Minimal valid HTML document."""
    return "<!DOCTYPE html><html><head></head><body></body></html>"
