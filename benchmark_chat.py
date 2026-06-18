import requests

questions = [
    "What is CESEDM?",
    "Who is the HOD of Civil Engineering?",
    "What is the fee structure for B.Tech?",
    "What is the academic calendar?",
    "What student clubs exist at JUIT?",
    "What is ICC?",
    "What is CESTRD?",
    "What exchange programs are available?",
    "What committees exist for student welfare?",
    "Tell me about the Biotechnology department.",
    "What research centers are available?",
    "What is the placement record of Civil Engineering?"
]

for q in questions:
    print("\n" + "="*80)
    print(q)

    r = requests.post(
        "http://127.0.0.1:8000/chat",
        json={"query": q}
    )

    print(r.json()["answer"])
