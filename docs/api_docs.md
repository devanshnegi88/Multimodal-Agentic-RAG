# API Documentation

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/api/docs` (Swagger UI)

---

## Authentication

### POST /auth/register
Create a new user account.

**Request:**
```json
{ "email": "user@example.com", "username": "myuser", "password": "securepass123" }
```
**Response:** `201 Created`
```json
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer" }
```

### POST /auth/login
Authenticate and receive tokens.

**Request:**
```json
{ "email": "user@example.com", "password": "securepass123" }
```

### POST /auth/refresh
Refresh an expired access token.

**Request:**
```json
{ "refresh_token": "eyJ..." }
```

---

## Chat

All chat endpoints require `Authorization: Bearer <token>`.

### POST /chat/message
Send a message and get an AI response.

**Request:**
```json
{
  "message": "What is the revenue for Q3?",
  "session_id": "optional-session-id",
  "document_ids": ["doc-uuid-1", "doc-uuid-2"],
  "use_web_search": false,
  "stream": false
}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "message": {
    "role": "assistant",
    "content": "Based on [SOURCE 1], Q3 revenue was $42M...",
    "sources": [...],
    "timestamp": "2025-01-01T00:00:00Z"
  },
  "citations": [
    { "ref_id": "SOURCE 1", "type": "document", "text_excerpt": "...", "document_id": "doc-uuid" }
  ]
}
```

### WebSocket /chat/ws/{session_id}
Stream responses in real-time.

**Send:**
```json
{ "message": "...", "document_ids": [...], "use_web_search": false }
```

**Receive events:**
```json
{ "type": "status", "data": { "agent": "planner", "status": "running" } }
{ "type": "token",  "data": { "text": "Based " } }
{ "type": "done",   "data": { "sources": [...], "citations": [...] } }
```

### GET /chat/sessions
List all chat sessions.

### GET /chat/sessions/{session_id}
Get a specific session with all messages.

### DELETE /chat/sessions/{session_id}
Delete a chat session.

---

## Upload

### POST /upload/
Upload one or more files for ingestion.

**Request:** `multipart/form-data` with `files[]` field.

**Response:**
```json
{
  "uploaded": [
    { "id": "doc-uuid", "original_name": "report.pdf", "status": "processing" }
  ],
  "count": 1
}
```

### GET /upload/status/{doc_id}
Poll ingestion status.

**Response:**
```json
{ "id": "doc-uuid", "status": "ready", "chunk_count": 42, "original_name": "report.pdf" }
```

Status values: `processing | ready | failed`

---

## Documents

### GET /documents/
List documents with pagination.

**Query params:** `page`, `page_size`, `file_type`, `status`

### GET /documents/{doc_id}
Get document metadata and details.

### DELETE /documents/{doc_id}
Delete a document and all its chunks.

### GET /documents/{doc_id}/chunks
Get all extracted chunks for a document.

---

## Analytics

### GET /analytics/overview
High-level system statistics.

### GET /analytics/usage?days=7
Daily query volume over N days.

### GET /analytics/agents
Agent invocation breakdown.

### GET /analytics/documents
Document type distribution.

---

## Settings

### GET /settings/
Get current user settings.

### PATCH /settings/
Update settings partially.

**Request:**
```json
{
  "llm_model": "claude-3-5-sonnet-20241022",
  "chunk_size": 512,
  "top_k": 5,
  "use_reranker": true,
  "use_hybrid_search": true
}
```

---

## Health

### GET /api/health
Service health check (no auth required).

**Response:**
```json
{ "status": "healthy", "version": "1.0.0", "service": "Multimodal Agentic RAG" }
```
