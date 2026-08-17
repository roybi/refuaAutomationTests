# Quick Start - Allure Reports

## TL;DR - Generate Report Now

```bash
# Option 1: Use batch file (Windows)
generate_report.bat

# Option 2: Use Python module
python -m refua_tests.reports.generate_report_java
```

## Three Steps to View Reports

### 1. Run Tests

```bash
TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v
```

### 2. Generate Report

```bash
python -m refua_tests.reports.generate_report_java
```

### 3. View Report

Report opens automatically in browser, or manually open:
```
allure/report/index.html
```

## All Available Commands

```bash
# Generate static HTML (Java - most reliable)
python -m refua_tests.reports.generate_report_java

# Generate static HTML (Node.js)
python -m refua_tests.reports.generate_report

# Serve with Allure server (dynamic)
python -m refua_tests.reports.serve_allure

# Serve with Python HTTP server
python -m refua_tests.reports.serve_http
python -m refua_tests.reports.serve_http --port 8001
```

## Troubleshooting

### No allure/results folder?
→ Run tests first with `--alluredir=allure/results`

### Java not found?
→ Install Java from https://www.oracle.com/java/technologies/downloads/

### Allure not found?
→ Use Java method (generate_report_java) - doesn't need Allure installed

### Missing images/icons in report?
→ Use HTTP server: `python -m refua_tests.reports.serve_http`

## See Also

- Full documentation: `README.md`
- Architecture: `documents/ARCHITECTURE.md`
- Test guide: `CLAUDE.md`
