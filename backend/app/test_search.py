from backend.app.retriever import search

results = search("CESEDM", n_results=20)

for i, meta in enumerate(results["metadatas"][0]):
    print(f"\nRESULT {i+1}")
    print(meta)
