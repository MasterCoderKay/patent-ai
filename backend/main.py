from fastapi import FastAPI
from app.api.llm_routes import router as llm_router
from app.api.patents import router as patents_router

app = FastAPI()

# Include routers
app.include_router(llm_router, prefix="/api/ai")
app.include_router(patents_router, prefix="/api/patents")

@app.get("/")
def home():
    return {"message": "PatentAI Backend Running!"}
    