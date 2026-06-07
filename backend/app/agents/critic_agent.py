"""
Critic Agent — evaluates retrieved context quality (RAGAS-style)
"""
from typing import List, Dict, Any
from app.utils.logger import logger


class CriticAgent:
    """
    Evaluates whether retrieved chunks are sufficient to answer the query.
    Returns a verdict: 'sufficient' | 'insufficient' | 'partial'
    """

    async def evaluate(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        web_results: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not chunks and not web_results:
            return {
                "verdict": "insufficient",
                "reason": "No context retrieved",
                "expanded_query": f"{query} detailed explanation",
                "confidence": 0.0,
            }

        try:
            import anthropic
            from app.config import settings

            context_preview = "\n".join(c.get("text", "")[:200] for c in chunks[:3])
            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=256,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Query: {query}\n\nRetrieved context (sample):\n{context_preview}\n\n"
                            "Rate whether this context is sufficient to answer the query.\n"
                            "Respond with JSON: {\"verdict\": \"sufficient|insufficient|partial\", "
                            "\"confidence\": 0.0-1.0, \"reason\": \"...\", \"expanded_query\": \"...\"}"
                        ),
                    }
                ],
            )
            import json
            raw = msg.content[0].text
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            logger.warning(f"[Critic] Evaluation failed: {e}")
            return {
                "verdict": "sufficient" if chunks else "insufficient",
                "confidence": 0.6,
                "reason": "Heuristic evaluation",
                "expanded_query": query,
            }
