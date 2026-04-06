"""AI fix suggestions black box tests."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.ai import AIFixService, AIFixSuggestion


@pytest.mark.blackbox
class TestNoApiKey:
    def test_no_key_returns_empty(self):
        service = AIFixService(api_key=None)
        assert not service.is_available()
        assert service.get_fix_suggestions({"flexbox"}, set(), "css", {}) == []

    def test_empty_key_returns_empty(self):
        service = AIFixService(api_key="")
        assert not service.is_available()

    def test_with_key_is_available(self):
        service = AIFixService(api_key="sk-test-123")
        assert service.is_available()


@pytest.mark.blackbox
class TestPromptBuilding:
    def test_prompt_contains_feature_info(self):
        service = AIFixService(api_key="sk-test")
        prompt = service._build_prompt(
            [{"id": "css-grid", "name": "CSS Grid", "status": "unsupported", "browsers": ["Safari 15"]}],
            "css",
        )
        assert "css-grid" in prompt
        assert "CSS Grid" in prompt
        assert "Safari 15" in prompt
        assert "CSS" in prompt
        assert "JSON" in prompt


@pytest.mark.blackbox
class TestResponseParsing:
    def test_valid_json_response(self):
        service = AIFixService(api_key="sk-test")
        features = [{"id": "css-grid", "name": "CSS Grid", "status": "unsupported", "browsers": ["Chrome 120"]}]
        raw = json.dumps([{
            "feature_id": "css-grid",
            "suggestion": "Use flexbox as fallback",
            "code_example": ".grid { display: flex; flex-wrap: wrap; }",
        }])
        result = service._parse_response(raw, features)
        assert len(result) == 1
        assert isinstance(result[0], AIFixSuggestion)
        assert result[0].feature_id == "css-grid"
        assert result[0].suggestion == "Use flexbox as fallback"

    def test_markdown_wrapped_json(self):
        service = AIFixService(api_key="sk-test")
        features = [{"id": "flexbox", "name": "Flexbox", "status": "unsupported", "browsers": []}]
        raw = '```json\n[{"feature_id": "flexbox", "suggestion": "Use float layout", "code_example": ""}]\n```'
        result = service._parse_response(raw, features)
        assert len(result) == 1

    def test_unknown_feature_id_skipped(self):
        service = AIFixService(api_key="sk-test")
        features = [{"id": "css-grid", "name": "CSS Grid", "status": "unsupported", "browsers": []}]
        raw = json.dumps([{"feature_id": "unknown-feature", "suggestion": "test", "code_example": ""}])
        assert service._parse_response(raw, features) == []

    def test_empty_features_returns_empty(self):
        service = AIFixService(api_key="sk-test")
        assert service.get_fix_suggestions(set(), set(), "css", {}) == []
