"""
文本向量化工具

使用 SentenceTransformer 将文本转换为向量
"""
from typing import List

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    文本向量化服务

    使用预训练的 SentenceTransformer 模型将文本转换为向量
    """

    DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self, model_name: str = None):
        """
        初始化向量化服务

        Args:
            model_name: 模型名称，默认使用多语言 MiniLM 模型
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.model = SentenceTransformer(self.model_name)

    def embed(self, text: str) -> List[float]:
        """
        将单个文本转换为向量

        Args:
            text: 输入文本

        Returns:
            文本的向量表示
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文本转换为向量

        Args:
            texts: 输入文本列表

        Returns:
            文本向量的列表
        """
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]

    def get_dimension(self) -> int:
        """
        获取向量维度

        Returns:
            向量维度大小
        """
        return self.model.get_sentence_embedding_dimension()
