"""
LLMService 服务层完整实现测试

测试 LLMService 作为服务层的封装功能
"""
import pytest
from unittest.mock import Mock, patch

from app.services.llm_service import get_llm_service
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.factory import ProviderType


class TestGetLLMService:
    """测试获取 LLM 服务实例"""

    @patch('app.services.providers.factory.create_llm_provider')
    def test_get_openai_service(self, mock_create):
        """获取 OpenAI 服务"""
        mock_provider = Mock(spec=OpenAIProvider)
        mock_create.return_value = mock_provider

        service = get_llm_service(provider_type="openai", api_key="test-key")

        assert service is mock_provider
        mock_create.assert_called_once_with(
            provider_type="openai",
            api_key="test-key",
            base_url=None
        )

    @patch('app.services.providers.factory.create_llm_provider')
    def test_get_anthropic_service(self, mock_create):
        """获取 Anthropic 服务"""
        mock_provider = Mock(spec=AnthropicProvider)
        mock_create.return_value = mock_provider

        service = get_llm_service(provider_type="anthropic", api_key="test-key")

        assert service is mock_provider
        mock_create.assert_called_once()

    @patch('app.services.providers.factory.create_llm_provider')
    def test_get_with_base_url(self, mock_create):
        """获取带自定义 URL 的服务"""
        mock_provider = Mock(spec=OpenAIProvider)
        mock_create.return_value = mock_provider

        service = get_llm_service(
            provider_type="openai",
            api_key="test-key",
            base_url="https://custom.com"
        )

        assert service is mock_provider
        mock_create.assert_called_once_with(
            provider_type="openai",
            api_key="test-key",
            base_url="https://custom.com"
        )


class TestLLMServiceIntegration:
    """测试 LLMService 与提供商集成"""

    @patch('app.services.providers.factory.create_llm_provider')
    def test_service_has_required_methods(self, mock_create):
        """服务应有所需方法"""
        mock_provider = Mock(spec=OpenAIProvider)
        mock_provider.chat.return_value = {"content": "response"}
        mock_create.return_value = mock_provider

        service = get_llm_service(provider_type="openai", api_key="test-key")

        # 验证方法存在并可调用
        assert hasattr(service, 'chat')
        assert hasattr(service, 'stream_chat')
        assert hasattr(service, 'list_models')

        # 验证方法可正常调用
        result = service.chat([{"role": "user", "content": "Hi"}], "gpt-4")
        assert result == {"content": "response"}

    @patch('app.services.providers.openai_provider.requests.post')
    def test_end_to_end_openai_chat(self, mock_post):
        """端到端测试 OpenAI 对话"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "Hello!"}
            }]
        }
        mock_post.return_value = mock_response

        service = get_llm_service(provider_type="openai", api_key="test-key")
        result = service.chat([{"role": "user", "content": "Hi"}], "gpt-4")

        assert result["content"] == "Hello!"


class TestLLMServiceErrors:
    """测试 LLMService 错误处理"""

    @patch('app.services.providers.factory.create_llm_provider')
    def test_invalid_provider_type_propagates(self, mock_create):
        """无效提供商类型应传播错误"""
        mock_create.side_effect = ValueError("Invalid provider type")

        with pytest.raises(ValueError) as exc_info:
            get_llm_service(provider_type="invalid", api_key="test-key")
        assert "Invalid provider type" in str(exc_info.value)
