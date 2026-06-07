"""
Hybrid Search — combines dense vector search with BM25 sparse retrieval
"""
from typing import List, Dict, Any
from app.rag.retriever import VectorRetriever
from app.utils.logger import logger


class HybridSearcher:
    """
    Reciprocal Rank Fusion (RRF) over:
    - Dense: Qdrant vector search
    - Sparse: BM25 over cached chunk texts
    """

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.vector_retriever = VectorRetriever()
        self._bm25 = None
        self._bm25_corpus: List[Dict] = []

    async def search(
        self, query: str, document_ids: List[str] = None, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        # Dense retrieval
        dense_results = await self.vector_retriever.search(
            query=query, document_ids=document_ids, top_k=top_k * 2
        )

        # BM25 sparse retrieval (over pre-loaded corpus)
        sparse_results = self._bm25_search(query, top_k=top_k * 2)

        # Reciprocal Rank Fusion
        if not sparse_results:
            return dense_results[:top_k]

        fused = self._rrf(dense_results, sparse_results, top_k=top_k)
        logger.info(f"[HybridSearch] RRF produced {len(fused)} results")
        return fused

    def _bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        if not self._bm25_corpus:
            return []
        try:
            from rank_bm25 import BM25Okapi

            tokenized_corpus = [doc["text"].lower().split() for doc in self._bm25_corpus]
            bm25 = BM25Okapi(tokenized_corpus)
            scores = bm25.get_scores(query.lower().split())
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            return [
                {**self._bm25_corpus[i], "score": float(scores[i])}
                for i in top_indices
                if scores[i] > 0
            ]
        except Exception as e:
            logger.warning(f"[HybridSearch] BM25 failed: {e}")
            return []

    def _rrf(
        self,
        dense: List[Dict],
        sparse: List[Dict],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        scores: Dict[str, float] = {}
        chunks: Dict[str, Dict] = {}

        def get_key(chunk: Dict) -> str:
            return f"{chunk.get('document_id','')}-{chunk.get('chunk_index', 0)}"

        for rank, chunk in enumerate(dense):
            key = get_key(chunk)
            scores[key] = scores.get(key, 0.0) + 1.0 / (self.rrf_k + rank + 1)
            chunks[key] = chunk

        for rank, chunk in enumerate(sparse):
            key = get_key(chunk)
            scores[key] = scores.get(key, 0.0) + 1.0 / (self.rrf_k + rank + 1)
            chunks[key] = chunk

        sorted_keys = sorted(scores, key=lambda k: scores[k], reverse=True)[:top_k]
        return [{**chunks[k], "score": scores[k]} for k in sorted_keys]

    def load_corpus(self, chunks: List[Dict[str, Any]]):
        """Pre-load BM25 corpus from document chunks."""
        self._bm25_corpus = chunks
