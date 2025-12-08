# refuaAutomationTests

**Test Automation Implementation for MEDITEK Medical Application**

## Overview

This repository contains comprehensive test automation for the MEDITEK medical application. It uses the **refuaAutomationCore** framework for all test infrastructure, allowing the test code to focus purely on test logic and page object design.

## What is This Repository?

This repository contains **only test implementation** - test cases, page objects, and test data. The reusable **framework infrastructure** is in a separate repository: [`refuaAutomationCore`](https://github.com/org/refuaAutomationCore)

### Key Principle

```
refuaAutomationCore (Framework) ← Reusable Infrastructure
         ↓
refuaAutomationTests (Tests) ← Application Test Implementation
```

The test repository **depends on** the framework, not the other way around.

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/org/refuaAutomationTests.git
cd refuaAutomationTests

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

### 2. Capture Session (One-Time)
```bash
# Capture session for test environment
python -m refua_core.scripts.capture_session --env test --user your_name

# When prompted:
# - Enter your MEDITEK credentials
# - Complete 2FA manually
# - Session is saved to ~/.refua_sessions/test_your_name.json
```

### 3. Run Tests
```bash
# Run all tests
TEST_ENV=test pytest refua_tests/tests/ -v

# Run specific feature tests
TEST_ENV=test pytest refua_tests/tests/test_authentication.py -v

# Run with Allure reporting
TEST_ENV=test pytest refua_tests/tests/ --alluredir=./allure-results -v
allure serve ./allure-results
```

## Project Structure

```
refuaAutomationTests/
├── refua_tests/
│   ├── pages/                      # Page Object Models
│   │   ├── login_page.py
│   │   ├── dashboard_page.py
│   │   └── patient_page.py
│   ├── tests/                      # Test Cases
│   │   ├── conftest.py            # Fixtures
│   │   ├── test_authentication.py
│   │   ├── test_smoke.py
│   │   └── test_patient_mgmt.py
│   └── fixtures/                   # Test Data & Helpers
│       ├── test_data.py
│       └── helpers.py
├── .env.test                       # Test credentials (do not commit)
├── .env.preprod                    # Preprod credentials (do not commit)
├── .env.prod                       # Production credentials (do not commit)
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python dependencies
├── CLAUDE.md                       # Guidance for Claude Code
├── ARCHITECTURE.md                 # Detailed architecture
└── README.md                       # This file
```

## Test Organization

### Page Objects (`refua_tests/pages/`)
- Encapsulate UI element interactions
- Use Page Object Model (POM) pattern
- Inherit from `refua_core.pages.BasePage`
- One file per page/screen

**Example**:
```python
# refua_tests/pages/login_page.py
from refua_core.pages.base_page import BasePage

class LoginPage(BasePage):
    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()
```

### Test Cases (`refua_tests/tests/`)
- Test implementations for features
- Inherit from `refua_core.core.BaseTest`
- One file per feature
- Use pytest markers for categorization

**Example**:
```python
# refua_tests/tests/test_authentication.py
import pytest
from refua_core.core.base_test import BaseTest
from refua_tests.pages.login_page import LoginPage

@pytest.mark.authentication
class TestAuthentication(BaseTest):
    def test_login_succeeds_with_valid_credentials(self):
        login_page = LoginPage(self.page)
        login_page.goto_login()
        login_page.login("user@test.com", "password")
        login_page.wait_for_url("/dashboard")
```

### Test Data & Fixtures (`refua_tests/fixtures/`)
- Test data factories
- Common helper functions
- Shared pytest fixtures (in `conftest.py`)

## Running Tests

### Basic Commands
```bash
# All tests
TEST_ENV=test pytest refua_tests/tests/ -v

# Specific file
TEST_ENV=test pytest refua_tests/tests/test_auth.py -v

# Specific test
TEST_ENV=test pytest refua_tests/tests/test_auth.py::TestAuth::test_login -v

# Tests matching pattern
TEST_ENV=test pytest refua_tests/tests/ -k "login" -v
```

### Test Markers
```bash
# Smoke tests (quick sanity checks)
TEST_ENV=test pytest refua_tests/tests/ -m smoke -v

# Regression tests (full test suite)
TEST_ENV=test pytest refua_tests/tests/ -m regression -v

# Exclude slow tests
TEST_ENV=test pytest refua_tests/tests/ -m "not slow" -v
```

### Parallel Execution
```bash
# Use all CPU cores
TEST_ENV=test pytest -n auto refua_tests/tests/ -v

# Use specific number of workers
TEST_ENV=test pytest -n 4 refua_tests/tests/ -v
```

### Device/Browser Testing
```bash
# Run on iPhone
TEST_ENV=test DEVICE=iphone_15 pytest refua_tests/tests/ -v

# Run on Android
TEST_ENV=test DEVICE=android_pixel pytest refua_tests/tests/ -v

# Run with Firefox
TEST_ENV=test BROWSER=firefox pytest refua_tests/tests/ -v
```

### Reporting
```bash
# Allure reporting
TEST_ENV=test pytest refua_tests/tests/ --alluredir=./allure-results -v
allure serve ./allure-results

# JUnit XML
TEST_ENV=test pytest refua_tests/tests/ --junit-xml=results.xml -v

# HTML report
TEST_ENV=test pytest refua_tests/tests/ --html=report.html -v
```

## Environment Variables

### Required
```bash
TEST_ENV=test|preprod|prod    # Target environment
```

### Optional
```bash
DEVICE=desktop|iphone|android  # Device profile (default: desktop)
BROWSER=chromium|firefox|webkit  # Browser (default: chromium)
RECORD_VIDEO=true|false        # Capture video (default: true)
SKIP_2FA=true|false            # Use session bypass (default: true)
```

## Features

### Multi-Environment Support
- **test**: Local development (3-day session TTL)
- **preprod**: Integration testing (3-day session TTL)
- **prod**: Production validation (30-min session TTL, read-only)

### 2FA Authentication Bypass
Sessions are captured once with manual 2FA, then reused for all tests:
```bash
# Capture session (once)
python -m refua_core.scripts.capture_session --env test --user your_name

# Tests run without manual 2FA
TEST_ENV=test pytest refua_tests/tests/ -v
```

### Mobile Device Testing
```bash
# Built-in device profiles
TEST_ENV=test DEVICE=iphone_15 pytest refua_tests/tests/ -v
TEST_ENV=test DEVICE=android_pixel pytest refua_tests/tests/ -v
```

### Parallel Execution
```bash
# Run tests on multiple workers
TEST_ENV=test pytest -n auto refua_tests/tests/ -v
```

### Automatic Artifact Management
- **On Pass**: Videos and screenshots are deleted (saves storage)
- **On Fail**: Artifacts are retained for debugging

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/test-new-feature
```

### 2. Write Tests
1. Create page object: `refua_tests/pages/<feature>_page.py`
2. Create test file: `refua_tests/tests/test_<feature>.py`
3. Add test data: `refua_tests/fixtures/test_data.py`

### 3. Run Tests Locally
```bash
TEST_ENV=test pytest refua_tests/tests/test_<feature>.py -v
```

### 4. Commit and Push
```bash
git add refua_tests/
git commit -m "test: add tests for feature"
git push origin feature/test-new-feature
```

### 5. Create Pull Request
Tests run automatically in CI pipeline

## Dependencies

### Core
- `refua-automation-core>=1.0.0` - Reusable framework
- `playwright>=1.40.0` - Browser automation
- `python-dotenv>=1.0.0` - Environment configuration
- `pytest>=7.0.0` - Test framework

### Reporting
- `pytest-xdist>=3.0.0` - Parallel execution
- `pytest-allure-adaptor>=1.0.0` - Allure reporting

### Optional
- `pytest-timeout>=2.1.0` - Test timeout handling
- `faker>=18.0.0` - Fake data generation

See `requirements.txt` for complete list.

## Configuration

### `.env.*` Files (Environment-Specific)
- `.env.test` - Test environment credentials
- `.env.preprod` - Preprod environment credentials
- `.env.prod` - Production environment credentials

**⚠️ Never commit `.env` files with real credentials!**

### `pytest.ini` (Pytest Configuration)
- Test discovery settings
- Markers and categorization
- Logging configuration
- Timeout settings

### `requirements.txt` (Python Dependencies)
- Framework package
- Test dependencies
- Development tools

## Documentation

- **ARCHITECTURE.md** - Detailed test architecture and patterns
- **CLAUDE.md** - Guidance for Claude Code
- **Framework Docs** - See [`refuaAutomationCore` repository](https://github.com/org/refuaAutomationCore)

## Troubleshooting

### Session Expired
```bash
# Recapture session
python -m refua_core.scripts.capture_session --env test --user your_name
```

### Framework Import Error
```bash
# Verify framework installation
python -c "from refua_core.config.environment import EnvironmentManager; print('OK')"

# Reinstall if needed
pip install refua-automation-core
```

### Tests Timeout
- Check `pytest.ini` timeout setting
- Increase for slow operations: `timeout = 600`
- Add explicit waits in page objects

### Flaky Tests
Check for:
- Missing waits (use `page.wait_for_selector()`)
- Race conditions
- Unreliable locators
- Network issues

## Best Practices

### Page Objects
✅ One page object per page/screen
✅ Group locators using @property
✅ Keep locators at top of class
✅ Encapsulate complex interactions
❌ Avoid hard-coded waits
❌ Don't mix UI logic with assertions

### Test Cases
✅ Use Arrange-Act-Assert pattern
✅ Descriptive test names
✅ Test one feature per test
✅ Use fixtures for setup
❌ Avoid test interdependencies
❌ Don't use hard-coded wait times

### Test Data
✅ Use factories to generate test data
✅ Randomize data to avoid conflicts
✅ Isolate test data per test
❌ Hard-coded test data
❌ Sharing test data between tests

## CI/CD Integration

Tests run automatically on:
- Push to feature branch
- Pull request creation
- Merge to main branch

Results are reported in:
- GitHub pull request checks
- Allure reports (if configured)
- Email notifications (if configured)

## Support

For issues or questions:
- Check `ARCHITECTURE.md` for detailed guidance
- Review `CLAUDE.md` for development tips
- Check framework docs: [`refuaAutomationCore`](https://github.com/org/refuaAutomationCore)

## Contributing

1. Create feature branch: `git checkout -b feature/description`
2. Write tests following established patterns
3. Run tests locally: `TEST_ENV=test pytest refua_tests/tests/ -v`
4. Commit with clear messages: `git commit -m "test: description"`
5. Push and create pull request

## License

[Specify your license here]

## See Also

- Framework Repository: [`refuaAutomationCore`](https://github.com/org/refuaAutomationCore)
- Framework Architecture: `refuaAutomationCore/ARCHITECTURE.md`
- Framework Documentation: `refuaAutomationCore/CLAUDE.md`
