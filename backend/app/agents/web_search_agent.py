"""
Web Search Agent — uses Tavily to fetch live web results
"""
from typing import List, Dict, Any
from app.utils.logger import logger


class WebSearchAgent:
    """Performs web searches using Tavily API."""

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        try:
            from tavily import AsyncTavilyClient
            from app.config import settings

            client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
            response = await client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
            )
            results = []
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": r.get("content"),
                    "score": r.get("score", 0.0),
                    "source": "web",
                })
            logger.info(f"[WebSearch] Found {len(results)} results for: {query[:60]}")
            return results
        except Exception as e:
            logger.warning(f"[WebSearch] Search failed: {e}")
            return []

    async def fetch_page(self, url: str) -> str:
        """Fetch full page content via Tavily."""
        try:
            from tavily import AsyncTavilyClient
            from app.config import settings

            client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
            response = await client.extract(urls=[url])
            return response.get("results", [{}])[0].get("raw_content", "")
        except Exception as e:
            logger.warning(f"[WebSearch] Page fetch failed: {e}")
            return ""
