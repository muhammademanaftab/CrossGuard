"""Tests for CustomRulesLoader singleton pattern behavior."""

import pytest
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    get_custom_rules_loader,
)


class TestSingleton:

    def test_singleton_returns_same_instance(self, tmp_rules_file):
        """Two calls to CustomRulesLoader() return same object."""
        loader1 = CustomRulesLoader()
        loader2 = CustomRulesLoader()
        assert loader1 is loader2

    def test_get_custom_rules_loader_returns_singleton(self, tmp_rules_file):
        """Module function returns same instance."""
        loader1 = get_custom_rules_loader()
        loader2 = get_custom_rules_loader()
        assert loader1 is loader2

    def test_singleton_preserves_loaded_data(self, tmp_rules_file):
        """Data persists across multiple accesses."""
        loader1 = CustomRulesLoader()
        css_rules = loader1.get_custom_css_rules()
        loader2 = CustomRulesLoader()
        assert loader2.get_custom_css_rules() == css_rules

    def test_singleton_after_reset_and_reload(self, tmp_rules_file):
        """After resetting _instance, new instance loads fresh."""
        loader1 = CustomRulesLoader()
        old_id = id(loader1)

        CustomRulesLoader._instance = None
        CustomRulesLoader._loaded = False

        loader2 = CustomRulesLoader()
        assert id(loader2) != old_id
        # Data should still be available from fresh load
        assert isinstance(loader2.get_custom_css_rules(), dict)

    def test_concurrent_access_same_instance(self, tmp_rules_file):
        """Multiple references point to same object."""
        refs = [CustomRulesLoader() for _ in range(5)]
        for ref in refs[1:]:
            assert ref is refs[0]

    def test_loaded_flag_set_after_init(self, tmp_rules_file):
        """_loaded is True after first init."""
        assert CustomRulesLoader._loaded is False
        CustomRulesLoader()
        assert CustomRulesLoader._loaded is True
