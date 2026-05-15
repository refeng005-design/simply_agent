"""
Prompt 构建器

构建 RAG 相关的提示词模板
"""
from typing import List, Dict, Any, Optional


class PromptBuilder:
    """
    Prompt 构建器

    用于构建各种场景的提示词模板
    """

    DEFAULT_RAG_TEMPLATE = """Please answer the following question based on the provided context.

[Context]
{context}

[Question]
{question}

[Answer]
"""

    DEFAULT_SYSTEM_TEMPLATE = """You are a helpful AI assistant. You provide accurate, concise, and friendly responses to user questions."""

    def __init__(self, template: Optional[str] = None):
        """
        初始化 Prompt 构建器

        Args:
            template: 自定义 RAG 模板，为空则使用默认模板
        """
        self.template = template or self.DEFAULT_RAG_TEMPLATE

    def build_rag(
        self,
        context: List[Any],
        question: str
    ) -> str:
        """
        构建 RAG 提示词

        Args:
            context: 上下文列表，可以是字符串或包含 text 字段的字典
            question: 用户问题

        Returns:
            格式化的 RAG 提示词
        """
        formatted_context = self._format_context(context)
        return self.template.format(
            context=formatted_context,
            question=question
        )

    def build_system_prompt(self, role: str = "assistant") -> str:
        """
        构建系统提示词

        Args:
            role: AI 角色

        Returns:
            系统提示词
        """
        if role == "assistant":
            return self.DEFAULT_SYSTEM_TEMPLATE
        elif role == "expert":
            return "You are an expert AI assistant with deep knowledge in many fields. Provide detailed, accurate, and well-reasoned answers."
        else:
            return f"You are a {role} AI assistant."

    def build_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        构建对话提示词

        Args:
            messages: 消息列表，每个消息包含 role 和 content

        Returns:
            格式化的对话提示词
        """
        if not messages:
            return ""

        parts = []
        for msg in messages:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            parts.append(f"{role}: {content}")

        return "\n".join(parts)

    def _format_context(self, context: List[Any]) -> str:
        """
        格式化上下文列表

        Args:
            context: 上下文列表

        Returns:
            格式化的上下文字符串
        """
        if not context:
            return "[No context available]"

        parts = []
        for i, item in enumerate(context, 1):
            if isinstance(item, dict):
                text = item.get("text", "")
                source = item.get("source", "")
                if source:
                    parts.append(f"[{i}] {text} (source: {source})")
                else:
                    parts.append(f"[{i}] {text}")
            else:
                parts.append(f"[{i}] {item}")

        return "\n".join(parts)
