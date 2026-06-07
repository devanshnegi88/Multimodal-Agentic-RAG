"""Document retrieval tool for direct chunk lookup."""
from typing import Optional

class DocumentTool:
    name = "document_lookup"
    description = "Look up specific content from a document by document_id and query."
    def __init__(self, db=None):
        self.db = db
    async def run(self, document_id: str, query: str) -> str:
        if self.db is None:
            return "Database unavailable."
        cursor = self.db["chunks"].find({"document_id": document_id}).limit(5)
        chunks = await cursor.to_list(length=5)
        return "\n---\n".join(c.get("text", "") for c in chunks) or "No content found."
