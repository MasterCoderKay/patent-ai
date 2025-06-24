from fastapi import FastAPI

# This must be named 'app' exactly
app = FastAPI()

@app.get("/")
def root():
    return {"status": "minimal test"}

# Add this at the bottom
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)