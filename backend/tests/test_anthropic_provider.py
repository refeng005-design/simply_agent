"""
Anthropic 提供商测试

测试 Anthropic Claude LLM 服务的实现
"""
import pytest
from unittest.mock import Mock, patch

from app.services.providers.anthropic_provider import AnthropicProvider


class TestAnthropicProviderInit:
    """测试 AnthropicProvider 初始化"""

    def test_init_with_api_key(self):
        """使用 API key 初始化"""
        provider = AnthropicProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.anthropic.com"

    def test_init_with_base_url(self):
        """使用自定义 base_url 初始化"""
        provider = AnthropicProvider(
            api_key="test-key",
            base_url="https://custom.anthropic.com"
        )
        assert provider.base_url == "https://custom.anthropic.com"


class TestAnthropicProviderChat:
    """测试非流式对话"""

    @patch('app.services.providers.anthropic_provider.requests.post')
    def test_chat_success(self, mock_post):
        """成功调用 chat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{
                "type": "text",
                "text": "Hello, world!"
            }]
        }
        mock_post.return_value = mock_response

        provider = AnthropicProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Hi"}]

        result = provider.chat(messages, "claude-3-sonnet")

        assert result["content"] == "Hello, world!"
        mock_post.assert_called_once()

    @patch('app.services.providers.anthropic_provider.requests.post')
    def test_chat_with_max_tokens(self, mock_post):
        """带 max_tokens 参数的 chat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "response"}]
        }
        mock_post.return_value = mock_response

        provider = AnthropicProvider(api_key="test-key")
        result = provider.chat(
            [{"role": "user", "content": "Hi"}],
            "claude-3-sonnet",
            max_tokens=1000
        )

        assert result["content"] == "response"
        call_args = mock_post.call_args
        assert call_args[1]["json"]["max_tokens"] == 1000

    @patch('app.services.providers.anthropic_provider.requests.post')
    def test_chat_api_error(self, mock_post):
        """API 返回错误"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        provider = AnthropicProvider(api_key="invalid-key")

        with pytest.raises(Exception) as exc_info:
            provider.chat([{"role": "user", "content": "Hi"}], "claude-3-sonnet")
        assert "401" in str(exc_info.value)


class TestAnthropicProviderStreamChat:
    """测试流式对话"""

    @patch('app.services.providers.anthropic_provider.requests.post')
    def test_stream_chat_success(self, mock_post):
        """成功调用流式 chat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'event: message_start',
            b'data: {"type": "message_start"}',
            b'event: content_block_delta',
            b'data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hello"}}',
            b'event: content_block_delta',
            b'data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": " world"}}',
            b'event: message_stop',
        ]
        mock_post.return_value = mock_response

        provider = AnthropicProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Hi"}]

        chunks = list(provider.stream_chat(messages, "claude-3-sonnet"))

        assert len(chunks) == 2
        assert chunks[0]["content"] == "Hello"
        assert chunks[1]["content"] == " world"


class TestAnthropicProviderListModels:
    """测试模型列表"""

    def test_list_models(self):
        """Anthropic 返回固定模型列表"""
        provider = AnthropicProvider(api_key="test-key")
        models = provider.list_models()

        assert "claude-3-sonnet" in models
        assert "claude-3-opus" in models
        assert "claude-3-haiku" in models
