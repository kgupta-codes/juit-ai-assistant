from backend.app.retriever import search
from backend.app.chat import generate_answer


def ask_juit(question: str):

    results = search(question, n_results=3)

    documents = results["documents"][0]
    sources = results["metadatas"][0]

    context = "\n\n".join(documents)

    prompt = f"""
You are the JUIT AI Assistant.

Answer ONLY using the provided context.

Rules:
- Maximum 5 sentences.
- Do not explain your reasoning.
- Do not think step-by-step.
- Do not use outside knowledge.
- If answer is not present, reply exactly:
I could not find that information in the JUIT knowledge base.

Context:
{context}

Question:
{question}

Answer:
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "sources": sources
    }
