"""
File upload API — multimodal document ingestion
"""
import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi import Form
from typing import List
from datetime import datetime

from app.config import settings
from app.database.mongodb import get_database
from app.services.upload_service import UploadService
from app.utils.logger import logger

router = APIRouter()

ALLOWED_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg", "gif", "webp",
    "mp4", "mov", "avi", "mp3", "wav", "m4a",
    "xlsx", "xls", "csv", "pptx", "ppt", "docx", "doc",
    "txt", "md",
}

FILE_TYPE_MAP = {
    "pdf": "pdfs", "png": "images", "jpg": "images", "jpeg": "images",
    "gif": "images", "webp": "images", "mp4": "videos", "mov": "videos",
    "avi": "videos", "mp3": "audio", "wav": "audio", "m4a": "audio",
    "xlsx": "excel", "xls": "excel", "csv": "excel",
    "pptx": "ppt", "ppt": "ppt", "docx": "pdfs", "doc": "pdfs",
    "txt": "pdfs", "md": "pdfs",
}


@router.post("/")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db=Depends(get_database),
):
    """Upload one or more files for ingestion into the RAG pipeline."""
    results = []

    for file in files:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File type .{ext} not supported")

        content = await file.read()
        file_size = len(content)
        if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large (max {settings.MAX_FILE_SIZE_MB}MB)")

        # Persist to disk
        subfolder = FILE_TYPE_MAP.get(ext, "pdfs")
        save_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
        os.makedirs(save_dir, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(save_dir, unique_name)

        with open(file_path, "wb") as f:
            f.write(content)

        # Save DB record
        doc_id = str(uuid.uuid4())
        doc_record = {
            "_id": doc_id,
            "user_id": "anonymous",
            "filename": unique_name,
            "original_name": file.filename,
            "file_type": ext,
            "file_size": file_size,
            "file_path": file_path,
            "status": "processing",
            "chunk_count": 0,
            "metadata": {},
            "created_at": datetime.utcnow(),
        }
        await db["documents"].insert_one(doc_record)

        # Background ingestion
        background_tasks.add_task(
            UploadService(db=db).process_document, doc_id, file_path, ext
        )

        results.append({
            "id": doc_id,
            "original_name": file.filename,
            "file_type": ext,
            "file_size": file_size,
            "status": "processing",
        })
        logger.info(f"Uploaded file: {file.filename} → {file_path}")

    return {"uploaded": results, "count": len(results)}


@router.get("/status/{doc_id}")
async def get_upload_status(doc_id: str, db=Depends(get_database)):
    """Poll ingestion status for a document."""
    doc = await db["documents"].find_one({"_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc["_id"],
        "status": doc["status"],
        "chunk_count": doc.get("chunk_count", 0),
        "original_name": doc["original_name"],
    }
