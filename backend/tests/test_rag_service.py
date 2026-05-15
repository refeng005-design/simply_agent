"""
RAG 服务测试

测试检索增强生成服务
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.rag_service import RAGService


class TestRAGServiceInit:
    """测试 RAG 服务初始化"""

    @patch('app.services.rag_service.VectorStore')
    @patch('app.services.rag_service.EmbeddingService')
    def test_init_default(self, mock_embedding, mock_store):
        """使用默认参数初始化"""
        service = RAGService()

        mock_embedding.assert_called_once()
        mock_store.assert_called_once()

    @patch('app.services.rag_service.VectorStore')
    @patch('app.services.rag_service.EmbeddingService')
    def test_init_custom_collection(self, mock_embedding, mock_store):
        """使用自定义集合名初始化"""
        service = RAGService(collection_name="custom_collection")

        mock_store.assert_called_once_with(collection_name="custom_collection")


class TestRAGServiceAddDocument:
    """测试添加文档"""

    @patch('app.services.rag_service.VectorStore')
    @patch('app.services.rag_service.EmbeddingService')
    def test_add_document(self, mock_embedding_cls, mock_store_cls):
        """添加单个文档"""
        mock_embedding = Mock()
        mock_embedding.embed.return_value = [0.1, 0.2, 0.3]
        mock_embedding_cls.return_value = mock_embedding

        mock_store = Mock()
        mock_store_cls.return_value = mock_store

        service = RAGService()
        service.add_document("doc1", "Test content", {"source": "test"})

        mock_store.add.assert_called_once()

    @patch('app.services.rag_service.VectorStore')
    @patch('app.services.rag_service.EmbeddingService')
    def test_add_document_batch(self, mock_embedding_cls, mock_store_cls):
        """批量添加文档"""
        mock_embedding = Mock()
        mock_embedding.embed_batch.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_embedding_cls.return_value = mock_embedding

        mock_store = Mock()
        mock_store_cls.return_value = mock_store

        service = RAGService()
        service.add_documents([
            ("doc1", "Content 1", {}),
            ("doc2", "Content 2", {}),
        ])

        mock_store.add_batch.assert_called_once()


class TestRAGServiceRetrieve:
    """测试文档检索"""

    @patch('app.services.rag_service.VectorStore')
    @patch('app.services.rag_service.EmbeddingService')
    def test_retrieve_documents(self, mock_embedding_cls, mock_store_cls):
        """检索相关文档"""
        mock_embedding = Mock()
        mock_embedding.embed.return_value = [0.1, 0.2, 0.3]
        mock_embedding_cls.return_value = mock_embedding

        mock_store = Mock()
        mock_store.search.return_value = [
            {"document": "Doc 1", "metadata": {}, "distance": 0.1},
            {"document": "Doc 2", "metadata": {}, "distance": 0.2},
        ]
        mock_store_cls.return_value = mock_store

        service = RAGService()
        results = service.retrieve("test query", n_results=2)

        assert len(results) == 2
        assert results[0]["document"] == "Doc 1"

    @patch('app.services.rag_service.VectorStore')
    @patch('app.services.rag_service.EmbeddingService')
    def test_retrieve_with_filter(self, mock_embedding_cls, mock_store_cls):
        """使用过滤条件检索"""
        mock_embedding = Mock()
        mock_embedding.embed.return_value = [0.1, 0.2, 0.3]
        mock_embedding_cls.return_value = mock_embedding

        mock_store = Mock()
        mock_store.search.return_value = []
        mock_store_cls.return_value = mock_store

        service = RAGService()
        service.retrieve("test query", where={"category": "tech"})

        mock_store.search.assert_called_once()
        call_kwargs = mock_store.search.call_args[1]
        assert call_kwargs["where"] == {"category": "tech"}


class TestRAGServiceGenerate:
    """测试生成增强的提示"""

    @patch('app.services.rag_service.VectorStore')
    @patch('app.services.rag_service.EmbeddingService')
    def test_generate_rag_prompt(self, mock_embedding_cls, mock_store_cls):
        """生成 RAG 增强的提示"""
        mock_embedding = Mock()
        mock_embedding.embed.return_value = [0.1, 0.2, 0.3]
        mock_embedding_cls.return_value = mock_embedding

        mock_store = Mock()
        mock_store.search.return_value = [
            {"document": "Context doc 1", "metadata": {}, "distance": 0.1},
            {"document": "Context doc 2", "metadata": {}, "distance": 0.2},
        ]
        mock_store_cls.return_value = mock_store

        service = RAGService()
        prompt = service.generate_prompt("What is AI?", n_results=2)

        assert "Context doc 1" in prompt
        assert "Context doc 2" in prompt
        assert "What is AI?" in prompt
        assert "[Context]" in prompt
        assert "[Question]" in prompt


class TestRAGServiceDelete:
    """测试删除文档"""

    @patch('app.services.rag_service.VectorStore')
    @patch('app.services.rag_service.EmbeddingService')
    def test_delete_document(self, mock_embedding_cls, mock_store_cls):
        """删除单个文档"""
        mock_store = Mock()
        mock_store_cls.return_value = mock_store

        service = RAGService()
        service.delete_document("doc1")

        mock_store.delete.assert_called_once_with("doc1")
