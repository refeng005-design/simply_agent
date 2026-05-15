"""
KnowledgeEntry数据模型

表示RAG知识库中的条目
"""
from datetime import datetime
from . import Base


class KnowledgeEntry(Base):
    """知识库条目模型"""

    # 模拟SQLAlchemy表对象
    class __table__:
        columns = [
            type('Column', (), {'name': 'id'}),
            type('Column', (), {'name': 'title'}),
            type('Column', (), {'name': 'content'}),
            type('Column', (), {'name': 'source'}),
            type('Column', (), {'name': 'embedding'}),
            type('Column', (), {'name': 'metadata'}),
            type('Column', (), {'name': 'created_at'})
        ]

    def __init__(self, title=None, content=None, source='manual', embedding=None, metadata=None):
        self.id = None
        self.title = title
        self.content = content
        self.source = source
        self.embedding = embedding
        self.metadata = metadata if metadata is not None else {}
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return f"<KnowledgeEntry id={self.id} title='{self.title}'>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'embedding': self.embedding,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
