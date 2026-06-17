from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_collection(
    name="juit_knowledge",
    embedding_function=embedding_function
)

query = input("Ask JUIT AI: ")

results = collection.query(
    query_texts=[query],
    n_results=3
)

print("\n===== RESULTS =====\n")

for i, doc in enumerate(results["documents"][0]):
    print(f"\nResult {i+1}\n")
    print(doc[:1000])
    print("\n--------------------")
