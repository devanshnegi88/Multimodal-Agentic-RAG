"""
Vector Memory — stores episodic memories as embeddings for long-term recall
"""
import uuid
from typing import List, Dict, Any
from datetime import datetime
from app.rag.embeddings import EmbeddingGenerator
from app.utils.logger import logger


class VectorMemory:
    """
    Long-term vector memory: stores key facts/summaries as embeddings
    so they can be recalled across sessions via semantic search.
    """

    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self._memories: List[Dict[str, Any]] = []  # In-process fallback
        self._embeddings: List[List[float]] = []

    async def store(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Store a memory and its embedding."""
        memory_id = str(uuid.uuid4())
        embedding = await self.embedder.embed_query(content)

        memory = {
            "id": memory_id,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }

        self._memories.append(memory)
        self._embeddings.append(embedding)

        logger.debug(f"[VectorMemory] Stored memory: {content[:60]}")
        return memory_id

    async def recall(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find semantically similar memories."""
        if not self._memories:
            return []

        query_embedding = await self.embedder.embed_query(query)

        import numpy as np
        scores = [
            EmbeddingGenerator.cosine_similarity(query_embedding, emb)
            for emb in self._embeddings
        ]

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0.5:  # Minimum relevance threshold
                result = self._memories[idx].copy()
                result["score"] = scores[idx]
                results.append(result)

        return results

    async def forget(self, memory_id: str):
        """Remove a specific memory."""
        for i, mem in enumerate(self._memories):
            if mem["id"] == memory_id:
                self._memories.pop(i)
                self._embeddings.pop(i)
                logger.debug(f"[VectorMemory] Forgot memory: {memory_id}")
                return

    def clear(self):
        """Clear all memories."""
        self._memories.clear()
        self._embeddings.clear()

    @property
    def count(self) -> int:
        return len(self._memories)
