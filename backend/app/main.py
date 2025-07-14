import os
from pathlib import Path
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from typing import Dict, Optional
import time
from fastapi.responses import JSONResponse

# ---------------------- Constants ----------------------
DEFAULT_MODEL = "llama-3.3-70b-versatile"
MAX_RETRIES = 3
RETRY_DELAY = 1

# ---------------------- Environment Setup ----------------------
load_dotenv(find_dotenv(raise_error_if_not_found=True))

# ---------------------- Logging Configuration ----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# ---------------------- API Client Initialization ----------------------
def initialize_groq_client() -> OpenAI:
    """Initialize and validate Groq client"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.critical("GROQ_API_KEY not found in environment variables")
        raise RuntimeError("GROQ_API_KEY is required")

    if not api_key.startswith("gsk_"):
        logger.warning("Invalid GROQ_API_KEY format (should start with 'gsk_')")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        timeout=30
    )

try:
    client = initialize_groq_client()
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize Groq client: {str(e)}")
    raise

# ---------------------- FastAPI App Setup ----------------------
app = FastAPI(
    title="Patent AI Analyzer",
    description="API for analyzing patent ideas using Groq's AI models",
    version="1.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- Helper Functions ----------------------
async def call_groq_api_with_retry(
    system_prompt: str,
    user_content: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """Enhanced API call with retry logic"""
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        except Exception as e:
            last_error = str(e)
            logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

    logger.error(f"All {MAX_RETRIES} attempts failed")
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Groq API request failed after {MAX_RETRIES} attempts: {last_error}"
    )

# ---------------------- API Endpoints ----------------------
@app.post("/analyze", summary="Analyze invention", response_description="Detailed analysis of the invention")
async def analyze_idea(payload: Dict = Body(..., example={
    "title": "Smart Solar Panel",
    "description": "A solar panel that automatically adjusts angle..."
})) -> Dict:
    required_fields = ["title", "description"]
    if missing := [f for f in required_fields if f not in payload]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {missing}"
        )

    try:
        analysis = await call_groq_api_with_retry(
            system_prompt=(
                "As a senior patent analyst with 20 years experience, provide:\n"
                "1. Innovation score (1-10)\n"
                "2. Technical feasibility assessment\n"
                "3. Market potential\n"
                "4. Competitive analysis\n"
                "Format with clear headings and bullet points"
            ),
            user_content=f"Title: {payload['title']}\nDescription: {payload['description']}"
        )

        return {
            "status": "success",
            "analysis": analysis,
            "model": DEFAULT_MODEL
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Analysis failed unexpectedly")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected analysis failure"
        )

@app.post("/score", summary="Score novelty", response_description="Novelty score with justification")
async def score_novelty(payload: Dict = Body(..., example={
    "description": "A new type of biodegradable battery..."
})) -> Dict:
    if "description" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description is required"
        )

    try:
        score = await call_groq_api_with_retry(
            system_prompt=(
                "Provide:\n"
                "1. Novelty score (1-10)\n"
                "2. 3-5 specific reasons justifying the score\n"
                "3. Prior art considerations\n"
                "Use markdown formatting"
            ),
            user_content=payload["description"],
            temperature=0.5
        )

        return {
            "status": "success",
            "novelty_score": score,
            "model": DEFAULT_MODEL
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Scoring failed unexpectedly")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected scoring failure"
        )

@app.post("/keywords", summary="Extract keywords", response_description="List of technical keywords")
async def extract_keywords(payload: Dict = Body(..., example={
    "description": "Quantum computing using photon entanglement..."
})) -> Dict:
    if "description" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description is required"
        )

    try:
        keywords = await call_groq_api_with_retry(
            system_prompt=(
                "Extract:\n"
                "1. Top 5 technical keywords\n"
                "2. Relevance score for each (1-5)\n"
                "Format as a markdown table with columns: Keyword, Relevance, Definition"
            ),
            user_content=payload["description"],
            temperature=0.3
        )

        return {
            "status": "success",
            "keywords": keywords,
            "model": DEFAULT_MODEL
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Keyword extraction failed unexpectedly")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected keyword extraction failure"
        )

@app.post("/market-pitch", summary="Generate pitch", response_description="Investor pitch")
async def generate_pitch(payload: Dict = Body(..., example={
    "description": "AI-powered medical diagnosis device..."
})) -> Dict:
    if "description" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description is required"
        )

    try:
        pitch = await call_groq_api_with_retry(
            system_prompt=(
                "Create a 60-second investor pitch with:\n"
                "1. Problem statement\n"
                "2. Solution overview\n"
                "3. Market size\n"
                "4. Competitive advantage\n"
                "5. Call to action\n"
                "Use professional but engaging tone"
            ),
            user_content=payload["description"],
            temperature=0.85,
            max_tokens=1000
        )

        return {
            "status": "success",
            "investor_pitch": pitch,
            "model": DEFAULT_MODEL
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Pitch generation failed unexpectedly")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected pitch generation failure"
        )

# ---------------------- Health Check ----------------------
@app.get("/health", summary="Service health", response_description="Service status")
async def health_check() -> Dict:
    groq_status = "active" if os.getenv("GROQ_API_KEY") else "inactive"

    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "groq_status": groq_status,
        "version": app.version,
        "uptime": time.time() - app.startup_time
    }

# ---------------------- Startup Event ----------------------
@app.on_event("startup")
async def startup_event():
    app.startup_time = time.time()
    logger.info("Application startup complete")

# ---------------------- Error Handling ----------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.critical(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Internal server error"},
    )
