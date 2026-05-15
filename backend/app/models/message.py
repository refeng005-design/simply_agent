"""
Message数据模型

表示对话中的单条消息
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Model


class Message(Model):
    """消息模型 - SQLAlchemy模型"""
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    conversation = relationship('Conversation', backref='messages')

    def __repr__(self):
        content_preview = (self.content[:20] + '...') if self.content and len(self.content) > 20 else self.content
        return f"<Message id={self.id} role='{self.role}' content='{content_preview}'>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'conversation_id': str(self.conversation_id) if self.conversation_id else None,
            'role': self.role,
            'content': self.content,
            'tokens': self.tokens,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
