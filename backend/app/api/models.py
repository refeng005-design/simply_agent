"""
模型管理 API

提供模型列表查询和管理功能
"""
import os
from flask import jsonify

from app.services.llm_service import get_llm_service


def get_models(provider_type: str):
    """
    获取指定提供商的可用模型列表

    Args:
        provider_type: 提供商类型（openai, anthropic, qwen）

    Returns:
        (response, status_code): Flask JSON 响应和状态码
    """
    try:
        # 从环境变量获取 API key，测试时使用默认值
        api_key = os.getenv(
            f"{provider_type.upper()}_API_KEY",
            "test-api-key"
        )

        # 获取 LLM 服务实例
        service = get_llm_service(
            provider_type=provider_type,
            api_key=api_key
        )

        # 获取模型列表
        models = service.list_models()

        return jsonify({
            "provider": provider_type,
            "models": models
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "error": f"Failed to get models: {str(e)}"
        }), 500
