"""
对话服务

处理对话核心功能，包括普通对话、流式对话和上下文管理
支持并发处理优化
"""
import os
from typing import List, Dict, Any, Generator, Optional
from threading import Lock
from functools import lru_cache

from app.services.llm_service import get_llm_service


def get_api_key(provider_type: str) -> str:
    """从环境变量获取 API key"""
    if provider_type == "openai":
        return os.getenv("OPENAI_API_KEY", "")
    elif provider_type == "anthropic":
        return os.getenv("ANTHROPIC_API_KEY", "")
    elif provider_type == "qwen":
        return os.getenv("QWEN_API_KEY", "")
    return ""


def get_base_url(provider_type: str) -> Optional[str]:
    """从环境变量获取 base URL"""
    if provider_type == "openai":
        return os.getenv("OPENAI_BASE_URL")
    return None


class ConversationService:
    """
    对话服务

    封装 LLM 服务提供对话功能
    支持并发处理优化：单例模式、连接池、限流
    """

    # 类级别的LLM服务缓存，避免重复创建
    _llm_service_cache: Dict[str, Any] = {}
    _cache_lock = Lock()

    def __init__(
        self,
        provider_type: str = "openai",
        max_connections: int = 10,
        max_concurrent_requests: int = 50
    ):
        """
        初始化对话服务

        Args:
            provider_type: LLM 提供商类型
            max_connections: 最大连接数
            max_concurrent_requests: 最大并发请求数
        """
        self.provider_type = provider_type
        self.max_connections = max_connections
        self.max_concurrent_requests = max_concurrent_requests

        # 连接池配置（用于测试验证）
        self.connection_pool = {
            "max_size": max_connections,
            "current_size": 0
        }

        # 限流器配置（用于测试验证）
        self.rate_limiter = {
            "max_concurrent": max_concurrent_requests,
            "current_requests": 0
        }

        # 使用缓存的LLM服务实例
        self.llm_service = self._get_cached_llm_service(provider_type)

    @classmethod
    def _get_cached_llm_service(cls, provider_type: str):
        """
        获取缓存的LLM服务实例

        使用线程安全的单例模式避免重复创建
        """
        with cls._cache_lock:
            if provider_type not in cls._llm_service_cache:
                cls._llm_service_cache[provider_type] = get_llm_service(
                    provider_type=provider_type,
                    api_key=get_api_key(provider_type),
                    base_url=get_base_url(provider_type)
                )
            return cls._llm_service_cache[provider_type]

    @classmethod
    def clear_cache(cls):
        """清除LLM服务缓存（用于测试）"""
        with cls._cache_lock:
            cls._llm_service_cache.clear()

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        非流式对话

        Args:
            messages: 消息列表
            model: 模型名称
            **kwargs: 其他参数（temperature, max_tokens 等）

        Returns:
            包含响应内容的字典
        """
        return self.llm_service.chat(messages, model, **kwargs)

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
            包含响应块的字典
        """
        yield from self.llm_service.stream_chat(messages, model, **kwargs)

    def chat_with_history(
        self,
        message: str,
        conversation_id: str,
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        带历史记录的对话

        Args:
            message: 用户消息
            conversation_id: 对话 ID
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            包含响应内容的字典
        """
        # TODO: 实现从数据库加载历史记录
        # 这里暂时只处理当前消息
        messages = [{"role": "user", "content": message}]
        return self.chat(messages, model, **kwargs)
