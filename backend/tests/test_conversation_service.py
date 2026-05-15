"""
对话服务测试

测试对话核心功能服务
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.conversation_service import ConversationService


class TestConversationServiceInit:
    """测试对话服务初始化"""

    @patch('app.services.conversation_service.get_llm_service')
    def test_init_default(self, mock_get_service):
        """使用默认参数初始化"""
        mock_llm = Mock()
        mock_get_service.return_value = mock_llm

        service = ConversationService()

        assert service.llm_service is not None

    @patch('app.services.conversation_service.get_llm_service')
    def test_init_with_provider(self, mock_get_service):
        """使用指定提供商初始化"""
        mock_llm = Mock()
        mock_get_service.return_value = mock_llm

        service = ConversationService(provider_type="openai")

        mock_get_service.assert_called_once()


class TestConversationServiceChat:
    """测试对话功能"""

    @patch('app.services.conversation_service.get_llm_service')
    def test_chat_success(self, mock_get_service):
        """成功进行对话"""
        mock_llm = Mock()
        mock_llm.chat.return_value = {
            "content": "Hello! How can I help you?",
            "model": "gpt-4"
        }
        mock_get_service.return_value = mock_llm

        service = ConversationService()
        response = service.chat([{"role": "user", "content": "Hi"}], "gpt-4")

        assert response["content"] == "Hello! How can I help you?"
        mock_llm.chat.assert_called_once()

    @patch('app.services.conversation_service.get_llm_service')
    def test_chat_with_system_message(self, mock_get_service):
        """带系统消息的对话"""
        mock_llm = Mock()
        mock_llm.chat.return_value = {"content": "Response"}
        mock_get_service.return_value = mock_llm

        service = ConversationService()
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hi"}
        ]
        response = service.chat(messages, "gpt-4")

        assert response["content"] == "Response"

    @patch('app.services.conversation_service.get_llm_service')
    def test_chat_with_parameters(self, mock_get_service):
        """带参数的对话"""
        mock_llm = Mock()
        mock_llm.chat.return_value = {"content": "Response"}
        mock_get_service.return_value = mock_llm

        service = ConversationService()
        response = service.chat(
            [{"role": "user", "content": "Hi"}],
            "gpt-4",
            temperature=0.7,
            max_tokens=1000
        )

        mock_llm.chat.assert_called_once()
        call_kwargs = mock_llm.chat.call_args[1]
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 1000


class TestConversationServiceStreamChat:
    """测试流式对话"""

    @patch('app.services.conversation_service.get_llm_service')
    def test_stream_chat(self, mock_get_service):
        """流式对话"""
        mock_llm = Mock()
        mock_llm.stream_chat.return_value = iter([
            {"content": "Hello"},
            {"content": " world"},
            {"content": "!"}
        ])
        mock_get_service.return_value = mock_llm

        service = ConversationService()
        chunks = list(service.stream_chat(
            [{"role": "user", "content": "Hi"}],
            "gpt-4"
        ))

        assert len(chunks) == 3
        assert chunks[0]["content"] == "Hello"


class TestConversationServiceWithContext:
    """测试带上下文的对话"""

    @patch('app.services.conversation_service.get_llm_service')
    def test_chat_with_history(self, mock_get_service):
        """带历史记录的对话"""
        mock_llm = Mock()
        mock_llm.chat.return_value = {"content": "Response to history"}
        mock_get_service.return_value = mock_llm

        service = ConversationService()
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"}
        ]
        messages = history + [{"role": "user", "content": "How are you?"}]

        response = service.chat(messages, "gpt-4")

        assert response["content"] == "Response to history"
