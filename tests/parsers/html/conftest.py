"""HTML parser test fixtures."""

import pytest
from src.parsers.html_parser import HTMLParser


@pytest.fixture
def html_parser():
    """Fresh HTMLParser instance for each test."""
    return HTMLParser()


@pytest.fixture
def parse_features(html_parser):
    """Parse HTML and return detected feature IDs as a set."""
    def _parse(html: str) -> set:
        return html_parser.parse_string(html)
    return _parse


@pytest.fixture
def get_detailed_report(html_parser):
    """Parse HTML and return detailed report."""
    def _report(html: str) -> dict:
        html_parser.parse_string(html)
        return html_parser.get_detailed_report()
    return _report


@pytest.fixture
def minimal_html():
    """Minimal valid HTML document."""
    return "<!DOCTYPE html><html><head></head><body></body></html>"
