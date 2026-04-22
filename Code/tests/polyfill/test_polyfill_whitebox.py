"""Whitebox tests for polyfill internals -- singleton, reload."""

import pytest

from src.polyfill.polyfill_loader import get_polyfill_loader


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def loader():
    return get_polyfill_loader()


# ---------------------------------------------------------------------------
# Singleton pattern
# ---------------------------------------------------------------------------

class TestSingleton:
    @pytest.mark.whitebox
    def test_factory_returns_same_instance(self):
        assert get_polyfill_loader() is get_polyfill_loader()


# ---------------------------------------------------------------------------
# Reload
# ---------------------------------------------------------------------------

class TestReload:
    @pytest.mark.whitebox
    def test_reload_preserves_data(self, loader):
        loader.reload()
        assert loader.get_polyfill('fetch') is not None
