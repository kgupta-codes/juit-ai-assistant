import os
import requests

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:1.7b"
)


def generate_answer(prompt: str):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "num_ctx": 2048,
                "num_predict": 250
            }
        },
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    answer = data["response"]

    if "</think>" in answer:
        answer = answer.split("</think>")[-1].strip()

    return answer
