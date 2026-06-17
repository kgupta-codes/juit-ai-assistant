from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.retriever import search
from backend.app.rag import ask_juit

app = FastAPI(
    title="JUIT AI Assistant"
)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "JUIT AI Assistant API Running"
    }


@app.post("/search")
def search_documents(request: QueryRequest):

    results = search(request.query)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    return {
        "question": request.query,
        "results_found": len(documents),
        "answers": documents,
        "sources": metadatas
    }


@app.post("/chat")
def chat(request: QueryRequest):

    result = ask_juit(request.query)

    return {
        "question": request.query,
        "answer": result["answer"],
        "sources": result["sources"]
    }
