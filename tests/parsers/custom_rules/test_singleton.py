"""Tests for CustomRulesLoader singleton pattern behavior."""

import pytest
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    get_custom_rules_loader,
)


class TestSingleton:

    def test_singleton_returns_same_instance(self, tmp_rules_file):
        """Multiple calls return same object, including module function."""
        loader1 = CustomRulesLoader()
        loader2 = CustomRulesLoader()
        assert loader1 is loader2

        module_loader = get_custom_rules_loader()
        assert module_loader is loader1

        # Multiple references all point to same object
        refs = [CustomRulesLoader() for _ in range(5)]
        assert all(ref is loader1 for ref in refs)

    def test_singleton_after_reset_and_reload(self, tmp_rules_file):
        """After resetting _instance, new instance loads fresh with _loaded set."""
        loader1 = CustomRulesLoader()
        assert CustomRulesLoader._loaded is True
        old_id = id(loader1)

        CustomRulesLoader._instance = None
        CustomRulesLoader._loaded = False

        loader2 = CustomRulesLoader()
        assert id(loader2) != old_id
        assert CustomRulesLoader._loaded is True
        assert isinstance(loader2.get_custom_css_rules(), dict)
