# refuaAutomationTests - Test Implementation Architecture

**Test Repository for MEDITEK Application**
**Last Updated:** December 2025
**Status:** Setting up test implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Repository Structure](#repository-structure)
3. [Test Organization](#test-organization)
4. [Page Object Model (POM)](#page-object-model-pom)
5. [Test Cases](#test-cases)
6. [Configuration](#configuration)
7. [Execution](#execution)
8. [Development Workflow](#development-workflow)
9. [Best Practices](#best-practices)

---

## Overview

### Purpose
This repository contains **test automation implementation** for the MEDITEK medical application. It uses the **refuaAutomationCore** framework as the foundation for all test infrastructure.

### Key Characteristics
- **Depends on**: `refua-automation-core` framework package
- **Contains**: Test cases, page objects, test data, and test configuration
- **Focus**: Business logic testing, not framework infrastructure
- **Versioning**: Independent from framework (tied to application releases)

### Relationship to Core Framework
```
refuaAutomationCore (Framework)
        ↑
        │ pip install refua-automation-core
        │
refuaAutomationTests (Tests) ← This Repository
```

**Important Principle**: This repository **depends on** the framework, not vice versa. The framework does NOT import from this repository.

---

## Repository Structure

### Full Directory Layout

```
refuaAutomationTests/
│
├── refua_tests/                   # Test package
│   ├── __init__.py
│   │
│   ├── pages/                     # Page Object Models
│   │   ├── __init__.py
│   │   ├── base_page.py           # Local base (inherits from framework)
│   │   ├── login_page.py          # Login page object
│   │   ├── dashboard_page.py      # Dashboard page object
│   │   ├── patient_page.py        # Patient management page
│   │   └── settings_page.py       # Settings page
│   │
│   ├── tests/                     # Test Cases
│   │   ├── __init__.py
│   │   ├── conftest.py            # Pytest fixtures and configuration
│   │   ├── test_authentication.py # Authentication tests
│   │   ├── test_smoke.py          # Smoke tests
│   │   ├── test_patient_mgmt.py   # Patient management tests
│   │   └── test_settings.py       # Settings tests
│   │
│   └── fixtures/                  # Test Fixtures and Utilities
│       ├── __init__.py
│       ├── test_data.py           # Test data factories
│       └── helpers.py             # Common helper functions
│
├── .env.test                      # Test environment credentials
├── .env.preprod                   # Preprod environment credentials
├── .env.prod                      # Production environment credentials
│
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Python dependencies
├── setup.py (optional)            # Optional: if packaging tests
│
├── CLAUDE.md                      # Guidance for Claude Code
├── README.md                      # Test repository overview
├── ARCHITECTURE.md                # This file
├── .gitignore                     # Git ignore rules
│
└── documents/                     # Documentation (optional)
    └── TEST_GUIDE.md              # Detailed testing guide
```

### Directory Purposes

#### `refua_tests/`
Main package directory containing all test code.

**Responsibilities**:
- Organize test code into logical modules
- Maintain clear separation between pages, tests, and fixtures
- Follow Python packaging conventions

#### `refua_tests/pages/`
Page Object Models implementing the POM pattern.

**Contains**:
- `base_page.py`: Local base class (extends refua_core's BasePage)
- Individual page objects for each screen/feature
- Locator definitions
- Page-specific actions

**Naming Convention**: `<feature>_page.py`

#### `refua_tests/tests/`
Test case files organized by feature.

**Contains**:
- `conftest.py`: Pytest fixtures and hooks
- Test case files with test functions
- Test markers (@pytest.mark.smoke, @pytest.mark.regression)
- Test documentation

**Naming Convention**: `test_<feature>.py`

#### `refua_tests/fixtures/`
Reusable test fixtures, utilities, and test data.

**Contains**:
- Test data factories (create_user_data, create_patient_data, etc.)
- Helper functions (common actions, assertions)
- Mock data and test datasets

**Files**:
- `test_data.py`: Test data factories and builders
- `helpers.py`: Common utility functions

---

## Test Organization

### Test File Structure

#### Test Anatomy
```python
# refua_tests/tests/test_authentication.py

import pytest
from playwright.sync_api import Page
from refua_core.core.base_test import BaseTest
from refua_tests.pages.login_page import LoginPage
from refua_tests.fixtures.test_data import create_test_user

# Markers for categorization
@pytest.mark.authentication
@pytest.mark.smoke
class TestAuthentication(BaseTest):
    """Authentication feature tests"""

    def test_valid_login(self):
        """Test: User can login with valid credentials"""
        # Arrange
        user_data = create_test_user()
        login_page = LoginPage(self.page)

        # Act
        login_page.goto("/login")
        login_page.login(user_data["email"], user_data["password"])

        # Assert
        login_page.wait_for_url("/dashboard")

    @pytest.mark.regression
    def test_invalid_password(self):
        """Test: Login fails with invalid password"""
        # Arrange
        login_page = LoginPage(self.page)
        user_data = create_test_user()

        # Act
        login_page.goto("/login")
        login_page.login(user_data["email"], "wrong_password")

        # Assert
        error_message = login_page.get_error_message()
        assert "Invalid credentials" in error_message
```

### Test Markers

```python
# In pytest.ini or conftest.py
markers = [
    "smoke: Quick sanity tests for critical functionality",
    "regression: Regression test suite",
    "authentication: Authentication-related tests",
    "patient_management: Patient management tests",
    "performance: Performance and load tests",
    "slow: Tests that take longer than normal",
    "integration: Integration tests",
    "ui: User interface tests",
]
```

### Test Naming Conventions

```
File:      test_<feature>.py
Class:     Test<Feature>
Method:    test_<action>_<expected_result>

Examples:
test_authentication.py
    ├─ TestAuthentication
    │   ├─ test_valid_login_succeeds
    │   ├─ test_invalid_password_shows_error
    │   └─ test_session_expires_redirects_to_login
    │
test_patient_management.py
    ├─ TestPatientCreation
    │   ├─ test_create_patient_with_valid_data
    │   └─ test_create_patient_missing_required_field_fails
    │
    ├─ TestPatientSearch
    │   └─ test_search_patient_by_id_returns_results
```

---

## Page Object Model (POM)

### Base Page Class

```python
# refua_tests/pages/base_page.py

from playwright.sync_api import Page
from refua_core.pages.base_page import BasePage as CoreBasePage
from refua_core.config.environment import EnvironmentManager

class BasePage(CoreBasePage):
    """
    Local base page extending framework's BasePage.
    Adds MEDITEK-specific functionality.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.env_manager = EnvironmentManager.get_instance()

    def wait_for_page_load(self, timeout: int = 30000):
        """Wait for page to fully load (custom indicator)"""
        # Custom implementation for MEDITEK
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        # Custom authentication check
        return self.page.evaluate("() => !!localStorage.getItem('auth_token')")
```

### Page Object Example

```python
# refua_tests/pages/login_page.py

from playwright.sync_api import Page, Locator
from refua_tests.pages.base_page import BasePage

class LoginPage(BasePage):
    """Login page object for MEDITEK application"""

    # Locators (specific to MEDITEK)
    @property
    def email_input(self) -> Locator:
        return self.page.locator("[data-testid='email-input']")

    @property
    def password_input(self) -> Locator:
        return self.page.locator("[data-testid='password-input']")

    @property
    def login_button(self) -> Locator:
        return self.page.locator("[data-testid='login-btn']")

    @property
    def error_message(self) -> Locator:
        return self.page.locator("[data-testid='error-message']")

    @property
    def remember_me_checkbox(self) -> Locator:
        return self.page.locator("[data-testid='remember-me']")

    # Actions
    def goto_login(self):
        """Navigate to login page"""
        self.goto("/login")
        self.page.wait_for_load_state("networkidle")

    def login(self, email: str, password: str, remember: bool = False):
        """Perform login with email and password"""
        self.email_input.fill(email)
        self.password_input.fill(password)

        if remember:
            self.remember_me_checkbox.click()

        self.login_button.click()
        self.page.wait_for_load_state("networkidle")

    def get_error_message(self) -> str:
        """Get displayed error message"""
        if self.error_message.is_visible():
            return self.error_message.text_content()
        return ""

    def is_error_displayed(self) -> bool:
        """Check if error message is visible"""
        return self.error_message.is_visible()
```

### Page Object Best Practices

```python
# ✅ GOOD: Clear method names, single responsibility
class PatientPage(BasePage):
    def search_patient(self, patient_id: str) -> bool:
        self.search_input.fill(patient_id)
        self.search_button.click()
        return self.page.wait_for_selector(".patient-result", timeout=5000)

    def get_patient_name(self) -> str:
        return self.patient_name_field.text_content()

# ❌ AVOID: Unclear names, multiple responsibilities
class PatientPage(BasePage):
    def do_stuff(self):
        self.input1.fill("data")
        self.button1.click()
        self.input2.fill("more")

# ✅ GOOD: Locators organized at top
class DashboardPage(BasePage):
    @property
    def welcome_message(self) -> Locator:
        return self.page.locator(".welcome")

    @property
    def patient_count(self) -> Locator:
        return self.page.locator("[data-metric='patient-count']")

# ❌ AVOID: Locators scattered in methods
class DashboardPage(BasePage):
    def get_welcome(self):
        return self.page.locator(".welcome").text_content()

    def get_count(self):
        welcome = self.page.locator(".welcome")  # Repeated locator logic
```

---

## Test Cases

### Test Structure

```python
# refua_tests/tests/test_patient_management.py

import pytest
from refua_core.core.base_test import BaseTest
from refua_tests.pages.patient_page import PatientPage
from refua_tests.fixtures.test_data import create_patient_data

@pytest.mark.patient_management
class TestPatientCreation(BaseTest):
    """Test patient creation functionality"""

    def setUp(self):
        """Called before each test"""
        super().setUp()
        self.patient_page = PatientPage(self.page)
        self.patient_page.goto_patient_list()

    @pytest.mark.smoke
    def test_create_patient_with_valid_data(self):
        """Verify patient can be created with valid data"""
        # Arrange
        patient_data = create_patient_data(
            first_name="John",
            last_name="Doe",
            email="john@test.com"
        )

        # Act
        self.patient_page.click_create_button()
        self.patient_page.fill_patient_form(patient_data)
        self.patient_page.submit_form()

        # Assert
        assert self.patient_page.is_success_message_visible()
        assert self.patient_page.get_patient_count() == "1"

    def test_create_patient_without_email_fails(self):
        """Verify patient creation fails without email"""
        # Arrange
        invalid_data = create_patient_data(email=None)

        # Act
        self.patient_page.click_create_button()
        self.patient_page.fill_patient_form(invalid_data)
        self.patient_page.submit_form()

        # Assert
        assert self.patient_page.is_error_message_visible()
        error_text = self.patient_page.get_error_message()
        assert "email" in error_text.lower()

    @pytest.mark.regression
    def test_form_validation_shows_all_required_field_errors(self):
        """Verify all required field validations are shown"""
        # Test implementation...
```

### Test Data Fixtures

```python
# refua_tests/fixtures/test_data.py

from dataclasses import dataclass
from datetime import datetime
import random
import string

@dataclass
class UserData:
    email: str
    password: str
    first_name: str
    last_name: str

@dataclass
class PatientData:
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: str

def generate_random_email() -> str:
    """Generate random email for testing"""
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_id}@test.local"

def create_test_user(
    email: str = None,
    password: str = "TestPassword123",
    first_name: str = "Test",
    last_name: str = "User"
) -> UserData:
    """Create test user data"""
    return UserData(
        email=email or generate_random_email(),
        password=password,
        first_name=first_name,
        last_name=last_name
    )

def create_patient_data(
    first_name: str = "John",
    last_name: str = "Doe",
    email: str = None,
    phone: str = "+1234567890",
    date_of_birth: str = "1990-01-15"
) -> PatientData:
    """Create patient data for testing"""
    return PatientData(
        first_name=first_name,
        last_name=last_name,
        email=email or generate_random_email(),
        phone=phone,
        date_of_birth=date_of_birth
    )
```

### Common Test Patterns

#### Arrange-Act-Assert Pattern
```python
def test_user_can_edit_profile(self):
    # Arrange - Setup test data
    user_data = create_test_user()
    profile_page = ProfilePage(self.page)
    profile_page.goto_profile()

    # Act - Perform the action
    profile_page.edit_profile(user_data)
    profile_page.save_changes()

    # Assert - Verify the result
    assert profile_page.is_success_message_visible()
    assert profile_page.get_name() == user_data.first_name
```

#### Given-When-Then Pattern
```python
def test_expired_session_redirects_to_login(self):
    # Given - User has expired session
    self.page.context.add_cookies([{
        "name": "session_id",
        "value": "expired_session",
        "domain": ".meditek.app"
    }])

    # When - User tries to access dashboard
    self.page.goto("/dashboard")
    self.page.wait_for_load_state()

    # Then - User is redirected to login
    assert "/login" in self.page.url
```

---

## Configuration

### Environment Files

#### `.env.test` - Test Environment
```bash
# Test environment configuration
TEST_BASE_URL=https://test.meditek.app
TEST_API_ENDPOINT=https://api-test.meditek.app

# Test user credentials
TEST_USER_EMAIL=testuser@test.local
TEST_USER_PASSWORD=SecureTestPassword123
TEST_USER_PHONE=+1234567890

# Optional test configuration
TEST_SKIP_2FA=true
TEST_SESSION_TTL=259200  # 3 days in seconds
```

#### `.env.preprod` - Preprod Environment
```bash
# Preprod environment configuration
PREPROD_BASE_URL=https://preprod.meditek.app
PREPROD_API_ENDPOINT=https://api-preprod.meditek.app

# Preprod user credentials
PREPROD_USER_EMAIL=testuser@preprod.local
PREPROD_USER_PASSWORD=SecurePreprodPassword123
PREPROD_USER_PHONE=+1234567890

PREPROD_SKIP_2FA=true
PREPROD_SESSION_TTL=259200  # 3 days in seconds
```

#### `.env.prod` - Production Environment
```bash
# Production environment configuration
PROD_BASE_URL=https://app.meditek.com
PROD_API_ENDPOINT=https://api.meditek.com

# Production user credentials (read-only test user)
PROD_USER_EMAIL=prod_readonly_user@meditek.com
PROD_USER_PASSWORD=SecureProdPassword123

PROD_SKIP_2FA=false
PROD_SESSION_TTL=1800  # 30 minutes
```

### pytest.ini Configuration

```ini
[pytest]
# Test discovery
testpaths = refua_tests/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output
addopts =
    -v
    --strict-markers
    --tb=short
    --capture=no
    -ra

# Markers
markers =
    smoke: Quick sanity tests
    regression: Full regression suite
    authentication: Authentication tests
    patient_management: Patient management tests
    performance: Performance tests
    slow: Slow running tests
    integration: Integration tests
    ui: UI tests

# Timeout
timeout = 300
timeout_method = thread

# Logging
log_cli = true
log_cli_level = INFO
log_file = test_execution.log
log_file_level = DEBUG
```

### requirements.txt

```
# Framework dependency
refua-automation-core>=1.0.0

# Test dependencies
pytest>=7.0.0
pytest-xdist>=3.0.0
pytest-allure-adaptor>=1.0.0
pytest-timeout>=2.1.0

# Browser automation (from framework, but list for clarity)
playwright>=1.40.0
python-dotenv>=1.0.0

# Utilities
requests>=2.31.0
```

---

## Execution

### Basic Commands

```bash
# Run all tests
TEST_ENV=test pytest refua_tests/tests/ -v

# Run specific test file
TEST_ENV=test pytest refua_tests/tests/test_authentication.py -v

# Run specific test class
TEST_ENV=test pytest refua_tests/tests/test_authentication.py::TestAuthentication -v

# Run specific test method
TEST_ENV=test pytest refua_tests/tests/test_authentication.py::TestAuthentication::test_valid_login -v
```

### Filter Tests

```bash
# Run only smoke tests
TEST_ENV=test pytest refua_tests/tests/ -m smoke -v

# Run only regression tests
TEST_ENV=test pytest refua_tests/tests/ -m regression -v

# Run tests matching pattern
TEST_ENV=test pytest refua_tests/tests/ -k "login" -v

# Run tests excluding slow tests
TEST_ENV=test pytest refua_tests/tests/ -m "not slow" -v
```

### Parallel Execution

```bash
# Run with all available CPU cores
TEST_ENV=test pytest -n auto refua_tests/tests/ -v

# Run with specific number of workers
TEST_ENV=test pytest -n 4 refua_tests/tests/ -v

# Load-based distribution across workers
TEST_ENV=test pytest -n auto --dist=loadscope refua_tests/tests/ -v
```

### Device/Browser Options

```bash
# Run on iPhone
TEST_ENV=test DEVICE=iphone_15 pytest refua_tests/tests/ -v

# Run on Android
TEST_ENV=test DEVICE=android_pixel pytest refua_tests/tests/ -v

# Run with Firefox
TEST_ENV=test BROWSER=firefox pytest refua_tests/tests/ -v

# Run with Safari
TEST_ENV=test BROWSER=webkit pytest refua_tests/tests/ -v
```

### Reporting

```bash
# Generate Allure report
TEST_ENV=test pytest refua_tests/tests/ --alluredir=./allure-results -v

# View Allure report
allure serve ./allure-results

# Generate JUnit XML report
TEST_ENV=test pytest refua_tests/tests/ --junit-xml=results.xml -v

# Generate HTML report
TEST_ENV=test pytest refua_tests/tests/ --html=report.html -v
```

### Environment Execution

```bash
# Run on test environment
TEST_ENV=test pytest refua_tests/tests/ -v

# Run on preprod environment
TEST_ENV=preprod pytest refua_tests/tests/ -m "not smoke" -v

# Run on production (smoke tests only)
TEST_ENV=prod pytest refua_tests/tests/ -m smoke -v --tb=short
```

---

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/org/refuaAutomationTests.git
cd refuaAutomationTests

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install browsers for Playwright
playwright install

# Create session directory
mkdir -p ~/.refua_sessions
```

### 2. Capture Session (One-Time Setup)

```bash
# Capture session for test environment
python -m refua_core.scripts.capture_session --env test --user your_name

# When prompted:
# - Enter email and password
# - Complete 2FA manually
# - Session saved to ~/.refua_sessions/test_your_name.json
```

### 3. Write Tests

```
# Create page object: refua_tests/pages/feature_page.py
# Create test file: refua_tests/tests/test_feature.py
# Create test data: refua_tests/fixtures/test_data.py
```

### 4. Run Tests Locally

```bash
# Run your new tests
TEST_ENV=test pytest refua_tests/tests/test_feature.py -v

# Run with specific markers
TEST_ENV=test pytest refua_tests/tests/ -m smoke -v

# Run with reporting
TEST_ENV=test pytest refua_tests/tests/ --alluredir=./allure-results -v
```

### 5. Commit Changes

```bash
# Create feature branch
git checkout -b feature/test-feature-name

# Stage changes
git add refua_tests/ pytest.ini

# Commit with message
git commit -m "test: add tests for feature name"

# Push to remote
git push origin feature/test-feature-name

# Create Pull Request
```

---

## Best Practices

### Page Object Model
✅ One page object per page/screen
✅ Group related locators using @property
✅ Keep locators at top of class
✅ Use descriptive locator names
✅ Encapsulate complex interactions
❌ Avoid hard-coded waits
❌ Don't mix UI logic with assertions
❌ Avoid returning DOM elements from page objects

### Test Cases
✅ Use Arrange-Act-Assert pattern
✅ One assertion per test (or related assertions)
✅ Descriptive test names
✅ Test one feature per test
✅ Use fixtures for setup
❌ Avoid test interdependencies
❌ Don't use hardcoded wait times
❌ Avoid testing framework, test application

### Test Data
✅ Use factories to generate test data
✅ Randomize data to avoid conflicts
✅ Use meaningful field values
✅ Isolate test data per test
❌ Hardcoded test data (except for fixed scenarios)
❌ Sharing test data between tests
❌ Using production data

### Assertions
✅ Use explicit waits before assertions
✅ Provide meaningful assertion messages
✅ Assert on visible/user-facing elements
✅ Verify single concern per assertion
❌ Multiple unrelated assertions
❌ Assertions without waits
❌ Assertions on internal state

### Error Handling
✅ Use meaningful error messages
✅ Log failed test steps
✅ Capture artifacts on failure
✅ Clean up resources in tearDown
❌ Swallow exceptions
❌ Generic error messages
❌ Leave resources un-cleaned

---

## Troubleshooting

### Common Issues

#### Session Expired
```bash
# Recapture session
python -m refua_core.scripts.capture_session --env test --user your_name
```

#### Tests Timeout
```bash
# Check pytest.ini timeout setting
# Increase timeout for slow operations:
# timeout = 600  # 10 minutes
```

#### Flaky Tests
```bash
# Check for:
# 1. Missing waits (use page.wait_for_selector)
# 2. Race conditions
# 3. Unreliable locators
# 4. Network issues
```

#### Import Errors
```bash
# Verify framework is installed:
python -c "from refua_core.config.environment import EnvironmentManager; print('OK')"

# Reinstall if needed:
pip install refua-automation-core
```

---

## Next Steps

1. Create page objects for each application feature
2. Write smoke tests for critical functionality
3. Expand with regression tests
4. Integrate with CI/CD pipeline
5. Set up Allure reporting
6. Document test scenarios

---

## See Also

- Framework Documentation: See `refuaAutomationCore/ARCHITECTURE.md`
- Test Execution Guide: See `TEST_EXECUTION_QUICK_REFERENCE.md` (in core repo)
- Parameter Guide: See `PARAMETER_GUIDE.md` (in core repo)
