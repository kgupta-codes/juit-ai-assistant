from retriever import search

results = search("What is RIDE?")

docs = results["documents"][0]
meta = results["metadatas"][0]

for i in range(len(docs)):
    print("\n===================")
    print(f"RESULT {i+1}")
    print("===================")

    print("TITLE:", meta[i]["title"])
    print("URL:", meta[i]["url"])
    print()

    print(docs[i][:500])
