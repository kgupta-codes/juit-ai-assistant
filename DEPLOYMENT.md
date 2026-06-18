# JUIT AI Assistant Deployment

This project has three runtime pieces:

- FastAPI backend on port `8000`
- ChromaDB persistent vector store at `chroma_db/`
- React/Vite frontend served as static files
- Ollama on port `11434` with model `qwen3:1.7b`

The retrieval system is stable. Deployment work should not change retriever ranking, RAG routing, HOD extraction, benchmark expectations, or ChromaDB contents unless a clear bug is found.

## Local Development

Backend:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Optional frontend API override:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

Ollama:

```bash
ollama pull qwen3:1.7b
ollama serve
```

## Docker Compose

Build and start:

```bash
docker compose up --build
```

Pull the model into the Ollama volume:

```bash
docker compose exec ollama ollama pull qwen3:1.7b
```

Open:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Ollama: `http://127.0.0.1:11434`

## Compose Networking Note

`backend/app/chat.py` currently calls Ollama at `http://localhost:11434/api/generate`. To preserve the stable backend code, `docker-compose.yml` runs the backend with:

```yaml
network_mode: "service:ollama"
```

That makes `localhost:11434` inside the backend resolve to the Ollama service network namespace. This avoids a backend code change, but it also means backend ports are published on the `ollama` service in compose.

Future deployment hardening can make `OLLAMA_URL` configurable, but that would be a backend change and should be validated with the stable benchmark.

## ChromaDB

The backend expects a populated ChromaDB directory at:

```text
chroma_db/
```

The compose setup mounts it read-only:

```yaml
./chroma_db:/app/chroma_db:ro
```

Do not rebuild ChromaDB during deployment unless explicitly performing an ingestion refresh. If ChromaDB is missing, restore the stable database artifact or run the existing ingestion process in a controlled environment and rerun the benchmark.

## Frontend Environment

The frontend uses:

```text
VITE_API_BASE_URL
```

Default:

```text
http://127.0.0.1:8000
```

For hosted deployment, set this value at build time to the public backend URL.

## Recommended Student-Friendly Deployment

Simplest split deployment:

- Frontend: Vercel, Netlify, or GitHub Pages-style static hosting.
- Backend: Render, Railway, a student VM, or a small VPS.
- Ollama: same VM as backend, or a GPU/CPU host reachable by the backend.
- ChromaDB: ship as a persistent artifact or mount as a volume.

Fully free deployment is difficult if Ollama must run server-side. A low-cost VM is the most predictable path because FastAPI, ChromaDB, and Ollama can run together.

## Validation Checklist

Frontend-only changes:

```bash
cd frontend
npm run build
```

Backend changes:

```bash
python benchmark_runner.py
```

The stable benchmark must remain:

```text
12/12 PASSED
```
