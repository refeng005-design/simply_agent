"""
向量存储测试

测试 Chroma 向量存储的封装功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.utils.vector_store import VectorStore


class TestVectorStoreInit:
    """测试向量存储初始化"""

    @patch('app.utils.vector_store.chromadb.Client')
    def test_init_default_collection(self, mock_client):
        """使用默认集合名初始化"""
        mock_collection = Mock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore()

        assert store.collection_name == "knowledge_base"
        mock_client.assert_called_once()

    @patch('app.utils.vector_store.chromadb.Client')
    def test_init_custom_collection(self, mock_client):
        """使用自定义集合名初始化"""
        mock_collection = Mock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore(collection_name="custom_collection")

        assert store.collection_name == "custom_collection"

    @patch('app.utils.vector_store.chromadb.Client')
    def test_init_with_persist_dir(self, mock_client):
        """使用持久化目录初始化"""
        mock_collection = Mock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore(persist_directory="/data/chroma")

        assert store.persist_directory == "/data/chroma"


class TestVectorStoreAdd:
    """测试添加文档到向量存储"""

    @patch('app.utils.vector_store.chromadb.Client')
    def test_add_document(self, mock_client):
        """添加单个文档"""
        mock_collection = Mock()
        mock_collection.add.return_value = None
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore()
        store.add("doc1", "This is a test document", {"source": "test"})

        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert call_args[1]["ids"] == ["doc1"]
        assert call_args[1]["documents"] == ["This is a test document"]
        assert call_args[1]["metadatas"] == [{"source": "test"}]

    @patch('app.utils.vector_store.chromadb.Client')
    def test_add_multiple_documents(self, mock_client):
        """添加多个文档"""
        mock_collection = Mock()
        mock_collection.add.return_value = None
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore()
        store.add_batch([
            ("doc1", "First document", {"source": "a"}),
            ("doc2", "Second document", {"source": "b"}),
        ])

        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert call_args[1]["ids"] == ["doc1", "doc2"]
        assert call_args[1]["documents"] == ["First document", "Second document"]


class TestVectorStoreSearch:
    """测试向量搜索"""

    @patch('app.utils.vector_store.chromadb.Client')
    def test_search_returns_documents(self, mock_client):
        """搜索返回相关文档"""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"source": "a"}, {"source": "b"}]],
            "distances": [[0.1, 0.2]]
        }
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore()
        results = store.search("test query", n_results=2)

        assert len(results) == 2
        assert results[0]["document"] == "doc1"
        assert results[0]["metadata"]["source"] == "a"
        assert results[0]["distance"] == 0.1

    @patch('app.utils.vector_store.chromadb.Client')
    def test_search_with_filter(self, mock_client):
        """使用元数据过滤搜索"""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [["doc1"]],
            "metadatas": [[{"source": "test"}]],
            "distances": [[0.1]]
        }
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore()
        results = store.search("test query", where={"source": "test"})

        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args
        assert call_args[1]["where"] == {"source": "test"}


class TestVectorStoreDelete:
    """测试删除文档"""

    @patch('app.utils.vector_store.chromadb.Client')
    def test_delete_by_id(self, mock_client):
        """根据 ID 删除文档"""
        mock_collection = Mock()
        mock_collection.delete.return_value = None
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore()
        store.delete("doc1")

        mock_collection.delete.assert_called_once_with(ids=["doc1"])

    @patch('app.utils.vector_store.chromadb.Client')
    def test_delete_multiple(self, mock_client):
        """删除多个文档"""
        mock_collection = Mock()
        mock_collection.delete.return_value = None
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore()
        store.delete_batch(["doc1", "doc2"])

        mock_collection.delete.assert_called_once_with(ids=["doc1", "doc2"])


class TestVectorStoreClear:
    """测试清空集合"""

    @patch('app.utils.vector_store.chromadb.Client')
    def test_clear_collection(self, mock_client):
        """清空整个集合"""
        mock_collection = Mock()
        mock_collection.delete.return_value = None
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        store = VectorStore()
        store.clear()

        mock_collection.delete.assert_called_once()
