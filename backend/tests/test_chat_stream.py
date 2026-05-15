"""
流式对话 API 测试

测试流式对话相关的 API 端点
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app import create_app
from app.api.chat import stream_chat


class TestStreamChatAPI:
    """测试流式对话 API"""

    @patch('app.api.chat.ConversationService')
    def test_stream_chat_success(self, mock_conv_cls):
        """成功流式对话"""
        app = create_app()
        mock_conv = Mock()
        mock_conv.stream_chat.return_value = iter([
            {"content": "Hello"},
            {"content": " world"},
            {"content": "!"}
        ])
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4"
            }
        ):
            response = stream_chat()

            assert response.status_code == 200
            assert "text/event-stream" in response.content_type

    @patch('app.api.chat.ConversationService')
    def test_stream_chat_missing_messages(self, mock_conv_cls):
        """缺少 messages 参数"""
        app = create_app()

        with app.test_request_context(json={"model": "gpt-4"}):
            response = stream_chat()
            # 错误情况返回 tuple (json_response, status_code)
            if isinstance(response, tuple):
                assert response[1] == 400
            else:
                assert response.status_code == 400

    @patch('app.api.chat.ConversationService')
    def test_stream_chat_missing_model(self, mock_conv_cls):
        """缺少 model 参数"""
        app = create_app()

        with app.test_request_context(
            json={"messages": [{"role": "user", "content": "Hi"}]}
        ):
            response = stream_chat()
            # 错误情况返回 tuple (json_response, status_code)
            if isinstance(response, tuple):
                assert response[1] == 400
            else:
                assert response.status_code == 400

    @patch('app.api.chat.ConversationService')
    def test_stream_chat_with_temperature(self, mock_conv_cls):
        """带 temperature 参数的流式对话"""
        app = create_app()
        mock_conv = Mock()
        mock_conv.stream_chat.return_value = iter([{"content": "Hi"}])
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4",
                "temperature": 0.7
            }
        ):
            response = stream_chat()

            assert response.status_code == 200
            assert "text/event-stream" in response.content_type

    @patch('app.api.chat.ConversationService')
    def test_stream_chat_empty_chunks(self, mock_conv_cls):
        """处理空响应块"""
        app = create_app()
        mock_conv = Mock()
        mock_conv.stream_chat.return_value = iter([
            {"content": ""},
            {"content": "Hi"}
        ])
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4"
            }
        ):
            response = stream_chat()

            assert response.status_code == 200
