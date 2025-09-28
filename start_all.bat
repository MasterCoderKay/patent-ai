@echo off
echo Starting PatentAI services...

start "PatentAI Backend" cmd /k "cd /d C:\Users\money\patent-ai\backend && .venv\Scripts\activate.bat && uvicorn app.main:app --host 127.0.0.1 --port 8000"

start "PatentAI Frontend" cmd /k "cd /d C:\Users\money\patent-ai\backend\frontend && ..\ .venv\Scripts\python.exe -m streamlit run frontend.py"

echo All services started.
pause
