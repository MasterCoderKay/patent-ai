# groq.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
import asyncio

app = FastAPI()

# CORS setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key from env or default
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "sk-your-real-key-here")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "mixtral-8x7b-32768"

class PromptInput(BaseModel):
    prompt: str

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

async def call_groq_api(prompt: str) -> str:
    try:
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful patent analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-idea")
async def analyze_idea(input: PromptInput):
    prompt = f"Analyze this invention idea for novelty and feasibility:\n\n{input.prompt}"
    return {"result": await call_groq_api(prompt)}

@app.post("/score-novelty")
async def score_novelty(input: PromptInput):
    prompt = f"Score the novelty of this invention from 1 to 10, and explain why:\n\n{input.prompt}"
    return {"result": await call_groq_api(prompt)}

@app.post("/extract-keywords")
async def extract_keywords(input: PromptInput):
    prompt = f"Extract the top 10 technical keywords from this invention idea:\n\n{input.prompt}"
    return {"result": await call_groq_api(prompt)}

@app.post("/generate-market-pitch")
async def generate_market_pitch(input: PromptInput):
    prompt = f"Generate a 2-paragraph investor pitch for this invention:\n\n{input.prompt}"
    return {"result": await call_groq_api(prompt)}
