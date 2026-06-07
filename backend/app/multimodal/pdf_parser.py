"""
PDF Parser — extracts text, images, and tables from PDFs
"""
import os
import base64
from typing import List, Dict, Any
from app.utils.logger import logger


class PDFParser:
    """
    Uses PyMuPDF (fitz) and pdfplumber for comprehensive PDF parsing.
    Extracts: text blocks, embedded images, and tables.
    """

    async def parse(self, file_path: str) -> Dict[str, Any]:
        result = {"text_chunks": [], "images": [], "tables": [], "metadata": {}}

        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            result["metadata"] = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
            }

            for page_num, page in enumerate(doc):
                # Extract text
                text = page.get_text("text")
                if text.strip():
                    result["text_chunks"].append({
                        "text": text.strip(),
                        "page": page_num + 1,
                        "modality": "text",
                    })

                # Extract images
                for img_index, img in enumerate(page.get_images(full=True)):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        img_bytes = base_image["image"]
                        img_b64 = base64.b64encode(img_bytes).decode()
                        result["images"].append({
                            "page": page_num + 1,
                            "index": img_index,
                            "image_base64": img_b64,
                            "mime_type": f"image/{base_image['ext']}",
                            "modality": "image",
                        })
                    except Exception:
                        pass

            doc.close()
        except Exception as e:
            logger.error(f"[PDFParser] PyMuPDF error: {e}")

        # Extract tables with pdfplumber
        try:
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    for tbl_idx, table in enumerate(tables):
                        if table:
                            result["tables"].append({
                                "page": page_num + 1,
                                "index": tbl_idx,
                                "data": table,
                                "modality": "table",
                            })
        except Exception as e:
            logger.warning(f"[PDFParser] pdfplumber error: {e}")

        logger.info(
            f"[PDFParser] Parsed {file_path}: "
            f"{len(result['text_chunks'])} pages, "
            f"{len(result['images'])} images, "
            f"{len(result['tables'])} tables"
        )
        return result
