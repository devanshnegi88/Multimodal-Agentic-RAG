"""
General utility helpers
"""
import hashlib
import uuid
import re
from typing import Any, Dict, List
from datetime import datetime


def generate_id() -> str:
    return str(uuid.uuid4())


def hash_file(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def truncate_text(text: str, max_chars: int = 200) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def sanitize_filename(filename: str) -> str:
    name = re.sub(r"[^\w\s\-.]", "", filename)
    return name.strip().replace(" ", "_")


def format_file_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def flatten_chunks(nested: List[List[Dict]]) -> List[Dict]:
    return [chunk for group in nested for chunk in group]


def utcnow_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def chunk_list(lst: List[Any], n: int) -> List[List[Any]]:
    """Split list into chunks of size n."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]
