"""
Chart Analyzer — extracts data and descriptions from chart images
"""
from typing import Dict, Any
from app.utils.logger import logger


class ChartAnalyzer:
    """Uses Claude Vision to extract insights from chart images."""

    CHART_PROMPT = """Analyze this chart/graph image and extract:
1. Chart type (bar, line, pie, scatter, etc.)
2. Title and axis labels if visible
3. Key data points and values
4. Main trend or insight
5. Any anomalies or notable patterns

Respond in a structured format suitable for a RAG system."""

    async def analyze(self, image_base64: str, mime_type: str = "image/png") -> Dict[str, Any]:
        try:
            import anthropic
            from app.config import settings

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {"type": "base64", "media_type": mime_type, "data": image_base64},
                            },
                            {"type": "text", "text": self.CHART_PROMPT},
                        ],
                    }
                ],
            )
            analysis = msg.content[0].text
            return {
                "analysis": analysis,
                "modality": "chart",
                "text": analysis,
            }
        except Exception as e:
            logger.error(f"[ChartAnalyzer] Failed: {e}")
            return {"analysis": "Chart analysis unavailable", "modality": "chart", "text": ""}
