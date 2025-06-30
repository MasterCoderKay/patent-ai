from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.patent_analyzer import PatentAnalyzer
from app.core.logger import logger

router = APIRouter(
    prefix="/patents",
    tags=["Patent Analysis"],
    responses={404: {"description": "Not found"}}
)

# Response model
class PatentAnalysisResult(BaseModel):
    novelty_score: float
    key_features: list[str]
    prior_art_suggestions: list[str]
    technical_terms: list[str]
    analysis_summary: str

# Request model
class PatentRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=10000,
                      description="Patent claim text to analyze")
    language: Optional[str] = Field("en", description="Language code for analysis")
    detailed: Optional[bool] = Field(False, description="Return detailed analysis")

# Singleton analyzer instance
analyzer = PatentAnalyzer()

@router.post(
    "/analyze",
    response_model=PatentAnalysisResult,
    summary="Analyze patent claims",
    description="""Performs AI analysis of patent claims including:
                - Novelty assessment
                - Technical feature extraction
                - Prior art identification"""
)
async def analyze_patent_claim(request: PatentRequest):
    try:
        logger.info(f"Patent analysis request received: {request.text[:50]}...")

        result = await analyzer.analyze_patent(
            text=request.text,
            language=request.language,
            detailed=request.detailed
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.critical(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Patent analysis service unavailable"
        )
