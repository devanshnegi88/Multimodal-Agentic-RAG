"""
Vector Manager — unified interface over Qdrant + FAISS
"""
from typing import List, Dict, Any, Optional
from app.vectorstore.qdrant_client import QdrantManager
from app.vectorstore.faiss_store import FAISSStore
from app.rag.embeddings import EmbeddingGenerator
from app.utils.logger import logger


class VectorManager:
    """
    Abstracts over primary (Qdrant) and fallback (FAISS) vector stores.
    Automatically falls back to FAISS if Qdrant is unavailable.
    """

    def __init__(self):
        self.qdrant = QdrantManager()
        self.faiss = FAISSStore()
        self.embedder = EmbeddingGenerator()
        self._use_qdrant = True

    async def initialize(self):
        """Initialize vector stores and check availability."""
        try:
            await self.qdrant.ensure_collection()
            self._use_qdrant = True
            logger.info("[VectorManager] Using Qdrant as primary store")
        except Exception:
            self._use_qdrant = False
            logger.warning("[VectorManager] Qdrant unavailable — using FAISS fallback")

    async def add_documents(self, chunks: List[Dict[str, Any]], document_id: str):
        """Embed and index document chunks."""
        texts = [c.get("text", "") for c in chunks if c.get("text")]
        if not texts:
            return

        embeddings = await self.embedder.embed(texts)

        if self._use_qdrant:
            from app.rag.retriever import VectorRetriever
            retriever = VectorRetriever()
            await retriever.upsert(chunks, document_id)
        else:
            metadata = [
                {
                    "text": chunk.get("text", ""),
                    "document_id": document_id,
                    "chunk_index": i,
                    "modality": chunk.get("modality", "text"),
                }
                for i, chunk in enumerate(chunks)
            ]
            self.faiss.add(embeddings, metadata)

    async def search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search across the active vector store."""
        query_embedding = await self.embedder.embed_query(query)

        if self._use_qdrant:
            from app.rag.retriever import VectorRetriever
            retriever = VectorRetriever()
            return await retriever.search(query=query, document_ids=document_ids, top_k=top_k)
        else:
            results = self.faiss.search(query_embedding, top_k=top_k)
            if document_ids:
                results = [r for r in results if r.get("document_id") in document_ids]
            return results

    async def delete_document(self, document_id: str):
        """Remove all vectors for a document."""
        if self._use_qdrant:
            await self.qdrant.delete_by_document(document_id)
        else:
            logger.warning("[VectorManager] FAISS does not support per-document deletion — rebuild required")

    async def get_stats(self) -> Dict[str, Any]:
        """Return stats for the active vector store."""
        if self._use_qdrant:
            return await self.qdrant.get_collection_stats()
        return {"total_vectors": self.faiss.total_vectors, "backend": "faiss"}
