"""Tests for reload() and reload_custom_rules() functionality."""

import json
import pytest
from src.parsers.custom_rules_loader import (
    CustomRulesLoader,
    reload_custom_rules,
    get_custom_rules_loader,
)


class TestReload:

    def test_reload_picks_up_new_rules(self, tmp_rules_file, sample_rules_json):
        """After modifying JSON, reload() returns updated data."""
        loader = CustomRulesLoader()
        assert "test-css-feature" in loader.get_custom_css_rules()

        # Modify the JSON file
        sample_rules_json["css"]["new-feature"] = {
            "patterns": ["new-pattern"],
            "description": "New Feature"
        }
        tmp_rules_file.write_text(json.dumps(sample_rules_json), encoding='utf-8')

        loader.reload()
        css = loader.get_custom_css_rules()
        assert "new-feature" in css

    def test_reload_custom_rules_module_function(self, tmp_rules_file, sample_rules_json):
        """Module-level reload_custom_rules() works."""
        loader = get_custom_rules_loader()
        assert "test-css-feature" in loader.get_custom_css_rules()

        sample_rules_json["css"]["added-feature"] = {
            "patterns": ["added"],
            "description": "Added"
        }
        tmp_rules_file.write_text(json.dumps(sample_rules_json), encoding='utf-8')

        reload_custom_rules()
        assert "added-feature" in loader.get_custom_css_rules()

    def test_reload_clears_old_data(self, tmp_rules_file):
        """Old rules no longer present after reload with different data."""
        loader = CustomRulesLoader()
        assert "test-css-feature" in loader.get_custom_css_rules()

        # Write new data without the old rule
        new_data = {
            "css": {
                "replacement-feature": {
                    "patterns": ["replacement"],
                    "description": "Replacement"
                }
            },
            "javascript": {},
            "html": {}
        }
        tmp_rules_file.write_text(json.dumps(new_data), encoding='utf-8')

        loader.reload()
        css = loader.get_custom_css_rules()
        assert "test-css-feature" not in css
        assert "replacement-feature" in css

    def test_reload_after_file_deletion(self, tmp_rules_file):
        """Handles missing file after reload."""
        loader = CustomRulesLoader()
        assert len(loader.get_custom_css_rules()) > 0

        # Delete the file
        tmp_rules_file.unlink()

        loader.reload()
        assert loader.get_custom_css_rules() == {}
        assert loader.get_custom_js_rules() == {}

    def test_reload_preserves_singleton(self, tmp_rules_file):
        """Same instance after reload."""
        loader = CustomRulesLoader()
        loader.reload()
        loader2 = CustomRulesLoader()
        assert loader is loader2
