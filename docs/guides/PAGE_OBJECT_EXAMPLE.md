# Page Object Example: MainPage with Dynamic Environment URLs

## Overview

This example shows how to create page objects that dynamically adapt to the current environment using the `EnvironmentManager` from the framework.

---

## Updated mainPage.py

### Key Features

#### 1. **Dynamic Environment-Based URL**

The `items_base_url` property automatically gets the correct URL based on `TEST_ENV`:

```python
@property
def items_base_url(self) -> str:
    """Get base URL dynamically based on current environment"""
    current_env = self.env_manager.current_env
    env_value = current_env.value

    if current_env == EnvType.PROD:
        # Production URL (no subdomain)
        return "https://meditik.medical.idf.il/home"
    else:
        # Test and preprod have subdomains
        return f"https://meditik.{env_value}.medical.idf.il/home"
```

#### 2. **Environment-Based URL Examples**

```bash
# Test environment
TEST_ENV=test pytest refua_tests/tests/
  → uses: https://meditik.test.medical.idf.il/home

# Preprod environment
TEST_ENV=preprod pytest refua_tests/tests/
  → uses: https://meditik.preprod.medical.idf.il/home

# Production environment
TEST_ENV=prod pytest refua_tests/tests/
  → uses: https://meditik.medical.idf.il/home
```

---

## How It Works

### 1. Import EnvironmentManager

```python
from refua_core.config.environment import EnvironmentManager, EnvType
```

### 2. Initialize in Constructor

```python
def __init__(self, page: Page):
    super().__init__(page)
    self.env_manager = EnvironmentManager()
```

### 3. Use Current Environment Value

```python
@property
def items_base_url(self) -> str:
    current_env = self.env_manager.current_env
    env_value = current_env.value  # 'test', 'preprod', 'prod'
    # ... build URL based on env_value
```

---

## Usage in Tests

### Example 1: Basic Test

```python
# refua_tests/tests/test_main_page.py
import pytest
from refua_core.core.base_test import BaseTest
from refua_tests.pages.mainPage import MainPage


class TestMainPage(BaseTest):
    def test_navigate_to_main_page(self):
        """Test: Navigate to main page"""
        # Arrange
        main_page = MainPage(self.page)

        # Act
        main_page.navigate_to_items()

        # Assert
        assert main_page.is_loaded()


    def test_logo_visible_in_all_environments(self):
        """Test: Logo is visible in all environments"""
        main_page = MainPage(self.page)
        main_page.navigate_to_items()

        # This works in: test, preprod, prod
        # Each uses the correct URL for its environment
        assert main_page.logo.is_visible()
```

### Example 2: Parametrized Test for Multiple Environments

```python
# Run same test against multiple environments
TEST_ENV=test pytest refua_tests/tests/test_main_page.py::TestMainPage::test_navigate_to_main_page -v
TEST_ENV=preprod pytest refua_tests/tests/test_main_page.py::TestMainPage::test_navigate_to_main_page -v
TEST_ENV=prod pytest refua_tests/tests/test_main_page.py::TestMainPage::test_navigate_to_main_page -v
```

---

## How Environment Values Flow

```
Terminal Command:
  TEST_ENV=test pytest refua_tests/tests/
         ↓
Environment Variable Set:
  os.environ['TEST_ENV'] = 'test'
         ↓
EnvironmentManager Reads It:
  env_manager = EnvironmentManager()
  current_env = env_manager.current_env  # EnvType.TEST
         ↓
Page Object Uses It:
  env_value = current_env.value  # 'test'
  url = f"https://meditik.{env_value}.medical.idf.il/home"
  # → "https://meditik.test.medical.idf.il/home"
         ↓
Tests Navigate to Correct Environment:
  main_page.navigate_to_items()  # Uses correct URL
```

---

## Advanced Usage: Environment-Specific Locators

You can also make locators environment-specific if needed:

```python
class MainPage(BasePage):
    @property
    def search_button(self):
        """Search button (might differ by environment)"""
        current_env = self.env_manager.current_env

        if current_env == EnvType.PROD:
            # Production locator
            return self.page.locator("[data-testid='search-prod']")
        else:
            # Test/preprod locator
            return self.page.locator("[data-testid='search']")

    def search(self, query: str):
        """Perform search"""
        self.search_button.click()
        self.page.locator("[data-testid='search-input']").fill(query)
        self.page.locator("[data-testid='search-submit']").click()
```

---

## Best Practices

### ✅ DO

- ✅ Use `EnvironmentManager` to get current environment
- ✅ Build URLs dynamically in properties
- ✅ Handle environment differences in page objects
- ✅ Test against all environments
- ✅ Document environment-specific behavior

### ❌ DON'T

- ❌ Hardcode URLs like `https://meditik.test.meditik.app`
- ❌ Use string replacement with placeholders: `{.test}`
- ❌ Create separate page objects for each environment
- ❌ Hardcode environment values in page objects
- ❌ Mix environment detection with test logic

---

## Common Patterns

### Pattern 1: Environment-Based URL

```python
@property
def base_url(self) -> str:
    env = self.env_manager.current_env
    if env == EnvType.PROD:
        return "https://app.meditik.com"
    else:
        return f"https://{env.value}.meditik.app"
```

### Pattern 2: Check Current Environment

```python
def is_production(self) -> bool:
    return self.env_manager.current_env == EnvType.PROD

def wait_for_page_load(self):
    if self.is_production():
        # Slower in production
        self.page.wait_for_load_state("networkidle", timeout=60000)
    else:
        # Faster in test/preprod
        self.page.wait_for_load_state("networkidle", timeout=30000)
```

### Pattern 3: Get Environment Value as String

```python
def get_environment_label(self) -> str:
    return self.env_manager.current_env.value  # 'test', 'preprod', 'prod'

def log_test_environment(self):
    env = self.get_environment_label()
    print(f"Running tests in {env.upper()} environment")
```

---

## Testing All Environments

Run the same test against all environments:

```bash
#!/bin/bash

echo "Testing in test environment..."
TEST_ENV=test pytest refua_tests/tests/ -v --tb=short

echo "Testing in preprod environment..."
TEST_ENV=preprod pytest refua_tests/tests/ -v --tb=short

echo "Testing in production environment..."
TEST_ENV=prod pytest refua_tests/tests/ -m smoke -v --tb=short
```

Or run in parallel:

```bash
# Create separate test suites
TEST_ENV=test pytest refua_tests/tests/ &
TEST_ENV=preprod pytest refua_tests/tests/ &
TEST_ENV=prod pytest refua_tests/tests/ -m smoke &

wait
```

---

## Troubleshooting

### Issue: URL not updating with environment

**Check:**
```python
# Print the environment value
print(f"Current env: {self.env_manager.current_env.value}")
print(f"URL: {self.items_base_url}")
```

**Solution:**
1. Ensure `TEST_ENV` is set before running tests
2. Verify `.env.{env}` file exists
3. Check EnvironmentManager initialization

### Issue: EnvironmentNotSetError

**Error:**
```
EnvironmentNotSetError: TEST_ENV environment variable is required.
```

**Solution:**
```bash
# Always set TEST_ENV when running tests
TEST_ENV=test pytest refua_tests/tests/
```

---

## See Also

- **ARCHITECTURE.md** - Complete test architecture
- **CLAUDE.md** - Development guidance
- **AUTH_STATE_SETUP.md** - Environment configuration
- **refuaAutomationCore/ARCHITECTURE.md** - Framework documentation

---

**Example Complete** ✅
