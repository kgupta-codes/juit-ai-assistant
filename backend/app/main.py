import os
import logging

from typing import Optional

from backend.app.memory import add_message, get_history, get_state
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from backend.app.retriever import search
from backend.app.rag import ask_juit

LOGGER = logging.getLogger(__name__)

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="JUIT AI Assistant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    session_id: Optional[str] = "default"


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "JUIT AI Assistant API Running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "juit-ai-assistant",
    }


@app.post("/search")
def search_documents(request: QueryRequest):
    try:
        results = search(request.query)
    except Exception as exc:
        LOGGER.exception("Search failed")
        raise HTTPException(status_code=503, detail="Search service unavailable") from exc

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    return {
        "question": request.query,
        "results_found": len(documents),
        "answers": documents,
        "sources": metadatas
    }


@app.post("/chat")
def chat(request: QueryRequest):

    history = get_history(request.session_id)
    state = get_state(request.session_id)

    try:
        result = ask_juit(
            request.query,
            history=history,
            state=state,
        )
    except Exception as exc:
        LOGGER.exception("Chat request failed")
        raise HTTPException(status_code=503, detail="Chat service unavailable") from exc

    add_message(
        request.session_id,
        "user",
        request.query
    )

    add_message(
        request.session_id,
        "assistant",
        result["answer"]
    )

    return {
        "question": request.query,
        "answer": result["answer"],
        "sources": result["sources"],
        "history": history,
        "confidence": result.get("confidence"),
        "rewritten_query": result.get("rewritten_query"),
    }
