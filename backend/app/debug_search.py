from backend.app.retriever import search

results = search("CESEDM", n_results=10)

for i in range(len(results["documents"][0])):

    print(f"\n===== RESULT {i+1} =====")
    print("DISTANCE:", results["distances"][0][i])
    print("TITLE:", results["metadatas"][0][i]["title"])

    print("\nDOCUMENT:")
    print(results["documents"][0][i][:500])
