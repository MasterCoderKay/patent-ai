from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ai.patent_analyzer import analyze_patent

router = APIRouter()

class PatentRequest(BaseModel):
    text: str

@router.post("/analyze")
async def analyze(request: PatentRequest):
    try:
        result = analyze_patent(request.text)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

