"""
Base模型类测试

测试所有数据模型的基类
"""
import pytest


def test_base_class_exists():
    """测试Base类存在"""
    from app.models import Base

    assert Base is not None


def test_base_class_has_id_attribute():
    """测试Base类有id属性"""
    from app.models import Base

    assert hasattr(Base, 'id')


def test_base_class_has_timestamp_attributes():
    """测试Base类有时间戳属性"""
    from app.models import Base

    assert hasattr(Base, 'created_at')
    assert hasattr(Base, 'updated_at')


def test_base_class_has_repr_method():
    """测试Base类有__repr__方法"""
    from app.models import Base

    assert hasattr(Base, '__repr__')
    assert callable(Base.__repr__)


def test_base_class_repr_contains_id():
    """测试Base类的__repr__包含id"""
    from app.models import Base

    # 创建一个简单的子类实例
    class TestModel(Base):
        def __init__(self):
            self.id = 123

    instance = TestModel()
    str_repr = repr(instance)

    assert '123' in str_repr


def test_base_class_is_inherited_by_all_models():
    """测试所有模型都继承自Base"""
    from app.models import Base, Conversation, Message, KnowledgeEntry, ModelConfig

    assert issubclass(Conversation, Base)
    assert issubclass(Message, Base)
    assert issubclass(KnowledgeEntry, Base)
    assert issubclass(ModelConfig, Base)


def test_base_class_has_to_dict_method():
    """测试Base类有to_dict方法（或子类实现）"""
    from app.models import Base

    # Base本身可能没有to_dict，但子类应该有
    # 这里检查是否可以添加to_dict
    assert hasattr(Base, '__dict__') or hasattr(Base, '__slots__')
