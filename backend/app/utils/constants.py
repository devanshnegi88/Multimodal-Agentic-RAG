"""
Application-wide constants
"""

# File types
SUPPORTED_FILE_TYPES = {
    "documents": ["pdf", "docx", "doc", "txt", "md"],
    "images": ["png", "jpg", "jpeg", "gif", "webp"],
    "spreadsheets": ["xlsx", "xls", "csv"],
    "presentations": ["pptx", "ppt"],
    "audio": ["mp3", "wav", "m4a"],
    "video": ["mp4", "mov", "avi"],
}

# RAG
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64
DEFAULT_TOP_K = 5
MAX_CONTEXT_TOKENS = 8000

# Agent names
AGENTS = ["coordinator", "planner", "retrieval", "vision", "web_search", "memory", "critic", "answer"]

# Collection names
USERS_COLLECTION = "users"
DOCUMENTS_COLLECTION = "documents"
CHUNKS_COLLECTION = "chunks"
SESSIONS_COLLECTION = "chat_sessions"
ANALYTICS_COLLECTION = "analytics"

# Status codes
STATUS_PROCESSING = "processing"
STATUS_READY = "ready"
STATUS_FAILED = "failed"
