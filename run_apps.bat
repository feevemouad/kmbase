@echo off
netstat -ano | findstr :5000 >nul
if %errorlevel% equ 0 (
    echo Flask API is already running
) else (
    start cmd /k "cd .\API\ && flask run"
)
start cmd /k "streamlit run main.py --server.headless true"