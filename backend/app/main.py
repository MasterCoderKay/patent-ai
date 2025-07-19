import os
import time
import logging
from typing import Dict

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.services.groq import initialize_groq_client
from app.api.analysis import analyze_idea, score_novelty, extract_keywords, generate_market_pitch

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

# App setup
app = FastAPI(
    title="PatentAI API",
    description="Backend API for PatentAI application",
    version="1.0.0"
)
app.startup_time = time.time()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize external clients
groq_client = initialize_groq_client()
logger.info("Groq client initialized successfully")

# ------------------- Root Endpoint -------------------
@app.get("/", summary="Root endpoint", response_description="API greeting")
async def root():
    return JSONResponse(
        content={
            "message": "PatentAI Backend is up and running 🚀",
            "endpoints": [
                "/health",
                "/analyze",
                "/analyze-idea",
                "/score",
                "/keywords",
                "/market-pitch"
            ]
        }
    )

# ------------------- Health Check -------------------
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

# ------------------- Core Endpoints -------------------
@app.post("/analyze", summary="Analyze patent idea")
async def analyze(payload: Dict = Body(...)):
    return await analyze_idea(payload)

@app.post("/analyze-idea", summary="Alias for /analyze")
async def analyze_idea_alias(payload: Dict = Body(...)):
    return await analyze_idea(payload)

@app.post("/score", summary="Score patent idea for novelty")
async def score(payload: Dict = Body(...)):
    return await score_novelty(payload)

@app.post("/keywords", summary="Extract keywords from idea")
async def keywords(payload: Dict = Body(...)):
    return await extract_keywords(payload)

@app.post("/market-pitch", summary="Generate market pitch")
async def pitch(payload: Dict = Body(...)):
    return await generate_market_pitch(payload)

# ------------------- Startup Logging -------------------
@app.on_event("startup")
async def on_startup():
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application shutdown complete")
