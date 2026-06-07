"""Analytics service — event tracking and aggregations."""
from datetime import datetime
from typing import Dict, Any
from app.utils.logger import logger

class AnalyticsService:
    def __init__(self, db):
        self.db = db

    async def track(self, event_type: str, user_id: str = "anonymous", metadata: Dict[str, Any] = None):
        try:
            await self.db["analytics"].insert_one({
                "event_type": event_type,
                "user_id": user_id,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow(),
            })
        except Exception as e:
            logger.warning(f"[Analytics] Track failed: {e}")

    async def track_query(self, user_id: str, query: str, response_time_ms: float, session_id: str = None):
        await self.track("query", user_id, {"query": query[:200], "response_time_ms": response_time_ms, "session_id": session_id})

    async def track_agent(self, agent_name: str, user_id: str = "anonymous"):
        await self.track("agent_invocation", user_id, {"agent_name": agent_name})
