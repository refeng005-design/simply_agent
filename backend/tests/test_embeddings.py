"""
文本向量化测试

测试文本向量化的工具类
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch

from app.utils.embeddings import EmbeddingService


class TestEmbeddingServiceInit:
    """测试向量化服务初始化"""

    @patch('app.utils.embeddings.SentenceTransformer')
    def test_init_default_model(self, mock_transformer):
        """使用默认模型初始化"""
        mock_model = Mock()
        mock_transformer.return_value = mock_model

        service = EmbeddingService()

        mock_transformer.assert_called_once_with("paraphrase-multilingual-MiniLM-L12-v2")

    @patch('app.utils.embeddings.SentenceTransformer')
    def test_init_custom_model(self, mock_transformer):
        """使用自定义模型初始化"""
        mock_model = Mock()
        mock_transformer.return_value = mock_model

        service = EmbeddingService(model_name="custom-model")

        mock_transformer.assert_called_once_with("custom-model")


class TestEmbed:
    """测试单个文本向量化"""

    @patch('app.utils.embeddings.SentenceTransformer')
    def test_embed_returns_vector(self, mock_transformer):
        """返回文本向量"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        mock_transformer.return_value = mock_model

        service = EmbeddingService()
        result = service.embed("test text")

        assert result == [0.1, 0.2, 0.3]
        mock_model.encode.assert_called_once_with("test text")

    @patch('app.utils.embeddings.SentenceTransformer')
    def test_embed_empty_text(self, mock_transformer):
        """处理空文本"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([0.0, 0.0, 0.0])
        mock_transformer.return_value = mock_model

        service = EmbeddingService()
        result = service.embed("")

        assert result == [0.0, 0.0, 0.0]


class TestEmbedBatch:
    """测试批量文本向量化"""

    @patch('app.utils.embeddings.SentenceTransformer')
    def test_embed_batch_returns_vectors(self, mock_transformer):
        """返回多个文本向量"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ])
        mock_transformer.return_value = mock_model

        service = EmbeddingService()
        result = service.embed_batch(["text1", "text2"])

        assert len(result) == 2
        assert result[0] == [0.1, 0.2, 0.3]
        assert result[1] == [0.4, 0.5, 0.6]

    @patch('app.utils.embeddings.SentenceTransformer')
    def test_embed_batch_empty_list(self, mock_transformer):
        """处理空列表"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([])
        mock_transformer.return_value = mock_model

        service = EmbeddingService()
        result = service.embed_batch([])

        assert result == []


class TestGetDimension:
    """测试获取向量维度"""

    @patch('app.utils.embeddings.SentenceTransformer')
    def test_get_dimension(self, mock_transformer):
        """获取向量维度"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([0.1] * 384)
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model

        service = EmbeddingService()
        dimension = service.get_dimension()

        assert dimension == 384
