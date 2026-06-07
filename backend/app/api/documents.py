"""
Documents management API
"""
import os
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from app.database.mongodb import get_database
from app.utils.logger import logger

router = APIRouter()


@router.get("/")
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_type: Optional[str] = None,
    status: Optional[str] = None,
    db=Depends(get_database),
):
    """List all documents with pagination and filtering."""
    query = {}
    if file_type:
        query["file_type"] = file_type
    if status:
        query["status"] = status

    total = await db["documents"].count_documents(query)
    skip = (page - 1) * page_size

    cursor = db["documents"].find(query).sort("created_at", -1).skip(skip).limit(page_size)
    docs = await cursor.to_list(length=page_size)
    for d in docs:
        d["id"] = d.pop("_id")

    return {"documents": docs, "total": total, "page": page, "page_size": page_size}


@router.get("/{doc_id}")
async def get_document(doc_id: str, db=Depends(get_database)):
    """Get document details."""
    doc = await db["documents"].find_one({"_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc["id"] = doc.pop("_id")
    return doc


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db=Depends(get_database)):
    """Delete a document and its chunks."""
    doc = await db["documents"].find_one({"_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove file from disk
    try:
        if os.path.exists(doc["file_path"]):
            os.remove(doc["file_path"])
    except Exception as e:
        logger.warning(f"Could not delete file: {e}")

    # Remove from DB
    await db["documents"].delete_one({"_id": doc_id})
    await db["chunks"].delete_many({"document_id": doc_id})

    logger.info(f"Deleted document: {doc_id}")
    return {"message": "Document deleted successfully"}


@router.get("/{doc_id}/chunks")
async def get_document_chunks(doc_id: str, db=Depends(get_database)):
    """Get all chunks for a document."""
    doc = await db["documents"].find_one({"_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    cursor = db["chunks"].find({"document_id": doc_id}).sort("chunk_index", 1)
    chunks = await cursor.to_list(length=1000)
    for c in chunks:
        c["id"] = c.pop("_id")
    return {"chunks": chunks, "count": len(chunks)}
