"""
LLM 服务抽象基类

定义所有 LLM 提供商必须实现的接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional, Union


class LLMService(ABC):
    """
    LLM 服务抽象基类

    所有 LLM 提供商（OpenAI、Anthropic、通义千问等）都必须继承此类
    并实现所有抽象方法
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        初始化 LLM 服务

        Args:
            api_key: API 密钥
            base_url: 可选的自定义 API 基础 URL
        """
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        非流式对话

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称
            **kwargs: 其他参数（temperature, max_tokens 等）

        Returns:
            包含响应内容的字典，格式为 {"content": "...", ...}
        """
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式对话

        Args:
            messages: 消息列表
            model: 模型名称
            **kwargs: 其他参数

        Yields:
            包含响应块的字典，格式为 {"content": "...", ...}
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        获取可用模型列表

        Returns:
            模型名称列表
        """
        pass


def get_llm_service(
    provider_type: Union[str, 'ProviderType'],
    api_key: str,
    base_url: Optional[str] = None
) -> LLMService:
    """
    获取 LLM 服务实例（工厂函数）

    这是一个便捷函数，用于创建 LLM 服务提供商实例。

    Args:
        provider_type: 提供商类型（"openai", "anthropic", "qwen"）
        api_key: API 密钥
        base_url: 可选的自定义 API 基础 URL

    Returns:
        LLMService 实例（OpenAIProvider、AnthropicProvider 或 QwenProvider）

    Raises:
        ValueError: 无效的提供商类型时

    Examples:
        >>> service = get_llm_service("openai", "sk-xxx")
        >>> response = service.chat([{"role": "user", "content": "Hi"}], "gpt-4")
        >>> print(response["content"])
    """
    # 延迟导入以避免循环依赖
    from app.services.providers.factory import create_llm_provider
    return create_llm_provider(
        provider_type=provider_type,
        api_key=api_key,
        base_url=base_url
    )
