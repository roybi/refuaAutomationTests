@echo off
REM Start the test-runner website on http://localhost:8080 (run tests from the browser, open Allure reports).
REM Needs: venv with requirements.txt + requirements-service.txt, and Allure CLI + Java for the reports.
REM Results, logs and reports are kept in .service_data\ (override with: set DATA_DIR=D:\refua_data)

cd /d "%~dp0"

if not defined SERVICE_PORT set SERVICE_PORT=8080

echo ============================================================
echo Refua automation runner  -  http://localhost:%SERVICE_PORT%
echo Press Ctrl+C to stop
echo ============================================================

start "" "http://localhost:%SERVICE_PORT%"
venv\Scripts\python.exe -m uvicorn refua_service.app:app --host 127.0.0.1 --port %SERVICE_PORT% --workers 1
