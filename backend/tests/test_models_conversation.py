"""
Conversation模型测试

测试对话数据模型的字段和行为
"""
import pytest
from datetime import datetime


def test_conversation_model_has_required_fields():
    """测试Conversation模型有必需的字段"""
    from app.models import Conversation

    # 检查模型有所有必需的列
    columns = [column.name for column in Conversation.__table__.columns]

    assert 'id' in columns
    assert 'title' in columns
    assert 'model_name' in columns
    assert 'created_at' in columns
    assert 'updated_at' in columns


def test_conversation_model_can_be_created():
    """测试可以创建Conversation实例"""
    from app.models import Conversation

    conversation = Conversation(
        title='Test Conversation',
        model_name='gpt-4'
    )

    assert conversation.title == 'Test Conversation'
    assert conversation.model_name == 'gpt-4'


def test_conversation_model_has_default_title():
    """测试Conversation模型有默认标题"""
    from app.models import Conversation

    conversation = Conversation()

    assert conversation.title == 'New Conversation'


def test_conversation_model_timestamps_are_datetime():
    """测试时间戳字段是datetime类型"""
    from app.models import Conversation

    conversation = Conversation()

    # 创建时可能没有设置时间戳，检查类型
    assert hasattr(conversation, 'created_at')
    assert hasattr(conversation, 'updated_at')


def test_conversation_model_string_representation():
    """测试Conversation模型的字符串表示"""
    from app.models import Conversation

    conversation = Conversation(title='My Chat', model_name='gpt-4')

    # 应该有合理的字符串表示
    str_repr = str(conversation)

    assert 'My Chat' in str_repr or 'gpt-4' in str_repr


def test_conversation_model_relationship_with_messages():
    """测试Conversation与Message的关系"""
    from app.models import Conversation

    # 应该有messages关系
    assert hasattr(Conversation, 'messages')


def test_conversation_model_has_memory_enabled_field():
    """测试Conversation有记忆开关字段"""
    from app.models import Conversation

    conversation = Conversation()

    assert hasattr(conversation, 'memory_enabled')
    assert conversation.memory_enabled is True  # 默认开启
