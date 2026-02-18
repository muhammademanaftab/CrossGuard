"""Shared fixtures for analyzer tests.

Module-scoped database loading avoids re-reading 570+ JSON feature files per test.
"""

import pytest

from src.analyzer.database import CanIUseDatabase
from src.analyzer.compatibility import CompatibilityAnalyzer
from src.analyzer.scorer import CompatibilityScorer
import src.analyzer.database as db_module


# ─── Database Fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def caniuse_db():
    """Loaded CanIUseDatabase instance shared across all tests in a module.

    Loading 570+ JSON files is slow; reuse the same instance everywhere.
    """
    db = CanIUseDatabase()
    success = db.load()
    assert success, "Failed to load Can I Use database"
    return db


@pytest.fixture
def fresh_db():
    """Unloaded CanIUseDatabase instance for load-testing."""
    return CanIUseDatabase()


@pytest.fixture
def reset_singleton():
    """Save and restore the module-level singleton around the test.

    Ensures tests that manipulate ``_database_instance`` don't leak state
    to later tests that depend on the singleton.
    """
    original = db_module._database_instance
    yield
    db_module._database_instance = original


# ─── Analyzer Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def analyzer():
    """CompatibilityAnalyzer wired to the shared DB (via singleton)."""
    return CompatibilityAnalyzer()


# ─── Scorer Fixtures ────────────────────────────────────────────────────

@pytest.fixture
def scorer():
    """CompatibilityScorer with default weights."""
    return CompatibilityScorer()


@pytest.fixture
def scorer_custom():
    """Factory fixture: create a scorer with custom browser weights."""
    def _make(weights):
        return CompatibilityScorer(browser_weights=weights)
    return _make


# ─── Browser Fixtures ───────────────────────────────────────────────────

@pytest.fixture
def modern_browsers():
    """Modern browser targets (all support most features)."""
    return {'chrome': '120', 'firefox': '121', 'safari': '17', 'edge': '120'}


@pytest.fixture
def legacy_browsers():
    """Modern + IE 11 for testing fallback/severity."""
    return {
        'chrome': '120',
        'firefox': '121',
        'safari': '17',
        'edge': '120',
        'ie': '11',
    }


# ─── Feature Fixtures ───────────────────────────────────────────────────

@pytest.fixture
def well_supported_features():
    """Features with near-universal modern browser support."""
    return {'flexbox', 'css-grid', 'promises', 'arrow-functions'}


@pytest.fixture
def mixed_support_features():
    """Mix of well-supported and poorly-supported features."""
    return {'flexbox', 'css-grid', 'dialog', 'css-container-queries'}
