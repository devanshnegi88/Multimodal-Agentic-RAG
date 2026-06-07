"""
User settings API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.database.mongodb import get_database

router = APIRouter()


class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    embedding_model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    top_k: Optional[int] = None
    use_reranker: Optional[bool] = None
    use_hybrid_search: Optional[bool] = None
    theme: Optional[str] = None


@router.get("/")
async def get_settings(db=Depends(get_database)):
    """Get current user settings."""
    # Return defaults
    return {
        "llm_provider": "anthropic",
        "llm_model": "claude-3-5-sonnet-20241022",
        "embedding_model": "text-embedding-3-small",
        "chunk_size": 512,
        "chunk_overlap": 64,
        "top_k": 5,
        "use_reranker": True,
        "use_hybrid_search": True,
        "theme": "dark",
    }


@router.patch("/")
async def update_settings(payload: SettingsUpdate, db=Depends(get_database)):
    """Update user settings."""
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    # In prod: update user's settings doc
    return {"message": "Settings updated", "updated": update_data}
