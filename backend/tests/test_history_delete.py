"""
对话删除功能测试

测试对话删除接口的各种场景
"""
import pytest
from unittest.mock import Mock, patch, call
from app import create_app


class TestHistoryDelete:
    """测试对话删除功能"""

    @patch('app.api.history.Conversation')
    @patch('app.api.history.db')
    def test_delete_conversation_success(self, mock_db, mock_conv_cls):
        """成功删除对话"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv-123"
        mock_conv.title = "Test Chat"
        mock_conv_cls.query.get.return_value = mock_conv

        with app.test_request_context():
            from app.api.history import delete_conversation
            response, status_code = delete_conversation("conv-123")

            assert status_code == 204
            assert response == ""
            mock_db.session.delete.assert_called_once_with(mock_conv)
            mock_db.session.commit.assert_called_once()

    @patch('app.api.history.Conversation')
    def test_delete_conversation_not_found(self, mock_conv_cls):
        """删除不存在的对话返回404"""
        app = create_app()

        mock_conv_cls.query.get.return_value = None

        with app.test_request_context():
            from app.api.history import delete_conversation
            response, status_code = delete_conversation("nonexistent")

            assert status_code == 404
            data = response.get_json()
            assert "error" in data
            assert "not found" in data["error"].lower()

    @patch('app.api.history.Conversation')
    @patch('app.api.history.db')
    def test_delete_conversation_rollback_on_error(self, mock_db, mock_conv_cls):
        """删除失败时回滚事务"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv-123"
        mock_conv_cls.query.get.return_value = mock_conv

        # 模拟数据库错误
        mock_db.session.commit.side_effect = Exception("DB Error")

        with app.test_request_context():
            from app.api.history import delete_conversation
            response, status_code = delete_conversation("conv-123")

            assert status_code == 500
            mock_db.session.rollback.assert_called_once()

    @patch('app.api.history.Conversation')
    @patch('app.api.history.db')
    def test_delete_conversation_with_messages(self, mock_db, mock_conv_cls):
        """删除包含消息的对话（级联删除）"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.id = "conv-123"
        mock_conv.title = "Chat with messages"

        # 模拟对话有多条消息
        mock_msg1 = Mock()
        mock_msg1.id = "msg-1"
        mock_msg2 = Mock()
        mock_msg2.id = "msg-2"
        mock_conv._messages = [mock_msg1, mock_msg2]

        mock_conv_cls.query.get.return_value = mock_conv

        with app.test_request_context():
            from app.api.history import delete_conversation
            response, status_code = delete_conversation("conv-123")

            assert status_code == 204
            mock_db.session.delete.assert_called_once_with(mock_conv)
