import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

print("Key loaded:", key[:10] + "...")

genai.configure(api_key=key)

for model in genai.list_models():
    print(model.name)
