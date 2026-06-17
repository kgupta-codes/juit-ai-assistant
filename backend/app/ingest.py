import json
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

PAGES_DIR = BASE_DIR / "data" / "pages"
CHROMA_DIR = BASE_DIR / "chroma_db"

# -----------------------------
# Chroma Client
# -----------------------------

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="juit_knowledge",
    embedding_function=embedding_function
)

# -----------------------------
# Text Splitter
# -----------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# -----------------------------
# Ingestion
# -----------------------------

def ingest_file(file_path: Path):

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "")
    url = data.get("url", "")
    content = data.get("content", "")

    chunks = splitter.split_text(content)

    documents = []
    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):

        chunk_id = f"{file_path.stem}_{i}"

        documents.append(chunk)

        ids.append(chunk_id)

        metadatas.append(
            {
                "title": title,
                "url": url,
                "chunk": i
            }
        )

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"[OK] {file_path.name} -> {len(chunks)} chunks")


def main():

    files = list(PAGES_DIR.glob("*.json"))

    print(f"[INFO] Found {len(files)} files")

    for file in files:
        ingest_file(file)

    print("\n[INFO] Ingestion complete")


if __name__ == "__main__":
    main()
