"""
Conversation数据模型

表示用户与AI的对话会话
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.extensions import Model


class Conversation(Model):
    """对话模型 - SQLAlchemy模型"""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, default='New Conversation')
    model_name = Column(String(100), nullable=False, default='gpt-4')
    memory_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Conversation id={self.id} title='{self.title}'>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': str(self.id),
            'title': self.title,
            'model_name': self.model_name,
            'memory_enabled': bool(self.memory_enabled),
            'message_count': self.message_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def message_count(self):
        """获取消息数量"""
        from app.extensions import db
        if hasattr(db.session, 'query'):
            # 真正的数据库查询
            from app.models import Message
            return db.session.query(Message).filter_by(conversation_id=self.id).count()
        else:
            # 内存查询
            count = 0
            for msg in db._messages.values():
                if msg.conversation_id == str(self.id):
                    count += 1
            return count
