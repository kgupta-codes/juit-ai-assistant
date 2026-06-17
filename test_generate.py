import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("Key found:", os.getenv("GEMINI_API_KEY") is not None)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content(
    "Say hello in one sentence."
)

print(response.text)
