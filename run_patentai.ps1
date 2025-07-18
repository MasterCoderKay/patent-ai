# Activate virtual environment
. .\backend\.venv\Scripts\Activate.ps1

# Start FastAPI backend in background
Start-Process powershell -ArgumentList "uvicorn app.main:app --host 0.0.0.0 --port 8000" -WorkingDirectory "backend"

# Wait a couple seconds for backend to boot
Start-Sleep -Seconds 2

# Start Streamlit frontend
streamlit run backend\frontend\app_ui.py
