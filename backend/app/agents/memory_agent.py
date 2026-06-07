"""
Memory Agent — manages conversation context via Redis + vector memory
"""
import json
from typing import List, Dict, Any
from app.utils.logger import logger


class MemoryAgent:
    def __init__(self, db=None):
        self.db = db
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                from app.config import settings
                self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                pass
        return self._redis

    async def load(self, session_id: str, history: List[Dict]) -> Dict[str, Any]:
        """Load recent conversation context."""
        # Try Redis first
        try:
            r = await self._get_redis()
            if r:
                cached = await r.get(f"memory:{session_id}")
                if cached:
                    return json.loads(cached)
        except Exception:
            pass

        # Build from history
        recent = history[-6:] if len(history) > 6 else history
        summary = " ".join(
            m.get("content", "")[:100] for m in recent if m.get("role") == "user"
        )
        return {
            "session_id": session_id,
            "recent_messages": recent,
            "summary": summary,
            "entity_memory": {},
        }

    async def save(self, session_id: str, user_query: str, assistant_answer: str):
        """Persist updated memory to Redis."""
        try:
            r = await self._get_redis()
            if r:
                from app.config import settings
                memory = {
                    "session_id": session_id,
                    "last_query": user_query,
                    "last_answer": assistant_answer[:200],
                }
                await r.setex(
                    f"memory:{session_id}",
                    settings.REDIS_TTL,
                    json.dumps(memory),
                )
        except Exception as e:
            logger.warning(f"[Memory] Redis save failed: {e}")

    async def clear(self, session_id: str):
        """Clear memory for a session."""
        try:
            r = await self._get_redis()
            if r:
                await r.delete(f"memory:{session_id}")
        except Exception as e:
            logger.warning(f"[Memory] Redis clear failed: {e}")
