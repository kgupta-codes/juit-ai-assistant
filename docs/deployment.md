# Deployment

This project can run locally with Docker Compose or as a split deployment with a static frontend and hosted backend.

## Runtime Components

- React/Vite frontend
- FastAPI backend
- ChromaDB persistent directory at `chroma_db/`
- Ollama model server

## Required Environment Variables

Backend:

```text
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen3:1.7b
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Frontend:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Local Deployment

Start Ollama:

```bash
ollama pull qwen3:1.7b
ollama serve
```

Start backend:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Start frontend:

```bash
cd frontend
npm run dev
```

## Docker Compose

```bash
docker compose up --build
docker compose exec ollama ollama pull qwen3:1.7b
```

Compose exposes:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Ollama: `http://127.0.0.1:11434`

The backend shares the Ollama service network namespace, so `localhost:11434` resolves to the Ollama container.

## ChromaDB

`chroma_db/` is required at runtime and is intentionally ignored by git.

Deployment options:

- Mount a persistent disk or volume at `chroma_db/`.
- Restore a known-good database artifact before backend startup.
- Rebuild the database with `python -m backend.app.ingest` only in a controlled refresh workflow.

Do not rely on ephemeral platform storage for ChromaDB.

## Vercel Frontend

Recommended settings:

```text
Root directory: frontend
Install command: npm ci
Build command: npm run build
Output directory: dist
```

Set:

```text
VITE_API_BASE_URL=https://<backend-host>
```

Vite injects this at build time. Redeploy after changing it.

## Render Backend

Use a Render Web Service.

```text
Build command: pip install -r requirements.txt
Start command: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Set:

```text
OLLAMA_URL=https://<ollama-host>/api/generate
OLLAMA_MODEL=qwen3:1.7b
CORS_ORIGINS=https://<frontend-domain>
```

Attach persistent storage or restore `chroma_db/` during deploy.

## Railway Backend

Use a Python or Docker service.

```text
Start command: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Railway volumes or deploy artifacts are required for ChromaDB.

## VPS Deployment

A VPS is the simplest production-like path because FastAPI, Ollama, and ChromaDB can run on one host.

Recommended:

- Use Docker Compose or a process manager.
- Persist `chroma_db/`.
- Persist Ollama model storage.
- Put a reverse proxy such as Nginx or Caddy in front of FastAPI.
- Restrict CORS to the deployed frontend domain.

## Health Check

Use:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "service": "juit-ai-assistant"
}
```

## Release Validation

Before deployment:

```bash
python3 -m pytest tests -q
cd frontend && npm run lint && npm run build
```

If retrieval or ingestion changes, also run:

```bash
python benchmark_runner.py
```
