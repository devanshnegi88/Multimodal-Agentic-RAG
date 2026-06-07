"""
OCR Engine — extract text from images using Tesseract + Claude Vision fallback
"""
from typing import Dict, Any
from app.utils.logger import logger


class OCREngine:
    async def extract_text(self, image_path: str = None, image_base64: str = None, mime_type: str = "image/png") -> str:
        """Extract text from image. Tries Tesseract first, falls back to Claude Vision."""
        # Try Tesseract
        tesseract_text = await self._tesseract_ocr(image_path) if image_path else ""
        if tesseract_text.strip() and len(tesseract_text) > 20:
            return tesseract_text

        # Fallback to Claude Vision OCR
        if image_base64:
            return await self._vision_ocr(image_base64, mime_type)
        return tesseract_text

    async def _tesseract_ocr(self, image_path: str) -> str:
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang="eng")
            return text.strip()
        except Exception as e:
            logger.warning(f"[OCR] Tesseract failed: {e}")
            return ""

    async def _vision_ocr(self, image_base64: str, mime_type: str) -> str:
        try:
            import anthropic
            from app.config import settings

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {"type": "base64", "media_type": mime_type, "data": image_base64},
                            },
                            {"type": "text", "text": "Extract ALL text from this image verbatim. Preserve formatting and structure. Only output the extracted text."},
                        ],
                    }
                ],
            )
            return msg.content[0].text
        except Exception as e:
            logger.error(f"[OCR] Vision OCR failed: {e}")
            return ""
