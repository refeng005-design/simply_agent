"""
LLM 服务提供商工厂

根据类型创建相应的 LLM 服务实例
"""
from enum import Enum
from typing import Union

from app.services.llm_service import LLMService
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.qwen_provider import QwenProvider


class ProviderType(Enum):
    """LLM 提供商类型枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"


def create_llm_provider(
    provider_type: Union[str, ProviderType],
    api_key: str,
    base_url: str = None
) -> LLMService:
    """
    创建 LLM 服务提供商实例

    Args:
        provider_type: 提供商类型（"openai", "anthropic", "qwen" 或 ProviderType 枚举）
        api_key: API 密钥
        base_url: 可选的自定义 API 基础 URL

    Returns:
        LLMService 实例

    Raises:
        ValueError: 无效的提供商类型时

    Examples:
        >>> provider = create_llm_provider("openai", "sk-xxx")
        >>> isinstance(provider, OpenAIProvider)
        True

        >>> provider = create_llm_provider(ProviderType.ANTHROPIC, "sk-xxx")
        >>> isinstance(provider, AnthropicProvider)
        True
    """
    # 如果传入枚举，获取其值
    if isinstance(provider_type, ProviderType):
        provider_type = provider_type.value

    provider_type = provider_type.lower()

    if provider_type == ProviderType.OPENAI.value:
        return OpenAIProvider(api_key=api_key, base_url=base_url)
    elif provider_type == ProviderType.ANTHROPIC.value:
        return AnthropicProvider(api_key=api_key, base_url=base_url)
    elif provider_type == ProviderType.QWEN.value:
        return QwenProvider(api_key=api_key, base_url=base_url)
    else:
        raise ValueError(
            f"Invalid provider type: {provider_type}. "
            f"Supported types: {', '.join([p.value for p in ProviderType])}"
        )
