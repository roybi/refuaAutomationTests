# BDD (Behavior-Driven Development) Testing

This package provides BDD/Gherkin testing capabilities using `pytest-bdd`. It complements the traditional pytest tests with human-readable feature files.

## Overview

**BDD tests run alongside traditional pytest tests** - they are an additional layer, not a replacement. Both test approaches can coexist:
- Traditional tests (`refua_tests/tests/`) - Technical, detailed testing
- BDD tests (`refua_tests/bdd/`) - Business-readable, scenario-based testing

## Structure

```
refua_tests/bdd/
├── __init__.py
├── conftest.py              # BDD-specific pytest configuration
├── features/                # Gherkin feature files
│   ├── __init__.py
│   └── main_page.feature    # Feature scenarios
└── step_defs/               # Step definitions (Python implementations)
    ├── __init__.py
    ├── common_steps.py      # Reusable steps
    └── main_page_steps.py   # Main page specific steps
```

## Feature Files

Feature files are written in Gherkin syntax and describe test scenarios in plain English.

### Example: `features/main_page.feature`

```gherkin
Feature: Main Page Functionality
  As a QA engineer
  I want to verify the Main Page works correctly
  So that users can access the application reliably

  @smoke @main_page
  Scenario: Test environment URL resolution
    Given I am testing the main page
    When I get the items base URL for "test" environment
    Then the URL should contain "meditik.test.medical.idf.il"
    And the full URL should be "https://meditik.test.medical.idf.il/home"
```

## Step Definitions

Step definitions are Python functions that implement the Gherkin steps.

### Example: `step_defs/main_page_steps.py`

```python
from pytest_bdd import given, when, then, parsers, scenarios

scenarios('../features/main_page.feature')

@given("I am testing the main page")
def testing_main_page(main_page, context):
    """Initialize main page for testing"""
    context['main_page'] = main_page

@when(parsers.parse('I get the items base URL for "{environment}" environment'))
def get_items_base_url_for_env(context, environment):
    """Get items base URL for specific environment"""
    main_page = context['main_page']
    url = main_page.items_base_url
    context['url'] = url
```

## Running BDD Tests

### Basic Execution

```bash
# Run all BDD tests
TEST_ENV=test pytest refua_tests/bdd/ -v

# Run specific feature file
TEST_ENV=test pytest refua_tests/bdd/features/main_page.feature -v

# Run specific scenario by name
TEST_ENV=test pytest refua_tests/bdd/ -k "URL resolution" -v
```

### With Markers

```bash
# Run only smoke tests
TEST_ENV=test pytest refua_tests/bdd/ -m smoke -v

# Run only regression tests
TEST_ENV=test pytest refua_tests/bdd/ -m regression -v

# Run specific tag
TEST_ENV=test pytest refua_tests/bdd/ -m main_page -v
```

### With Reporting

```bash
# Generate Allure report
TEST_ENV=test pytest refua_tests/bdd/ --alluredir=allure/results -v

# View report
python -m refua_tests.reports.serve_http
```

## Running Both Test Types

You can run traditional and BDD tests together:

```bash
# Run all tests (traditional + BDD)
TEST_ENV=test pytest refua_tests/ -v

# Run only traditional tests
TEST_ENV=test pytest refua_tests/tests/ -v

# Run only BDD tests
TEST_ENV=test pytest refua_tests/bdd/ -v
```

## Writing New BDD Tests

### 1. Create Feature File

Create a new `.feature` file in `features/` directory:

```gherkin
Feature: Login Functionality
  As a user
  I want to log in to the application
  So that I can access my account

  @smoke @authentication
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see my username displayed
```

### 2. Create Step Definitions

Create corresponding step definitions in `step_defs/`:

```python
# step_defs/login_steps.py

from pytest_bdd import given, when, then, scenarios
from refua_tests.pages.login_page import LoginPage

scenarios('../features/login.feature')

@given("I am on the login page")
def on_login_page(setup_browser):
    login_page = LoginPage(setup_browser)
    login_page.goto("/login")

@when("I enter valid credentials")
def enter_valid_credentials(login_page, context):
    login_page.login("user@test.com", "password123")
```

### 3. Run the Tests

```bash
TEST_ENV=test pytest refua_tests/bdd/features/login.feature -v
```

## BDD Best Practices

### ✅ DO

- **Write from user perspective**: "As a user, I want..."
- **Use business language**: Avoid technical jargon in feature files
- **Keep scenarios independent**: Each scenario should run standalone
- **Use Background**: For common setup steps
- **Use Scenario Outline**: For data-driven tests
- **Reuse steps**: Create common steps for frequently used actions
- **Tag scenarios**: Use `@smoke`, `@regression`, etc. for filtering

### ❌ DON'T

- **Don't write technical details in features**: Keep them business-readable
- **Don't couple scenarios**: Each should be independent
- **Don't over-complicate**: Keep scenarios simple and focused
- **Don't duplicate steps**: Reuse existing step definitions

## Gherkin Syntax

### Keywords

- **Feature**: High-level description of the functionality
- **Scenario**: Individual test case
- **Given**: Preconditions/setup
- **When**: Action being tested
- **Then**: Expected outcome
- **And/But**: Additional steps
- **Background**: Steps run before each scenario
- **Scenario Outline**: Data-driven testing with Examples

### Example with All Keywords

```gherkin
Feature: User Management

  Background:
    Given the application is running
    And I am logged in as admin

  @smoke
  Scenario: Create new user
    Given I am on the users page
    When I click "Add User" button
    And I fill in the user details
    Then a new user should be created
    And I should see a success message

  @regression
  Scenario Outline: Search users by different criteria
    Given I am on the users page
    When I search for "<search_term>"
    Then I should see "<result_count>" results

    Examples:
      | search_term | result_count |
      | john        | 5            |
      | admin       | 2            |
      | test        | 10           |
```

## Integration with Traditional Tests

BDD tests complement traditional tests:

| Aspect | Traditional Tests | BDD Tests |
|--------|------------------|-----------|
| **Audience** | Developers, QA | Business, QA, Developers |
| **Language** | Python (technical) | Gherkin (business) |
| **Detail Level** | Low-level, detailed | High-level, scenario-based |
| **Use Case** | Unit, integration testing | Acceptance, E2E testing |
| **Location** | `refua_tests/tests/` | `refua_tests/bdd/` |

### When to Use Each

**Use Traditional Tests** for:
- Low-level technical verification
- Edge cases and error conditions
- Complex setup and teardown
- Performance testing

**Use BDD Tests** for:
- User acceptance criteria
- Business scenarios
- Feature specifications
- Living documentation

## Troubleshooting

### "No steps found"

**Problem**: pytest-bdd can't find step definitions

**Solution**: Ensure `scenarios()` is called in step definition files:
```python
from pytest_bdd import scenarios
scenarios('../features/main_page.feature')
```

### "Fixture not found"

**Problem**: Missing fixture in conftest.py

**Solution**: Add fixture to `refua_tests/bdd/conftest.py`:
```python
@pytest.fixture
def setup_browser():
    # Browser setup code
    pass
```

### "Feature file not found"

**Problem**: Incorrect path to feature file

**Solution**: Use relative path from step definition file:
```python
scenarios('../features/my_feature.feature')
```

## Installation

Add pytest-bdd to your environment:

```bash
pip install pytest-bdd>=7.0.0
```

Or install from requirements.txt (already included):

```bash
pip install -r requirements.txt
```

## See Also

- **pytest-bdd Documentation**: https://pytest-bdd.readthedocs.io/
- **Gherkin Reference**: https://cucumber.io/docs/gherkin/reference/
- **Traditional Tests**: `refua_tests/tests/`
- **Architecture**: `ARCHITECTURE.md`

## Example Workflow

```bash
# 1. Write feature file
vim refua_tests/bdd/features/new_feature.feature

# 2. Write step definitions
vim refua_tests/bdd/step_defs/new_feature_steps.py

# 3. Run tests
TEST_ENV=test pytest refua_tests/bdd/features/new_feature.feature -v

# 4. Generate report
TEST_ENV=test pytest refua_tests/bdd/ --alluredir=allure/results -v
python -m refua_tests.reports.generate_report_java
```

---

**BDD tests provide living documentation that evolves with your application!** 📝✨
