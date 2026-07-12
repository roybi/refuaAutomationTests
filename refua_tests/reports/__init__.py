"""
Allure Report Generation and Serving Package

This package contains utilities for generating and serving Allure HTML reports
from test execution results.

Modules:
- generate_report: Generate Allure HTML report using Node.js wrapper
- generate_report_java: Generate Allure HTML report using Java directly
- serve_allure: Serve Allure report with built-in server
- serve_http: Serve static HTML report via HTTP server
"""

__all__ = [
    'generate_allure_report',
    'generate_report_with_java',
    'serve_allure_report',
    'serve_report'
]
