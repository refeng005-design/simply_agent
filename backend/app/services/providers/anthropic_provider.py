"""
Anthropic Claude API 提供商实现

使用 Anthropic Claude API 进行对话
"""
import json
import requests
from typing import List, Dict, Any, Generator

from app.services.llm_service import LLMService


class AnthropicProvider(LLMService):
    """Anthropic Claude LLM 服务提供商"""

    DEFAULT_BASE_URL = "https://api.anthropic.com"
    DEFAULT_API_VERSION = "2023-06-01"

    # Anthropic 支持的模型列表（目前 API 不提供动态查询）
    AVAILABLE_MODELS = [
        "claude-3-5-sonnet",
        "claude-3-5-haiku",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku",
    ]

    def __init__(self, api_key: str, base_url: str = None):
        super().__init__(api_key, base_url)
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.api_version = self.DEFAULT_API_VERSION

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        非流式对话

        Args:
            messages: 消息列表
            model: 模型名称（如 claude-3-sonnet）
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数（temperature, top_p 等）

        Returns:
            {"content": "响应内容"}

        Raises:
            Exception: API 调用失败时
        """
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json"
        }

        # Anthropic API 要求消息格式略有不同
        # 第一条必须是 system 或 user 消息
        system_message = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)

        data = {
            "model": model,
            "messages": filtered_messages,
            "max_tokens": max_tokens,
            **kwargs
        }
        if system_message:
            data["system"] = system_message

        response = requests.post(url, headers=headers, json=data, timeout=60)

        if response.status_code != 200:
            raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")

        result = response.json()
        # 提取文本内容
        content_blocks = result.get("content", [])
        text_content = ""
        for block in content_blocks:
            if block.get("type") == "text":
                text_content += block.get("text", "")

        return {
            "content": text_content,
            "model": result.get("model", model),
            "usage": result.get("usage")
        }

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1024,
        **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式对话

        Args:
            messages: 消息列表
            model: 模型名称
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数

        Yields:
            {"content": "响应块内容"}
        """
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json"
        }

        system_message = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)

        data = {
            "model": model,
            "messages": filtered_messages,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }
        if system_message:
            data["system"] = system_message

        response = requests.post(
            url,
            headers=headers,
            json=data,
            stream=True,
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        data_json = json.loads(data_str)
                        if data_json.get("type") == "content_block_delta":
                            delta = data_json.get("delta", {})
                            text = delta.get("text", "")
                            if text:
                                yield {"content": text}
                    except json.JSONDecodeError:
                        continue

    def list_models(self) -> List[str]:
        """
        获取可用模型列表

        Anthropic 目前不提供动态模型查询 API，返回已知模型列表

        Returns:
            模型名称列表
        """
        return self.AVAILABLE_MODELS.copy()
