# CLAUDE.md - Test Repository Guidance

This file provides guidance to Claude Code when working with the refuaAutomationTests repository.

## ⚠️ Multi-Agent Handoff (MANDATORY)

This repository is worked on by multiple LLM agents (Claude Code and GitHub Copilot).
**At the start of every session, read `AGENT_HANDOFF.md` in the repo root.**

- If its `STATUS` is `IN_PROGRESS`, continue from the `RESUME POINT` — do NOT restart the task.
- Follow the PROTOCOL rules in that file: update the checklist and WORK LOG as you work, and fill in the RESUME POINT before you stop.

## Project Overview

**refuaAutomationTests** is the test automation implementation for the MEDITEK medical application. This repository contains:

- Test cases organized by feature
- Page objects using the Page Object Model pattern
- Test fixtures and test data factories
- Test configuration files
- Environment-specific credentials

**This repository depends on** `refua-automation-core` framework package.

## Repository Architecture

### This Repository: refuaAutomationTests (Test Implementation)

**Purpose**: Test automation for MEDITEK application
**Responsibility**: Test development, page objects, test organization
**Users**: QA team, CI/CD pipeline
**Release**: Project versioning (independent from framework)

```
refuaAutomationTests/           (This repo - test implementation)
├── refua_tests/               # Test package
│   ├── pages/                 # Page Object Models
│   │   ├── login_page.py
│   │   ├── dashboard_page.py
│   │   └── patient_page.py
│   ├── tests/                 # Test cases
│   │   ├── conftest.py        # Pytest fixtures
│   │   ├── test_auth.py
│   │   ├── test_smoke.py
│   │   └── test_patient_mgmt.py
│   └── fixtures/              # Test utilities
│       ├── test_data.py       # Data factories
│       └── helpers.py         # Helper functions
├── .env.test                  # Test credentials
├── .env.preprod               # Preprod credentials
├── .env.prod                  # Production credentials
├── pytest.ini                 # Pytest configuration
├── requirements.txt           # Dependencies
├── CLAUDE.md                  # This file
├── ARCHITECTURE.md            # Detailed architecture
└── README.md                  # Test guide
```

### Separate Repository: refuaAutomationCore (Framework)

**Purpose**: Reusable test automation framework
**Contains**: Configuration, base classes, infrastructure
**Published**: As `refua-automation-core` package
**Location**: https://github.com/org/refuaAutomationCore

## Key Files and Their Purposes

### Test Code

#### `refua_tests/pages/` - Page Object Models

- **Purpose**: Encapsulate UI element interactions
- **Pattern**: Page Object Model (POM)
- **Inheritance**: Inherit from `refua_core.pages.BasePage`
- **Organization**: One file per page/screen
- **Naming**: `<feature>_page.py`

**Example Structure**:

```python
# refua_tests/pages/login_page.py
from playwright.sync_api import Page, Locator
from refua_core.pages.base_page import BasePage

class LoginPage(BasePage):
    @property
    def email_input(self) -> Locator:
        return self.page.locator("[data-testid='email']")

    def login(self, email: str, password: str):
        self.email_input.fill(email)
        # ... continue implementation
```

#### `refua_tests/tests/` - Test Cases

- **Purpose**: Test implementations for features
- **Base Class**: Inherit from `refua_core.core.BaseTest`
- **Organization**: One file per feature
- **Naming**: `test_<feature>.py`
- **Markers**: Use `@pytest.mark` for categorization

**Example Structure**:

```python
# refua_tests/tests/test_authentication.py
import pytest
from refua_core.core.base_test import BaseTest
from refua_tests.pages.login_page import LoginPage

@pytest.mark.authentication
class TestAuthentication(BaseTest):
    def test_login_with_valid_credentials(self):
        # Test implementation
        pass
```

#### `refua_tests/tests/conftest.py` - Pytest Fixtures

- **Purpose**: Shared fixtures for tests
- **Scope**: Can be function, class, module, or session
- **Usage**: Used via pytest parameters

**Example**:

```python
# refua_tests/tests/conftest.py
import pytest
from refua_tests.fixtures.test_data import create_test_user

@pytest.fixture
def test_user():
    """Provide test user data"""
    return create_test_user()
```

#### `refua_tests/fixtures/test_data.py` - Test Data Factories

- **Purpose**: Generate test data for tests
- **Pattern**: Factory pattern for reusability
- **Usage**: Called from tests or fixtures

**Example**:

```python
# refua_tests/fixtures/test_data.py
from dataclasses import dataclass

@dataclass
class UserData:
    email: str
    password: str

def create_test_user(email: str = None) -> UserData:
    return UserData(email=email or "test@test.local", password="password")
```

### Configuration Files

#### `.env.test`, `.env.preprod`, `.env.prod`

- **Purpose**: Environment-specific credentials
- **Security**: Never commit to version control
- **Usage**: Loaded by `EnvironmentManager` from framework
- **Variables**: User emails, passwords, API endpoints

#### `pytest.ini`

- **Purpose**: Pytest configuration
- **Defines**: Test markers, timeout, logging, paths
- **Usage**: Automatically loaded by pytest

#### `requirements.txt`

- **Purpose**: Python package dependencies
- **Key Dependency**: `refua-automation-core` framework
- **Usage**: `pip install -r requirements.txt`

#### `CLAUDE.md` (this file)

- **Purpose**: Guidance for Claude Code
- **Usage**: Context for AI assistance

#### `ARCHITECTURE.md`

- **Purpose**: Detailed architecture documentation
- **Contents**: Test structure, patterns, best practices

#### `README.md`

- **Purpose**: Test repository overview
- **Contents**: Quick start, setup instructions

## For Different Roles

### Test Author / QA Engineer

**Your Focus**: Write and maintain tests

**Setup**:

```bash
git clone https://github.com/org/refuaAutomationTests.git
cd refuaAutomationTests
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

**Capture Session** (once per environment):

```bash
python -m refua_core.scripts.capture_session --env test --user your_name
# Complete 2FA manually when prompted
```

**Write Tests**:

1. Create page object: `refua_tests/pages/<feature>_page.py`
2. Create test file: `refua_tests/tests/test_<feature>.py`
3. Add test data: `refua_tests/fixtures/test_data.py`

**Run Tests**:

```bash
# Run all tests
TEST_ENV=test pytest refua_tests/tests/ -v

# Run specific tests
TEST_ENV=test pytest refua_tests/tests/test_auth.py -v -k "login"

# Run with reporting
TEST_ENV=test pytest refua_tests/tests/ --alluredir=./allure/results -v
```

**CI Integration**:

- Repository will auto-run tests on push
- Tests execute with TEST_ENV=test
- Results reported in pull requests

### Test Architect

**Your Focus**: Architecture, patterns, test strategy

**Responsibilities**:

- Design test architecture and organization
- Define test markers and categories
- Establish page object patterns
- Create test data strategies
- Plan test coverage
- Document test procedures

**Key Files to Review**:

- `docs/architecture/ARCHITECTURE.md` - Test structure and patterns
- `refua_tests/tests/conftest.py` - Shared fixtures
- `refua_tests/fixtures/test_data.py` - Data strategies
- `pytest.ini` - Configuration and markers

**Common Tasks**:

- Add new test markers in `pytest.ini`
- Create test data factories in `fixtures/test_data.py`
- Design page object hierarchy
- Define test organization structure

### CI/CD Engineer

**Your Focus**: Test execution infrastructure

**Key Files**:

- `.github/workflows/` - CI/CD pipelines
- `pytest.ini` - Test execution settings
- `requirements.txt` - Dependencies
- `.env.test` - Test credentials (via secrets)

**CI Pipeline Template**:

```yaml
- name: Run tests
  run: |
    TEST_ENV=test pytest refua_tests/tests/ -v --alluredir=./allure/results

- name: Upload reports
  uses: actions/upload-artifact@v3
  with:
    name: allure/results
    path: allure/results/
```

## Setup & Installation

### Prerequisites

- Python 3.9+
- Git
- Virtual environment

### Installation Steps

1. **Clone Repository**:

   ```bash
   git clone https://github.com/org/refuaAutomationTests.git
   cd refuaAutomationTests
   ```

2. **Create Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Verify Installation**:

   ```bash
   python -c "from refua_core.config.environment import EnvironmentManager; print('Framework installed OK')"
   ```

5. **Create Session Directory**:

   ```bash
   mkdir -p ~/.refua_sessions
   ```

6. **Capture Session** (one-time per user/environment):
   ```bash
   python -m refua_core.scripts.capture_session --env test --user your_name
   # Enter credentials and complete 2FA manually
   ```

## Running Tests

### Basic Execution

```bash
# Run all tests
TEST_ENV=test pytest refua_tests/tests/ -v

# Run specific test file
TEST_ENV=test pytest refua_tests/tests/test_authentication.py -v

# Run specific test
TEST_ENV=test pytest refua_tests/tests/test_authentication.py::TestAuthentication::test_login -v
```

### Test Filtering

```bash
# Run only smoke tests
TEST_ENV=test pytest refua_tests/tests/ -m smoke -v

# Run tests matching pattern
TEST_ENV=test pytest refua_tests/tests/ -k "login" -v

# Skip slow tests
TEST_ENV=test pytest refua_tests/tests/ -m "not slow" -v
```

### Parallel Execution

```bash
# Auto CPU cores
TEST_ENV=test pytest -n auto refua_tests/tests/ -v

# Specific workers
TEST_ENV=test pytest -n 4 refua_tests/tests/ -v
```

### Mobile/Device Testing

```bash
# Run on iPhone
TEST_ENV=test DEVICE=iphone_15 pytest refua_tests/tests/ -v

# Run on Android
TEST_ENV=test DEVICE=android_pixel pytest refua_tests/tests/ -v
```

### Reporting

```bash
# Allure report
TEST_ENV=test pytest refua_tests/tests/ --alluredir=./allure/results -v
allure serve ./allure/results

# JUnit XML
TEST_ENV=test pytest refua_tests/tests/ --junit-xml=results.xml -v

# HTML report
TEST_ENV=test pytest refua_tests/tests/ --html=report.html -v
```

## Development Workflow

### Create Feature Branch

```bash
git checkout -b feature/test-new-feature
```

### Write Tests

1. Create page object: `refua_tests/pages/<feature>_page.py`
2. Create test file: `refua_tests/tests/test_<feature>.py`
3. Add fixtures if needed: `refua_tests/fixtures/test_data.py`

### Run Tests Locally

```bash
TEST_ENV=test pytest refua_tests/tests/test_feature.py -v
```

### Commit Changes

```bash
git add refua_tests/
git commit -m "test: add tests for feature"
git push origin feature/test-new-feature
```

### Create Pull Request

- Tests run automatically in CI
- Provide test coverage information
- Document test scenarios

## Environment Variables

### Required

```bash
TEST_ENV=test|preprod|prod    # Target environment (required)
```

### Optional

```bash
SKIP_2FA=true|false            # Use session bypass (default: true)
DEVICE=desktop|iphone|android  # Device profile (default: desktop)
BROWSER=chromium|firefox|webkit # Browser (default: chromium)
RECORD_VIDEO=true|false        # Capture video (default: true)
```

## Project Structure Reference

```
refuaAutomationTests/
├── refua_tests/
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── base_page.py           # Local base (extends framework)
│   │   ├── login_page.py
│   │   ├── dashboard_page.py
│   │   └── patient_page.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py            # Shared fixtures
│   │   ├── test_authentication.py
│   │   ├── test_smoke.py
│   │   └── test_patient_mgmt.py
│   └── fixtures/
│       ├── __init__.py
│       ├── test_data.py           # Data factories
│       └── helpers.py             # Helpers
├── pytest.ini
├── requirements.txt
├── .env.test
├── .env.preprod
├── .env.prod
├── CLAUDE.md                      # This file
├── ARCHITECTURE.md
├── README.md
└── .gitignore
```

## Common Tasks

### Add New Test

1. Create page object in `refua_tests/pages/<feature>_page.py`
2. Create test in `refua_tests/tests/test_<feature>.py`
3. Create test data in `refua_tests/fixtures/test_data.py`
4. Run: `TEST_ENV=test pytest refua_tests/tests/test_<feature>.py -v`

### Add New Page Object

1. Create file: `refua_tests/pages/<feature>_page.py`
2. Inherit from `BasePage` (from base_page.py)
3. Define locators using @property
4. Implement page-specific actions
5. Use in tests

### Add Test Marker

1. Edit `pytest.ini`
2. Add marker in `[pytest]` markers section
3. Use in tests: `@pytest.mark.my_marker`

### Debug Test

```bash
# Run with verbose output
TEST_ENV=test pytest refua_tests/tests/test_file.py::TestClass::test_method -vv -s

# Stop on first failure
TEST_ENV=test pytest refua_tests/tests/test_file.py -x

# Show print statements
TEST_ENV=test pytest refua_tests/tests/test_file.py -s

# Last failed tests
TEST_ENV=test pytest --lf refua_tests/tests/
```

## Troubleshooting

### Framework Not Found

```bash
# Verify installation
python -c "from refua_core.config.environment import EnvironmentManager; print('OK')"

# Reinstall if needed
pip install refua-automation-core
```

### Session Expired

```bash
# Recapture session
python -m refua_core.scripts.capture_session --env test --user your_name
```

### Tests Timeout

- Check `pytest.ini` timeout setting
- Increase for slow operations: `timeout = 600`
- Add explicit waits in page objects

### Import Errors

- Ensure virtual environment is activated
- Verify `requirements.txt` is installed
- Check `PYTHONPATH` if using local framework

## Documentation

- **Detailed Architecture**: See `docs/architecture/ARCHITECTURE.md`
- **Framework Documentation**: See `refuaAutomationCore/ARCHITECTURE.md`
- **Framework API**: See `refuaAutomationCore/CLAUDE.md`
- **Quick Reference**: See `refuaAutomationCore/PARAMETER_GUIDE.md`

## Next Steps

1. Complete setup and install dependencies
2. Capture session for test environment
3. Review existing page objects and tests
4. Write tests for assigned features
5. Run tests locally before pushing
6. Create pull request with test implementation

---

**Questions?** Refer to:

- `docs/architecture/ARCHITECTURE.md` - Test structure and patterns
- `README.md` - Quick start guide
- Framework repo `CLAUDE.md` - Framework documentation
