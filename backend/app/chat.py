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
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()