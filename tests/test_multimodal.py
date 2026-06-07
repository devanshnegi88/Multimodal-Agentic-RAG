"""
Tests for multimodal processing components
"""
import pytest
import os
import tempfile


class TestRecursiveTextSplitter:
    """Already in test_rag.py but adding multimodal-specific chunk tests."""
    pass


class TestTableExtractor:
    @pytest.mark.asyncio
    async def test_extract_from_csv(self):
        from backend.app.multimodal.table_extractor import TableExtractor

        # Create a temporary CSV
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            f.write("name,age,score\nAlice,30,95\nBob,25,87\nCharlie,35,91\n")
            csv_path = f.name

        try:
            extractor = TableExtractor()
            tables = await extractor.extract_from_csv(csv_path)
            assert len(tables) == 1
            table = tables[0]
            assert table["shape"][0] == 3  # 3 data rows
            assert table["shape"][1] == 3  # 3 columns
            assert "name" in table["text"]
        finally:
            os.unlink(csv_path)

    def test_table_to_text(self):
        from backend.app.multimodal.table_extractor import TableExtractor
        extractor = TableExtractor()
        table = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
        text = extractor.table_to_text(table)
        assert "Name" in text
        assert "Alice" in text
        assert "Bob" in text

    def test_empty_table(self):
        from backend.app.multimodal.table_extractor import TableExtractor
        extractor = TableExtractor()
        assert extractor.table_to_text([]) == ""


class TestOCREngine:
    @pytest.mark.asyncio
    async def test_empty_input_returns_empty(self):
        from backend.app.multimodal.ocr_engine import OCREngine
        engine = OCREngine()
        result = await engine.extract_text(image_path=None, image_base64=None)
        assert result == ""

    @pytest.mark.asyncio
    async def test_tesseract_fallback(self):
        """Test that OCR gracefully fails when Tesseract is not configured."""
        from backend.app.multimodal.ocr_engine import OCREngine
        engine = OCREngine()
        # Pass a non-existent path — should return empty string, not raise
        result = await engine._tesseract_ocr("/nonexistent/path.png")
        assert result == ""


class TestImageProcessor:
    @pytest.mark.asyncio
    async def test_process_nonexistent_file(self):
        from backend.app.multimodal.image_processor import ImageProcessor
        processor = ImageProcessor()
        result = await processor.process("/nonexistent/image.png")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_process_valid_image(self):
        from backend.app.multimodal.image_processor import ImageProcessor
        from PIL import Image
        import io

        # Create a tiny test image
        img = Image.new("RGB", (100, 100), color=(73, 109, 137))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f.name)
            img_path = f.name

        try:
            processor = ImageProcessor()
            result = await processor.process(img_path)
            assert "image_base64" in result
            assert result["mime_type"] == "image/jpeg"
            assert "original_size" in result
        finally:
            os.unlink(img_path)


class TestUploadService:
    @pytest.mark.asyncio
    async def test_parse_txt_file(self):
        from backend.app.services.upload_service import UploadService

        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("Hello, this is test content for the upload service.\nLine two.")
            txt_path = f.name

        try:
            service = UploadService(db=None)
            chunks = await service._parse(txt_path, "txt")
            assert len(chunks) == 1
            assert "Hello" in chunks[0]["text"]
            assert chunks[0]["modality"] == "text"
        finally:
            os.unlink(txt_path)

    @pytest.mark.asyncio
    async def test_update_status_no_db(self):
        """Should not raise when db is None."""
        from backend.app.services.upload_service import UploadService
        service = UploadService(db=None)
        await service._update_status("doc-1", "ready", 10)  # Should not raise
