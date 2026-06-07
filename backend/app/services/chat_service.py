"""Chat service — session management and message persistence."""
from datetime import datetime
from bson import ObjectId
from app.utils.logger import logger

class ChatService:
    def __init__(self, db):
        self.db = db

    async def get_or_create_session(self, session_id: str = None, user_id: str = "anonymous") -> dict:
        if session_id:
            session = await self.db["chat_sessions"].find_one({"_id": session_id})
            if session:
                return session
        sid = session_id or str(ObjectId())
        session = {"_id": sid, "user_id": user_id, "title": "New Chat", "messages": [], "document_ids": [], "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        await self.db["chat_sessions"].insert_one(session)
        return session

    async def append_message(self, session_id: str, message: dict):
        await self.db["chat_sessions"].update_one(
            {"_id": session_id},
            {"$push": {"messages": message}, "$set": {"updated_at": datetime.utcnow()}},
        )

    async def update_title(self, session_id: str, title: str):
        await self.db["chat_sessions"].update_one({"_id": session_id}, {"$set": {"title": title[:80]}})
