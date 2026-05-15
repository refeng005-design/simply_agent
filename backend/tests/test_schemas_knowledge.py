"""
知识库 Schema 测试

测试知识库相关的请求和响应 Schema
"""
import pytest
from marshmallow import ValidationError

from app.schemas.knowledge import (
    AddDocumentRequest,
    AddDocumentResponse,
    SearchDocumentsRequest,
    SearchDocumentsResponse,
    DeleteDocumentRequest
)


class TestAddDocumentRequest:
    """测试添加文档请求 Schema"""

    def test_valid_request(self):
        """有效的请求"""
        data = {
            "doc_id": "test1",
            "content": "This is a test document",
            "metadata": {"source": "test"}
        }
        schema = AddDocumentRequest()
        result = schema.load(data)

        assert result["doc_id"] == "test1"
        assert result["content"] == "This is a test document"
        assert result["metadata"]["source"] == "test"

    def test_minimal_request(self):
        """最小请求"""
        data = {
            "doc_id": "test1",
            "content": "Content"
        }
        schema = AddDocumentRequest()
        result = schema.load(data)

        assert result["doc_id"] == "test1"
        assert result["content"] == "Content"

    def test_missing_doc_id(self):
        """缺少 doc_id"""
        data = {"content": "Content"}
        schema = AddDocumentRequest()

        with pytest.raises(ValidationError):
            schema.load(data)

    def test_missing_content(self):
        """缺少 content"""
        data = {"doc_id": "test1"}
        schema = AddDocumentRequest()

        with pytest.raises(ValidationError):
            schema.load(data)


class TestAddDocumentResponse:
    """测试添加文档响应 Schema"""

    def test_dump_response(self):
        """导出响应"""
        data = {
            "message": "Document added",
            "doc_id": "test1"
        }
        schema = AddDocumentResponse()
        result = schema.dump(data)

        assert result["message"] == "Document added"
        assert result["doc_id"] == "test1"


class TestSearchDocumentsRequest:
    """测试搜索文档请求 Schema"""

    def test_valid_request(self):
        """有效的请求"""
        data = {
            "query": "test query",
            "n_results": 5
        }
        schema = SearchDocumentsRequest()
        result = schema.load(data)

        assert result["query"] == "test query"
        assert result["n_results"] == 5

    def test_minimal_request(self):
        """最小请求"""
        data = {"query": "test"}
        schema = SearchDocumentsRequest()
        result = schema.load(data)

        assert result["query"] == "test"
        assert result["n_results"] == 5  # 默认值

    def test_missing_query(self):
        """缺少 query"""
        data = {}
        schema = SearchDocumentsRequest()

        with pytest.raises(ValidationError):
            schema.load(data)

    def test_with_where_filter(self):
        """带过滤条件"""
        data = {
            "query": "test",
            "where": {"category": "tech"}
        }
        schema = SearchDocumentsRequest()
        result = schema.load(data)

        assert result["where"]["category"] == "tech"


class TestSearchDocumentsResponse:
    """测试搜索文档响应 Schema"""

    def test_dump_response(self):
        """导出响应"""
        data = {
            "query": "test",
            "results": [
                {"document": "Doc 1", "metadata": {}, "distance": 0.1}
            ],
            "count": 1
        }
        schema = SearchDocumentsResponse()
        result = schema.dump(data)

        assert result["query"] == "test"
        assert result["count"] == 1
        assert len(result["results"]) == 1


class TestDeleteDocumentRequest:
    """测试删除文档请求 Schema"""

    def test_valid_request(self):
        """有效的请求"""
        data = {"doc_id": "test1"}
        schema = DeleteDocumentRequest()
        result = schema.load(data)

        assert result["doc_id"] == "test1"

    def test_missing_doc_id(self):
        """缺少 doc_id"""
        data = {}
        schema = DeleteDocumentRequest()

        with pytest.raises(ValidationError):
            schema.load(data)
