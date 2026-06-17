from retriever import search

results = search("Research Innovation Development Entrepreneurship RIDE")

for i, doc in enumerate(results["documents"][0][:5], start=1):
    print(f"\n===== RESULT {i} =====\n")
    print(doc[:800])
