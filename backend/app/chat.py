import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_answer(prompt: str):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3:1.7b",
            "prompt": prompt,
            "stream": False,
            "think": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]
