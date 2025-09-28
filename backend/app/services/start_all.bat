@echo off
title Start PatentAI Backend and Frontend
echo Starting PatentAI services...

REM Activate the virtual environment
call C:\Users\money\patent-ai\backend\.venv\Scripts\activate.bat

REM Start the FastAPI backend server in a new command window (logs to backend.log)
start "Backend Server" cmd /k "cd C:\Users\money\patent-ai\backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1"

REM Start the Streamlit frontend in a new command window (logs to frontend.log)
start "Frontend App" cmd /k "cd C:\Users\money\patent-ai\frontend && streamlit run frontend.py > frontend.log 2>&1"

echo All services started. Check backend.log and frontend.log for output.
pause
