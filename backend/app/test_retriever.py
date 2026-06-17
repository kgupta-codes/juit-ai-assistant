from retriever import search

query = "What is the hostel capacity?"

results = search(query)

print("\n===== RESULTS =====\n")

for i, doc in enumerate(results["documents"][0]):
    print(f"\nResult {i+1}\n")
    print(doc[:500])
    print("\n--------------------")
