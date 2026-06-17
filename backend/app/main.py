"""
Multimodal Agentic RAG — FastAPI Application Entry Point
"""
import os
from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.middleware.gzip import GZipMiddleware
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.api import auth, chat, upload, documents, analytics, settings as settings_router
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Multimodal Agentic RAG API...")
    await connect_to_mongo()
    logger.info("✅ MongoDB connected")
    yield
    # Shutdown
    await close_mongo_connection()
    logger.info("👋 Application shutdown complete")


app = FastAPI(
    title="Multimodal Agentic RAG API",
    description="A production-grade multimodal agentic RAG system with LangGraph workflows",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── Middleware ────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ── Static Files ──────────────────────────────────────────────


os.makedirs("uploads", exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router,       prefix="/api/auth",      tags=["Auth"])
app.include_router(chat.router,       prefix="/api/chat",      tags=["Chat"])
app.include_router(upload.router,     prefix="/api/upload",    tags=["Upload"])
app.include_router(documents.router,  prefix="/api/documents", tags=["Documents"])
app.include_router(analytics.router,  prefix="/api/analytics", tags=["Analytics"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "service": "Multimodal Agentic RAG"}
