from pydantic import BaseModel
from typing import List, Optional

class PatentAnalysisRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    detailed: Optional[bool] = False

class PatentAnalysisResult(BaseModel):
    novelty_score: float
    key_features: List[str]
    prior_art_suggestions: List[str]
    technical_terms: List[str]
    detailed_analysis: Optional[str] = None