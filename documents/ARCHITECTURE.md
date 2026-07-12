# refuaAutomationCore - Complete Architecture Overview

**Last Updated:** December 2025
**Project Status:** Core Framework Complete | Implementation in Progress
**Version:** 1.0.0

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Strategy](#architecture-strategy)
3. [Repository Separation](#repository-separation)
4. [Core Framework Components](#core-framework-components)
5. [Dependencies and Integration](#dependencies-and-integration)
6. [Data Flow Architecture](#data-flow-architecture)
7. [Configuration Management](#configuration-management)
8. [Test Execution Pipeline](#test-execution-pipeline)
9. [Development Workflow](#development-workflow)
10. [Deployment and Distribution](#deployment-and-distribution)

---

## Project Overview

### Vision
**refuaAutomationCore** is a production-ready, reusable test automation framework for the MEDITEK medical system. It provides complete infrastructure for building robust, scalable browser automation tests with modern DevOps practices.

### Key Principles
- **Modularity**: Separate framework from test implementation
- **Reusability**: Single framework supports multiple test suites
- **Maintainability**: Clear separation of concerns
- **Scalability**: Support for parallel execution and multiple environments
- **Security**: 2FA bypass with session management
- **Observability**: Automatic artifact capture (videos, screenshots, reports)

### Target Users
- **Framework Developers**: Maintain and enhance the core framework
- **QA Engineers**: Write and execute tests using the framework
- **Test Architects**: Design test strategies and infrastructure

---

## Architecture Strategy

### Two-Repository Model

The project follows a **two-repository architecture** to achieve clear separation between reusable infrastructure and test-specific implementation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    refuaAutomationCore                           │
│                    (Core Framework Package)                      │
│                                                                  │
│  • Configuration management (EnvironmentManager)                │
│  • Session management (SessionStateManager)                     │
│  • Base test classes (BaseTest)                                 │
│  • Device profiles (iOS, Android, Desktop)                      │
│  • Artifact management (Video, Screenshots)                     │
│  • Visual regression (Figma integration)                        │
│  • Utility scripts (Session capture)                            │
│                                                                  │
│  Published as: refua-automation-core (PyPI/Internal Registry)  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ imports
                              │
┌─────────────────────────────┴──────────────────────────────────┐
│                   refuaAutomationTests                          │
│                  (Test Implementation)                          │
│                                                                │
│  • Page objects (LoginPage, DashboardPage, etc.)             │
│  • Test cases (test_auth.py, test_smoke.py, etc.)           │
│  • Test fixtures (conftest.py)                               │
│  • Environment credentials (.env files)                      │
│  • Test configuration (pytest.ini)                           │
└────────────────────────────────────────────────────────────────┘
```

### Design Benefits

| Aspect | Benefit |
|--------|---------|
| **Versioning** | Framework and tests versioned independently |
| **Reusability** | Multiple test suites can use same framework |
| **Clarity** | Clear API contracts between layers |
| **Maintenance** | Changes to tests don't affect framework |
| **Distribution** | Framework published as standalone package |
| **Onboarding** | New test suites can reuse mature framework |

---

## Repository Separation

### refuaAutomationCore Repository (This Repository)

#### Purpose
Provide reusable test automation framework infrastructure

#### Ownership
Framework Development Team

#### Release Cycle
Semantic versioning (1.0.0, 1.1.0, 2.0.0, etc.)

#### Contains

```
refuaAutomationCore/
├── refua_core/                    # Published Python package
│   ├── __init__.py
│   ├── version.py
│   ├── config/
│   │   ├── environment.py         # EnvironmentManager singleton
│   │   ├── session_manager.py     # 2FA session handling
│   │   ├── devices.json           # Device profiles
│   │   └── __init__.py
│   ├── core/
│   │   ├── base_test.py           # Base test class
│   │   ├── device_manager.py      # Device emulation
│   │   ├── artifact_manager.py    # Video/screenshot capture
│   │   ├── visual_regression.py   # Figma integration
│   │   └── __init__.py
│   └── pages/
│       ├── base_page.py           # Base page object template
│       └── __init__.py
├── scripts/
│   ├── capture_session.py         # Interactive session capture
│   └── __init__.py
├── setup.py                       # Package configuration
├── requirements.txt               # Dependencies
├── CLAUDE.md                      # Framework documentation
├── README.md                      # Framework overview
├── PARAMETER_GUIDE.md             # Parameter documentation
└── ARCHITECTURE.md                # This file
```

#### Does NOT Contain
- ❌ Application-specific page objects
- ❌ Test cases
- ❌ Test fixtures or conftest.py
- ❌ Application credentials (.env files)
- ❌ Test-specific configuration (pytest.ini)

### refuaAutomationTests Repository (Separate)

#### Purpose
Test implementation for MEDITEK application

#### Ownership
QA/Test Team

#### Release Cycle
Project versioning (tied to application releases)

#### Contains

```
refuaAutomationTests/
├── refua_tests/
│   ├── __init__.py
│   ├── pages/                     # Application page objects
│   │   ├── login_page.py
│   │   ├── dashboard_page.py
│   │   ├── patient_page.py
│   │   ├── base_page.py           # Inherits from refua_core
│   │   └── __init__.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py            # Test fixtures
│   │   ├── test_authentication.py
│   │   ├── test_smoke.py
│   │   ├── test_regression.py
│   │   └── test_performance.py
│   └── fixtures/
│       ├── __init__.py
│       └── test_data.py
├── .env.test                      # Test credentials
├── .env.preprod                   # Preprod credentials
├── .env.prod                      # Production credentials
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Dependencies (includes refua-automation-core)
├── setup.py (optional)
├── CLAUDE.md                      # Test-specific guidance
└── README.md                      # Test guide
```

#### Dependencies
```text
refuaAutomationTests
  └── refua-automation-core (>=1.0.0)
      ├── playwright
      ├── python-dotenv
      └── requests
```

---

## Core Framework Components

### 1. Configuration Management (`refua_core/config/`)

#### `environment.py` - EnvironmentManager

**Purpose**: Centralized environment configuration singleton

**Responsibility**:
- Manage multi-environment configuration (test, preprod, prod)
- Load credentials from .env files
- Provide base URLs and API endpoints
- Handle environment validation

**Key Classes**:
```python
class EnvironmentManager:
    # Singleton pattern
    get_instance() -> EnvironmentManager

    # Configuration access
    get_base_url() -> str
    get_api_endpoint(endpoint: str) -> str
    get_credential(key: str) -> str

    # Environment info
    get_environment() -> EnvType
    get_browser_type() -> BrowserType
```

**Environment Types**:
- `test`: Local development (3-day session TTL)
- `preprod`: Integration testing (3-day session TTL)
- `prod`: Production validation (30-min session TTL)

**Configuration Flow**:
```
Environment Variables (TEST_ENV, BROWSER, DEVICE, etc.)
         ↓
EnvironmentManager.get_instance()
         ↓
Load .env.<env> file from test repository
         ↓
Return configuration for framework and tests
```

#### `session_manager.py` - SessionStateManager

**Purpose**: Manage 2FA authentication bypass through session reuse

**Responsibility**:
- Validate session files (cookies, localStorage)
- Check session state before test execution
- Enforce session TTL (time-to-live)
- Store sessions externally for reuse

**Key Classes**:
```python
class SessionStateManager:
    # Session validation
    is_session_valid(session_path: str) -> bool
    validate_session_state() -> bool

    # Session lifecycle
    load_session(session_file: Path) -> dict
    save_session(session_data: dict, session_file: Path) -> None

    # TTL management
    get_session_ttl() -> timedelta
    is_session_expired() -> bool
```

**Session Storage**:
- Location: `~/.refua_sessions/` (configurable via SESSION_DIR)
- Format: JSON files containing cookies and localStorage
- Naming: `<environment>_<username>.json`

**Session Workflow**:
```
1. Capture Phase (Manual - runs once)
   User runs: python scripts/capture_session.py --env test --user john.doe
   → Opens browser with manual 2FA
   → Completes authentication
   → Saves session to ~/.refua_sessions/test_john_doe.json

2. Reuse Phase (Automated - runs many times)
   Tests run with SKIP_2FA=true
   → SessionStateManager loads session from ~/.refua_sessions/
   → Injects cookies and localStorage into browser context
   → Tests run without manual 2FA

3. Expiration Phase (Refresh needed)
   Session older than TTL (3 days)
   → SessionStateManager detects expiration
   → Framework prompts for new session capture
```

#### `devices.json` - Device Profiles

**Purpose**: Pre-configured device profiles for mobile emulation

**Profiles Included**:
- **Desktop**: Standard desktop browser
- **iPhone 12, 13, 14, 15**: iOS emulation
- **Pixel, Galaxy**: Android emulation

**Device Properties**:
```json
{
  "iphone_15": {
    "viewport": { "width": 393, "height": 852 },
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)...",
    "device_scale_factor": 3,
    "has_touch": true,
    "is_mobile": true,
    "locale": "en-US"
  }
}
```

### 2. Core Infrastructure (`refua_core/core/`)

#### `base_test.py` - BaseTest

**Purpose**: Foundation for all test classes

**Responsibility**:
- Browser context lifecycle management
- Session validation on test start
- Page object initialization
- Video and screenshot capture
- Test artifact management

**Key Features**:
```python
class BaseTest(unittest.TestCase):
    # Browser setup
    browser: Browser
    context: BrowserContext
    page: Page

    # Hooks
    def setUp(self) -> None  # Runs before each test
    def tearDown(self) -> None  # Runs after each test

    # Utilities
    def capture_screenshot(self, name: str) -> None
    def take_video(self, name: str) -> None
```

**Initialization Flow**:
```
Test starts
    ↓
setUp() called
    ↓
Validate session (if 2FA enabled)
    ↓
Launch browser with device profile
    ↓
Create browser context
    ↓
Enable video recording (if enabled)
    ↓
Create page object
    ↓
Test runs
    ↓
tearDown() called
    ↓
Capture artifacts (if test failed)
    ↓
Clean up browser resources
```

#### `device_manager.py` - DeviceManager

**Purpose**: Mobile device emulation configuration

**Responsibility**:
- Load device profiles from devices.json
- Apply device settings to browser context
- Handle device-specific configurations

**Key Methods**:
```python
class DeviceManager:
    load_device_profile(device_name: str) -> dict
    apply_device_config(context: BrowserContext, device: str) -> None
    get_viewport(device: str) -> dict
    get_user_agent(device: str) -> str
```

**Supported Devices**:
```bash
# Via DEVICE environment variable:
desktop        # Default
iphone_12
iphone_13
iphone_14
iphone_15
pixel_5
galaxy_s21
```

#### `artifact_manager.py` - ArtifactManager

**Purpose**: Manage test artifacts (videos, screenshots)

**Responsibility**:
- Configure video recording
- Capture screenshots
- Manage artifact storage
- Conditional retention (delete on pass, keep on fail)

**Behavior**:
```
Test Passes:
  └─ Artifacts deleted (saves storage)

Test Fails:
  ├─ Videos retained: ./test-artifacts/<test_name>.webm
  ├─ Screenshots retained: ./test-artifacts/<test_name>_*.png
  └─ Debug information preserved
```

#### `visual_regression.py` - VisualRegression

**Purpose**: Visual regression testing with Figma

**Responsibility**:
- Compare current screenshots with design frames
- Generate visual diff reports
- Support Figma integration for design comparison

**Key Methods**:
```python
class VisualRegression:
    compare_screenshot(
        screenshot_path: str,
        figma_frame_id: str
    ) -> ComparisonResult

    generate_diff_report(
        expected: str,
        actual: str,
        output_path: str
    ) -> None
```

### 3. Page Objects (`refua_core/pages/`)

#### `base_page.py` - BasePage

**Purpose**: Base class template for application page objects

**Responsibility**:
- Provide common navigation methods
- Handle environment-aware URL construction
- Offer element interaction patterns

**Template Methods**:
```python
class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, path: str) -> None:
        """Navigate to path on current environment"""

    def wait_for_url(self, path: str, timeout: int = 30000) -> None:
        """Wait for URL navigation"""
```

**Inheritance Pattern** (in test repository):
```python
# base_page.py in test repo
from refua_core.pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.locator("[data-testid='email']")
        self.login_button = page.locator("[data-testid='login']")

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.login_button.click()
```

### 4. Utilities (`scripts/`)

#### `capture_session.py`

**Purpose**: Interactive 2FA session capture tool

**Responsibility**:
- Provide interactive browser for manual 2FA completion
- Support multiple browser engines
- Save session cookies and localStorage

**Usage**:
```bash
# Capture session for test environment
python scripts/capture_session.py --env test --user john.doe

# Capture for preprod with Safari
python scripts/capture_session.py --env preprod --user jane.smith --browser safari

# Use specific browser
python scripts/capture_session.py --env prod --user admin --browser firefox
```

**Supported Browsers**:
- chromium (default)
- firefox
- webkit
- safari

**Output**:
```
Saved session to: ~/.refua_sessions/test_john_doe.json
Session contains:
  - Cookies
  - LocalStorage
  - SessionStorage
  - Timestamp (for TTL calculation)
```

---

## Dependencies and Integration

### Package Dependencies

#### Core Dependencies
```
playwright>=1.40.0          # Browser automation
python-dotenv>=1.0.0        # .env file loading
requests>=2.31.0            # HTTP requests (Figma API)
pytest>=7.0.0               # Test framework
```

#### Optional Dependencies
```
# For visual regression
pillow>=9.0.0               # Image processing (Figma integration)

# For parallel execution
pytest-xdist>=3.0.0         # Parallel test execution
pytest-allure-adaptor>=1.0.0 # Allure reporting

# Development tools
black>=23.0.0               # Code formatter
flake8>=6.0.0               # Linter
mypy>=1.0.0                 # Type checker
isort>=5.12.0               # Import sorter
```

### Integration Points

#### Test Repository Import Pattern
```python
# In refuaAutomationTests/refua_tests/pages/login_page.py
from refua_core.core.base_test import BaseTest
from refua_core.pages.base_page import BasePage
from refua_core.config.environment import EnvironmentManager
from playwright.sync_api import Page

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.env_mgr = EnvironmentManager.get_instance()
        # ... page object implementation
```

#### Environment Variable Flow
```
Test Repository:
  .env.test
  .env.preprod
  .env.prod

Framework:
  EnvironmentManager
  (loads .env.<TEST_ENV>)

Environment Variables:
  TEST_ENV=test (required)
  SKIP_2FA=true (optional)
  DEVICE=iphone (optional)
  BROWSER=chromium (optional)
```

---

## Data Flow Architecture

### Test Execution Flow

```
1. CONFIGURATION PHASE
   ├─ Read TEST_ENV from environment
   ├─ Load .env.<TEST_ENV> file
   ├─ Parse device profile (DEVICE)
   ├─ Select browser (BROWSER)
   └─ Validate session (if SKIP_2FA=true)

2. SETUP PHASE
   ├─ Launch browser instance
   ├─ Create browser context with device settings
   ├─ Load session cookies/localStorage (if available)
   ├─ Apply recording settings (video, screenshots)
   └─ Initialize page object

3. TEST EXECUTION PHASE
   ├─ Test code runs
   ├─ Page objects interact with application
   ├─ Video/screenshots captured automatically
   └─ Assertions validated

4. ARTIFACT MANAGEMENT PHASE
   ├─ If test passes:
   │  └─ Delete video and screenshots (cleanup)
   └─ If test fails:
      ├─ Retain video and screenshots
      └─ Generate debug artifacts

5. CLEANUP PHASE
   ├─ Close browser context
   ├─ Close browser instance
   └─ Save test report
```

### Session Flow (2FA Bypass)

```
CAPTURE PHASE (Once per user/environment):
  User: python scripts/capture_session.py --env test --user john.doe
  ↓
  Opens browser → User completes 2FA manually
  ↓
  Extracts cookies and localStorage
  ↓
  Saves to ~/.refua_sessions/test_john_doe.json
  ↓
  Session TTL set (3 days for test/preprod)

REUSE PHASE (Every test execution):
  TEST_ENV=test SKIP_2FA=true pytest tests/
  ↓
  SessionStateManager checks TTL
  ↓
  If valid: Load session from ~/.refua_sessions/
  ↓
  Inject cookies/localStorage into browser context
  ↓
  Tests run without 2FA
  ↓
  If invalid: Prompt user to re-capture session
```

---

## Configuration Management

### Environment Variables

#### Required
```bash
TEST_ENV=test|preprod|prod    # Target environment (required)
```

#### Optional
```bash
SKIP_2FA=true|false            # Use session bypass (default: true for test/preprod)
DEVICE=desktop|iphone|android  # Device profile (default: desktop)
BROWSER=chromium|firefox|webkit|safari  # Browser (default: chromium)
RECORD_VIDEO=true|false        # Capture video (default: true)
CAPTURE_SCREENSHOTS=true|false # Capture screenshots (default: true)
SESSION_DIR=path/to/sessions   # Session storage (default: ~/.refua_sessions/)
```

### .env Files (Test Repository)

```bash
# .env.test
TEST_USER_EMAIL=user@test.local
TEST_USER_PASSWORD=secure_password
TEST_USER_PHONE=+1234567890
TEST_BASE_URL=https://test.meditek.app

# .env.preprod
PREPROD_USER_EMAIL=user@preprod.local
PREPROD_USER_PASSWORD=secure_password
PREPROD_BASE_URL=https://preprod.meditek.app

# .env.prod
PROD_USER_EMAIL=user@production.com
PROD_USER_PASSWORD=secure_password
PROD_BASE_URL=https://app.meditek.com
```

### Devices Configuration (devices.json)

```json
{
  "desktop": {
    "viewport": { "width": 1280, "height": 720 },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "device_scale_factor": 1,
    "has_touch": false,
    "is_mobile": false
  },
  "iphone_15": {
    "viewport": { "width": 393, "height": 852 },
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)...",
    "device_scale_factor": 3,
    "has_touch": true,
    "is_mobile": true
  },
  "android_pixel": {
    "viewport": { "width": 412, "height": 915 },
    "user_agent": "Mozilla/5.0 (Linux; Android 13)...",
    "device_scale_factor": 2.75,
    "has_touch": true,
    "is_mobile": true
  }
}
```

---

## Test Execution Pipeline

### Command Examples

#### Basic Execution
```bash
# Run all tests on test environment
TEST_ENV=test pytest tests/

# Run specific test file
TEST_ENV=test pytest tests/test_authentication.py

# Run tests matching pattern
TEST_ENV=test pytest tests/ -k "login"
```

#### With Options
```bash
# Verbose output
TEST_ENV=test pytest tests/ -v

# Stop on first failure
TEST_ENV=test pytest tests/ -x

# Show print statements
TEST_ENV=test pytest tests/ -s

# Short traceback
TEST_ENV=test pytest tests/ --tb=short
```

#### With Device Options
```bash
# Run on iPhone
TEST_ENV=test DEVICE=iphone_15 pytest tests/

# Run on Android
TEST_ENV=test DEVICE=android_pixel pytest tests/

# Run on specific Safari
TEST_ENV=test BROWSER=webkit pytest tests/
```

#### Parallel Execution
```bash
# Run with all CPU cores
TEST_ENV=test pytest -n auto tests/

# Run with 4 workers
TEST_ENV=test pytest -n 4 tests/

# Load-based distribution
TEST_ENV=test pytest -n auto --dist=loadscope tests/
```

#### Reporting
```bash
# Generate Allure report
TEST_ENV=test pytest --alluredir=./allure/results tests/

# View Allure report
allure serve ./allure/results

# Generate JUnit XML
TEST_ENV=test pytest --junit-xml=results.xml tests/

# Generate HTML report
TEST_ENV=test pytest --html=report.html tests/
```

#### Production Validation
```bash
# Production with short session TTL (30 min)
TEST_ENV=prod SKIP_2FA=false pytest tests/ --tb=short

# Production without 2FA bypass
TEST_ENV=prod pytest tests/ -m "smoke"
```

---

## Development Workflow

### Framework Developer Workflow

#### 1. Setup Development Environment
```bash
# Clone repository
git clone https://github.com/org/refuaAutomationCore.git
cd refuaAutomationCore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

#### 2. Create Feature Branch
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes to refua_core/
# Update tests
# Update documentation
```

#### 3. Test Changes
```bash
# Run framework tests
pytest tests/ -v

# Check code style
black refua_core/
flake8 refua_core/

# Type checking
mypy refua_core/

# Import sorting
isort refua_core/
```

#### 4. Commit and Push
```bash
# Stage changes
git add refua_core/ tests/ CLAUDE.md

# Commit with conventional message
git commit -m "feat: add new feature to framework"

# Push feature branch
git push origin feature/new-feature
```

#### 5. Version Update
```bash
# Update version in setup.py
# From: version="1.0.0"
# To: version="1.1.0"

# Tag release
git tag v1.1.0

# Push tag
git push origin v1.1.0
```

### Test Author Workflow

#### 1. Setup Test Repository
```bash
# Clone test repository
git clone https://github.com/org/refuaAutomationTests.git
cd refuaAutomationTests

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create session directory
mkdir -p ~/.refua_sessions
```

#### 2. Capture Session (One-time)
```bash
# Capture session for test environment
python -m refua_core.scripts.capture_session --env test --user john.doe

# Enter credentials when prompted
# Complete 2FA manually
# Session saved to ~/.refua_sessions/test_john_doe.json
```

#### 3. Write Tests
```bash
# Create page object
# refua_tests/pages/login_page.py
from refua_core.pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.email = page.locator("[data-testid='email']")

    def login(self, email, password):
        self.email.fill(email)

# Create test
# refua_tests/tests/test_auth.py
from refua_core.core.base_test import BaseTest
from refua_tests.pages.login_page import LoginPage

class TestAuthentication(BaseTest):
    def test_login(self):
        login_page = LoginPage(self.page)
        login_page.goto("/login")
        login_page.login("user@test.com", "password")
        login_page.wait_for_url("/dashboard")
```

#### 4. Execute Tests
```bash
# Run tests
TEST_ENV=test pytest refua_tests/tests/ -v

# Run with reporting
TEST_ENV=test pytest refua_tests/tests/ --alluredir=./allure/results -v

# View results
allure serve ./allure/results
```

### Release Workflow

#### 1. Prepare Release
```bash
# Create release branch
git checkout -b release/v1.1.0

# Update version in setup.py
# Update CHANGELOG.md
# Commit changes
git commit -m "chore: prepare v1.1.0 release"

# Push to release branch
git push origin release/v1.1.0
```

#### 2. Build Package
```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Verify build
ls dist/
# refua-automation-core-1.1.0.tar.gz
# refua-automation-core-1.1.0-py3-none-any.whl
```

#### 3. Publish Package

#### Option A: PyPI (Public)
```bash
# Publish to PyPI
python -m twine upload dist/*

# Verify installation
pip install refua-automation-core==1.1.0
```

#### Option B: Internal Registry
```bash
# Publish to internal registry
python -m twine upload -r internal dist/*

# Verify installation
pip install refua-automation-core==1.1.0 -i https://internal-registry.company.com
```

#### 4. Tag Release
```bash
# Create git tag
git tag v1.1.0

# Push tag
git push origin v1.1.0

# Create GitHub release
gh release create v1.1.0 --title "Release v1.1.0" --notes "Release notes here"
```

#### 5. Update Test Repository
```bash
# In refuaAutomationTests/requirements.txt
# Update from: refua-automation-core>=1.0.0
# Update to: refua-automation-core>=1.1.0

# Test import
pip install -r requirements.txt
python -c "from refua_core.config.environment import EnvironmentManager; print('OK')"
```

---

## Deployment and Distribution

### Installation Methods

#### 1. PyPI Installation (Recommended)
```bash
# Latest version
pip install refua-automation-core

# Specific version
pip install refua-automation-core==1.0.0

# Version range
pip install "refua-automation-core>=1.0.0,<2.0.0"
```

#### 2. Git Installation (Development)
```bash
# Latest from main branch
pip install git+https://github.com/org/refuaAutomationCore.git@main

# Specific tag
pip install git+https://github.com/org/refuaAutomationCore.git@v1.0.0

# With editable flag
pip install -e git+https://github.com/org/refuaAutomationCore.git@main#egg=refua-automation-core
```

#### 3. Local Editable Installation (Local Development)
```bash
# In test repository, if framework is local
pip install -e ../refuaAutomationCore

# Or in requirements.txt
refua-automation-core @ file://../refuaAutomationCore
```

#### 4. Internal Registry Installation
```bash
# From internal package registry
pip install -i https://internal-registry.company.com refua-automation-core

# With authentication
pip install -i https://user:password@internal-registry.company.com refua-automation-core
```

### CI/CD Integration

#### GitHub Actions Example
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          playwright install

      - name: Run tests
        run: TEST_ENV=test pytest tests/ -v

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-artifacts
          path: test-artifacts/
```

#### Test Repository CI/CD Example
```yaml
# .github/workflows/test.yml (in refuaAutomationTests)
name: Test Execution

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install

      - name: Create session directory
        run: mkdir -p ~/.refua_sessions

      - name: Load session
        run: |
          echo "${{ secrets.TEST_SESSION }}" > ~/.refua_sessions/test_ci.json

      - name: Run tests
        run: |
          TEST_ENV=test pytest refua_tests/tests/ -v --alluredir=./allure/results

      - name: Upload Allure report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: allure/results
          path: allure/results/
```

### Version Management

#### Semantic Versioning
```
Version: MAJOR.MINOR.PATCH

1.0.0 - Initial release
1.1.0 - New feature (backward compatible)
1.1.1 - Bug fix (backward compatible)
1.2.0 - Another feature
2.0.0 - Breaking change (new major version)
```

#### Backward Compatibility Policy
```
Breaking Changes (Major Version Bump):
  ❌ Change EnvironmentManager API
  ❌ Change BaseTest class signature
  ❌ Change device.json format
  ❌ Change session file format

Safe Changes (Minor Version Bump):
  ✅ Add new methods to existing classes
  ✅ Add optional parameters
  ✅ Fix bugs
  ✅ Improve performance
  ✅ Add documentation
```

---

## Architecture Diagram

### High-Level Component Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                         Test Repository                          │
│                     (refuaAutomationTests)                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ LoginPage    │  │ DashboardPage│  │ PatientPage  │          │
│  │ (inherits)   │  │ (inherits)   │  │ (inherits)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                           │                                      │
│                  ┌────────▼────────┐                            │
│                  │  TestCase Classes│                            │
│                  │ (test_*.py files)│                            │
│                  └────────┬────────┘                            │
│                           │                                      │
│                imports from refua_core                          │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            │ pip install refua-automation-core
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                   Framework Repository                           │
│               (refuaAutomationCore - This Repo)                  │
│                                                                  │
│  ┌───────────────┐  ┌─────────────┐  ┌──────────────┐          │
│  │    Config     │  │    Core     │  │   Pages      │          │
│  │               │  │             │  │              │          │
│  │ • EnvironmentM│  │ • BaseTest  │  │ • BasePage   │          │
│  │ • SessionMgr  │  │ • DeviceMgr │  │              │          │
│  │ • devices.json│  │ • ArtifactMg│  │              │          │
│  │               │  │ • VisReg    │  │              │          │
│  └───────────────┘  └─────────────┘  └──────────────┘          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │               External Scripts                          │    │
│  │        (capture_session.py)                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            Package Distribution                        │    │
│  │     (setup.py) → PyPI / Internal Registry              │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                            ▲
                            │
                    External Dependencies:
                    • playwright
                    • python-dotenv
                    • requests
```

### Test Execution Flow Diagram
```
┌─────────────────────┐
│  Test Execution     │
│  TEST_ENV=test      │
│  DEVICE=iphone      │
│  pytest             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 1. Configuration Phase              │
├─────────────────────────────────────┤
│ • Read environment variables        │
│ • Load .env.test                    │
│ • Parse device profile              │
│ • Validate session TTL              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 2. Setup Phase                      │
├─────────────────────────────────────┤
│ • Launch browser                    │
│ • Create context with device config │
│ • Load session (cookies, storage)   │
│ • Enable recording (video/screens)  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 3. Test Execution Phase             │
├─────────────────────────────────────┤
│ • Page object interactions          │
│ • User actions                      │
│ • Assertions                        │
│ • Auto screenshot capture           │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 4. Artifact Management Phase        │
├─────────────────────────────────────┤
│ • If PASS:                          │
│   └─ Delete video/screenshots       │
│ • If FAIL:                          │
│   └─ Retain artifacts for debugging │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 5. Cleanup Phase                    │
├─────────────────────────────────────┤
│ • Close context                     │
│ • Close browser                     │
│ • Generate report (Allure)          │
│ • Return exit code                  │
└─────────────────────────────────────┘
```

---

## Summary

### Architecture Highlights
- **Two-Repository Model**: Clear separation between framework and tests
- **Reusable Framework**: Published as PyPI package for distribution
- **Multi-Environment**: Support for test, preprod, and production
- **2FA Bypass**: Secure session management for authentication
- **Mobile Testing**: Built-in device profiles for iOS and Android
- **Scalability**: Support for parallel test execution
- **Observability**: Automatic artifact capture and Allure reporting

### Key Strengths
✅ Modularity and reusability
✅ Clear API contracts
✅ Professional artifact management
✅ Enterprise-grade reporting
✅ Flexible deployment options
✅ Easy team onboarding

### Next Steps
1. Review the separation plan (REPOSITORY_SEPARATION_PLAN.md)
2. Complete code cleanup in refuaAutomationCore
3. Create refuaAutomationTests repository
4. Test framework installation and test imports
5. Release v1.0.0 of framework
6. Document for team

---

**For detailed component documentation, see:**
- `CLAUDE.md` - Framework component guide
- `README.md` - Framework overview
- `PARAMETER_GUIDE.md` - Environment parameters
- `REPOSITORY_SEPARATION_PLAN.md` - Migration strategy
- `SEPARATION_SUMMARY.md` - Status overview
