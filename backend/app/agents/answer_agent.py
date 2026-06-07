"""
Answer Agent — synthesizes the final answer with citations
"""
from typing import List, Dict, Any
from app.utils.prompts import ANSWER_SYSTEM_PROMPT
from app.rag.citation_generator import CitationGenerator
from app.utils.logger import logger


class AnswerAgent:
    def __init__(self):
        self.citation_gen = CitationGenerator()

    async def generate(
        self,
        query: str,
        chunks: List[Dict[str, Any]] = None,
        image_descriptions: List[Dict[str, Any]] = None,
        web_results: List[Dict[str, Any]] = None,
        memory_context: Dict[str, Any] = None,
        plan: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        chunks = chunks or []
        image_descriptions = image_descriptions or []
        web_results = web_results or []

        # Build context string
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(f"[SOURCE {i+1}] {chunk.get('text', '')}")
        for img in image_descriptions:
            context_parts.append(f"[IMAGE] {img.get('description', '')}")
        for w in web_results:
            context_parts.append(f"[WEB] {w.get('title', '')}: {w.get('content', '')[:300]}")

        context = "\n\n".join(context_parts)

        try:
            import anthropic
            from app.config import settings

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=ANSWER_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Question: {query}\n\n"
                            f"Context:\n{context[:6000]}\n\n"
                            "Provide a comprehensive, well-cited answer. Reference sources as [SOURCE N]."
                        ),
                    }
                ],
            )
            answer = msg.content[0].text

        except Exception as e:
            logger.warning(f"[Answer] LLM call failed: {e}")
            if chunks:
                answer = f"Based on the retrieved documents: {chunks[0].get('text', 'No content available.')[:500]}"
            else:
                answer = "I couldn't find relevant information to answer your question. Please try rephrasing or uploading relevant documents."

        # Generate citations
        citations = self.citation_gen.generate(answer, chunks, web_results)
        sources = [
            {
                "text": c.get("text", "")[:200],
                "document_id": c.get("document_id"),
                "score": c.get("score", 0.0),
                "metadata": c.get("metadata", {}),
            }
            for c in chunks[:5]
        ]

        return {
            "answer": answer,
            "sources": sources,
            "citations": citations,
        }
