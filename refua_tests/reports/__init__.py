"""
Allure Report Generation and Serving Package

This package contains utilities for generating and serving Allure HTML reports
from test execution results.

Modules:
- generateReport: Generate Allure HTML report using Node.js wrapper
- generateReportJava: Generate Allure HTML report using Java directly
- serveAllure: Serve Allure report with built-in server
- serveHttp: Serve static HTML report via HTTP server
"""

__all__ = [
    'generate_allure_report',
    'generate_report_with_java',
    'serve_allure_report',
    'serve_report'
]
