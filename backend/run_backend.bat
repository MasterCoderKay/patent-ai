@echo off
REM Activate your virtual environment
call .venv\Scripts\activate.bat

REM Run Uvicorn with your app
uvicorn app.main:app --host 0.0.0.0 --port 8000

REM Keep the window open after the server stops
pause
