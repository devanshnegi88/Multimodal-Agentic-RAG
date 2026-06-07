# Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for infrastructure)
- Tesseract OCR (for image text extraction)

### 1. Clone & configure
```bash
git clone <repo-url>
cd multimodal-agentic-rag
cp .env .env.local
# Edit .env with your API keys
```

### 2. Start infrastructure
```bash
docker compose -f docker/docker-compose.yml up mongodb redis qdrant -d
```

### 3. Backend
```bash
cd backend
pip install -r ../requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

---

## Production Deployment (Docker)

### Full stack
```bash
# Build and start everything
docker compose -f docker/docker-compose.yml up --build -d

# Check logs
docker compose -f docker/docker-compose.yml logs -f

# Stop
docker compose -f docker/docker-compose.yml down
```

The system will be available at:
- Frontend: `http://localhost`
- API: `http://localhost/api`
- API Docs: `http://localhost/api/docs`

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key |
| `OPENAI_API_KEY` | ✅ | For embeddings & Whisper |
| `MONGODB_URL` | ✅ | MongoDB connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `QDRANT_URL` | ✅ | Qdrant HTTP URL |
| `JWT_SECRET` | ✅ | Random secret for JWT signing |
| `TAVILY_API_KEY` | ⚠️ | Required for web search |
| `COHERE_API_KEY` | ⚠️ | Required for reranking |

---

## Infrastructure Requirements

| Service | RAM | CPU | Storage |
|---------|-----|-----|---------|
| Backend | 2GB | 2 cores | 10GB |
| Frontend (nginx) | 256MB | 0.5 cores | — |
| MongoDB | 1GB | 1 core | 20GB+ |
| Redis | 512MB | 0.5 cores | 2GB |
| Qdrant | 2GB | 2 cores | 20GB+ |

Minimum recommended: **8GB RAM, 4 vCPUs**

---

## Scaling

### Horizontal scaling (backend)
```yaml
# docker-compose.yml
backend:
  deploy:
    replicas: 4
```

### Qdrant clustering
Use the Qdrant distributed mode for large-scale deployments.

### MongoDB Atlas
Replace `MONGODB_URL` with your Atlas connection string.

---

## Monitoring

The `/api/health` endpoint can be used with any monitoring tool:
```bash
curl http://your-domain/api/health
# {"status": "healthy", "version": "1.0.0"}
```
