@echo off
setlocal enabledelayedexpansion

echo 🚀 Initializing AI Currency Guardian PRO Suite for Windows...

:: Check if venv exists
if not exist "venv" (
    echo 📦 Virtual environment not found. Setting up...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ❌ Failed to create virtual environment.
        exit /b 1
    )
    call venv\Scripts\activate
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

:: Function to start streamlit
echo 🛡️  Starting Streamlit Pro UI at http://localhost:8501 ...
start /B streamlit run app.py --server.port 8501 > streamlit.log 2>&1

:: Function to start flask
echo 🌐 Starting Flask Classic UI at http://127.0.0.1:5000 ...
start /B python server.py > server.log 2>&1

echo -------------------------------------------------------
echo 📊 Dashboard Status:
echo 👉 Pro Interface: http://localhost:8501
echo 👉 Classic Interface: http://127.0.0.1:5000
echo -------------------------------------------------------
echo Use stop.bat to terminate all services.
echo Logs are being written to streamlit.log and server.log
pause
