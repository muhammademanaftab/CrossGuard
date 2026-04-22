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
