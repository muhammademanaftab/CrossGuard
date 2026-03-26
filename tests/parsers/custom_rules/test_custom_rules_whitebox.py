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
        """Multiple instantiations and module function all return same object."""
        loader1 = CustomRulesLoader()
        loader2 = CustomRulesLoader()
        module_loader = get_custom_rules_loader()
        assert loader1 is loader2 is module_loader

    def test_reset_creates_new_instance(self, tmp_rules_file):
        """After clearing _instance, a fresh loader is created with _loaded set."""
        loader1 = CustomRulesLoader()
        old_id = id(loader1)

        CustomRulesLoader._instance = None
        CustomRulesLoader._loaded = False

        loader2 = CustomRulesLoader()
        assert id(loader2) != old_id
        assert CustomRulesLoader._loaded is True


@pytest.mark.whitebox
class TestSaveAndRoundtrip:

    def test_save_writes_valid_json(self, mock_custom_rules_path):
        """save_custom_rules writes parseable JSON preserving all sections."""
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
        assert "my-el" in saved["html"]["elements"]

    def test_save_roundtrip(self, mock_custom_rules_path):
        """Saved rules are immediately available via the loader after auto-reload."""
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
        assert css["roundtrip-feature"]["patterns"] == [r"roundtrip\s*:"]

    def test_save_preserves_special_regex_chars(self, mock_custom_rules_path):
        """Regex patterns with special characters survive save/load."""
        rules = {
            "css": {
                "special": {
                    "patterns": [r"color\s*:\s*rgba?\(", r"background\s*:\s*#[0-9a-f]+"],
                    "description": "Special",
                }
            },
            "javascript": {},
            "html": {},
        }
        save_custom_rules(rules)
        saved = json.loads(mock_custom_rules_path.read_text(encoding="utf-8"))
        assert r"color\s*:\s*rgba?\(" in saved["css"]["special"]["patterns"]


@pytest.mark.whitebox
class TestReload:

    def test_reload_picks_up_new_rules(self, tmp_rules_file, sample_rules_json):
        """After modifying JSON on disk, reload() returns updated data."""
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
        """Old rules disappear after reloading with different data."""
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

    def test_reload_after_file_deletion(self, tmp_rules_file):
        """Reload handles a deleted file gracefully, producing empty rules."""
        loader = CustomRulesLoader()
        assert len(loader.get_custom_css_rules()) > 0

        tmp_rules_file.unlink()
        loader.reload()
        assert loader.get_custom_css_rules() == {}
        assert loader.get_custom_js_rules() == {}


@pytest.mark.whitebox
class TestEdgeCases:

    def test_invalid_types_in_json_skipped(self, mock_custom_rules_path):
        """Non-dict feature entries (string, list) are silently skipped."""
        data = {
            "css": {
                "string-entry": "not a dict",
                "list-entry": [1, 2, 3],
                "valid-entry": {"patterns": ["valid"], "description": "Valid"},
            },
            "javascript": {},
            "html": {},
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding="utf-8")
        loader = CustomRulesLoader()
        css = loader.get_custom_css_rules()
        assert "string-entry" not in css
        assert "list-entry" not in css
        assert "valid-entry" in css

    def test_duplicate_ids_across_sections(self, mock_custom_rules_path):
        """Same feature ID in CSS and JS sections stays independent."""
        data = {
            "css": {"shared-id": {"patterns": ["css-p"], "description": "CSS"}},
            "javascript": {"shared-id": {"patterns": ["js-p"], "description": "JS"}},
            "html": {},
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding="utf-8")
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules()["shared-id"]["patterns"] == ["css-p"]
        assert loader.get_custom_js_rules()["shared-id"]["patterns"] == ["js-p"]

    def test_extra_unknown_keys_ignored(self, mock_custom_rules_path):
        """Unknown top-level JSON keys don't cause errors."""
        data = {
            "css": {},
            "javascript": {},
            "html": {},
            "unknown_section": {"foo": "bar"},
            "metadata": {"version": 1},
        }
        mock_custom_rules_path.write_text(json.dumps(data), encoding="utf-8")
        loader = CustomRulesLoader()
        assert loader.get_custom_css_rules() == {}
