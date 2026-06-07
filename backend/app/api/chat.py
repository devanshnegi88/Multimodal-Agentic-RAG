"""
Chat API — REST + WebSocket streaming with agentic RAG
"""
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from bson import ObjectId
from datetime import datetime

from app.database.mongodb import get_database
from app.database.schemas import ChatRequest, ChatResponse
from app.agents.coordinator_agent import CoordinatorAgent
from app.utils.logger import logger

router = APIRouter()


@router.post("/message")
async def send_message(payload: ChatRequest, db=Depends(get_database)):
    """Non-streaming chat endpoint."""
    session_id = payload.session_id or str(ObjectId())

    # Get or create session
    session = await db["chat_sessions"].find_one({"_id": session_id})
    if not session:
        session = {
            "_id": session_id,
            "title": payload.message[:50],
            "messages": [],
            "document_ids": payload.document_ids or [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await db["chat_sessions"].insert_one(session)

    # Add user message
    user_msg = {"role": "user", "content": payload.message, "timestamp": datetime.utcnow().isoformat()}
    await db["chat_sessions"].update_one(
        {"_id": session_id},
        {"$push": {"messages": user_msg}, "$set": {"updated_at": datetime.utcnow()}},
    )

    # Run agentic workflow
    coordinator = CoordinatorAgent(db=db)
    result = await coordinator.run(
        query=payload.message,
        session_id=session_id,
        document_ids=payload.document_ids,
        use_web_search=payload.use_web_search,
        history=session.get("messages", []),
    )

    # Save assistant message
    assistant_msg = {
        "role": "assistant",
        "content": result["answer"],
        "sources": result.get("sources", []),
        "agent_steps": result.get("agent_steps", []),
        "timestamp": datetime.utcnow().isoformat(),
    }
    await db["chat_sessions"].update_one(
        {"_id": session_id},
        {"$push": {"messages": assistant_msg}},
    )

    return {
        "session_id": session_id,
        "message": assistant_msg,
        "citations": result.get("citations", []),
    }


@router.websocket("/ws/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str, db=Depends(get_database)):
    """WebSocket endpoint for streaming chat."""
    await websocket.accept()
    logger.info(f"WebSocket connected: {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            query = payload.get("message", "")
            document_ids = payload.get("document_ids", [])
            use_web_search = payload.get("use_web_search", False)

            # Stream agent status updates
            await websocket.send_json({"type": "status", "data": {"agent": "coordinator", "status": "starting"}})

            coordinator = CoordinatorAgent(db=db)

            async for chunk in coordinator.stream(
                query=query,
                session_id=session_id,
                document_ids=document_ids,
                use_web_search=use_web_search,
            ):
                await websocket.send_json(chunk)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"type": "error", "data": {"message": str(e)}})
        await websocket.close()


@router.get("/sessions")
async def list_sessions(db=Depends(get_database)):
    """List all chat sessions."""
    cursor = db["chat_sessions"].find().sort("updated_at", -1).limit(50)
    sessions = await cursor.to_list(length=50)
    for s in sessions:
        s["id"] = s.pop("_id")
    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db=Depends(get_database)):
    """Get a specific chat session."""
    session = await db["chat_sessions"].find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["id"] = session.pop("_id")
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db=Depends(get_database)):
    """Delete a chat session."""
    result = await db["chat_sessions"].delete_one({"_id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}
