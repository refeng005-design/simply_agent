"""
LLMService 基类测试

测试 LLMService 抽象基类的接口定义
"""
import pytest
from abc import ABC, abstractmethod

from app.services.llm_service import LLMService


class TestLLMServiceAbstractBase:
    """测试 LLMService 是抽象基类"""

    def test_cannot_instantiate_base_class(self):
        """不能直接实例化 LLMService 基类"""
        with pytest.raises(TypeError) as exc_info:
            LLMService(api_key="test-key")
        assert "abstract" in str(exc_info.value).lower()


class TestLLMServiceInterface:
    """测试 LLMService 定义的接口"""

    def test_has_chat_method(self):
        """应有 chat 抽象方法"""
        assert hasattr(LLMService, 'chat')
        assert getattr(LLMService, 'chat').__isabstractmethod__

    def test_has_stream_chat_method(self):
        """应有 stream_chat 抽象方法"""
        assert hasattr(LLMService, 'stream_chat')
        assert getattr(LLMService, 'stream_chat').__isabstractmethod__

    def test_has_list_models_method(self):
        """应有 list_models 抽象方法"""
        assert hasattr(LLMService, 'list_models')
        assert getattr(LLMService, 'list_models').__isabstractmethod__

    def test_has_init_api_key(self):
        """构造函数应接受 api_key 参数"""
        import inspect
        sig = inspect.signature(LLMService.__init__)
        assert 'api_key' in sig.parameters


class TestLLMServiceConcreteImplementation:
    """测试具体实现必须实现所有抽象方法"""

    def test_minimal_implementation(self):
        """最小实现应能正常工作"""
        class MinimalLLM(LLMService):
            def chat(self, messages, model, **kwargs):
                return [{"content": "response"}]

            def stream_chat(self, messages, model, **kwargs):
                yield {"content": "chunk"}

            def list_models(self):
                return ["model1", "model2"]

        # 应该能实例化
        service = MinimalLLM(api_key="test-key")
        assert service.api_key == "test-key"

        # 应该能调用方法
        result = service.chat([], "model")
        assert result == [{"content": "response"}]

        chunks = list(service.stream_chat([], "model"))
        assert chunks == [{"content": "chunk"}]

        models = service.list_models()
        assert models == ["model1", "model2"]

    def test_missing_chat_raises_error(self):
        """缺少 chat 方法应报错"""
        class IncompleteLLM(LLMService):
            def stream_chat(self, messages, model, **kwargs):
                yield {}

            def list_models(self):
                return []

        with pytest.raises(TypeError) as exc_info:
            IncompleteLLM(api_key="test")
        assert "chat" in str(exc_info.value).lower()

    def test_missing_stream_chat_raises_error(self):
        """缺少 stream_chat 方法应报错"""
        class IncompleteLLM(LLMService):
            def chat(self, messages, model, **kwargs):
                return {}

            def list_models(self):
                return []

        with pytest.raises(TypeError) as exc_info:
            IncompleteLLM(api_key="test")
        assert "stream_chat" in str(exc_info.value).lower()

    def test_missing_list_models_raises_error(self):
        """缺少 list_models 方法应报错"""
        class IncompleteLLM(LLMService):
            def chat(self, messages, model, **kwargs):
                return {}

            def stream_chat(self, messages, model, **kwargs):
                yield {}

        with pytest.raises(TypeError) as exc_info:
            IncompleteLLM(api_key="test")
        assert "list_models" in str(exc_info.value).lower()
