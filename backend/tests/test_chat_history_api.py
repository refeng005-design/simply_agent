"""
对话历史 API 测试

测试对话历史记录的获取、删除等功能
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app import create_app


class TestChatHistoryAPI:
    """测试对话历史 API"""

    def test_get_conversations_list(self):
        """获取对话列表"""
        app = create_app()

        mock_conv1 = Mock()
        mock_conv1.id = "conv1"
        mock_conv1.title = "Chat 1"
        mock_conv1.model_name = "gpt-4"
        mock_conv1.created_at = datetime(2026, 1, 1)
        mock_conv1.to_dict.return_value = {
            "id": "conv1",
            "title": "Chat 1",
            "model_name": "gpt-4"
        }

        mock_conv2 = Mock()
        mock_conv2.id = "conv2"
        mock_conv2.title = "Chat 2"
        mock_conv2.model_name = "gpt-3.5"
        mock_conv2.created_at = datetime(2026, 1, 2)
        mock_conv2.to_dict.return_value = {
            "id": "conv2",
            "title": "Chat 2",
            "model_name": "gpt-3.5"
        }

        with patch('app.api.history.db') as mock_db:
            mock_db.session.query.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [
                mock_conv1, mock_conv2
            ]

            with app.test_request_context():
                from app.api.history import get_conversations
                response = get_conversations()

                assert response[1] == 200
                data = response[0].get_json()
                assert len(data["conversations"]) == 2

    def test_get_conversation_by_id(self):
        """获取单个对话详情"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv1"
        mock_conv.title = "My Chat"
        mock_conv.model_name = "gpt-4"
        mock_conv.memory_enabled = True
        mock_conv.to_dict.return_value = {
            "id": "conv1",
            "title": "My Chat",
            "model_name": "gpt-4",
            "memory_enabled": True
        }

        with patch('app.api.history.db') as mock_db:
            mock_db.session.query.return_value.get.return_value = mock_conv

            with app.test_request_context():
                from app.api.history import get_conversation
                response = get_conversation("conv1")

                assert response[1] == 200
                data = response[0].get_json()
                assert data["id"] == "conv1"

    def test_get_conversation_not_found(self):
        """对话不存在"""
        app = create_app()

        with patch('app.api.history.db') as mock_db:
            mock_db.session.query.return_value.get.return_value = None

            with app.test_request_context():
                from app.api.history import get_conversation
                response = get_conversation("nonexistent")

                assert response[1] == 404

    def test_delete_conversation(self):
        """删除对话"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv1"

        with patch('app.api.history.db') as mock_db:
            mock_db.session.query.return_value.get.return_value = mock_conv

            with app.test_request_context():
                from app.api.history import delete_conversation
                response = delete_conversation("conv1")

                assert response[1] == 204
                mock_db.session.delete.assert_called_once_with(mock_conv)
                mock_db.session.commit.assert_called_once()

    def test_delete_conversation_not_found(self):
        """删除不存在的对话"""
        app = create_app()

        with patch('app.api.history.db') as mock_db:
            mock_db.session.query.return_value.get.return_value = None

            with app.test_request_context():
                from app.api.history import delete_conversation
                response = delete_conversation("nonexistent")

                assert response[1] == 404

    def test_get_conversation_messages(self):
        """获取对话的消息列表"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv1"

        mock_msg1 = Mock()
        mock_msg1.id = "msg1"
        mock_msg1.role = "user"
        mock_msg1.content = "Hello"
        mock_msg1.to_dict.return_value = {
            "id": "msg1",
            "role": "user",
            "content": "Hello"
        }

        mock_msg2 = Mock()
        mock_msg2.id = "msg2"
        mock_msg2.role = "assistant"
        mock_msg2.content = "Hi there"
        mock_msg2.to_dict.return_value = {
            "id": "msg2",
            "role": "assistant",
            "content": "Hi there"
        }

        with patch('app.api.history.db') as mock_db:
            mock_db.session.query.return_value.get.return_value = mock_conv
            mock_db.session.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [
                mock_msg1, mock_msg2
            ]

            with app.test_request_context():
                from app.api.history import get_conversation_messages
                response = get_conversation_messages("conv1")

                assert response[1] == 200
                data = response[0].get_json()
                assert len(data["messages"]) == 2
