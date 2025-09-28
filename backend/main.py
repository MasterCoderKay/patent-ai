from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os, json, httpx
from dotenv import load_dotenv

# --------------------------
# Load env variables
# --------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("❌ Missing GROQ_API_KEY")

# --------------------------
# FastAPI setup
# --------------------------
app = FastAPI(title="PatentAI Backend", version="0.1.0")

# Enable CORS for React frontend
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# History storage
# --------------------------
HISTORY_FILE = "claim_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

history_data = load_history()

# --------------------------
# Models
# --------------------------
class ClaimPolishRequest(BaseModel):
    claim: str

class ClaimHistoryItem(BaseModel):
    original: str
    polished: str

# --------------------------
# Routes
# --------------------------
@app.get("/")
def root():
    return {"message": "PatentAI Backend is running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/history", response_model=List[ClaimHistoryItem])
def get_history():
    return history_data

@app.post("/polish-claim")
async def polish_claim(request: ClaimPolishRequest):
    try:
        prompt = f"""
You are a patent attorney assistant trained to rewrite patent claims for clarity, technical accuracy, and USPTO compliance.

**Original Claim:**
{request.claim}

**Polished Claim:**
<polished claim text>

**Suggestions for Improvement:**
- Suggestion 1
- Suggestion 2
- Suggestion 3
"""
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that formats responses in Markdown."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }
            )
            res.raise_for_status()
            data = res.json()

        polished_output = data["choices"][0]["message"]["content"]

        # Save to history
        entry = {"original": request.claim, "polished": polished_output}
        history_data.append(entry)
        save_history(history_data)

        return {"result": polished_output}

    except Exception as e:
        print(f"❌ ERROR polishing claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Optional GET for browser testing
@app.get("/polish-claim")
def polish_claim_get():
    return {"message": "Use POST to polish a claim. GET is only for testing."}
