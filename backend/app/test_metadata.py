from retriever import search

results = search("hostel capacity")

print(results.keys())
print()
print("METADATA:")
print(results["metadatas"][0][0])
