# Allure Reports Package

This package contains utilities for generating and serving Allure HTML reports from test execution results.

## Overview

According to the project architecture (see `documents/ARCHITECTURE.md`), report generation belongs in the **TEST repository** (refuaAutomationTests), not in the core framework. This package provides multiple methods to generate and view Allure reports.

## Package Structure

```
refua_tests/reports/
├── __init__.py              # Package initialization
├── generate_report.py       # Generate report using Node.js wrapper
├── generate_report_java.py  # Generate report using Java directly (recommended)
├── serve_allure.py          # Serve report with Allure built-in server
├── serve_http.py            # Serve report via Python HTTP server
└── README.md                # This file
```

## Usage

### Quick Start (Recommended)

From the project root, run:

```bash
# Generate report using Java (most reliable)
python -m refua_tests.reports.generate_report_java

# Or use the batch file
generate_report.bat
```

### Method 1: Generate Static HTML Report (Java)

**Recommended** - Bypasses npm wrapper issues with spaces in Windows usernames.

```bash
python -m refua_tests.reports.generate_report_java
```

**What it does:**
- Generates static HTML report in `allure/report/` folder
- Opens report in default browser
- Works around Windows path issues

**Pros:**
- Most reliable method
- No server required
- Can view offline

**Cons:**
- May have CORS issues with some resources

### Method 2: Generate Static HTML Report (Node.js)

Uses the Node.js wrapper for Allure.

```bash
python -m refua_tests.reports.generate_report
```

**What it does:**
- Generates static HTML report using npm's allure-commandline
- Opens report in default browser

**Pros:**
- Official method
- Good for standard setups

**Cons:**
- May fail with spaces in Windows username
- Requires proper npm installation

### Method 3: Serve with Allure Server

Uses Allure's built-in server.

```bash
python -m refua_tests.reports.serve_allure
```

**What it does:**
- Generates report and starts Allure server
- Opens browser automatically
- Server runs until Ctrl+C

**Pros:**
- No CORS issues
- Dynamic server
- Official Allure method

**Cons:**
- Keeps terminal occupied
- Requires manual stop (Ctrl+C)

### Method 4: Serve with Python HTTP Server

Uses Python's built-in HTTP server.

```bash
# Default port 8000
python -m refua_tests.reports.serve_http

# Custom port
python -m refua_tests.reports.serve_http --port 8001
```

**What it does:**
- Serves existing `allure/report/` via HTTP
- Opens browser automatically
- Fixes CORS issues

**Pros:**
- No CORS issues
- Simple Python server
- Custom port support

**Cons:**
- Requires report to be generated first
- Keeps terminal occupied

## Prerequisites

### Required

1. **Python packages** (already in requirements.txt):
   ```bash
   pip install -r requirements.txt
   ```

2. **Playwright** (for test execution):
   ```bash
   playwright install
   ```

### Optional (for Node.js methods)

3. **Allure Commandline** (for generate_report.py and serve_allure.py):
   ```bash
   npm install -g allure-commandline
   ```

### Optional (for Java method)

4. **Java** (for generate_report_java.py):
   ```bash
   # Check if Java is installed
   java -version

   # If not installed, download from:
   # https://www.oracle.com/java/technologies/downloads/
   ```

## Workflow

### 1. Run Tests

First, execute tests to generate results:

```bash
# Run all tests
TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v

# Run specific tests
TEST_ENV=test pytest refua_tests/tests/test_main_page.py --alluredir=allure/results -v
```

This creates `allure/results/` folder with test results.

### 2. Generate Report

Use any of the methods above:

```bash
# Recommended
python -m refua_tests.reports.generate_report_java
```

### 3. View Report

Report opens automatically in your browser. You can also:

```bash
# View manually
start allure/report\index.html

# Or serve via HTTP
python -m refua_tests.reports.serve_http
```

## Troubleshooting

### "Allure not found"

**Solution 1** (Recommended): Use Java method
```bash
python -m refua_tests.reports.generate_report_java
```

**Solution 2**: Install Allure commandline
```bash
npm install -g allure-commandline
```

### "Java not found"

Download and install Java:
- https://www.oracle.com/java/technologies/downloads/

### "allure/results not found"

You need to run tests first:
```bash
TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v
```

### "Port already in use"

Use a different port:
```bash
python -m refua_tests.reports.serve_http --port 8001
```

### Report shows missing icons/images

This is a CORS issue. Use one of these solutions:

**Option 1**: Serve via HTTP server
```bash
python -m refua_tests.reports.serve_http
```

**Option 2**: Serve via Allure server
```bash
python -m refua_tests.reports.serve_allure
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run tests
  run: |
    TEST_ENV=test pytest refua_tests/tests/ --alluredir=allure/results -v

- name: Generate report
  if: always()
  run: |
    python -m refua_tests.reports.generate_report_java

- name: Upload report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: allure/report
    path: allure/report/
```

## Directory Structure

After running tests and generating reports:

```
refuaAutomationTests/
├── allure/results/          # Test execution results (gitignored)
├── allure/report/           # Generated HTML report (gitignored)
├── refua_tests/
│   └── reports/             # This package
├── generate_report.bat      # Quick access script (Windows)
└── pytest.ini               # Pytest configuration
```

## Related Documentation

- **Architecture**: See `documents/ARCHITECTURE.md`
- **Test Guide**: See `CLAUDE.md`
- **Quick Start**: See `README.md`

## Notes

- Report directories (`allure/results/`, `allure/report/`) are gitignored
- Reports are specific to the TEST repository, not the core framework
- Multiple report generation methods are provided for flexibility
- Java method is most reliable for Windows environments with spaces in usernames
