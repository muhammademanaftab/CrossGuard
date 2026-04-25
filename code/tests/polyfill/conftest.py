"""Shared fixtures for polyfill tests — ensures singleton state is restored."""

import pytest

from src.polyfill.polyfill_loader import get_polyfill_loader


@pytest.fixture(autouse=True)
def restore_polyfill_singleton():
    """Reload the polyfill loader after each test to undo any singleton corruption."""
    yield
    get_polyfill_loader().reload()
