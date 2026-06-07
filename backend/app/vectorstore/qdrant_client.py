"""
Qdrant vector store client — collection management and CRUD
"""
from typing import List, Optional
from app.config import settings
from app.utils.logger import logger


class QdrantManager:
    """High-level Qdrant operations: create collections, upsert, delete, stats."""

    def __init__(self):
        self._client = None

    async def get_client(self):
        if self._client is None:
            try:
                from qdrant_client import AsyncQdrantClient
                self._client = AsyncQdrantClient(url=settings.QDRANT_URL)
            except Exception as e:
                logger.warning(f"[Qdrant] Client init failed: {e}")
        return self._client

    async def ensure_collection(self, collection_name: str = None, vector_size: int = None):
        """Create collection if it doesn't exist."""
        name = collection_name or settings.QDRANT_COLLECTION
        size = vector_size or settings.EMBEDDING_DIM

        client = await self.get_client()
        if client is None:
            return

        try:
            from qdrant_client.models import Distance, VectorParams
            collections = await client.get_collections()
            existing = [c.name for c in collections.collections]

            if name not in existing:
                await client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=size, distance=Distance.COSINE),
                )
                logger.info(f"[Qdrant] Created collection '{name}' (dim={size})")
            else:
                logger.debug(f"[Qdrant] Collection '{name}' already exists")
        except Exception as e:
            logger.error(f"[Qdrant] Collection ensure failed: {e}")

    async def delete_by_document(self, document_id: str, collection_name: str = None):
        """Delete all vectors for a given document."""
        name = collection_name or settings.QDRANT_COLLECTION
        client = await self.get_client()
        if client is None:
            return

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            await client.delete(
                collection_name=name,
                points_selector=Filter(
                    must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
                ),
            )
            logger.info(f"[Qdrant] Deleted vectors for document: {document_id}")
        except Exception as e:
            logger.error(f"[Qdrant] Delete failed: {e}")

    async def get_collection_stats(self, collection_name: str = None) -> dict:
        """Get collection statistics."""
        name = collection_name or settings.QDRANT_COLLECTION
        client = await self.get_client()
        if client is None:
            return {}

        try:
            info = await client.get_collection(collection_name=name)
            return {
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "status": str(info.status),
            }
        except Exception as e:
            logger.error(f"[Qdrant] Stats failed: {e}")
            return {}
