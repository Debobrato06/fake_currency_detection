@echo off
echo 🛑 Terminating AI Currency Guardian Services...

:: Stop Streamlit and Flask by killing python processes running them
:: Note: This kills all python processes that match the script names.
echo ✅ Stopping Streamlit...
for /f "tokens=2" %%i in ('tasklist /nh /fi "imagename eq python.exe" /v ^| findstr /i "app.py"') do (
    taskkill /F /PID %%i >nul 2>&1
)

echo ✅ Stopping Flask...
for /f "tokens=2" %%i in ('tasklist /nh /fi "imagename eq python.exe" /v ^| findstr /i "server.py"') do (
    taskkill /F /PID %%i >nul 2>&1
)

:: Fallback: Kill any remaining streamlit processes
taskkill /F /IM streamlit.exe /T >nul 2>&1

echo ✅ All services stopped.
pause
