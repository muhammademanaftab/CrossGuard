"""AI fix suggestions white box tests."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.ai.ai_service import AIFixService


@pytest.mark.whitebox
class TestProviderSelection:
    def test_anthropic_is_default(self):
        service = AIFixService(api_key="sk-test")
        assert service._provider == "anthropic"

    def test_openai_provider(self):
        service = AIFixService(api_key="sk-test", provider="openai")
        assert service._provider == "openai"

    def test_unknown_provider_raises(self):
        service = AIFixService(api_key="sk-test", provider="unknown")
        with pytest.raises(ValueError, match="Unknown AI provider"):
            service._call_api("test prompt")


@pytest.mark.whitebox
class TestApiCalls:
    @patch('src.ai.ai_service.requests.post')
    def test_anthropic_call_structure(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"content": [{"text": "[]"}]},
        )
        mock_post.return_value.raise_for_status = MagicMock()

        service = AIFixService(api_key="sk-ant-test", provider="anthropic")
        service._call_anthropic("test prompt")

        call_kwargs = mock_post.call_args
        assert "x-api-key" in call_kwargs.kwargs["headers"]
        assert call_kwargs.kwargs["headers"]["x-api-key"] == "sk-ant-test"

    @patch('src.ai.ai_service.requests.post')
    def test_openai_call_structure(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"choices": [{"message": {"content": "[]"}}]},
        )
        mock_post.return_value.raise_for_status = MagicMock()

        service = AIFixService(api_key="sk-openai-test", provider="openai")
        service._call_openai("test prompt")

        call_kwargs = mock_post.call_args
        assert "Bearer sk-openai-test" in call_kwargs.kwargs["headers"]["Authorization"]

    @patch('src.ai.ai_service.requests.post')
    def test_network_error_returns_empty(self, mock_post):
        mock_post.side_effect = ConnectionError("Network error")

        service = AIFixService(api_key="sk-test", provider="anthropic")
        result = service.get_fix_suggestions({"css-grid"}, set(), "css", {"chrome": "120"})
        assert result == []
