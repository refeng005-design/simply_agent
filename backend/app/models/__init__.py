"""
数据模型模块

包含所有数据模型类和基类
"""
from datetime import datetime


class Base:
    """所有数据模型的基类"""

    id = None
    created_at = None
    updated_at = None

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"<{class_name} id={self.id}>"


# 导入具体模型（在实现后取消注释）
from .conversation import Conversation  # noqa: E402
from .message import Message  # noqa: E402
from .knowledge import KnowledgeEntry  # noqa: E402
from .model_config import ModelConfig  # noqa: E402

__all__ = [
    'Base',
    'Conversation',
    'Message',
    'KnowledgeEntry',
    'ModelConfig'
]
