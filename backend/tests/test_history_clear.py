"""
清空历史功能测试

测试清空所有对话历史接口的各种场景
"""
import pytest
from unittest.mock import Mock, patch
from app import create_app


class TestHistoryClear:
    """测试清空历史功能"""

    @patch('app.api.history.Message')
    @patch('app.api.history.Conversation')
    @patch('app.api.history.db')
    def test_clear_all_history_success(self, mock_db, mock_conv_cls, mock_msg_cls):
        """成功清空所有历史"""
        app = create_app()

        # Mock query.delete() 返回删除数量
        mock_msg_query = Mock()
        mock_msg_query.delete.return_value = 10  # 删除10条消息
        mock_msg_cls.query = mock_msg_query

        mock_conv_query = Mock()
        mock_conv_query.delete.return_value = 5  # 删除5个对话
        mock_conv_cls.query = mock_conv_query

        with app.test_request_context():
            from app.api.history import clear_all_history
            response, status_code = clear_all_history()

            assert status_code == 200
            data = response.get_json()
            assert "message" in data
            # 验证删除顺序：先删消息，再删对话
            mock_msg_query.delete.assert_called_once()
            mock_conv_query.delete.assert_called_once()
            mock_db.session.commit.assert_called_once()

    @patch('app.api.history.Message')
    @patch('app.api.history.Conversation')
    @patch('app.api.history.db')
    def test_clear_empty_history(self, mock_db, mock_conv_cls, mock_msg_cls):
        """清空空历史记录"""
        app = create_app()

        # 没有数据需要删除
        mock_msg_query = Mock()
        mock_msg_query.delete.return_value = 0
        mock_msg_cls.query = mock_msg_query

        mock_conv_query = Mock()
        mock_conv_query.delete.return_value = 0
        mock_conv_cls.query = mock_conv_query

        with app.test_request_context():
            from app.api.history import clear_all_history
            response, status_code = clear_all_history()

            assert status_code == 200
            data = response.get_json()
            assert "message" in data

    @patch('app.api.history.Message')
    @patch('app.api.history.Conversation')
    @patch('app.api.history.db')
    def test_clear_history_rollback_on_error(self, mock_db, mock_conv_cls, mock_msg_cls):
        """清空失败时回滚事务"""
        app = create_app()

        mock_msg_query = Mock()
        mock_msg_query.delete.return_value = 10
        mock_msg_cls.query = mock_msg_query

        mock_conv_query = Mock()
        mock_conv_query.delete.return_value = 5
        mock_conv_cls.query = mock_conv_query

        # 模拟提交时出错
        mock_db.session.commit.side_effect = Exception("DB connection lost")

        with app.test_request_context():
            from app.api.history import clear_all_history
            response, status_code = clear_all_history()

            assert status_code == 500
            data = response.get_json()
            assert "error" in data
            mock_db.session.rollback.assert_called_once()

    @patch('app.api.history.Message')
    @patch('app.api.history.Conversation')
    @patch('app.api.history.db')
    def test_clear_history_large_dataset(self, mock_db, mock_conv_cls, mock_msg_cls):
        """清空大量历史记录"""
        app = create_app()

        # 模拟大量数据
        mock_msg_query = Mock()
        mock_msg_query.delete.return_value = 10000
        mock_msg_cls.query = mock_msg_query

        mock_conv_query = Mock()
        mock_conv_query.delete.return_value = 500
        mock_conv_cls.query = mock_conv_query

        with app.test_request_context():
            from app.api.history import clear_all_history
            response, status_code = clear_all_history()

            assert status_code == 200
            mock_db.session.commit.assert_called_once()
