"""
Citation Generator — maps [SOURCE N] references to structured citations
"""
import re
from typing import List, Dict, Any


class CitationGenerator:
    def generate(
        self,
        answer: str,
        chunks: List[Dict[str, Any]],
        web_results: List[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Parse [SOURCE N] and [WEB] markers from the answer
        and map them to structured citation objects.
        """
        citations = []
        seen = set()

        # Find all [SOURCE N] references
        source_refs = re.findall(r"\[SOURCE\s+(\d+)\]", answer)
        for ref in source_refs:
            idx = int(ref) - 1
            if 0 <= idx < len(chunks) and idx not in seen:
                seen.add(idx)
                chunk = chunks[idx]
                citations.append({
                    "ref_id": f"SOURCE {ref}",
                    "type": "document",
                    "text_excerpt": chunk.get("text", "")[:200],
                    "document_id": chunk.get("document_id"),
                    "metadata": chunk.get("metadata", {}),
                    "score": chunk.get("score", 0.0),
                })

        # Find [WEB] references
        web_count = len(re.findall(r"\[WEB\]", answer))
        for i in range(min(web_count, len(web_results or []))):
            w = (web_results or [])[i]
            citations.append({
                "ref_id": f"WEB {i+1}",
                "type": "web",
                "title": w.get("title"),
                "url": w.get("url"),
                "text_excerpt": w.get("content", "")[:200],
            })

        return citations
