"""
Embedding generation — OpenAI + local sentence-transformers fallback
"""
from typing import List
import numpy as np
from app.utils.logger import logger


class EmbeddingGenerator:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._local_model = None

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            return await self._openai_embed(texts)
        except Exception as e:
            logger.warning(f"[Embeddings] OpenAI failed, using local: {e}")
            return self._local_embed(texts)

    async def embed_query(self, query: str) -> List[float]:
        embeddings = await self.embed([query])
        return embeddings[0]

    async def _openai_embed(self, texts: List[str]) -> List[List[float]]:
        from openai import AsyncOpenAI
        from app.config import settings

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def _local_embed(self, texts: List[str]) -> List[List[float]]:
        """Use sentence-transformers as fallback."""
        if self._local_model is None:
            from sentence_transformers import SentenceTransformer
            self._local_model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = self._local_model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        a_arr = np.array(a)
        b_arr = np.array(b)
        return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr) + 1e-10))
