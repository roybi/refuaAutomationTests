# Quick Start - BDD Testing

## Installation

```bash
# Install dependencies (includes pytest-bdd)
pip install -r requirements.txt
```

## Run BDD Tests

### Basic Commands

```bash
# Run all BDD tests
TEST_ENV=test python -m pytest refua_tests/bdd/test_meditik_bdd.py -v

# Run Meditik scenarios only
TEST_ENV=test python -m pytest refua_tests/bdd/ -m meditik -v

# Run one Meditik area
TEST_ENV=test python -m pytest refua_tests/bdd/ -m "meditik and request_forms" -v

# Exclude known product issues
TEST_ENV=test python -m pytest refua_tests/bdd/ -m "meditik and not known_issue" -v
```

Tags are application-aware: `@meditik` selects Meditik scenarios, while
`@cprgo` is reserved for future CPRGO scenarios. Area tags include `@home`,
`@menu`, and `@request_forms`.

### With Reporting

```bash
# Generate Allure report
TEST_ENV=test python -m pytest refua_tests/bdd/ -m meditik --alluredir=allure/results -v
python -m refua_tests.reports.generate_report_java
python -m refua_tests.reports.serve_http
```

Every executed Given/When/Then step is attached to the scenario's Allure result
as `BDD scenario action`, including the action status. This lets a report reader
see which Gherkin actions completed before a failure.

## Run Both Test Types

```bash
# Run traditional + BDD tests together
TEST_ENV=test python -m pytest refua_tests/ -v

# Traditional only
TEST_ENV=test python -m pytest refua_tests/tests/ -v

# BDD only
TEST_ENV=test python -m pytest refua_tests/bdd/ -v
```

## Current Meditik BDD Coverage

`test_meditik_bdd.py` loads **69 scenarios**, matching the Home, side-menu, and
request-form pytest coverage. The feature files are:

- `meditik_home.feature`
- `meditik_menu.feature`
- `meditik_request_forms.feature`

New pytest UI coverage must include a matching executable BDD scenario and
step definition. Keep application-specific steps separate so future CPRGO
features can use `@cprgo` and their own adapter without Meditik coupling.

## Creating New BDD Tests

### 1. Create Feature File

`refua_tests/bdd/features/login.feature`:

```gherkin
Feature: User Login
  As a user
  I want to log in to the system
  So that I can access my account

  @smoke @authentication
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter email "user@test.com" and password "password123"
    And I click the login button
    Then I should be redirected to "/dashboard"
    And I should see my username displayed
```

### 2. Create Step Definitions

`refua_tests/bdd/step_defs/login_steps.py`:

```python
from pytest_bdd import given, when, then, parsers, scenarios
from refua_tests.pages.login_page import LoginPage

# Load scenarios
scenarios('../features/login.feature')

@given("I am on the login page")
def on_login_page(setup_browser):
    login_page = LoginPage(setup_browser)
    login_page.goto("/login")

@when(parsers.parse('I enter email "{email}" and password "{password}"'))
def enter_credentials(context, email, password):
    # Implementation
    pass
```

### 3. Run Tests

```bash
TEST_ENV=test pytest refua_tests/bdd/features/login.feature -v
```

## Documentation

- **Full BDD Guide**: `refua_tests/bdd/README.md`
- **Architecture**: `ARCHITECTURE.md` (see BDD Testing section)
- **Summary**: `documents/BDD_IMPLEMENTATION_SUMMARY.md`

## See Also

- Traditional tests: `refua_tests/tests/`
- Reports: `refua_tests/reports/README.md`
- pytest-bdd docs: https://pytest-bdd.readthedocs.io/
