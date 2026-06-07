"""
Web Search Tool — LangChain-compatible tool wrapping Tavily
"""
from typing import Optional, Type
from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query to look up on the web")
    max_results: int = Field(default=5, description="Maximum number of results to return")


class WebSearchTool:
    """LangChain-compatible web search tool using Tavily."""

    name = "web_search"
    description = "Search the internet for current information. Use for questions about recent events, live data, or topics not in the document corpus."
    args_schema: Type[BaseModel] = WebSearchInput

    async def run(self, query: str, max_results: int = 5) -> str:
        from app.agents.web_search_agent import WebSearchAgent
        results = await WebSearchAgent().search(query, max_results=max_results)

        if not results:
            return "No results found."

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"[{i}] {r['title']}\n{r['url']}\n{r['content'][:300]}")

        return "\n\n".join(formatted)
