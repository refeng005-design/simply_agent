"""
Prompt 构建器测试

测试 RAG Prompt 模板构建功能
"""
import pytest

from app.utils.prompt_builder import PromptBuilder


class TestPromptBuilderInit:
    """测试 Prompt 构建器初始化"""

    def test_init_default_template(self):
        """使用默认模板初始化"""
        builder = PromptBuilder()
        assert builder.template is not None

    def test_init_custom_template(self):
        """使用自定义模板初始化"""
        custom = "Context: {context}\nQuestion: {question}"
        builder = PromptBuilder(template=custom)
        assert builder.template == custom


class TestBuildRAGPrompt:
    """测试构建 RAG 提示词"""

    def test_build_with_context(self):
        """构建带上下文的提示词"""
        builder = PromptBuilder()
        context = ["Doc 1 content", "Doc 2 content"]
        prompt = builder.build_rag(context, "What is AI?")

        assert "Doc 1 content" in prompt
        assert "Doc 2 content" in prompt
        assert "What is AI?" in prompt

    def test_build_with_empty_context(self):
        """构建空上下文的提示词"""
        builder = PromptBuilder()
        prompt = builder.build_rag([], "What is AI?")

        assert "What is AI?" in prompt
        # 空上下文时应该有提示信息
        assert "no context" in prompt.lower()

    def test_build_with_single_context(self):
        """构建单个上下文的提示词"""
        builder = PromptBuilder()
        context = ["Only document"]
        prompt = builder.build_rag(context, "Question?")

        assert "Only document" in prompt
        assert "Question?" in prompt

    def test_escape_special_chars(self):
        """正确处理特殊字符"""
        builder = PromptBuilder()
        context = ["Doc with {brace} and {{double}}"]
        prompt = builder.build_rag(context, "Question?")

        # 应该包含原文内容
        assert "Doc with" in prompt


class TestBuildSystemPrompt:
    """测试构建系统提示词"""

    def test_build_system_prompt_default(self):
        """构建默认系统提示词"""
        builder = PromptBuilder()
        prompt = builder.build_system_prompt()

        assert "assistant" in prompt.lower()
        assert "helpful" in prompt.lower()

    def test_build_system_prompt_custom_role(self):
        """构建自定义角色的系统提示词"""
        builder = PromptBuilder()
        prompt = builder.build_system_prompt(role="expert")

        assert "expert" in prompt.lower()


class TestBuildChatPrompt:
    """测试构建对话提示词"""

    def test_build_chat_prompt(self):
        """构建对话提示词"""
        builder = PromptBuilder()
        messages = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "How are you?"}
        ]
        prompt = builder.build_chat_prompt(messages)

        assert "Hi" in prompt
        assert "Hello" in prompt
        assert "How are you?" in prompt

    def test_build_chat_prompt_empty(self):
        """构建空对话提示词"""
        builder = PromptBuilder()
        prompt = builder.build_chat_prompt([])

        # 空对话应该返回空或提示
        assert prompt == "" or "no messages" in prompt.lower()


class TestFormatContext:
    """测试上下文格式化"""

    def test_format_context_list(self):
        """格式化上下文列表"""
        builder = PromptBuilder()
        context = ["Doc 1", "Doc 2", "Doc 3"]
        formatted = builder._format_context(context)

        # 应该有编号
        assert "1." in formatted or "[1]" in formatted
        assert "Doc 1" in formatted

    def test_format_context_with_metadata(self):
        """格式化带元数据的上下文"""
        builder = PromptBuilder()
        context = [
            {"text": "Doc 1", "source": "wiki"},
            {"text": "Doc 2", "source": "news"}
        ]
        formatted = builder._format_context(context)

        assert "Doc 1" in formatted
        assert "wiki" in formatted
