"""
OpenAI 提供商测试

测试 OpenAI LLM 服务的实现
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.providers.openai_provider import OpenAIProvider


class TestOpenAIProviderInit:
    """测试 OpenAIProvider 初始化"""

    def test_init_with_api_key(self):
        """使用 API key 初始化"""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.openai.com/v1"

    def test_init_with_base_url(self):
        """使用自定义 base_url 初始化"""
        provider = OpenAIProvider(
            api_key="test-key",
            base_url="https://custom.openai.com"
        )
        assert provider.base_url == "https://custom.openai.com"


class TestOpenAIProviderChat:
    """测试非流式对话"""

    @patch('app.services.providers.openai_provider.requests.post')
    def test_chat_success(self, mock_post):
        """成功调用 chat"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Hello, world!"
                }
            }]
        }
        mock_post.return_value = mock_response

        provider = OpenAIProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Hi"}]

        result = provider.chat(messages, "gpt-4")

        assert result["content"] == "Hello, world!"
        mock_post.assert_called_once()

    @patch('app.services.providers.openai_provider.requests.post')
    def test_chat_with_temperature(self, mock_post):
        """带 temperature 参数的 chat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "response"}
            }]
        }
        mock_post.return_value = mock_response

        provider = OpenAIProvider(api_key="test-key")
        result = provider.chat(
            [{"role": "user", "content": "Hi"}],
            "gpt-4",
            temperature=0.7
        )

        assert result["content"] == "response"
        # 验证请求包含 temperature
        call_args = mock_post.call_args
        assert call_args[1]["json"]["temperature"] == 0.7

    @patch('app.services.providers.openai_provider.requests.post')
    def test_chat_api_error(self, mock_post):
        """API 返回错误"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        provider = OpenAIProvider(api_key="invalid-key")

        with pytest.raises(Exception) as exc_info:
            provider.chat([{"role": "user", "content": "Hi"}], "gpt-4")
        assert "401" in str(exc_info.value)


class TestOpenAIProviderStreamChat:
    """测试流式对话"""

    @patch('app.services.providers.openai_provider.requests.post')
    def test_stream_chat_success(self, mock_post):
        """成功调用流式 chat"""
        # Mock 流式响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
            b'data: {"choices": [{"delta": {"content": " world"}}]}\n\n',
            b'data: [DONE]\n\n'
        ]
        mock_post.return_value = mock_response

        provider = OpenAIProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Hi"}]

        chunks = list(provider.stream_chat(messages, "gpt-4"))

        assert len(chunks) == 2
        assert chunks[0]["content"] == "Hello"
        assert chunks[1]["content"] == " world"


class TestOpenAIProviderListModels:
    """测试模型列表"""

    @patch('app.services.providers.openai_provider.requests.get')
    def test_list_models(self, mock_get):
        """获取模型列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-4"},
                {"id": "gpt-3.5-turbo"}
            ]
        }
        mock_get.return_value = mock_response

        provider = OpenAIProvider(api_key="test-key")
        models = provider.list_models()

        assert "gpt-4" in models
        assert "gpt-3.5-turbo" in models
