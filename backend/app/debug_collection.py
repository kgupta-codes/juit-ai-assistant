import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_collection("juit_knowledge")

data = collection.peek(limit=5)

print("\n=== DOCUMENTS ===\n")

for doc in data["documents"]:
    print(doc[:500])
    print("\n" + "=" * 50 + "\n")
