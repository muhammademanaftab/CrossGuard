"""White-box tests for custom rules loader internals.

Tests singleton pattern, save/reload cycle, and edge-case resilience.
"""

import json
import pytest
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    get_custom_rules_loader,
    save_custom_rules,
    reload_custom_rules,
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

    def test_save_writes_valid_json(self, mock_custom_rules_path):
        rules = {
            "css": {"css-rule": {"patterns": ["p1"], "description": "CSS"}},
            "javascript": {"js-rule": {"patterns": ["p2"], "description": "JS"}},
            "html": {
                "elements": {"my-el": "feat-id"},
                "attributes": {},
                "input_types": {},
                "attribute_values": {},
            },
        }
        assert save_custom_rules(rules) is True

        saved = json.loads(mock_custom_rules_path.read_text(encoding="utf-8"))
        assert "css-rule" in saved["css"]
        assert "js-rule" in saved["javascript"]

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


@pytest.mark.whitebox
class TestReload:

    def test_reload_picks_up_new_rules(self, tmp_rules_file, sample_rules_json):
        loader = CustomRulesLoader()
        assert "test-css-feature" in loader.get_custom_css_rules()

        sample_rules_json["css"]["new-feature"] = {
            "patterns": ["new-pattern"],
            "description": "New",
        }
        tmp_rules_file.write_text(json.dumps(sample_rules_json), encoding="utf-8")

        loader.reload()
        assert "new-feature" in loader.get_custom_css_rules()

    def test_reload_clears_old_data(self, tmp_rules_file):
        loader = CustomRulesLoader()
        assert "test-css-feature" in loader.get_custom_css_rules()

        new_data = {
            "css": {"replacement": {"patterns": ["r"], "description": "R"}},
            "javascript": {},
            "html": {},
        }
        tmp_rules_file.write_text(json.dumps(new_data), encoding="utf-8")
        loader.reload()

        css = loader.get_custom_css_rules()
        assert "test-css-feature" not in css
        assert "replacement" in css
