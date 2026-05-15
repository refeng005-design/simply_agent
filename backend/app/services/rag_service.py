"""
RAG (检索增强生成) 服务

结合向量检索和 LLM 生成，提供增强的问答能力
"""
from typing import List, Dict, Any, Optional

from app.utils.vector_store import VectorStore
from app.utils.embeddings import EmbeddingService


class RAGService:
    """
    检索增强生成服务

    使用向量存储和向量化实现文档检索和增强生成
    """

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        embedding_model: str = None
    ):
        """
        初始化 RAG 服务

        Args:
            collection_name: 向量存储集合名称
            embedding_model: 向量化模型名称
        """
        self.embedding_service = EmbeddingService(model_name=embedding_model)
        self.vector_store = VectorStore(collection_name=collection_name)

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        添加单个文档到知识库

        Args:
            doc_id: 文档唯一标识
            text: 文档文本内容
            metadata: 可选的元数据
        """
        self.vector_store.add(doc_id, text, metadata)

    def add_documents(
        self,
        documents: List[tuple[str, str, Optional[Dict[str, Any]]]]
    ) -> None:
        """
        批量添加文档到知识库

        Args:
            documents: 文档列表，每个元素为 (doc_id, text, metadata) 元组
        """
        self.vector_store.add_batch(documents)

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        根据查询检索相关文档

        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件

        Returns:
            检索结果列表
        """
        results = self.vector_store.search(query, n_results=n_results, where=where)
        return results

    def generate_prompt(
        self,
        query: str,
        n_results: int = 3
    ) -> str:
        """
        生成 RAG 增强的提示词

        Args:
            query: 用户查询
            n_results: 检索的文档数量

        Returns:
            增强后的提示词
        """
        # 检索相关文档
        results = self.retrieve(query, n_results=n_results)

        # 构建上下文
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Document {i}] {result['document']}")

        context = "\n".join(context_parts)

        # 构建提示词
        prompt = f"""Based on the following context, please answer the question.

[Context]
{context}

[Question]
{query}

[Answer]
"""

        return prompt

    def delete_document(self, doc_id: str) -> None:
        """
        从知识库删除文档

        Args:
            doc_id: 文档 ID
        """
        self.vector_store.delete(doc_id)
