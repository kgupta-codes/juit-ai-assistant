import os
from dotenv import load_dotenv

load_dotenv()

from groq import Groq
MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(prompt: str):

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": """
You are JUIT AI Assistant.

Rules:
- Answer ONLY using the provided context.
- Never invent information.
- If the answer is not present, say:
  "I couldn't find that information in the JUIT knowledge base."
- Be concise.
- Use bullet points whenever appropriate.
- Format responses cleanly.
- Do not mention that you are an AI model.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()