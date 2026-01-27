"""Shared fixtures for all tests."""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def create_temp_file(temp_dir):
    """Factory fixture to create temporary files."""
    def _create(filename: str, content: str) -> Path:
        filepath = temp_dir / filename
        filepath.write_text(content, encoding='utf-8')
        return filepath
    return _create


@pytest.fixture
def create_html_file(create_temp_file):
    """Factory fixture to create temporary HTML files."""
    def _create(content: str, filename: str = "test.html") -> Path:
        return create_temp_file(filename, content)
    return _create
