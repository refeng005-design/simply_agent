"""
API 蓝图模块

提供统一的API接口、错误处理和限流
"""
from flask import Blueprint, jsonify, request

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0'
    }), 200


# 导入聊天 API 路由
from .chat import chat, stream_chat

# 注册聊天路由
api_bp.add_url_rule('/chat', 'chat', chat, methods=['POST'])
api_bp.add_url_rule('/chat/stream', 'stream_chat', stream_chat, methods=['GET', 'POST'])

# 导入历史 API 路由
from .history import (
    get_conversations,
    get_conversation,
    delete_conversation,
    get_conversation_messages,
    clear_all_history,
    toggle_conversation_memory
)

# 注册历史路由
api_bp.add_url_rule('/conversations', 'get_conversations', get_conversations, methods=['GET'])
api_bp.add_url_rule('/conversations/<conversation_id>', 'get_conversation', get_conversation, methods=['GET'])
api_bp.add_url_rule('/conversations/<conversation_id>', 'delete_conversation', delete_conversation, methods=['DELETE'])
api_bp.add_url_rule('/conversations/<conversation_id>/messages', 'get_conversation_messages', get_conversation_messages, methods=['GET'])
api_bp.add_url_rule('/conversations/clear', 'clear_all_history', clear_all_history, methods=['POST'])
api_bp.add_url_rule('/conversations/<conversation_id>/memory', 'toggle_conversation_memory', toggle_conversation_memory, methods=['PUT'])


def register_blueprints(app):
    """
    注册所有蓝图和中间件

    Args:
        app: Flask应用实例
    """
    from app.api.errors import init_error_handlers
    from app.api.rate_limit import init_rate_limiting

    # 初始化错误处理
    init_error_handlers(app)

    # 初始化限流
    init_rate_limiting(app)

    # 注册API蓝图
    app.register_blueprint(api_bp)

    return app
