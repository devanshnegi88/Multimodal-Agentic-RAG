"""
Document chunking strategies
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "metadata": self.metadata or {},
        }


class RecursiveTextSplitter:
    """Recursive character-based text splitter."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def split(self, text: str) -> List[Chunk]:
        chunks = []
        current_pos = 0
        chunk_idx = 0

        while current_pos < len(text):
            end_pos = min(current_pos + self.chunk_size, len(text))

            # Find best split point
            if end_pos < len(text):
                for sep in self.separators:
                    split_pos = text.rfind(sep, current_pos, end_pos)
                    if split_pos > current_pos:
                        end_pos = split_pos + len(sep)
                        break

            chunk_text = text[current_pos:end_pos].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        chunk_index=chunk_idx,
                        start_char=current_pos,
                        end_char=end_pos,
                    )
                )
                chunk_idx += 1

            current_pos = max(current_pos + 1, end_pos - self.chunk_overlap)

        return chunks


class SemanticChunker:
    """Splits text at semantic boundaries (paragraphs, sections)."""

    def split(self, text: str, max_chunk_size: int = 1024) -> List[Chunk]:
        # Split on double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current = ""
        start = 0
        idx = 0

        for para in paragraphs:
            if len(current) + len(para) > max_chunk_size and current:
                chunks.append(Chunk(text=current.strip(), chunk_index=idx, start_char=start, end_char=start + len(current)))
                start += len(current)
                idx += 1
                current = para + "\n\n"
            else:
                current += para + "\n\n"

        if current.strip():
            chunks.append(Chunk(text=current.strip(), chunk_index=idx, start_char=start, end_char=start + len(current)))

        return chunks


class MarkdownChunker:
    """Splits markdown documents at heading boundaries."""

    HEADING_RE = re.compile(r"^#{1,3}\s+.+$", re.MULTILINE)

    def split(self, text: str) -> List[Chunk]:
        positions = [m.start() for m in self.HEADING_RE.finditer(text)]
        positions.append(len(text))

        chunks = []
        for i, pos in enumerate(positions[:-1]):
            chunk_text = text[pos:positions[i + 1]].strip()
            if chunk_text:
                chunks.append(
                    Chunk(text=chunk_text, chunk_index=i, start_char=pos, end_char=positions[i + 1])
                )
        return chunks
