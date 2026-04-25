"""White-box tests for custom rules loader internals.

Tests the save/reload cycle.
"""

import pytest
from src.parsers.custom_rules_loader import (
    get_custom_rules_loader,
    save_custom_rules,
)


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
