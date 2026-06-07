"""Citation formatting tool."""
from typing import List, Dict, Any
class CitationTool:
    name = "format_citations"
    description = "Format source references into proper citations."
    def run(self, sources: List[Dict[str, Any]]) -> str:
        lines = []
        for i, src in enumerate(sources, 1):
            doc_id = src.get("document_id", "unknown")
            excerpt = src.get("text", "")[:100]
            lines.append(f"[{i}] Document {doc_id}: \"{excerpt}...\"")
        return "\n".join(lines)
