"""
知识库 API 测试

测试知识库管理相关的 API 端点
"""
import pytest
from unittest.mock import Mock, patch

from app import create_app
from app.api.knowledge import add_document, search_documents, delete_document, get_documents


class TestAddDocument:
    """测试添加文档 API"""

    @patch('app.api.knowledge.RAGService')
    def test_add_document_success(self, mock_rag_cls):
        """成功添加文档"""
        app = create_app()
        mock_rag = Mock()
        mock_rag_cls.return_value = mock_rag

        with app.test_request_context(
            json={"doc_id": "test1", "content": "Test content"}
        ):
            response = add_document()

            assert response[1] == 201
            data = response[0].get_json()
            assert data["doc_id"] == "test1"
            assert "message" in data
            mock_rag.add_document.assert_called_once()

    @patch('app.api.knowledge.RAGService')
    def test_add_document_missing_fields(self, mock_rag_cls):
        """缺少必需字段"""
        app = create_app()

        with app.test_request_context(json={"doc_id": "test1"}):
            response = add_document()
            assert response[1] == 400

    @patch('app.api.knowledge.RAGService')
    def test_add_document_with_metadata(self, mock_rag_cls):
        """添加带元数据的文档"""
        app = create_app()
        mock_rag = Mock()
        mock_rag_cls.return_value = mock_rag

        with app.test_request_context(
            json={
                "doc_id": "test1",
                "content": "Test content",
                "metadata": {"source": "test", "category": "tech"}
            }
        ):
            response = add_document()

            assert response[1] == 201
            mock_rag.add_document.assert_called_once()


class TestSearchDocuments:
    """测试搜索文档 API"""

    @patch('app.api.knowledge.RAGService')
    def test_search_documents_success(self, mock_rag_cls):
        """成功搜索文档"""
        app = create_app()
        mock_rag = Mock()
        mock_rag.retrieve.return_value = [
            {"document": "Doc 1", "metadata": {}, "distance": 0.1},
            {"document": "Doc 2", "metadata": {}, "distance": 0.2}
        ]
        mock_rag_cls.return_value = mock_rag

        with app.test_request_context(
            json={"query": "test query", "n_results": 5}
        ):
            response = search_documents()

            assert response[1] == 200
            data = response[0].get_json()
            assert data["count"] == 2
            assert "results" in data

    @patch('app.api.knowledge.RAGService')
    def test_search_documents_missing_query(self, mock_rag_cls):
        """缺少查询参数"""
        app = create_app()

        with app.test_request_context(json={}):
            response = search_documents()
            assert response[1] == 400


class TestDeleteDocument:
    """测试删除文档 API"""

    @patch('app.api.knowledge.RAGService')
    def test_delete_document_success(self, mock_rag_cls):
        """成功删除文档"""
        app = create_app()
        mock_rag = Mock()
        mock_rag_cls.return_value = mock_rag

        with app.test_request_context(json={"doc_id": "test1"}):
            response = delete_document()

            assert response[1] == 200
            data = response[0].get_json()
            assert data["doc_id"] == "test1"
            mock_rag.delete_document.assert_called_once()

    @patch('app.api.knowledge.RAGService')
    def test_delete_document_missing_id(self, mock_rag_cls):
        """缺少文档 ID"""
        app = create_app()

        with app.test_request_context(json={}):
            response = delete_document()
            assert response[1] == 400


class TestGetDocuments:
    """测试获取文档列表 API"""

    @patch('app.api.knowledge.RAGService')
    def test_get_documents_success(self, mock_rag_cls):
        """成功获取文档列表"""
        app = create_app()
        mock_rag = Mock()
        mock_rag.retrieve.return_value = [
            {"document": "Doc 1", "metadata": {}, "distance": 0.1}
        ]
        mock_rag_cls.return_value = mock_rag

        with app.test_request_context(query_string="query=test&limit=10"):
            response = get_documents()

            assert response[1] == 200
            data = response[0].get_json()
            assert "results" in data
            assert data["count"] == 1

    @patch('app.api.knowledge.RAGService')
    def test_get_documents_missing_query(self, mock_rag_cls):
        """缺少查询参数"""
        app = create_app()

        with app.test_request_context(query_string="limit=10"):
            response = get_documents()
            assert response[1] == 400
