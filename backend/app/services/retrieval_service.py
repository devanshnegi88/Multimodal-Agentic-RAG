"""Retrieval service — orchestrates hybrid search pipeline."""
from typing import List, Dict, Any
from app.rag.hybrid_search import HybridSearcher
from app.rag.reranker import Reranker

class RetrievalService:
    def __init__(self):
        self.searcher = HybridSearcher()
        self.reranker = Reranker()

    async def retrieve(self, query: str, document_ids: List[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        chunks = await self.searcher.search(query=query, document_ids=document_ids or [], top_k=top_k * 2)
        if len(chunks) > top_k:
            chunks = await self.reranker.rerank(query, chunks, top_k=top_k)
        return chunks
