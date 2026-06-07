"""
Image Processor — resize, normalize, extract metadata from images
"""
import base64
import io
from typing import Dict, Any, Tuple
from app.utils.logger import logger


class ImageProcessor:
    MAX_SIZE = (1024, 1024)

    async def process(self, file_path: str) -> Dict[str, Any]:
        try:
            from PIL import Image, ExifTags

            img = Image.open(file_path)
            original_size = img.size
            img_format = img.format or "PNG"

            # Resize if needed
            if img.width > self.MAX_SIZE[0] or img.height > self.MAX_SIZE[1]:
                img.thumbnail(self.MAX_SIZE, Image.LANCZOS)

            # Convert to RGB for JPEG
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Encode to base64
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            b64 = base64.b64encode(buffer.getvalue()).decode()

            # Extract EXIF
            exif_data = {}
            try:
                raw_exif = img._getexif()
                if raw_exif:
                    exif_data = {
                        ExifTags.TAGS.get(tag, tag): str(val)
                        for tag, val in raw_exif.items()
                        if tag in ExifTags.TAGS
                    }
            except Exception:
                pass

            return {
                "image_base64": b64,
                "mime_type": "image/jpeg",
                "original_size": original_size,
                "processed_size": img.size,
                "format": img_format,
                "exif": exif_data,
                "modality": "image",
            }
        except Exception as e:
            logger.error(f"[ImageProcessor] Failed: {e}")
            return {"error": str(e)}

    async def to_base64(self, file_path: str) -> Tuple[str, str]:
        """Return (base64_str, mime_type) for a raw image file."""
        try:
            from PIL import Image
            import io

            img = Image.open(file_path)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode(), "image/png"
        except Exception as e:
            logger.error(f"[ImageProcessor] to_base64 failed: {e}")
            return "", "image/png"
