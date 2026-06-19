# JUIT AI Assistant Deployment

This project has four runtime pieces:

- FastAPI backend on port `8000`
- ChromaDB persistent vector store at `chroma_db/`
- React/Vite frontend served as static files
- Ollama on port `11434` with model `qwen3:1.7b`

The retrieval system is stable. Deployment work should not change retriever ranking, RAG routing, HOD extraction, benchmark expectations, or ChromaDB contents unless a clear bug is found.

## Deployment Readiness Audit

Current readiness: suitable for local Docker and VPS demos, partially ready for split cloud deployment.

Ready:

- FastAPI exposes `/`, `/search`, and `/chat`.
- React/Vite builds to static files.
- Dockerfiles exist for backend and frontend.
- Docker Compose runs frontend, backend, Ollama, and a read-only ChromaDB mount.
- Backend now supports configurable `CORS_ORIGINS`.
- Backend now supports configurable `OLLAMA_URL`.

Remaining constraints:

- `chroma_db/` is required at runtime and is ignored by git.
- Hosted backend deployments need a persistent disk, volume, or artifact restore for ChromaDB.
- Ollama requires a model pull after first startup and may exceed free-tier memory/CPU limits.
- The backend container does not copy `chroma_db/`; this is intentional for Compose, but standalone Docker deployments must mount the directory.

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

Backend environment:

```bash
export OLLAMA_URL=http://localhost:11434/api/generate
export OLLAMA_MODEL=qwen3:1.7b
export CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
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

By default, the backend calls Ollama at `http://localhost:11434/api/generate`. `docker-compose.yml` runs the backend with:

```yaml
network_mode: "service:ollama"
```

That makes `localhost:11434` inside the backend resolve to the Ollama service network namespace. The backend also supports `OLLAMA_URL` for hosted deployments where Ollama runs on another host.

Because the backend uses `network_mode: "service:ollama"`, backend ports are published on the `ollama` service in Compose.

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

## Vercel Frontend Deployment

Vercel settings:

```text
Root directory: frontend
Install command: npm ci
Build command: npm run build
Output directory: dist
```

Required environment variable:

```text
VITE_API_BASE_URL=https://<backend-host>
```

Vite injects this value at build time, so redeploy after changing it.

## Render Backend Deployment

Use a Render Web Service.

```text
Build command: pip install -r requirements.txt
Start command: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```text
OLLAMA_URL=https://<ollama-host>/api/generate
OLLAMA_MODEL=qwen3:1.7b
CORS_ORIGINS=https://<vercel-app>.vercel.app
```

ChromaDB must be restored or mounted at `chroma_db/`. Use a persistent disk or an explicit artifact restore step. Do not rely on Render's ephemeral filesystem for the stable vector store.

## Railway Backend Deployment

Use a Python service or Docker service.

```text
Start command: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```text
OLLAMA_URL=https://<ollama-host>/api/generate
OLLAMA_MODEL=qwen3:1.7b
CORS_ORIGINS=https://<vercel-app>.vercel.app
```

ChromaDB must be available at `chroma_db/` through a Railway volume or deploy-time artifact. Ollama may need a separate larger service or VPS if the selected Railway plan cannot sustain the model.

## Ollama Strategy

Local:

- Best current developer experience.
- Run `ollama serve` and keep `OLLAMA_URL=http://localhost:11434/api/generate`.

VPS:

- Recommended public-demo path.
- Run FastAPI, ChromaDB, and Ollama on one host or one Docker Compose stack.
- Persist the Ollama model volume and mount `chroma_db/` read-only if possible.

Future hosted alternatives:

- A hosted LLM API or managed inference endpoint can replace Ollama later.
- Treat that as a model-provider migration and rerun `python benchmark_runner.py`.

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
