"""
模型管理 API 测试

测试模型列表和模型管理相关的 API 端点
"""
import pytest
from unittest.mock import Mock, patch

from app import create_app
from app.api.models import get_models


class TestGetModels:
    """测试获取模型列表 API"""

    @patch('app.api.models.get_llm_service')
    def test_get_models_openai(self, mock_get_service):
        """获取 OpenAI 模型列表"""
        app = create_app()
        mock_provider = Mock()
        mock_provider.list_models.return_value = ["gpt-4", "gpt-3.5-turbo"]
        mock_get_service.return_value = mock_provider

        with app.app_context():
            response = get_models("openai")

            assert response[1] == 200
            data = response[0].get_json()
            assert "models" in data
            assert "gpt-4" in data["models"]
            assert "gpt-3.5-turbo" in data["models"]

    @patch('app.api.models.get_llm_service')
    def test_get_models_anthropic(self, mock_get_service):
        """获取 Anthropic 模型列表"""
        app = create_app()
        mock_provider = Mock()
        mock_provider.list_models.return_value = [
            "claude-3-sonnet",
            "claude-3-opus"
        ]
        mock_get_service.return_value = mock_provider

        with app.app_context():
            response = get_models("anthropic")

            assert response[1] == 200
            data = response[0].get_json()
            assert "claude-3-sonnet" in data["models"]

    @patch('app.api.models.get_llm_service')
    def test_get_models_qwen(self, mock_get_service):
        """获取通义千问模型列表"""
        app = create_app()
        mock_provider = Mock()
        mock_provider.list_models.return_value = ["qwen-turbo", "qwen-plus"]
        mock_get_service.return_value = mock_provider

        with app.app_context():
            response = get_models("qwen")

            assert response[1] == 200
            data = response[0].get_json()
            assert "qwen-turbo" in data["models"]

    @patch('app.api.models.get_llm_service')
    def test_get_models_invalid_provider(self, mock_get_service):
        """无效提供商返回错误"""
        app = create_app()
        mock_get_service.side_effect = ValueError("Invalid provider type")

        with app.app_context():
            response = get_models("invalid")

            assert response[1] == 400
            data = response[0].get_json()
            assert "error" in data

    @patch('app.api.models.get_llm_service')
    def test_get_models_service_error(self, mock_get_service):
        """服务层错误传播"""
        app = create_app()
        mock_provider = Mock()
        mock_provider.list_models.side_effect = Exception("API error")
        mock_get_service.return_value = mock_provider

        with app.app_context():
            response = get_models("openai")

            assert response[1] == 500
            data = response[0].get_json()
            assert "error" in data
