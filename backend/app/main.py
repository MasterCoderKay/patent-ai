import os
from pathlib import Path
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
from openai import OpenAI
from typing import Dict
import time
from fastapi.responses import JSONResponse
import uvicorn

# ---------------------- Constants ----------------------
DEFAULT_MODEL = "llama-3.3-70b-versatile"
MAX_RETRIES = 3
RETRY_DELAY = 1

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
async def analyze_idea(payload: Dict = Body(...)):
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

# Alias endpoint for /analyze-idea to avoid 404
@app.post("/analyze-idea")
async def analyze_idea_alias(payload: Dict = Body(...)):
    return await analyze_idea(payload)

# You can add other endpoints like /score, /keywords, /market-pitch here...

# ---------------------- Health Check ----------------------
@app.get("/health", summary="Service health", response_description="Service status")
async def health_check():
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

# ---------------------- Run with Uvicorn ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
