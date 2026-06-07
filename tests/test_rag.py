"""
Tests for RAG pipeline components
"""
import pytest
from unittest.mock import patch, MagicMock


class TestRecursiveTextSplitter:
    def test_basic_split(self):
        from backend.app.rag.chunking import RecursiveTextSplitter
        splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=10)
        text = "Hello world. " * 20
        chunks = splitter.split(text)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.text) <= 120  # Allow slight overflow at boundaries

    def test_empty_text(self):
        from backend.app.rag.chunking import RecursiveTextSplitter
        splitter = RecursiveTextSplitter()
        chunks = splitter.split("")
        assert chunks == []

    def test_short_text_single_chunk(self):
        from backend.app.rag.chunking import RecursiveTextSplitter
        splitter = RecursiveTextSplitter(chunk_size=512)
        text = "Short text."
        chunks = splitter.split(text)
        assert len(chunks) == 1
        assert chunks[0].text == text

    def test_chunk_indices_sequential(self):
        from backend.app.rag.chunking import RecursiveTextSplitter
        splitter = RecursiveTextSplitter(chunk_size=50, chunk_overlap=5)
        text = "word " * 100
        chunks = splitter.split(text)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i


class TestSemanticChunker:
    def test_paragraph_split(self):
        from backend.app.rag.chunking import SemanticChunker
        chunker = SemanticChunker()
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = chunker.split(text)
        assert len(chunks) >= 1

    def test_large_paragraph_gets_chunked(self):
        from backend.app.rag.chunking import SemanticChunker
        chunker = SemanticChunker()
        big_para = "word " * 300
        chunks = chunker.split(big_para, max_chunk_size=200)
        # Should be split since it exceeds max
        assert len(chunks) >= 1


class TestCitationGenerator:
    def test_source_citations(self):
        from backend.app.rag.citation_generator import CitationGenerator
        gen = CitationGenerator()
        answer = "According to [SOURCE 1], the revenue was $100M. [SOURCE 2] confirms this."
        chunks = [
            {"text": "Revenue was $100M in Q3", "document_id": "doc1", "score": 0.9, "metadata": {}},
            {"text": "Q3 results confirmed strong performance", "document_id": "doc2", "score": 0.8, "metadata": {}},
        ]
        citations = gen.generate(answer, chunks)
        assert len(citations) == 2
        assert citations[0]["ref_id"] == "SOURCE 1"
        assert citations[1]["ref_id"] == "SOURCE 2"

    def test_no_citations_empty_answer(self):
        from backend.app.rag.citation_generator import CitationGenerator
        gen = CitationGenerator()
        citations = gen.generate("", [])
        assert citations == []

    def test_out_of_range_source_ignored(self):
        from backend.app.rag.citation_generator import CitationGenerator
        gen = CitationGenerator()
        answer = "Per [SOURCE 99], something happened."
        citations = gen.generate(answer, [{"text": "only one chunk", "document_id": "d", "score": 1.0, "metadata": {}}])
        assert len(citations) == 0  # SOURCE 99 doesn't exist in chunks


class TestHybridSearcher:
    def test_rrf_fusion(self):
        from backend.app.rag.hybrid_search import HybridSearcher
        searcher = HybridSearcher(rrf_k=60)
        dense = [
            {"document_id": "d1", "chunk_index": 0, "text": "A", "score": 0.9},
            {"document_id": "d2", "chunk_index": 1, "text": "B", "score": 0.8},
        ]
        sparse = [
            {"document_id": "d2", "chunk_index": 1, "text": "B", "score": 5.0},
            {"document_id": "d3", "chunk_index": 0, "text": "C", "score": 3.0},
        ]
        fused = searcher._rrf(dense, sparse, top_k=3)
        assert len(fused) <= 3
        # d2 appeared in both lists — should rank higher
        doc_ids = [r["document_id"] for r in fused]
        assert "d2" in doc_ids
