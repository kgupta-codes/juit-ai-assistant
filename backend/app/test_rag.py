from rag import ask_juit

result = ask_juit(
    "What is the hostel capacity?"
)

print("\nANSWER:\n")
print(result["answer"])

print("\nSOURCES:\n")
for source in result["sources"]:
    print(source["title"])
