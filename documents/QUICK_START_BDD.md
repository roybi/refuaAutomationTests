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
TEST_ENV=test pytest refua_tests/bdd/ -v

# Run specific feature
TEST_ENV=test pytest refua_tests/bdd/features/main_page.feature -v

# Run with smoke marker
TEST_ENV=test pytest refua_tests/bdd/ -m smoke -v

# Run with regression marker
TEST_ENV=test pytest refua_tests/bdd/ -m regression -v
```

### With Reporting

```bash
# Generate Allure report
TEST_ENV=test pytest refua_tests/bdd/ --alluredir=allure/results -v
python -m refua_tests.reports.generate_report_java
python -m refua_tests.reports.serve_http
```

## Run Both Test Types

```bash
# Run traditional + BDD tests together
TEST_ENV=test pytest refua_tests/ -v

# Traditional only
TEST_ENV=test pytest refua_tests/tests/ -v

# BDD only
TEST_ENV=test pytest refua_tests/bdd/ -v
```

## Example: Current BDD Tests

We have **15 Gherkin scenarios** covering Main Page functionality:

### Smoke Tests (@smoke)
1. Test environment URL resolution
2. Preprod environment URL resolution
3. Main page inherits from base page
4. Main page has environment manager
5. Get current environment returns valid string
6. Items base URL is a property
7. Logo locator exists
8. Main menu locator exists
9. Items list locator exists
10. Navigate to items method exists
11. Is loaded method exists

### Regression Tests (@regression)
12. URL contains correct domain for each environment (data-driven)
13. All URLs use HTTPS protocol
14. URL ends with home path

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
