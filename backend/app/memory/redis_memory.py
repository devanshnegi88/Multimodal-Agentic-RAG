"""
Redis-backed short-term conversation memory
"""
import json
from typing import Any, Dict, List, Optional
from app.config import settings
from app.utils.logger import logger


class RedisMemory:
    """
    Stores conversation context in Redis with TTL.
    Keys: memory:{session_id}, history:{session_id}
    """

    def __init__(self):
        self._client = None

    async def _get(self):
        if self._client is None:
            try:
                import redis.asyncio as aioredis
                self._client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                await self._client.ping()
            except Exception as e:
                logger.warning(f"[RedisMemory] Connection failed: {e}")
                self._client = None
        return self._client

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        r = await self._get()
        if r is None:
            return False
        try:
            await r.set(key, json.dumps(value), ex=ttl or settings.REDIS_TTL)
            return True
        except Exception as e:
            logger.error(f"[RedisMemory] set error: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        r = await self._get()
        if r is None:
            return None
        try:
            val = await r.get(key)
            return json.loads(val) if val else None
        except Exception:
            return None

    async def delete(self, key: str) -> bool:
        r = await self._get()
        if r is None:
            return False
        try:
            await r.delete(key)
            return True
        except Exception:
            return False

    async def push_history(self, session_id: str, message: Dict[str, Any], max_len: int = 20):
        """Append a message to the session history list (capped at max_len)."""
        r = await self._get()
        if r is None:
            return
        key = f"history:{session_id}"
        try:
            await r.rpush(key, json.dumps(message))
            await r.ltrim(key, -max_len, -1)
            await r.expire(key, settings.REDIS_TTL)
        except Exception as e:
            logger.error(f"[RedisMemory] push_history error: {e}")

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get the full conversation history for a session."""
        r = await self._get()
        if r is None:
            return []
        key = f"history:{session_id}"
        try:
            items = await r.lrange(key, 0, -1)
            return [json.loads(i) for i in items]
        except Exception:
            return []

    async def clear_session(self, session_id: str):
        """Clear all memory for a session."""
        r = await self._get()
        if r is None:
            return
        try:
            await r.delete(f"memory:{session_id}", f"history:{session_id}")
        except Exception:
            pass

    async def is_available(self) -> bool:
        r = await self._get()
        if r is None:
            return False
        try:
            await r.ping()
            return True
        except Exception:
            return False
