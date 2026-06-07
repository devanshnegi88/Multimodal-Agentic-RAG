"""
Conversation Memory — sliding window + summarization for long conversations
"""
from typing import List, Dict, Any
from app.memory.redis_memory import RedisMemory
from app.utils.logger import logger


class ConversationMemory:
    """
    Manages conversation history with:
    - Short-term: Redis sliding window (last N messages)
    - Long-term: Periodic summarization via LLM
    """

    WINDOW_SIZE = 10  # Keep last 10 message pairs
    SUMMARIZE_EVERY = 20  # Summarize after 20 total messages

    def __init__(self):
        self.redis = RedisMemory()

    async def add_message(self, session_id: str, role: str, content: str):
        """Add a message to conversation memory."""
        msg = {"role": role, "content": content}
        await self.redis.push_history(session_id, msg, max_len=self.WINDOW_SIZE * 2)

        # Check if we should summarize
        history = await self.redis.get_history(session_id)
        if len(history) >= self.SUMMARIZE_EVERY and len(history) % self.SUMMARIZE_EVERY == 0:
            await self._summarize(session_id, history)

    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for RAG."""
        history = await self.redis.get_history(session_id)
        summary = await self.redis.get(f"summary:{session_id}")

        return {
            "history": history[-self.WINDOW_SIZE:],
            "summary": summary or "",
            "message_count": len(history),
        }

    async def _summarize(self, session_id: str, history: List[Dict[str, Any]]):
        """Summarize the conversation to free up context window."""
        try:
            import anthropic
            from app.config import settings
            from app.utils.prompts import MEMORY_SUMMARY_PROMPT

            history_text = "\n".join(
                f"{m['role'].upper()}: {m['content'][:200]}"
                for m in history
            )

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=256,
                system=MEMORY_SUMMARY_PROMPT,
                messages=[{"role": "user", "content": history_text}],
            )
            summary = msg.content[0].text
            await self.redis.set(f"summary:{session_id}", summary)
            logger.info(f"[ConversationMemory] Summarized session {session_id}")
        except Exception as e:
            logger.warning(f"[ConversationMemory] Summarization failed: {e}")

    async def clear(self, session_id: str):
        """Clear all memory for a session."""
        await self.redis.clear_session(session_id)
        await self.redis.delete(f"summary:{session_id}")
