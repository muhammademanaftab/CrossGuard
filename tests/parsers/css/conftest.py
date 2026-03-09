"""CSS parser test fixtures."""

import pytest
from src.parsers.css_parser import CSSParser


@pytest.fixture
def css_parser():
    """Fresh CSSParser instance for each test."""
    return CSSParser()


@pytest.fixture
def parse_features(css_parser):
    """Parse CSS and return detected feature IDs as a set."""
    def _parse(css: str) -> set:
        return css_parser.parse_string(css)
    return _parse


@pytest.fixture
def get_detailed_report(css_parser):
    """Parse CSS and return detailed report."""
    def _report(css: str) -> dict:
        css_parser.parse_string(css)
        return css_parser.get_detailed_report()
    return _report


@pytest.fixture
def minimal_css():
    """Minimal valid CSS content."""
    return "body { margin: 0; }"
