"""
LLM 提供商工厂测试

测试工厂模式创建不同的 LLM 服务提供商
"""
import pytest

from app.services.providers.factory import create_llm_provider, ProviderType
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.qwen_provider import QwenProvider
from app.services.llm_service import LLMService


class TestCreateLLMProvider:
    """测试创建 LLM 提供商"""

    def test_create_openai_provider(self):
        """创建 OpenAI 提供商"""
        provider = create_llm_provider(
            provider_type="openai",
            api_key="test-key"
        )
        assert isinstance(provider, OpenAIProvider)
        assert isinstance(provider, LLMService)
        assert provider.api_key == "test-key"

    def test_create_openai_with_enum(self):
        """使用枚举创建 OpenAI 提供商"""
        provider = create_llm_provider(
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        )
        assert isinstance(provider, OpenAIProvider)

    def test_create_anthropic_provider(self):
        """创建 Anthropic 提供商"""
        provider = create_llm_provider(
            provider_type="anthropic",
            api_key="test-key"
        )
        assert isinstance(provider, AnthropicProvider)
        assert provider.api_key == "test-key"

    def test_create_qwen_provider(self):
        """创建通义千问提供商"""
        provider = create_llm_provider(
            provider_type="qwen",
            api_key="test-key"
        )
        assert isinstance(provider, QwenProvider)
        assert provider.api_key == "test-key"

    def test_create_with_base_url(self):
        """创建带自定义 base_url 的提供商"""
        provider = create_llm_provider(
            provider_type="openai",
            api_key="test-key",
            base_url="https://custom.com"
        )
        assert provider.base_url == "https://custom.com"

    def test_invalid_provider_type(self):
        """无效的提供商类型应报错"""
        with pytest.raises(ValueError) as exc_info:
            create_llm_provider(
                provider_type="invalid",
                api_key="test-key"
            )
        assert "invalid" in str(exc_info.value).lower()
        assert "provider" in str(exc_info.value).lower()


class TestProviderTypeEnum:
    """测试 ProviderType 枚举"""

    def test_enum_values(self):
        """枚举值应正确"""
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.ANTHROPIC.value == "anthropic"
        assert ProviderType.QWEN.value == "qwen"

    def test_enum_members(self):
        """枚举成员数量"""
        assert len(ProviderType) == 3
