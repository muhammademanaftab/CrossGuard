"""Shared fixtures for analyzer tests.

Module-scoped database loading avoids re-reading 570+ JSON feature files per test.
"""

import pytest

from src.analyzer.database import CanIUseDatabase
from src.analyzer.compatibility import CompatibilityAnalyzer
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
def reset_singleton():
    """Save and restore the module-level singleton around the test."""
    original = db_module._database_instance
    yield
    db_module._database_instance = original


# ─── Analyzer Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def analyzer():
    """CompatibilityAnalyzer wired to the shared DB (via singleton)."""
    return CompatibilityAnalyzer()


# ─── Browser Fixtures ───────────────────────────────────────────────────

@pytest.fixture
def modern_browsers():
    """Modern browser targets (all support most features)."""
    return {'chrome': '120', 'firefox': '121', 'safari': '17', 'edge': '120'}


# ─── Feature Fixtures ───────────────────────────────────────────────────

@pytest.fixture
def well_supported_features():
    """Features with near-universal modern browser support."""
    return {'flexbox', 'css-grid', 'promises', 'arrow-functions'}
