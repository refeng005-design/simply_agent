"""
RAG 增强对话测试

测试 RAG 集成到对话流程的功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app import create_app
from app.api.chat import chat


class TestChatWithRAG:
    """测试 RAG 增强对话"""

    @patch('app.api.chat.RAGService')
    @patch('app.api.chat.ConversationService')
    def test_chat_with_rag_enabled(self, mock_conv_cls, mock_rag_cls):
        """启用 RAG 的对话"""
        app = create_app()

        # Mock RAG service
        mock_rag = Mock()
        mock_rag.generate_prompt.return_value = "Context: test context\nQuestion: Hi"
        mock_rag_cls.return_value = mock_rag

        # Mock conversation service
        mock_conv = Mock()
        mock_conv.chat.return_value = {"content": "Test response", "model": "gpt-4"}
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4",
                "use_rag": True
            }
        ):
            response = chat()

            assert response[1] == 200
            # 验证 RAG 服务被调用
            mock_rag.generate_prompt.assert_called_once_with("Hi", n_results=3)

    @patch('app.api.chat.RAGService')
    @patch('app.api.chat.ConversationService')
    def test_chat_with_rag_custom_n_results(self, mock_conv_cls, mock_rag_cls):
        """自定义 RAG 检索数量的对话"""
        app = create_app()

        mock_rag = Mock()
        mock_rag.generate_prompt.return_value = "Context: test\nQuestion: Hi"
        mock_rag_cls.return_value = mock_rag

        mock_conv = Mock()
        mock_conv.chat.return_value = {"content": "Response", "model": "gpt-4"}
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4",
                "use_rag": True,
                "rag_n_results": 5
            }
        ):
            response = chat()

            assert response[1] == 200
            mock_rag.generate_prompt.assert_called_once_with("Hi", n_results=5)

    @patch('app.api.chat.RAGService')
    @patch('app.api.chat.ConversationService')
    def test_chat_without_rag(self, mock_conv_cls, mock_rag_cls):
        """不启用 RAG 的对话"""
        app = create_app()

        mock_conv = Mock()
        mock_conv.chat.return_value = {"content": "Direct response", "model": "gpt-4"}
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4"
            }
        ):
            response = chat()

            assert response[1] == 200
            # RAG 服务不应该被调用
            mock_rag_cls.assert_not_called()

    @patch('app.api.chat.RAGService')
    @patch('app.api.chat.ConversationService')
    def test_chat_with_rag_streaming(self, mock_conv_cls, mock_rag_cls):
        """RAG 增强的流式对话"""
        app = create_app()

        mock_rag = Mock()
        mock_rag.generate_prompt.return_value = "Context: test\nQuestion: Hi"
        mock_rag_cls.return_value = mock_rag

        mock_conv = Mock()
        mock_conv.stream_chat.return_value = iter([
            {"content": "Hello"},
            {"content": " world"}
        ])
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4",
                "use_rag": True
            }
        ):
            from app.api.chat import stream_chat
            response = stream_chat()

            assert response.status_code == 200
            assert "text/event-stream" in response.content_type
            mock_rag.generate_prompt.assert_called_once()

    @patch('app.api.chat.RAGService')
    @patch('app.api.chat.ConversationService')
    def test_chat_with_rag_error_handling(self, mock_conv_cls, mock_rag_cls):
        """RAG 服务出错时的处理"""
        app = create_app()

        mock_rag = Mock()
        mock_rag.generate_prompt.side_effect = Exception("RAG error")
        mock_rag_cls.return_value = mock_rag

        mock_conv = Mock()
        mock_conv.chat.return_value = {"content": "Fallback response", "model": "gpt-4"}
        mock_conv_cls.return_value = mock_conv

        with app.test_request_context(
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "model": "gpt-4",
                "use_rag": True
            }
        ):
            response = chat()

            # 应该降级到普通对话
            assert response[1] == 200
            mock_conv.chat.assert_called_once()
