@echo off
REM View Allure Report via HTTP Server
REM Fixes CORS issues with file:// protocol

cd /d "%~dp0"

echo ============================================================
echo Allure Report Viewer
echo ============================================================
echo.
echo Starting HTTP server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python -m refua_tests.reports.serveHttp
