"""SQL query tool (read-only) for structured document metadata."""
class SQLTool:
    name = "sql_query"
    description = "Run read-only SQL-like queries on document metadata."
    def __init__(self, db=None):
        self.db = db
    async def run(self, collection: str, filter_dict: dict, limit: int = 10) -> str:
        if self.db is None:
            return "Database unavailable."
        cursor = self.db[collection].find(filter_dict).limit(limit)
        docs = await cursor.to_list(length=limit)
        return str([{k: v for k, v in d.items() if k != "_id"} for d in docs])
