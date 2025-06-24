# app/ai/patent_analyzer.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env")

genai.configure(api_key=api_key)

def analyze_patent(text: str) -> str:
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(text)
    return response.text
