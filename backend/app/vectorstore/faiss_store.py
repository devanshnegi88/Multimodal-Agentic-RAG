"""
FAISS local vector store — for offline / embedded deployments
"""
import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.logger import logger


class FAISSStore:
    """
    Local FAISS index for dense retrieval.
    Used as a fallback when Qdrant is unavailable, or for local dev.
    """

    def __init__(self, index_path: str = None, dim: int = None):
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.meta_path = self.index_path.replace(".faiss", "_meta.pkl")
        self.dim = dim or settings.EMBEDDING_DIM
        self._index = None
        self._metadata: List[Dict] = []

    def _get_index(self):
        if self._index is None:
            try:
                import faiss
                if os.path.exists(self.index_path):
                    self._index = faiss.read_index(self.index_path)
                    if os.path.exists(self.meta_path):
                        with open(self.meta_path, "rb") as f:
                            self._metadata = pickle.load(f)
                    logger.info(f"[FAISS] Loaded index from {self.index_path}")
                else:
                    self._index = faiss.IndexFlatIP(self.dim)  # Inner product (cosine after normalize)
                    logger.info(f"[FAISS] Created new index (dim={self.dim})")
            except Exception as e:
                logger.error(f"[FAISS] Index init failed: {e}")
        return self._index

    def add(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]):
        """Add vectors with metadata."""
        import faiss
        index = self._get_index()
        if index is None:
            return

        vecs = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(vecs)
        index.add(vecs)
        self._metadata.extend(metadata)
        self._save()
        logger.info(f"[FAISS] Added {len(embeddings)} vectors. Total: {index.ntotal}")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for nearest neighbors."""
        import faiss
        index = self._get_index()
        if index is None or index.ntotal == 0:
            return []

        q = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(q)
        scores, indices = index.search(q, min(top_k, index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = self._metadata[idx].copy()
            meta["score"] = float(score)
            results.append(meta)
        return results

    def _save(self):
        """Persist index and metadata to disk."""
        try:
            import faiss
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self._index, self.index_path)
            with open(self.meta_path, "wb") as f:
                pickle.dump(self._metadata, f)
        except Exception as e:
            logger.error(f"[FAISS] Save failed: {e}")

    def reset(self):
        """Clear the entire index."""
        import faiss
        self._index = faiss.IndexFlatIP(self.dim)
        self._metadata = []
        self._save()
        logger.info("[FAISS] Index reset")

    @property
    def total_vectors(self) -> int:
        idx = self._get_index()
        return idx.ntotal if idx else 0
