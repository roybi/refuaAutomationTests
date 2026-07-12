@echo off
REM Allure Report Generator - Quick Access Script
REM Calls the Python package module

cd /d "%~dp0"

echo ============================================================
echo Allure Report Generator
echo ============================================================
echo.
echo Running: python -m refua_tests.reports.generate_report_java
echo.

python -m refua_tests.reports.generate_report_java

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Report generation failed
    echo.
    echo Alternative methods:
    echo   1. python -m refua_tests.reports.generate_report
    echo   2. python -m refua_tests.reports.serve_allure
    echo.
    pause
)
