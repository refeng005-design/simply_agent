"""
知识库管理 API

提供文档添加、检索、删除等知识库管理功能
"""
from flask import jsonify, request

from app.services.rag_service import RAGService


def add_document():
    """
    添加文档到知识库

    JSON Body:
        {
            "doc_id": str,
            "content": str,
            "metadata": dict (optional)
        }

    Returns:
        JSON 响应和状态码
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        doc_id = data.get("doc_id")
        content = data.get("content")
        metadata = data.get("metadata", {})

        if not doc_id or not content:
            return jsonify({
                "error": "doc_id and content are required"
            }), 400

        rag_service = RAGService()
        rag_service.add_document(doc_id, content, metadata)

        return jsonify({
            "message": "Document added successfully",
            "doc_id": doc_id
        }), 201

    except Exception as e:
        return jsonify({
            "error": f"Failed to add document: {str(e)}"
        }), 500


def search_documents():
    """
    搜索知识库文档

    JSON Body:
        {
            "query": str,
            "n_results": int (optional, default 5),
            "where": dict (optional)
        }

    Returns:
        JSON 响应和状态码
    """
    try:
        data = request.get_json()

        if not data or not data.get("query"):
            return jsonify({"error": "query is required"}), 400

        query = data["query"]
        n_results = data.get("n_results", 5)
        where = data.get("where")

        rag_service = RAGService()
        results = rag_service.retrieve(query, n_results=n_results, where=where)

        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Search failed: {str(e)}"
        }), 500


def delete_document():
    """
    从知识库删除文档

    JSON Body:
        {
            "doc_id": str
        }

    Returns:
        JSON 响应和状态码
    """
    try:
        data = request.get_json()

        if not data or not data.get("doc_id"):
            return jsonify({"error": "doc_id is required"}), 400

        doc_id = data["doc_id"]

        rag_service = RAGService()
        rag_service.delete_document(doc_id)

        return jsonify({
            "message": "Document deleted successfully",
            "doc_id": doc_id
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to delete document: {str(e)}"
        }), 500


def get_documents():
    """
    获取文档列表

    Query Args:
        query: 搜索查询
        limit: 返回数量限制

    Returns:
        JSON 响应和状态码
    """
    try:
        query = request.args.get("query", "")
        limit = int(request.args.get("limit", 10))

        if not query:
            return jsonify({
                "error": "query parameter is required"
            }), 400

        rag_service = RAGService()
        results = rag_service.retrieve(query, n_results=limit)

        return jsonify({
            "results": results,
            "count": len(results)
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to get documents: {str(e)}"
        }), 500
