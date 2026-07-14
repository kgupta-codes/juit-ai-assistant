# JUIT AI Assistant

A production-oriented Retrieval Augmented Generation (RAG) assistant for Jaypee University of Information Technology (JUIT), Waknaghat. The assistant answers questions using retrieved content from the official JUIT website and returns source links for traceability.

This repository contains a FastAPI backend, a React/Vite frontend, a deterministic query-understanding layer, ChromaDB-backed retrieval, and Ollama-based answer generation.

## Features

- Chat interface for admissions, academics, departments, hostels, placements, scholarships, research, committees, clubs, and official notices.
- Deterministic query normalization for common university abbreviations such as VC, HOD, CSE, ECE, BTech, MTech, and PhD.
- Conversation memory for follow-up questions within a chat session.
- Hybrid retrieval combining dense ChromaDB search with keyword scoring and entity-aware reranking.
- Source-grounded answer generation through local Ollama.
- Compact source chips linking back to official JUIT pages.
- Persistent local chat history in the frontend.
- Docker and split-deployment support for local, Vercel, Render, Railway, and VPS workflows.

## Screenshots

Screenshots are stored in `screenshots/`.

| Home | Example Answer |
| --- | --- |
| `screenshots/Home-Screen.png` | `screenshots/HOD.png` |

## Architecture Overview

```text
Frontend
  -> FastAPI API
    -> Deterministic NLU
      -> Conversation Memory
        -> Hybrid Retrieval
          -> ChromaDB Vector Database
            -> Context Builder
              -> Ollama LLM
                -> Answer Generation
```

See [docs/architecture.md](docs/architecture.md) for component-level details.

## Technology Stack

- Frontend: React, Vite, CSS
- Backend: Python, FastAPI, Pydantic, Uvicorn
- Retrieval: ChromaDB, sentence-transformers, keyword scoring
- Generation: Ollama with `qwen3:1.7b`
- Data pipeline: BeautifulSoup crawler/scraper, JSON page corpus, ChromaDB ingestion
- Deployment: Docker, Docker Compose, Vercel frontend, Render/Railway/VPS backend

## Folder Structure

```text
backend/              FastAPI app, RAG pipeline, scraper, ingestion
data/                 Scraped official JUIT page corpus and URL lists
docs/                 Architecture, API, deployment, and evaluation docs
frontend/             React/Vite chat application
screenshots/          Release screenshots
tests/                Automated Python tests
benchmark_*.py        Retrieval/RAG evaluation scripts
docker-compose.yml    Local multi-service runtime
```

## Installation

### Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

### Ollama

```bash
ollama pull qwen3:1.7b
ollama serve
```

## Environment Variables

Copy `.env.example` and set values for your environment:

```bash
cp .env.example .env
```

| Variable | Used By | Default | Description |
| --- | --- | --- | --- |
| `OLLAMA_URL` | Backend | `http://localhost:11434/api/generate` | Ollama generation endpoint |
| `OLLAMA_MODEL` | Backend | `qwen3:1.7b` | Ollama model name |
| `CORS_ORIGINS` | Backend | local Vite origins | Comma-separated allowed frontend origins |
| `VITE_API_BASE_URL` | Frontend | `http://127.0.0.1:8000` | Backend URL injected at frontend build time |

Never commit `.env` or API keys.

## Running Locally

Start the backend:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Start the frontend:

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

Open `http://127.0.0.1:5173`.

## Docker

```bash
docker compose up --build
docker compose exec ollama ollama pull qwen3:1.7b
```

The backend expects a populated `chroma_db/` directory mounted at runtime.

## Deployment

- Frontend: deploy `frontend/` to Vercel with `VITE_API_BASE_URL` set to the backend URL.
- Backend: deploy FastAPI to Render, Railway, or a VPS.
- Vector database: restore or mount `chroma_db/` as a persistent artifact or volume.
- LLM: run Ollama on the same VPS or on a reachable model host.

See [docs/deployment.md](docs/deployment.md).

## API Documentation

See [docs/api.md](docs/api.md).

## Evaluation

Run deterministic tests:

```bash
python3 -m pytest tests -q
```

Run the benchmark:

```bash
python benchmark_runner.py
```

See [docs/evaluation.md](docs/evaluation.md).

## Future Roadmap

- Persistent server-side chat storage.
- Scheduled crawler and incremental Chroma refresh.
- Managed model-provider option for hosted deployments.
- Expanded regression evaluation set.
- PDF and document ingestion for official downloads.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
