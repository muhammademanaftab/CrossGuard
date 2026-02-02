"""JavaScript parser test fixtures."""

import pytest
from src.parsers.js_parser import JavaScriptParser


@pytest.fixture
def js_parser():
    """Fresh JavaScriptParser instance for each test."""
    return JavaScriptParser()


@pytest.fixture
def parse_js(js_parser):
    """Helper fixture to parse JS and return features set."""
    def _parse(js: str) -> set:
        return js_parser.parse_string(js)
    return _parse


@pytest.fixture
def parse_and_check(js_parser):
    """Helper fixture to parse JS and check for specific feature."""
    def _check(js: str, expected_feature: str) -> bool:
        features = js_parser.parse_string(js)
        return expected_feature in features
    return _check


@pytest.fixture
def parse_and_check_multiple(js_parser):
    """Helper fixture to parse JS and check for multiple features."""
    def _check(js: str, expected_features: list) -> bool:
        features = js_parser.parse_string(js)
        return all(f in features for f in expected_features)
    return _check


@pytest.fixture
def parse_and_check_not(js_parser):
    """Helper fixture to parse JS and check that feature is NOT detected."""
    def _check(js: str, feature: str) -> bool:
        features = js_parser.parse_string(js)
        return feature not in features
    return _check


@pytest.fixture
def get_detailed_report(js_parser):
    """Helper fixture to parse JS and return detailed report."""
    def _report(js: str) -> dict:
        js_parser.parse_string(js)
        return js_parser.get_detailed_report()
    return _report


@pytest.fixture
def get_feature_details(js_parser):
    """Helper fixture to get feature details after parsing."""
    def _details(js: str) -> list:
        js_parser.parse_string(js)
        return js_parser.feature_details
    return _details


@pytest.fixture
def minimal_js():
    """Minimal valid JS content."""
    return "var x = 1;"
