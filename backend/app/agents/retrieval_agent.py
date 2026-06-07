"""
Retrieval Agent — hybrid semantic + BM25 search with reranking
"""
from typing import List, Dict, Any, Optional
from app.rag.retriever import VectorRetriever
from app.rag.hybrid_search import HybridSearcher
from app.rag.reranker import Reranker
from app.utils.logger import logger


class RetrievalAgent:
    def __init__(self, db=None):
        self.db = db
        self.vector_retriever = VectorRetriever()
        self.hybrid_searcher = HybridSearcher()
        self.reranker = Reranker()

    async def retrieve(
        self,
        query: str,
        document_ids: List[str] = None,
        top_k: int = 5,
        use_hybrid: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Run hybrid retrieval (dense + sparse) then rerank.
        Falls back to DB-based retrieval if vector stores unavailable.
        """
        try:
            if use_hybrid:
                chunks = await self.hybrid_searcher.search(
                    query=query,
                    document_ids=document_ids or [],
                    top_k=top_k * 2,
                )
            else:
                chunks = await self.vector_retriever.search(
                    query=query,
                    document_ids=document_ids or [],
                    top_k=top_k * 2,
                )

            # Rerank
            if len(chunks) > top_k:
                chunks = await self.reranker.rerank(query, chunks, top_k=top_k)

            logger.info(f"[Retrieval] Retrieved {len(chunks)} chunks for query: {query[:60]}")
            return chunks

        except Exception as e:
            logger.warning(f"[Retrieval] Vector search failed, falling back to DB: {e}")
            return await self._db_fallback(query, document_ids, top_k)

    async def _db_fallback(
        self, query: str, document_ids: Optional[List[str]], top_k: int
    ) -> List[Dict[str, Any]]:
        """Simple MongoDB text search fallback."""
        if self.db is None:
            return []
        filter_q = {}
        if document_ids:
            filter_q["document_id"] = {"$in": document_ids}
        cursor = self.db["chunks"].find(filter_q).limit(top_k)
        chunks = await cursor.to_list(length=top_k)
        return [
            {
                "text": c.get("text", ""),
                "document_id": c.get("document_id"),
                "chunk_index": c.get("chunk_index", 0),
                "score": 1.0,
                "modality": c.get("modality", "text"),
                "metadata": c.get("metadata", {}),
            }
            for c in chunks
        ]
