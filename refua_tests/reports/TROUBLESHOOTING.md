# Troubleshooting Allure Reports

## Issue: Report Shows Empty Data

### Problem
The Allure HTML report opens but shows no test data, graphs, or results.

### Root Cause
Modern browsers block certain resources when opening HTML files via `file://` protocol due to **CORS (Cross-Origin Resource Sharing)** security restrictions. The Allure report uses JavaScript to fetch JSON data files, which browsers block when served from local file system.

### Solution: Serve via HTTP

**Option 1: Use Batch File** (Easiest)
```bash
view_report.bat
```

**Option 2: Use Python Module**
```bash
python -m refua_tests.reports.serve_http
```

**Option 3: Use Allure Server**
```bash
python -m refua_tests.reports.serve_allure
```

### Why This Works
- HTTP server serves the report on `http://localhost:8000`
- Browser allows cross-origin requests when served via HTTP
- All JavaScript and JSON data loads correctly
- Report displays with all data and graphs

## Complete Workflow

### 1. Generate Fresh Results
```bash
# Clean old data
rm -rf allure/results allure/report

# Run tests
TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v
```

### 2. Generate Report
```bash
python -m refua_tests.reports.generate_report_java
```

### 3. View Report (via HTTP)
```bash
# Use batch file
view_report.bat

# OR use Python
python -m refua_tests.reports.serve_http
```

### 4. Access in Browser
- Opens automatically at: `http://localhost:8000`
- Or manually navigate to: `http://localhost:8000`

## Quick Commands

```bash
# Full workflow - one command
TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v && python -m refua_tests.reports.generate_report_java && python -m refua_tests.reports.serve_http
```

## Other Issues

### No Test Results
**Symptom**: Report says "No data available"
**Solution**: Run tests with `--alluredir=allure/results` flag
```bash
TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v
```

### Old Data Showing
**Symptom**: Report shows old test results
**Solution**: Clean directories first
```bash
rm -rf allure/results allure/report
TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v
python -m refua_tests.reports.generate_report_java
```

### Port Already in Use
**Symptom**: "Port 8000 is already in use"
**Solution**: Use different port
```bash
python -m refua_tests.reports.serve_http --port 8001
```

### Java Not Found
**Symptom**: "Java not found" error
**Solution**: Install Java or use alternative method
```bash
# Alternative: Use Node.js method
python -m refua_tests.reports.generate_report

# Alternative: Use Allure server (requires npm allure-commandline)
python -m refua_tests.reports.serve_allure
```

### Allure Not Found
**Symptom**: "Allure not found" error
**Solution**: Use Java method (doesn't require Allure installation)
```bash
python -m refua_tests.reports.generate_report_java
```

## Recommended Workflow

For best results, use this workflow:

```bash
# 1. Clean
rm -rf allure/results allure/report

# 2. Run tests
TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v

# 3. Generate report
python -m refua_tests.reports.generate_report_java

# 4. View via HTTP (fixes CORS issues)
view_report.bat
# OR
python -m refua_tests.reports.serve_http
```

## Key Points

✅ **Always use HTTP server** to view reports (not file://)
✅ **Clean old data** before running new tests
✅ **Use --alluredir flag** when running pytest
✅ **Java method is most reliable** for report generation

## See Also

- Quick Start: `QUICK_START.md`
- Full Documentation: `README.md`
- Report Migration: `documents/REPORTS_MIGRATION_SUMMARY.md`
