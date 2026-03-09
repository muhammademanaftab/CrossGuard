"""JavaScript parser test fixtures."""

import pytest
from src.parsers.js_parser import JavaScriptParser


@pytest.fixture
def js_parser():
    """Fresh JavaScriptParser instance for each test."""
    return JavaScriptParser()


@pytest.fixture
def parse_features(js_parser):
    """Parse JS and return detected feature IDs as a set."""
    def _parse(js: str) -> set:
        return js_parser.parse_string(js)
    return _parse


@pytest.fixture
def get_detailed_report(js_parser):
    """Parse JS and return detailed report."""
    def _report(js: str) -> dict:
        js_parser.parse_string(js)
        return js_parser.get_detailed_report()
    return _report


@pytest.fixture
def get_feature_details(js_parser):
    """Get feature details after parsing."""
    def _details(js: str) -> list:
        js_parser.parse_string(js)
        return js_parser.feature_details
    return _details


@pytest.fixture
def minimal_js():
    """Minimal valid JS content."""
    return "var x = 1;"
