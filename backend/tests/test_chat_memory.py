"""
对话记忆控制测试

测试对话记忆开关的控制逻辑
"""
import pytest
from unittest.mock import Mock, patch

from app import create_app


class TestChatMemory:
    """测试对话记忆控制"""

    def test_chat_with_memory_enabled(self):
        """启用记忆的对话 - 应加载历史消息"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv1"
        mock_conv.memory_enabled = True

        mock_msg = Mock()
        mock_msg.to_dict.return_value = {"role": "user", "content": "Previous"}

        mock_service = Mock()
        mock_service.chat.return_value = {"content": "Response", "model": "gpt-4"}

        with patch('app.api.chat.Conversation') as mock_conv_cls:
            mock_conv_cls.query.get.return_value = mock_conv

            with patch('app.api.chat.Message') as mock_msg_cls:
                mock_msg_query = Mock()
                mock_msg_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_msg]
                mock_msg_cls.query = mock_msg_query

                with patch('app.api.chat.ConversationService', return_value=mock_service):
                    with app.test_request_context(
                        json={
                            "messages": [{"role": "user", "content": "Hi"}],
                            "model": "gpt-4",
                            "conversation_id": "conv1"
                        }
                    ):
                        from app.api.chat import chat
                        response = chat()

                        assert response[1] == 200

    def test_chat_with_memory_disabled(self):
        """禁用记忆的对话 - 不加载历史消息"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv1"
        mock_conv.memory_enabled = False

        mock_service = Mock()
        mock_service.chat.return_value = {"content": "Response", "model": "gpt-4"}

        with patch('app.api.chat.Conversation') as mock_conv_cls:
            mock_conv_cls.query.get.return_value = mock_conv

            with patch('app.api.chat.ConversationService', return_value=mock_service):
                with app.test_request_context(
                    json={
                        "messages": [{"role": "user", "content": "Hi"}],
                        "model": "gpt-4",
                        "conversation_id": "conv1"
                    }
                ):
                    from app.api.chat import chat
                    response = chat()

                    assert response[1] == 200

    def test_chat_without_conversation_id(self):
        """没有 conversation_id 的新对话"""
        app = create_app()

        mock_service = Mock()
        mock_service.chat.return_value = {"content": "Response", "model": "gpt-4"}

        with patch('app.api.chat.ConversationService', return_value=mock_service):
            with app.test_request_context(
                json={
                    "messages": [{"role": "user", "content": "Hi"}],
                    "model": "gpt-4"
                }
            ):
                from app.api.chat import chat
                response = chat()

                assert response[1] == 200

    def test_conversation_memory_toggle(self):
        """切换对话记忆状态"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv1"
        mock_conv.memory_enabled = True

        with patch('app.api.history.Conversation') as mock_conv_cls:
            mock_conv_cls.query.get.return_value = mock_conv

            with patch('app.api.history.db') as mock_db:
                with app.test_request_context():
                    from app.api.history import toggle_conversation_memory
                    response = toggle_conversation_memory("conv1", False)

                    assert response[1] == 200
                    assert mock_conv.memory_enabled == False

    def test_toggle_conversation_memory_not_found(self):
        """切换不存在对话的记忆状态"""
        app = create_app()

        with patch('app.api.history.Conversation') as mock_conv_cls:
            mock_conv_cls.query.get.return_value = None

            with app.test_request_context():
                from app.api.history import toggle_conversation_memory
                response = toggle_conversation_memory("nonexistent", True)

                assert response[1] == 404

    def test_stream_chat_with_memory(self):
        """流式对话的记忆控制"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv1"
        mock_conv.memory_enabled = True

        mock_msg = Mock()
        mock_msg.to_dict.return_value = {"role": "user", "content": "Previous"}

        mock_service = Mock()
        mock_service.stream_chat.return_value = iter([{"content": "Hi"}])

        with patch('app.api.chat.Conversation') as mock_conv_cls:
            mock_conv_cls.query.get.return_value = mock_conv

            with patch('app.api.chat.Message') as mock_msg_cls:
                mock_msg_query = Mock()
                mock_msg_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_msg]
                mock_msg_cls.query = mock_msg_query

                with patch('app.api.chat.ConversationService', return_value=mock_service):
                    with app.test_request_context(
                        json={
                            "messages": [{"role": "user", "content": "Hello"}],
                            "model": "gpt-4",
                            "conversation_id": "conv1"
                        }
                    ):
                        from app.api.chat import stream_chat
                        response = stream_chat()

                        assert response.status_code == 200
                        assert "text/event-stream" in response.content_type
