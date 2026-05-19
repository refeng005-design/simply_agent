"""
清空历史功能测试

测试清空所有对话历史接口的各种场景
"""
import pytest
from unittest.mock import Mock, patch
from app import create_app


class TestHistoryClear:
    """测试清空历史功能"""

    def test_clear_all_history_success(self):
        """成功清空所有历史"""
        app = create_app()

        with patch('app.api.history.db') as mock_db:
            mock_msg_query = Mock()
            mock_msg_query.delete.return_value = 10
            mock_conv_query = Mock()
            mock_conv_query.delete.return_value = 5

            mock_db.session.query.side_effect = lambda model: mock_msg_query if model.__name__ == 'Message' else mock_conv_query

            with app.test_request_context():
                from app.api.history import clear_all_history
                response, status_code = clear_all_history()

                assert status_code == 200
                data = response.get_json()
                assert "message" in data
                mock_msg_query.delete.assert_called_once()
                mock_conv_query.delete.assert_called_once()
                mock_db.session.commit.assert_called_once()

    def test_clear_empty_history(self):
        """清空空历史记录"""
        app = create_app()

        with patch('app.api.history.db') as mock_db:
            mock_msg_query = Mock()
            mock_msg_query.delete.return_value = 0
            mock_conv_query = Mock()
            mock_conv_query.delete.return_value = 0

            mock_db.session.query.side_effect = lambda model: mock_msg_query if model.__name__ == 'Message' else mock_conv_query

            with app.test_request_context():
                from app.api.history import clear_all_history
                response, status_code = clear_all_history()

                assert status_code == 200
                data = response.get_json()
                assert "message" in data

    def test_clear_history_rollback_on_error(self):
        """清空失败时回滚事务"""
        app = create_app()

        with patch('app.api.history.db') as mock_db:
            mock_msg_query = Mock()
            mock_msg_query.delete.return_value = 10
            mock_conv_query = Mock()
            mock_conv_query.delete.return_value = 5

            mock_db.session.query.side_effect = lambda model: mock_msg_query if model.__name__ == 'Message' else mock_conv_query
            mock_db.session.commit.side_effect = Exception("DB connection lost")

            with app.test_request_context():
                from app.api.history import clear_all_history
                response, status_code = clear_all_history()

                assert status_code == 500
                data = response.get_json()
                assert "error" in data
                mock_db.session.rollback.assert_called_once()

    def test_clear_history_large_dataset(self):
        """清空大量历史记录"""
        app = create_app()

        with patch('app.api.history.db') as mock_db:
            mock_msg_query = Mock()
            mock_msg_query.delete.return_value = 10000
            mock_conv_query = Mock()
            mock_conv_query.delete.return_value = 500

            mock_db.session.query.side_effect = lambda model: mock_msg_query if model.__name__ == 'Message' else mock_conv_query

            with app.test_request_context():
                from app.api.history import clear_all_history
                response, status_code = clear_all_history()

                assert status_code == 200
                mock_db.session.commit.assert_called_once()
