import os

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_answer(question: str, context: str):
prompt = f"""
You are JUIT AI Assistant.

Answer only using the provided context.

Guidelines:
- Be accurate and factual.
- Use information from all relevant context.
- Give complete answers rather than overly short summaries.
- If facilities, departments, hostel details, placement statistics, research centres, committees, or contact information are mentioned in the context, include the important details.
- If the answer is not present in the context, say that the information could not be found in the available JUIT knowledge base.
- Do not make up information.

Context:
{context}

Question:
{question}

Answer:
"""
    response = model.generate_content(prompt)

    return response.text
