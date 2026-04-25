"""AI fix suggestions white box tests."""

import pytest
from unittest.mock import patch, MagicMock

from src.ai.ai_service import AIFixService


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
