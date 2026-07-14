# Architecture

## Overview

JUIT AI Assistant is a source-grounded RAG application. It is designed to answer questions only from the official JUIT knowledge base and return supporting source metadata.

```text
Frontend
  -> API
    -> Deterministic NLU
      -> Conversation Memory
        -> Hybrid Retrieval
          -> Vector Database
            -> LLM
              -> Answer Generation
```

## Frontend

The frontend is a React/Vite chat application in `frontend/`.

Responsibilities:

- Render the chat interface, sidebar, source chips, and markdown answers.
- Persist local chat history in browser storage.
- Send questions to the backend `/chat` endpoint.
- Pass `session_id` so the backend can resolve follow-up questions within a conversation.
- Surface loading, error, stop-generation, copy, regenerate, rename, and delete-chat controls.

The frontend does not perform retrieval or answer generation.

## API

The FastAPI app is in `backend/app/main.py`.

Primary endpoints:

- `GET /`
- `GET /health`
- `POST /search`
- `POST /chat`

The API validates request shape, applies CORS policy from `CORS_ORIGINS`, and wraps retrieval/chat failures with service-level errors.

## Deterministic NLU

The deterministic NLU layer lives in:

- `backend/app/query_config.py`
- `backend/app/nlu.py`
- `backend/app/query_rewriter.py`

It recognizes common university entities and aliases without using an LLM. Examples include:

- Roles: VC, Vice Chancellor, HOD, Registrar, Dean
- Departments: CSE, ECE, Civil, Biotechnology and Bioinformatics, Mathematics, Physics and Materials Science, HSS
- Programs: BTech, MTech, PhD, MBA, BBA, BCA
- Topics: Fee, Hostel, Scholarship, Placement, Laboratory, Admission

This layer expands and normalizes queries before retrieval.

## Conversation Memory

Session state is managed in `backend/app/memory.py`.

The current implementation is in-memory and suitable for local demos or single-process deployments. It tracks:

- Message history
- Active department
- Active program
- Active topic

This enables follow-up questions such as "Who is the HOD?" after "Tell me about Civil Engineering."

For production at scale, replace this module with Redis or a database-backed session store.

## Hybrid Retrieval

Retrieval is implemented in `backend/app/retriever.py`.

The pipeline:

1. Normalize and expand the query.
2. Retrieve dense candidates from ChromaDB.
3. Retrieve keyword candidates from stored Chroma documents.
4. Merge candidates.
5. Deduplicate by chunk identity.
6. Apply entity-aware ranking and domain-specific boosts.
7. Return top ranked documents, metadata, distances, and scores.

This improves exact institutional queries such as "Who is the VC?" or "Who is the HOD of CSE?" where pure embedding search may retrieve semantically similar but institutionally wrong pages.

## Vector Database

ChromaDB stores embedded chunks in `chroma_db/`.

The backend expects an existing collection named `juit_knowledge_v2`. The directory is ignored by git and should be restored or mounted in deployment.

## Knowledge Pipeline

The maintenance pipeline is:

1. `backend/app/crawler.py` discovers official JUIT URLs.
2. `backend/app/scraper.py` extracts clean page text into `data/pages/`.
3. `backend/app/ingest.py` builds chunks, metadata, embeddings, and Chroma records.

Ingestion metadata includes title, URL, canonical URL, page type, department, chunk index, hashes, and content type.

## LLM

The answer generator is in `backend/app/chat.py`.

The backend calls Ollama with:

- deterministic generation settings
- low temperature
- a bounded prediction length
- explicit context-only answer instructions

The default model is `qwen3:1.7b`.

## Answer Generation

The RAG orchestration is in `backend/app/rag.py`.

Responsibilities:

- Process the user query.
- Retrieve top evidence.
- Build the model context.
- Apply confidence and entity-support checks.
- Use deterministic structured answers for known high-signal cases.
- Call the LLM for general questions.
- Return answer text and source metadata.

If evidence is missing or low-confidence, the assistant returns:

```text
I could not confidently find this information on the official JUIT website.
```

## Structured Answers

`backend/app/structured_answers.py` contains deterministic answer builders for selected official categories, including clubs, committees, research centers, and placement statistics.

These functions are used only when the retrieval and query type indicate that a structured answer is appropriate.
