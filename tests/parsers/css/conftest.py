"""CSS parser test fixtures."""

import pytest
from src.parsers.css_parser import CSSParser


@pytest.fixture
def css_parser():
    """Fresh CSSParser instance for each test."""
    return CSSParser()


@pytest.fixture
def parse_css(css_parser):
    """Helper fixture to parse CSS and return features set."""
    def _parse(css: str) -> set:
        return css_parser.parse_string(css)
    return _parse


@pytest.fixture
def parse_and_check(css_parser):
    """Helper fixture to parse CSS and check for specific feature."""
    def _check(css: str, expected_feature: str) -> bool:
        features = css_parser.parse_string(css)
        return expected_feature in features
    return _check


@pytest.fixture
def parse_and_check_multiple(css_parser):
    """Helper fixture to parse CSS and check for multiple features."""
    def _check(css: str, expected_features: list) -> bool:
        features = css_parser.parse_string(css)
        return all(f in features for f in expected_features)
    return _check


@pytest.fixture
def get_detailed_report(css_parser):
    """Helper fixture to parse CSS and return detailed report."""
    def _report(css: str) -> dict:
        css_parser.parse_string(css)
        return css_parser.get_detailed_report()
    return _report


@pytest.fixture
def minimal_css():
    """Minimal valid CSS content."""
    return "body { margin: 0; }"
