"""
对话 API 测试

测试对话相关的 API 端点
"""
import pytest
from unittest.mock import Mock, patch

from app import create_app
from app.api.chat import chat


class TestChatAPI:
    """测试对话 API"""

    @patch('app.api.chat.ConversationService')
    def test_chat_success(self, mock_conv_cls):
        """成功对话"""
        app = create_app()
        mock_conv = Mock()
        mock_conv.chat.return_value = {
            "content": "Hello!",
            "model": "gpt-4"
        }
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4"
            }
        ):
            response = chat()

            assert response[1] == 200
            data = response[0].get_json()
            assert data["content"] == "Hello!"

    @patch('app.api.chat.ConversationService')
    def test_chat_missing_messages(self, mock_conv_cls):
        """缺少 messages 参数"""
        app = create_app()

        with app.test_request_context(json={"model": "gpt-4"}):
            response = chat()
            assert response[1] == 400

    @patch('app.api.chat.ConversationService')
    def test_chat_missing_model(self, mock_conv_cls):
        """缺少 model 参数"""
        app = create_app()

        with app.test_request_context(
            json={"messages": [{"role": "user", "content": "Hi"}]}
        ):
            response = chat()
            assert response[1] == 400

    @patch('app.api.chat.ConversationService')
    def test_chat_with_temperature(self, mock_conv_cls):
        """带 temperature 参数的对话"""
        app = create_app()
        mock_conv = Mock()
        mock_conv.chat.return_value = {"content": "Response"}
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4",
                "temperature": 0.7
            }
        ):
            response = chat()

            assert response[1] == 200
            mock_conv.chat.assert_called_once()

    @patch('app.api.chat.ConversationService')
    def test_chat_service_error(self, mock_conv_cls):
        """服务层错误"""
        app = create_app()
        mock_conv = Mock()
        mock_conv.chat.side_effect = Exception("LLM error")
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4"
            }
        ):
            response = chat()
            assert response[1] == 500
