"""White-box tests for custom rules loader internals.

Tests singleton pattern, save/reload cycle, and edge-case resilience.
"""

import pytest
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    get_custom_rules_loader,
    save_custom_rules,
)


@pytest.mark.whitebox
class TestSingleton:

    def test_returns_same_instance(self, tmp_rules_file):
        loader1 = CustomRulesLoader()
        loader2 = CustomRulesLoader()
        module_loader = get_custom_rules_loader()
        assert loader1 is loader2 is module_loader


@pytest.mark.whitebox
class TestSaveAndRoundtrip:

    def test_save_roundtrip(self, mock_custom_rules_path):
        rules = {
            "css": {
                "roundtrip-feature": {
                    "patterns": [r"roundtrip\s*:"],
                    "description": "Roundtrip",
                }
            },
            "javascript": {},
            "html": {},
        }
        save_custom_rules(rules)

        loader = get_custom_rules_loader()
        css = loader.get_custom_css_rules()
        assert "roundtrip-feature" in css
