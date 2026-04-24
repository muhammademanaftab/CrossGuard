"""White-box tests for analyzer internals -- database loading.

Tests internal state and loading correctness that is not exposed through the
public analysis API.
"""

import pytest

from src.analyzer.database import CanIUseDatabase


# ============================================================================
# Database Loading
# ============================================================================

class TestDatabaseLoading:
    """Tests for load(), _load_feature_files(), _build_index()."""

    @pytest.mark.whitebox
    def test_load_returns_true_and_has_features(self, caniuse_db):
        assert caniuse_db.loaded is True
        assert len(caniuse_db.features) > 500
        assert len(caniuse_db.feature_index) > 0
