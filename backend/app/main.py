from fastapi import FastAPI, Body, HTTPException
import logging
from openai import OpenAI
import os

# ---------------------- Logging Setup ----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- Environment & Client ----------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logger.error("❌ GROQ_API_KEY is not set in environment variables.")
    raise RuntimeError("GROQ_API_KEY is not set in environment variables.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# ---------------------- FastAPI App ----------------------
app = FastAPI()

# ---------------------- ROUTES ----------------------

@app.post("/analyze")
async def analyze_idea(payload: dict = Body(...)):
    try:
        title = payload["title"]
        description = payload["description"]
        logger.info(f"🔍 Analyzing idea: {title}")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You're an expert at analyzing new inventions for innovation and practicality."},
                {"role": "user", "content": f"Title: {title}\nDescription: {description}"}
            ],
            temperature=0.7
        )
        result = response.choices[0].message.content
        return {"analysis": result}
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score")
async def score_novelty(payload: dict = Body(...)):
    try:
        description = payload["description"]
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Rate the novelty of this invention on a scale of 1 to 10 and briefly justify."},
                {"role": "user", "content": description}
            ],
            temperature=0.7
        )
        result = response.choices[0].message.content
        return {"novelty_score": result}
    except Exception as e:
        logger.error(f"❌ Scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/keywords")
async def extract_keywords(payload: dict = Body(...)):
    try:
        description = payload["description"]
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Extract the top 5 keywords or technical terms from the invention description."},
                {"role": "user", "content": description}
            ],
            temperature=0.3
        )
        result = response.choices[0].message.content
        return {"keywords": result}
    except Exception as e:
        logger.error(f"❌ Keyword extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/market-pitch")
async def generate_pitch(payload: dict = Body(...)):
    try:
        description = payload["description"]
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You're a pitch coach. Write a compelling 60-second investor pitch for the product."},
                {"role": "user", "content": description}
            ],
            temperature=0.85
        )
        result = response.choices[0].message.content
        return {"investor_pitch": result}
    except Exception as e:
        logger.error(f"❌ Pitch generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
