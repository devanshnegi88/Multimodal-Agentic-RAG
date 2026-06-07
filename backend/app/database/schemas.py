"""
API request/response schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Auth ─────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime


# ── Chat ─────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    document_ids: Optional[List[str]] = []
    use_web_search: bool = False
    stream: bool = True


class ChatResponse(BaseModel):
    session_id: str
    message: ChatMessage
    agent_steps: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None


# ── Documents ─────────────────────────────────────────────────
class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int


# ── Analytics ─────────────────────────────────────────────────
class AnalyticsResponse(BaseModel):
    total_queries: int
    total_documents: int
    avg_response_time: float
    top_document_types: List[Dict[str, Any]]
    daily_usage: List[Dict[str, Any]]
    agent_usage: Dict[str, int]
