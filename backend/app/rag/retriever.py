"""
Vector Retriever — wraps Qdrant for dense retrieval
"""
from typing import List, Dict, Any
from app.rag.embeddings import EmbeddingGenerator
from app.utils.logger import logger


class VectorRetriever:
    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                from qdrant_client import AsyncQdrantClient
                from app.config import settings
                self._client = AsyncQdrantClient(url=settings.QDRANT_URL)
            except Exception as e:
                logger.warning(f"[Retriever] Qdrant unavailable: {e}")
        return self._client

    async def search(
        self, query: str, document_ids: List[str] = None, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Dense vector search."""
        query_vector = await self.embedder.embed_query(query)
        client = await self._get_client()

        if client is None:
            return []

        from qdrant_client.models import Filter, FieldCondition, MatchAny
        from app.config import settings

        query_filter = None
        if document_ids:
            query_filter = Filter(
                must=[FieldCondition(key="document_id", match=MatchAny(any=document_ids))]
            )

        results = await client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        return [
            {
                "text": r.payload.get("text", ""),
                "document_id": r.payload.get("document_id"),
                "chunk_index": r.payload.get("chunk_index", 0),
                "score": r.score,
                "modality": r.payload.get("modality", "text"),
                "metadata": r.payload.get("metadata", {}),
            }
            for r in results
        ]

    async def upsert(self, chunks: List[Dict[str, Any]], document_id: str):
        """Upsert chunk embeddings into Qdrant."""
        client = await self._get_client()
        if client is None:
            return

        from qdrant_client.models import PointStruct
        from app.config import settings
        import uuid

        texts = [c["text"] for c in chunks]
        embeddings = await self.embedder.embed(texts)

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload={
                    "text": chunk["text"],
                    "document_id": document_id,
                    "chunk_index": chunk.get("chunk_index", i),
                    "modality": chunk.get("modality", "text"),
                    "metadata": chunk.get("metadata", {}),
                },
            )
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]

        await client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
        logger.info(f"[Retriever] Upserted {len(points)} chunks for doc {document_id}")
