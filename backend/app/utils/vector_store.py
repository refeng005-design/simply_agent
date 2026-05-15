"""
向量存储封装

使用 ChromaDB 进行向量存储和检索
"""
from typing import List, Dict, Any, Optional, Tuple
import chromadb


class VectorStore:
    """
    向量存储封装类

    使用 ChromaDB 进行文档的向量存储、检索和管理
    """

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        persist_directory: Optional[str] = None
    ):
        """
        初始化向量存储

        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录，None 表示使用内存存储
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # 创建 ChromaDB 客户端
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        添加单个文档到向量存储

        Args:
            doc_id: 文档唯一标识
            text: 文档文本内容
            metadata: 可选的元数据
        """
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata] if metadata else None
        )

    def add_batch(
        self,
        documents: List[Tuple[str, str, Optional[Dict[str, Any]]]]
    ) -> None:
        """
        批量添加文档

        Args:
            documents: 文档列表，每个元素为 (doc_id, text, metadata) 元组
        """
        ids = [doc[0] for doc in documents]
        texts = [doc[1] for doc in documents]
        metadatas = [doc[2] for doc in documents]

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        向量搜索相似文档

        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件

        Returns:
            搜索结果列表，每个结果包含 document, metadata, distance
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        # 格式化结果
        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })

        return formatted_results

    def delete(self, doc_id: str) -> None:
        """
        删除单个文档

        Args:
            doc_id: 文档 ID
        """
        self.collection.delete(ids=[doc_id])

    def delete_batch(self, doc_ids: List[str]) -> None:
        """
        批量删除文档

        Args:
            doc_ids: 文档 ID 列表
        """
        self.collection.delete(ids=doc_ids)

    def clear(self) -> None:
        """清空整个集合"""
        # 获取所有文档 ID 并删除
        # 注意：ChromaDB 没有直接清空的方法，需要通过其他方式实现
        # 这里使用删除所有文档的方式
        self.collection.delete(where={})
