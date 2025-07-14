import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

class PatentAnalyzer:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_claim(self, text: str) -> str:
        prompt = """Analyze this patent claim for novelty:
        {text}
        Return analysis in Markdown with sections:
        - Technical Features
        - Novelty Assessment
        - Prior Art Suggestions"""
        return self.model.generate_content(prompt.format(text=text)).text
