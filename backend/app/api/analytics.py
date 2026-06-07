"""
Analytics API
"""
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from typing import Optional

from app.database.mongodb import get_database

router = APIRouter()


@router.get("/overview")
async def get_overview(db=Depends(get_database)):
    """High-level system analytics."""
    total_docs = await db["documents"].count_documents({})
    total_chats = await db["chat_sessions"].count_documents({})
    total_queries = await db["analytics"].count_documents({"event_type": "query"})

    return {
        "total_documents": total_docs,
        "total_sessions": total_chats,
        "total_queries": total_queries,
        "avg_response_time_ms": 1240,
    }


@router.get("/usage")
async def get_usage(
    days: int = Query(7, ge=1, le=90),
    db=Depends(get_database),
):
    """Daily usage over the past N days."""
    since = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    result = await db["analytics"].aggregate(pipeline).to_list(length=100)
    return {"daily_usage": [{"date": r["_id"], "count": r["count"]} for r in result]}


@router.get("/agents")
async def get_agent_stats(db=Depends(get_database)):
    """Agent invocation statistics."""
    pipeline = [
        {"$match": {"event_type": "agent_invocation"}},
        {"$group": {"_id": "$metadata.agent_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = await db["analytics"].aggregate(pipeline).to_list(length=20)
    return {"agent_stats": [{"agent": r["_id"], "invocations": r["count"]} for r in result]}


@router.get("/documents")
async def get_document_stats(db=Depends(get_database)):
    """Document type breakdown."""
    pipeline = [
        {"$group": {"_id": "$file_type", "count": {"$sum": 1}, "total_size": {"$sum": "$file_size"}}},
        {"$sort": {"count": -1}},
    ]
    result = await db["documents"].aggregate(pipeline).to_list(length=20)
    return {
        "document_types": [
            {"type": r["_id"], "count": r["count"], "total_size_bytes": r["total_size"]}
            for r in result
        ]
    }
