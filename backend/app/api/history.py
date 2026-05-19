"""
对话历史 API

提供对话历史记录的查询、删除等操作
"""
from flask import jsonify, request

from app.models import Conversation, Message
from app.extensions import db


def get_conversations():
    """
    获取对话列表

    Query Parameters:
        limit (int): 返回数量限制
        offset (int): 偏移量

    Returns:
        JSON 响应和状态码
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        conversations = db.session.query(Conversation).order_by(
            Conversation.created_at.desc()
        ).limit(limit).offset(offset).all()

        return jsonify({
            "conversations": [c.to_dict() for c in conversations],
            "count": len(conversations)
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to get conversations: {str(e)}"
        }), 500


def get_conversation(conversation_id: str):
    """
    获取单个对话详情

    Args:
        conversation_id: 对话 ID

    Returns:
        JSON 响应和状态码
    """
    try:
        conversation = db.session.query(Conversation).get(conversation_id)

        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404

        return jsonify(conversation.to_dict()), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to get conversation: {str(e)}"
        }), 500


def delete_conversation(conversation_id: str):
    """
    删除对话

    Args:
        conversation_id: 对话 ID

    Returns:
        JSON 响应和状态码
    """
    try:
        conversation = db.session.query(Conversation).get(conversation_id)

        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404

        # 先删除关联的消息
        db.session.query(Message).filter_by(conversation_id=conversation_id).delete()

        # 再删除对话
        db.session.delete(conversation)
        db.session.commit()

        return "", 204

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Failed to delete conversation: {str(e)}"
        }), 500


def get_conversation_messages(conversation_id: str):
    """
    获取对话的消息列表

    Args:
        conversation_id: 对话 ID

    Query Parameters:
        limit (int): 返回数量限制
        offset (int): 偏移量

    Returns:
        JSON 响应和状态码
    """
    try:
        conversation = db.session.query(Conversation).get(conversation_id)

        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404

        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        messages = db.session.query(Message).filter_by(
            conversation_id=conversation_id
        ).order_by(
            Message.created_at.asc()
        ).limit(limit).offset(offset).all()

        return jsonify({
            "messages": [m.to_dict() for m in messages],
            "count": len(messages)
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to get messages: {str(e)}"
        }), 500


def clear_all_history():
    """
    清空所有对话历史

    Returns:
        JSON 响应和状态码
    """
    try:
        # 删除所有消息
        db.session.query(Message).delete()
        # 删除所有对话
        db.session.query(Conversation).delete()
        db.session.commit()

        return jsonify({"message": "All history cleared"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Failed to clear history: {str(e)}"
        }), 500


def toggle_conversation_memory(conversation_id: str, enabled: bool):
    """
    切换对话记忆开关

    Args:
        conversation_id: 对话 ID
        enabled: 记忆是否启用

    Returns:
        JSON 响应和状态码
    """
    try:
        conversation = db.session.query(Conversation).get(conversation_id)

        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404

        conversation.memory_enabled = enabled
        db.session.commit()

        return jsonify({
            "id": conversation.id,
            "memory_enabled": conversation.memory_enabled
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Failed to toggle memory: {str(e)}"
        }), 500
