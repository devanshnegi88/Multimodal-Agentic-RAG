# Multimodal Agentic RAG — Architecture

## Overview

A production-grade, full-stack Retrieval-Augmented Generation (RAG) system with:

- **8 specialized AI agents** orchestrated by LangGraph
- **Multimodal ingestion** — PDF, images, audio, video, Excel, PPTX
- **Hybrid search** — dense (Qdrant) + sparse (BM25) with reranking
- **Real-time streaming** via WebSocket
- **React frontend** with live agent pipeline visualization

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│   Dashboard │ Chat │ Documents │ Analytics │ Settings            │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP REST + WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend                              │
│   /api/auth │ /api/chat │ /api/upload │ /api/documents           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   Coordinator Agent                              │
│                    (LangGraph DAG)                               │
└──┬────────┬─────────┬──────────┬────────┬────────┬─────────────┘
   │        │         │          │        │        │
 Memory  Planner  Retrieval  Vision  WebSearch  Critic  Answer
   │        │         │          │        │        │      │
 Redis   Claude   Qdrant+    Claude  Tavily  Claude Claude
         Haiku    BM25+      Vision   API    Haiku  Sonnet
                  Cohere
```

---

## Agent Pipeline

### 1. Memory Agent
- Loads conversation history from Redis
- Maintains sliding window (last 10 messages)
- Periodic LLM summarization for long conversations
- Vector memory for cross-session recall

### 2. Planner Agent
- Classifies query intent (QA, summarization, comparison, extraction)
- Decomposes complex queries into sub-queries
- Selects retrieval strategy (rag_only | web_only | rag_and_web | vision_rag)
- Determines `top_k` based on query complexity

### 3. Retrieval Agent
- **Dense retrieval**: Qdrant vector search (OpenAI embeddings)
- **Sparse retrieval**: BM25 over document corpus
- **Fusion**: Reciprocal Rank Fusion (RRF) combining both
- **Reranking**: Cohere cross-encoder for final ordering

### 4. Vision Agent
- Processes image chunks using Claude 3.5 Sonnet vision
- Extracts data from charts, diagrams, screenshots
- OCR fallback via Tesseract + Claude Vision

### 5. Web Search Agent
- Real-time internet search via Tavily API
- Triggered when: (a) plan decides, (b) user enables, (c) critic finds insufficient context

### 6. Critic Agent
- Evaluates retrieved context quality (RAGAS-inspired)
- Returns: `sufficient | insufficient | partial` verdict
- Triggers retry with expanded query if insufficient

### 7. Answer Agent
- Synthesizes final answer from all context sources
- Generates structured citations `[SOURCE N]`
- Produces source attribution cards

---

## Data Flow — Document Ingestion

```
Upload → Parse → Chunk → Embed → Upsert
   │        │       │       │       │
 HTTP    PyMuPDF  512-tok OpenAI  Qdrant
        Pillow   overlap  3-small  +FAISS
        Whisper  Semantic          (fallback)
        OpenPyXL Markdown
```

### Supported Formats
| Type | Parser | Output |
|------|--------|--------|
| PDF | PyMuPDF + pdfplumber | text, images, tables |
| Images | Pillow + Tesseract + Claude Vision | text, description |
| Audio | OpenAI Whisper | transcript |
| Video | OpenCV + Whisper | frames, transcript |
| Excel/CSV | pandas | structured tables |
| PPTX | python-pptx | slide text |
| DOCX | python-docx | paragraphs |

---

## Technology Stack

### Backend
- **FastAPI** — async REST API + WebSocket
- **LangGraph** — agent state machine orchestration
- **Anthropic Claude** — LLM for all reasoning tasks
- **OpenAI** — embeddings (text-embedding-3-small)
- **Qdrant** — primary vector database
- **FAISS** — local fallback vector store
- **MongoDB** — document metadata and chat history
- **Redis** — session memory and caching
- **Cohere** — cross-encoder reranking
- **Tavily** — web search API

### Frontend
- **React 18** — UI framework
- **React Router v6** — client-side routing
- **TanStack Query** — server state management
- **Recharts** — analytics charts
- **Framer Motion** — animations
- **React Dropzone** — file uploads
- **React Markdown** — message rendering

---

## Security

- JWT authentication with refresh token rotation
- BCrypt password hashing
- CORS configured for production
- Non-root Docker user
- Nginx security headers (X-Frame-Options, CSP, etc.)
- File size limits (100MB default)
- File type validation whitelist
