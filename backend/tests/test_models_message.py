"""
Message模型测试

测试消息数据模型的字段和行为
"""
import pytest


def test_message_model_has_required_fields():
    """测试Message模型有必需的字段"""
    from app.models import Message

    columns = [column.name for column in Message.__table__.columns]

    assert 'id' in columns
    assert 'conversation_id' in columns
    assert 'role' in columns
    assert 'content' in columns
    assert 'created_at' in columns


def test_message_model_can_be_created():
    """测试可以创建Message实例"""
    from app.models import Message

    message = Message(
        conversation_id=1,
        role='user',
        content='Hello, AI!'
    )

    assert message.conversation_id == 1
    assert message.role == 'user'
    assert message.content == 'Hello, AI!'


def test_message_model_role_validation():
    """测试消息角色验证"""
    from app.models import Message

    # 有效角色
    valid_roles = ['user', 'assistant', 'system']

    for role in valid_roles:
        message = Message(conversation_id=1, role=role, content='test')
        assert message.role == role


def test_message_model_has_timestamp():
    """测试Message有创建时间"""
    from app.models import Message

    message = Message(conversation_id=1, role='user', content='test')

    assert hasattr(message, 'created_at')
    assert message.created_at is not None


def test_message_model_string_representation():
    """测试Message模型的字符串表示"""
    from app.models import Message

    message = Message(conversation_id=1, role='user', content='Hello')

    str_repr = str(message)

    assert 'user' in str_repr or 'Hello' in str_repr


def test_message_model_supports_long_content():
    """测试Message支持长内容"""
    from app.models import Message

    long_content = 'A' * 10000

    message = Message(
        conversation_id=1,
        role='assistant',
        content=long_content
    )

    assert len(message.content) == 10000


def test_message_model_has_tokens_field():
    """测试Message有token计数字段"""
    from app.models import Message

    message = Message(conversation_id=1, role='user', content='test')

    assert hasattr(message, 'tokens')
    assert message.tokens is None or isinstance(message.tokens, int)
