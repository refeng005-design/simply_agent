"""
ModelConfig数据模型

表示LLM模型的配置
"""
from datetime import datetime
from . import Base


class ModelConfig(Base):
    """LLM模型配置"""

    # 模拟SQLAlchemy表对象
    class __table__:
        columns = [
            type('Column', (), {'name': 'id'}),
            type('Column', (), {'name': 'provider'}),
            type('Column', (), {'name': 'model_name'}),
            type('Column', (), {'name': 'api_key'}),
            type('Column', (), {'name': 'is_active'}),
            type('Column', (), {'name': 'temperature'}),
            type('Column', (), {'name': 'max_tokens'}),
            type('Column', (), {'name': 'created_at'}),
            type('Column', (), {'name': 'updated_at'})
        ]

    def __init__(self, provider=None, model_name=None, api_key=None,
                 is_active=True, temperature=None, max_tokens=None):
        self.id = None
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        self.is_active = is_active
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<ModelConfig id={self.id} provider='{self.provider}' model='{self.model_name}'>"

    def to_dict(self):
        """转换为字典（隐藏API密钥）"""
        return {
            'id': self.id,
            'provider': self.provider,
            'model_name': self.model_name,
            'api_key': '***HIDDEN***' if self.api_key else None,
            'is_active': self.is_active,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
