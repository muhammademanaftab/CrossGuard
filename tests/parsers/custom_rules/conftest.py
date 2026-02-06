"""Shared fixtures for CustomRulesLoader tests."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from src.parsers.custom_rules_loader import CustomRulesLoader, CUSTOM_RULES_PATH


@pytest.fixture(autouse=True)
def fresh_loader():
    """Reset singleton state before and after each test."""
    CustomRulesLoader._instance = None
    CustomRulesLoader._loaded = False
    # Also reset the module-level _loader cache
    import src.parsers.custom_rules_loader as mod
    mod._loader = None
    yield
    CustomRulesLoader._instance = None
    CustomRulesLoader._loaded = False
    import src.parsers.custom_rules_loader as mod2
    mod2._loader = None


@pytest.fixture
def sample_rules_json():
    """Valid custom rules dict with CSS, JS, and HTML entries."""
    return {
        "css": {
            "test-css-feature": {
                "patterns": [r"test-property\s*:"],
                "description": "Test CSS Property"
            },
            "another-css-feature": {
                "patterns": [r"another-prop\s*:", r"alt-prop\s*:"],
                "description": "Another CSS Feature"
            }
        },
        "javascript": {
            "test-js-feature": {
                "patterns": [r"\bTestAPI\b"],
                "description": "Test JS API"
            },
            "another-js-feature": {
                "patterns": [r"anotherMethod\s*\("],
                "description": "Another JS Feature"
            }
        },
        "html": {
            "elements": {
                "test-element": "test-feature-id"
            },
            "attributes": {
                "test-attr": "test-attr-feature"
            },
            "input_types": {
                "test-type": "test-input-feature"
            },
            "attribute_values": {
                "data-test:value1": "test-value-feature"
            }
        }
    }


@pytest.fixture
def tmp_rules_file(tmp_path, sample_rules_json):
    """Write temp JSON to disk and patch loader path to use it."""
    rules_file = tmp_path / "custom_rules.json"
    rules_file.write_text(json.dumps(sample_rules_json), encoding='utf-8')
    with patch('src.parsers.custom_rules_loader.CUSTOM_RULES_PATH', rules_file):
        yield rules_file


@pytest.fixture
def mock_custom_rules_path(tmp_path):
    """Patch CUSTOM_RULES_PATH to a temp directory for isolated tests."""
    rules_file = tmp_path / "custom_rules.json"
    with patch('src.parsers.custom_rules_loader.CUSTOM_RULES_PATH', rules_file):
        yield rules_file
