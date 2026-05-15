"""
OpenAI API 提供商实现

使用 OpenAI API 进行对话
"""
import json
import requests
from typing import List, Dict, Any, Generator

from app.services.llm_service import LLMService


class OpenAIProvider(LLMService):
    """OpenAI LLM 服务提供商"""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: str, base_url: str = None):
        super().__init__(api_key, base_url)
        self.base_url = base_url or self.DEFAULT_BASE_URL

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
            model: 模型名称（如 gpt-4, gpt-3.5-turbo）
            **kwargs: 其他参数（temperature, max_tokens 等）

        Returns:
            {"content": "响应内容"}

        Raises:
            Exception: API 调用失败时
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        response = requests.post(url, headers=headers, json=data, timeout=60)

        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

        result = response.json()
        return {
            "content": result["choices"][0]["message"]["content"],
            "model": result.get("model", model),
            "usage": result.get("usage")
        }

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
            {"content": "响应块内容"}
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }

        response = requests.post(
            url,
            headers=headers,
            json=data,
            stream=True,
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]  # 去掉 "data: " 前缀
                    if data_str == '[DONE]':
                        break
                    try:
                        data_json = json.loads(data_str)
                        # 检查 choices 是否存在且非空
                        if "choices" in data_json and len(data_json["choices"]) > 0:
                            delta = data_json["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield {"content": content}
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    def list_models(self) -> List[str]:
        """
        获取可用模型列表

        Returns:
            模型名称列表
        """
        url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

        result = response.json()
        return [model["id"] for model in result["data"]]
