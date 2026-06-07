"""
Reranker — Cohere cross-encoder reranking with fallback
"""
from typing import List, Dict, Any
from app.utils.logger import logger


class Reranker:
    async def rerank(
        self, query: str, chunks: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Rerank chunks using Cohere or fallback to score-based sorting."""
        try:
            return await self._cohere_rerank(query, chunks, top_k)
        except Exception as e:
            logger.warning(f"[Reranker] Cohere failed, using score sort: {e}")
            return sorted(chunks, key=lambda x: x.get("score", 0.0), reverse=True)[:top_k]

    async def _cohere_rerank(
        self, query: str, chunks: List[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        import cohere
        from app.config import settings

        co = cohere.AsyncClientV2(api_key=settings.ANTHROPIC_API_KEY)  # uses same env pattern
        documents = [c.get("text", "") for c in chunks]

        response = await co.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=documents,
            top_n=top_k,
        )

        reranked = []
        for result in response.results:
            chunk = chunks[result.index].copy()
            chunk["rerank_score"] = result.relevance_score
            reranked.append(chunk)

        return reranked
