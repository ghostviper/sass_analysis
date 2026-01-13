"""
向量存储服务 - Pinecone 封装

简单封装，不过度设计。
"""

import os
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI

# Pinecone
try:
    from pinecone import Pinecone
    HAS_PINECONE = True
except ImportError:
    HAS_PINECONE = False
    Pinecone = None

# 配置
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "buildwhat")

# Embedding 配置（独立于 OpenAI，支持第三方服务）
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL") or os.getenv("OPENAI_BASE_URL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))


class VectorStore:
    """向量存储服务"""
    
    def __init__(self):
        self._pc = None
        self._index = None
        self._openai = None
    
    @property
    def enabled(self) -> bool:
        """检查是否可用"""
        return HAS_PINECONE and bool(PINECONE_API_KEY)
    
    def _get_index(self):
        """懒加载 Pinecone index"""
        if not self.enabled:
            raise RuntimeError("Pinecone 未配置，请设置 PINECONE_API_KEY")
        
        if self._index is None:
            self._pc = Pinecone(api_key=PINECONE_API_KEY)
            self._index = self._pc.Index(PINECONE_INDEX)
        
        return self._index
    
    def _get_openai(self) -> AsyncOpenAI:
        """懒加载 OpenAI 兼容的 embedding client"""
        if self._openai is None:
            self._openai = AsyncOpenAI(
                api_key=EMBEDDING_API_KEY,
                base_url=EMBEDDING_BASE_URL
            )
        return self._openai
    
    async def get_embedding(self, text: str) -> List[float]:
        """获取文本的 embedding 向量"""
        client = self._get_openai()
        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """批量获取 embeddings"""
        client = self._get_openai()
        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def upsert(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str = "products"
    ) -> int:
        """
        插入或更新向量
        
        Args:
            vectors: [{"id": "product_1", "values": [...], "metadata": {...}}]
            namespace: 命名空间
            
        Returns:
            成功插入的数量
        """
        index = self._get_index()
        
        # Pinecone 批量限制 100 条
        batch_size = 100
        total = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch, namespace=namespace)
            total += len(batch)
        
        return total
    
    def query(
        self,
        vector: List[float],
        namespace: str = "products",
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        向量查询
        
        Args:
            vector: 查询向量
            namespace: 命名空间
            top_k: 返回数量
            filter: 元数据过滤条件
            include_metadata: 是否返回元数据
            
        Returns:
            匹配结果列表 [{"id": "...", "score": 0.9, "metadata": {...}}]
        """
        index = self._get_index()
        
        results = index.query(
            vector=vector,
            namespace=namespace,
            top_k=top_k,
            filter=filter,
            include_metadata=include_metadata
        )
        
        return [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata or {}
            }
            for match in results.matches
        ]
    
    async def search(
        self,
        query: str,
        namespace: str = "products",
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        语义搜索（文本 -> embedding -> 查询）
        
        Args:
            query: 自然语言查询
            namespace: 命名空间
            top_k: 返回数量
            filter: 元数据过滤条件
            
        Returns:
            匹配结果列表
        """
        embedding = await self.get_embedding(query)
        return self.query(
            vector=embedding,
            namespace=namespace,
            top_k=top_k,
            filter=filter
        )
    
    def delete(
        self,
        ids: List[str],
        namespace: str = "products"
    ):
        """删除向量"""
        index = self._get_index()
        index.delete(ids=ids, namespace=namespace)
    
    def delete_all(self, namespace: str = "products"):
        """删除命名空间下所有向量"""
        index = self._get_index()
        try:
            index.delete(delete_all=True, namespace=namespace)
        except Exception as e:
            # namespace 不存在时忽略错误
            if "not found" in str(e).lower():
                pass
            else:
                raise
    
    def stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        index = self._get_index()
        return index.describe_index_stats()


# 全局单例
vector_store = VectorStore()
