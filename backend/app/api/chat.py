"""
对话 API

提供对话相关的 API 端点
"""
from flask import jsonify, request
import uuid

from app.services.conversation_service import ConversationService
from app.services.rag_service import RAGService
from app.models import Conversation, Message
from app.extensions import db


def _get_or_create_conversation(conversation_id, model_name):
    """获取或创建对话"""
    if conversation_id:
        conversation = db.session.query(Conversation).get(conversation_id)
        if conversation:
            return conversation

    # 创建新对话
    conversation = Conversation(
        title='新对话',
        model_name=model_name,
        memory_enabled=True
    )
    db.session.add(conversation)
    db.session.commit()
    return conversation


def _save_messages(conversation_id, messages):
    """保存消息到数据库"""
    for msg in messages:
        message = Message(
            conversation_id=conversation_id,
            role=msg.get('role', 'user'),
            content=msg.get('content', '')
        )
        db.session.add(message)
    db.session.commit()


def chat():
    """
    对话 API（非流式）

    JSON Body:
        {
            "messages": list[dict],  # 消息列表
            "model": str,            # 模型名称
            "temperature": float (optional),
            "max_tokens": int (optional),
            "provider": str (optional, default "openai"),
            "use_rag": bool (optional, default False),
            "rag_n_results": int (optional, default 3),
            "conversation_id": str (optional),
            "memory_enabled": bool (optional)
        }

    Returns:
        JSON 响应和状态码
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        messages = data.get("messages")
        model = data.get("model")

        if not messages:
            return jsonify({"error": "messages is required"}), 400

        if not model:
            return jsonify({"error": "model is required"}), 400

        provider = data.get("provider", "openai")
        use_rag = data.get("use_rag", False)
        conversation_id = data.get("conversation_id")

        # 获取或创建对话
        conversation = _get_or_create_conversation(conversation_id, model)
        conversation_id = conversation.id

        # 可选参数
        kwargs = {}
        if "temperature" in data:
            kwargs["temperature"] = data["temperature"]
        if "max_tokens" in data:
            kwargs["max_tokens"] = data["max_tokens"]

        # 记忆控制 - 如果提供了 conversation_id，检查记忆是否启用
        use_memory = data.get("memory_enabled", True)
        if conversation_id and use_memory and conversation.memory_enabled:
            # 加载历史消息
            history_messages = db.session.query(Message).filter_by(
                conversation_id=conversation_id
            ).order_by(Message.created_at.asc()).all()
            # 将历史消息添加到当前消息列表之前
            messages = [m.to_dict() for m in history_messages] + messages

        # 调用对话服务
        service = ConversationService(provider_type=provider)

        # RAG 增强
        if use_rag:
            try:
                rag_service = RAGService()
                rag_n_results = data.get("rag_n_results", 3)

                # 获取最后一条用户消息
                user_message = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_message = msg.get("content", "")
                        break

                # 使用 RAG 生成增强提示词
                if user_message:
                    enhanced_prompt = rag_service.generate_prompt(
                        user_message,
                        n_results=rag_n_results
                    )
                    # 替换最后一条用户消息为增强的提示词
                    messages = [
                        m for m in messages
                        if m.get("role") != "user" or m != messages[-1]
                    ] if messages and messages[-1].get("role") == "user" else messages
                    messages.append({"role": "user", "content": enhanced_prompt})
            except Exception as rag_error:
                # RAG 失败时降级到普通对话
                pass

        response = service.chat(messages, model, **kwargs)

        # 保存用户消息（只保存当前用户发送的消息）
        user_message = messages[-1] if messages and messages[-1].get("role") == "user" else None
        if user_message:
            msg = Message(
                conversation_id=conversation_id,
                role='user',
                content=user_message.get('content', '')
            )
            db.session.add(msg)

        # 保存AI响应
        assistant_message = Message(
            conversation_id=conversation_id,
            role='assistant',
            content=response.get("content", "")
        )
        db.session.add(assistant_message)
        db.session.commit()

        # 更新对话标题（使用第一条用户消息的前30个字符）
        if conversation.title == '新对话' or conversation.title == 'New Conversation':
            first_user_msg = messages[0] if messages and messages[0].get("role") == "user" else None
            if first_user_msg:
                content = first_user_msg.get('content', '')
                conversation.title = content[:30] + ('...' if len(content) > 30 else '')
                db.session.commit()

        return jsonify({
            "conversation_id": conversation_id,
            "content": response.get("content"),
            "model": response.get("model", model),
            "usage": response.get("usage")
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Chat failed: {str(e)}"
        }), 500


def stream_chat():
    """
    流式对话 API (SSE)

    JSON Body:
        {
            "messages": list[dict],
            "model": str,
            "temperature": float (optional),
            "max_tokens": int (optional),
            "provider": str (optional),
            "use_rag": bool (optional),
            "rag_n_results": int (optional),
            "conversation_id": str (optional),
            "memory_enabled": bool (optional)
        }

    Returns:
        Server-Sent Events 流
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        messages = data.get("messages")
        model = data.get("model")

        if not messages:
            return jsonify({"error": "messages is required"}), 400

        if not model:
            return jsonify({"error": "model is required"}), 400

        provider = data.get("provider", "openai")
        use_rag = data.get("use_rag", False)
        conversation_id = data.get("conversation_id")

        # 获取或创建对话
        conversation = _get_or_create_conversation(conversation_id, model)
        conversation_id = conversation.id

        # 可选参数
        kwargs = {}
        if "temperature" in data:
            kwargs["temperature"] = data["temperature"]
        if "max_tokens" in data:
            kwargs["max_tokens"] = data["max_tokens"]

        # 记忆控制
        use_memory = data.get("memory_enabled", True)
        if conversation_id and use_memory and conversation.memory_enabled:
            # 加载历史消息
            history_messages = db.session.query(Message).filter_by(
                conversation_id=conversation_id
            ).order_by(Message.created_at.asc()).all()
            # 将历史消息添加到当前消息列表之前
            messages = [m.to_dict() for m in history_messages] + messages

        # 调用流式对话服务
        service = ConversationService(provider_type=provider)

        # RAG 增强
        if use_rag:
            try:
                rag_service = RAGService()
                rag_n_results = data.get("rag_n_results", 3)

                # 获取最后一条用户消息
                user_message = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_message = msg.get("content", "")
                        break

                # 使用 RAG 生成增强提示词
                if user_message:
                    enhanced_prompt = rag_service.generate_prompt(
                        user_message,
                        n_results=rag_n_results
                    )
                    # 替换最后一条用户消息为增强的提示词
                    messages = [
                        m for m in messages
                        if m.get("role") != "user" or m != messages[-1]
                    ] if messages and messages[-1].get("role") == "user" else messages
                    messages.append({"role": "user", "content": enhanced_prompt})
            except Exception:
                # RAG 失败时使用原始消息
                pass

        # 保存用户消息
        user_message = messages[-1] if messages and messages[-1].get("role") == "user" else None
        if user_message:
            msg = Message(
                conversation_id=conversation_id,
                role='user',
                content=user_message.get('content', '')
            )
            db.session.add(msg)

            # 更新对话标题（使用第一条用户消息的前30个字符）
            if conversation.title == '新对话' or conversation.title == 'New Conversation':
                content = user_message.get('content', '')
                conversation.title = content[:30] + ('...' if len(content) > 30 else '')

        # 用于收集完整响应
        full_response = []

        def generate():
            """生成 SSE 流"""
            try:
                for chunk in service.stream_chat(messages, model, **kwargs):
                    content = chunk.get("content", "")
                    if content:
                        full_response.append(content)
                        yield f"data: {{\"content\": \"{content}\"}}\n\n"

                # 保存完整的AI响应
                if full_response:
                    assistant_message = Message(
                        conversation_id=conversation_id,
                        role='assistant',
                        content=''.join(full_response)
                    )
                    db.session.add(assistant_message)
                    db.session.commit()

                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

        from flask import Response
        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        return jsonify({
            "error": f"Stream chat failed: {str(e)}"
        }), 500
