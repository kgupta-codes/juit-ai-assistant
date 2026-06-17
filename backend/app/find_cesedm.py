import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_collection("juit_knowledge")

results = collection.get(
    where={"title": "CESEDM"}
)

print("FOUND:", len(results["documents"]))

for i, doc in enumerate(results["documents"]):
    print("\n===== DOC", i + 1, "=====\n")
    print(doc[:2000])
