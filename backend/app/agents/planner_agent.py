"""
Planner Agent — decomposes the user query into a structured execution plan
"""
import json
from typing import Dict, Any
from app.utils.prompts import PLANNER_SYSTEM_PROMPT
from app.utils.logger import logger


class PlannerAgent:
    """
    Uses an LLM to create a structured plan:
    - Intent classification
    - Sub-query decomposition
    - Tool selection
    - Strategy (RAG-only, web+RAG, image+RAG, etc.)
    """

    async def plan(self, query: str, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import anthropic
            from app.config import settings

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=512,
                system=PLANNER_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Query: {query}\nContext summary: {json.dumps(memory_context)[:500]}\n\nCreate a retrieval plan as JSON.",
                    }
                ],
            )
            raw = msg.content[0].text
            # Strip markdown fences if present
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            plan = json.loads(raw.strip())
            logger.info(f"[Planner] Plan: {plan}")
            return plan
        except Exception as e:
            logger.warning(f"[Planner] LLM call failed, using default plan: {e}")
            return self._default_plan(query)

    def _default_plan(self, query: str) -> Dict[str, Any]:
        return {
            "intent": "question_answering",
            "sub_queries": [query],
            "needs_web_search": False,
            "needs_vision": False,
            "top_k": 5,
            "strategy": "rag_only",
        }
