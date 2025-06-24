from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def status():
    return {"message": "USPTO AI is running!"}

@router.get("/favicon.ico")
def favicon():
    return {}

