"""
通义千问提供商测试

测试阿里云通义千问 LLM 服务的实现
"""
import pytest
from unittest.mock import Mock, patch

from app.services.providers.qwen_provider import QwenProvider


class TestQwenProviderInit:
    """测试 QwenProvider 初始化"""

    def test_init_with_api_key(self):
        """使用 API key 初始化"""
        provider = QwenProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def test_init_with_base_url(self):
        """使用自定义 base_url 初始化"""
        provider = QwenProvider(
            api_key="test-key",
            base_url="https://custom.qwen.com"
        )
        assert provider.base_url == "https://custom.qwen.com"


class TestQwenProviderChat:
    """测试非流式对话"""

    @patch('app.services.providers.qwen_provider.requests.post')
    def test_chat_success(self, mock_post):
        """成功调用 chat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "你好！"
                }
            }]
        }
        mock_post.return_value = mock_response

        provider = QwenProvider(api_key="test-key")
        messages = [{"role": "user", "content": "你好"}]

        result = provider.chat(messages, "qwen-turbo")

        assert result["content"] == "你好！"
        mock_post.assert_called_once()

    @patch('app.services.providers.qwen_provider.requests.post')
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

        provider = QwenProvider(api_key="test-key")
        result = provider.chat(
            [{"role": "user", "content": "Hi"}],
            "qwen-turbo",
            temperature=0.7
        )

        assert result["content"] == "response"
        call_args = mock_post.call_args
        assert call_args[1]["json"]["temperature"] == 0.7

    @patch('app.services.providers.qwen_provider.requests.post')
    def test_chat_api_error(self, mock_post):
        """API 返回错误"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        provider = QwenProvider(api_key="invalid-key")

        with pytest.raises(Exception) as exc_info:
            provider.chat([{"role": "user", "content": "Hi"}], "qwen-turbo")
        assert "401" in str(exc_info.value)


class TestQwenProviderStreamChat:
    """测试流式对话"""

    @patch('app.services.providers.qwen_provider.requests.post')
    def test_stream_chat_success(self, mock_post):
        """成功调用流式 chat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            'data: {"choices": [{"delta": {"content": "你好"}}]}'.encode('utf-8'),
            'data: {"choices": [{"delta": {"content": "！"}}]}'.encode('utf-8'),
            'data: [DONE]'.encode('utf-8')
        ]
        mock_post.return_value = mock_response

        provider = QwenProvider(api_key="test-key")
        messages = [{"role": "user", "content": "你好"}]

        chunks = list(provider.stream_chat(messages, "qwen-turbo"))

        assert len(chunks) == 2
        assert chunks[0]["content"] == "你好"
        assert chunks[1]["content"] == "！"


class TestQwenProviderListModels:
    """测试模型列表"""

    def test_list_models(self):
        """通义千问返回固定模型列表"""
        provider = QwenProvider(api_key="test-key")
        models = provider.list_models()

        assert "qwen-turbo" in models
        assert "qwen-plus" in models
        assert "qwen-max" in models
