"""
Vision Agent — processes image and chart chunks via LLM vision
"""
import base64
from typing import List, Dict, Any
from app.utils.logger import logger


class VisionAgent:
    """Uses Claude's vision capability to describe images/charts from document chunks."""

    async def process_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process all image-modality chunks and return descriptions."""
        results = []
        for chunk in chunks:
            if chunk.get("modality") != "image":
                continue
            desc = await self._describe_image(chunk)
            if desc:
                results.append({
                    "chunk_id": chunk.get("id"),
                    "document_id": chunk.get("document_id"),
                    "description": desc,
                    "original_chunk": chunk,
                })
        return results

    async def _describe_image(self, chunk: Dict[str, Any]) -> str:
        """Call Claude vision to describe an image chunk."""
        try:
            import anthropic
            from app.config import settings

            image_data = chunk.get("image_base64")
            if not image_data:
                return ""

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": chunk.get("mime_type", "image/png"),
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Describe this image/chart concisely for use in a RAG answer. Focus on data, labels, trends, and key takeaways.",
                            },
                        ],
                    }
                ],
            )
            return msg.content[0].text
        except Exception as e:
            logger.warning(f"[Vision] Failed to process image chunk: {e}")
            return chunk.get("alt_text", "")

    async def analyze_uploaded_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        """Analyze an arbitrary uploaded image."""
        try:
            import anthropic
            from app.config import settings

            b64 = base64.b64encode(image_bytes).decode()
            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": b64}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
            return msg.content[0].text
        except Exception as e:
            logger.error(f"[Vision] Image analysis failed: {e}")
            return "Image analysis unavailable."
