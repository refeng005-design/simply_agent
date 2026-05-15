"""
聊天相关Schema

定义聊天请求和响应的数据结构
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChatRequest:
    """聊天请求Schema"""
    message: str
    conversation_id: Optional[int] = None
    model: Optional[str] = None
    stream: bool = False
    memory_enabled: bool = True


@dataclass
class ChatResponse:
    """聊天响应Schema"""
    message: str
    conversation_id: Optional[int] = None
    message_id: Optional[int] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None


@dataclass
class ChatStreamChunk:
    """流式聊天响应块"""
    delta: str
    conversation_id: Optional[int] = None
    message_id: Optional[int] = None
    finished: bool = False


__all__ = ['ChatRequest', 'ChatResponse', 'ChatStreamChunk']
