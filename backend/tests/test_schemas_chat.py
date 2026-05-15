"""
聊天相关Schema测试

测试聊天请求和响应的Schema验证
"""
import pytest


def test_chat_request_schema_exists():
    """测试ChatRequest schema存在"""
    from app.schemas.chat import ChatRequest

    assert ChatRequest is not None


def test_chat_request_has_required_fields():
    """测试ChatRequest有必需字段"""
    from app.schemas.chat import ChatRequest

    # 检查schema有必需的字段验证
    schema = ChatRequest.__dict__ if hasattr(ChatRequest, '__dict__') else {}
    annotations = getattr(ChatRequest, '__annotations__', {})

    # 应该有message字段
    assert 'message' in annotations or hasattr(ChatRequest, 'message')


def test_chat_request_validates_message():
    """测试ChatRequest验证消息"""
    from app.schemas.chat import ChatRequest

    # 应该能创建有效的请求
    request = ChatRequest(message='Hello, AI!')

    assert request.message == 'Hello, AI!'


def test_chat_request_accepts_optional_conversation_id():
    """测试ChatRequest接受可选的conversation_id"""
    from app.schemas.chat import ChatRequest

    request = ChatRequest(message='Hello', conversation_id=123)

    assert request.conversation_id == 123


def test_chat_request_accepts_optional_model():
    """测试ChatRequest接受可选的model参数"""
    from app.schemas.chat import ChatRequest

    request = ChatRequest(message='Hello', model='gpt-4')

    assert request.model == 'gpt-4'


def test_chat_response_schema_exists():
    """测试ChatResponse schema存在"""
    from app.schemas.chat import ChatResponse

    assert ChatResponse is not None


def test_chat_response_has_message_field():
    """测试ChatResponse有message字段"""
    from app.schemas.chat import ChatResponse

    response = ChatResponse(message='Hi there!')

    assert response.message == 'Hi there!'


def test_chat_response_has_conversation_id():
    """测试ChatResponse有conversation_id"""
    from app.schemas.chat import ChatResponse

    response = ChatResponse(message='Hello', conversation_id=1)

    assert response.conversation_id == 1


def test_chat_response_can_include_message_id():
    """测试ChatResponse可以包含message_id"""
    from app.schemas.chat import ChatResponse

    response = ChatResponse(message='Hello', message_id=456)

    assert response.message_id == 456


def test_chat_request_supports_stream_parameter():
    """测试ChatRequest支持stream参数"""
    from app.schemas.chat import ChatRequest

    request = ChatRequest(message='Hello', stream=True)

    assert request.stream is True


def test_chat_request_supports_memory_disabled():
    """测试ChatRequest支持禁用记忆"""
    from app.schemas.chat import ChatRequest

    request = ChatRequest(message='Hello', memory_enabled=False)

    assert request.memory_enabled is False
