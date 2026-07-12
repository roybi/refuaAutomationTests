# Authentication State Setup Guide

**Comprehensive Guide for 2FA Authentication Bypass using JSON State Files**

---

## Overview

This guide explains how to configure and use authentication state JSON files for 2FA bypass across different environments (test, preprod, production) and deployment scenarios (local development, Docker, CI/CD).

## Quick Setup

### 1. Place Your Auth State Files

Organize your authentication state files in the following structure:

```
C:\_Dev\python\skipp_2FA_auth\
└── auth_states\
    ├── auth_state_test_chromium_latest.json
    ├── auth_state_test_firefox_latest.json
    ├── auth_state_test_webkit_latest.json
    ├── auth_state_preprod_chromium_latest.json
    ├── auth_state_preprod_firefox_latest.json
    ├── auth_state_preprod_webkit_latest.json
    ├── auth_state_prod_chromium_latest.json
    ├── auth_state_prod_firefox_latest.json
    └── auth_state_prod_webkit_latest.json
```

### 2. Configure Environment Variables

Update your `.env.*` files with the auth state file paths:

**`.env.test`:**
```bash
TEST_AUTH_STATE_FILE=C:\_Dev\python\skipp_2FA_auth\auth_states\auth_state_test_chromium_latest.json
```

**`.env.preprod`:**
```bash
PREPROD_AUTH_STATE_FILE=C:\_Dev\python\skipp_2FA_auth\auth_states\auth_state_preprod_chromium_latest.json
```

**`.env.prod`:**
```bash
PROD_AUTH_STATE_FILE=C:\_Dev\python\skipp_2FA_auth\auth_states\auth_state_prod_chromium_latest.json
```

### 3. Run Tests

Tests will automatically use the configured auth state files:

```bash
# Test environment
TEST_ENV=test pytest refua_tests/tests/ -v

# Preprod environment
TEST_ENV=preprod pytest refua_tests/tests/ -v

# Production environment (read-only)
TEST_ENV=prod pytest refua_tests/tests/ -m smoke -v
```

---

## Environment Variable Configuration

### Priority Order

The framework resolves auth state files using this priority:

1. **{ENV}_AUTH_STATE_FILE** - Specific auth state file for environment
   ```bash
   TEST_AUTH_STATE_FILE=/path/to/auth_state_test_chromium.json
   ```

2. **{ENV}_AUTH_STATE_{BROWSER}** - Browser-specific auth state file
   ```bash
   TEST_AUTH_STATE_CHROMIUM=/path/to/auth_state_test_chromium.json
   TEST_AUTH_STATE_FIREFOX=/path/to/auth_state_test_firefox.json
   ```

3. **Default** - Uses session directory (fallback)
   ```bash
   # ~/.refua_sessions/auth_state_test_chromium_latest.json
   ```

### Variable Naming Convention

For each environment, use these variable names:

| Environment | Variable | Example |
|-------------|----------|---------|
| **test** | `TEST_AUTH_STATE_FILE` | `TEST_AUTH_STATE_FILE=C:\auth_states\auth_state_test_chromium.json` |
| **preprod** | `PREPROD_AUTH_STATE_FILE` | `PREPROD_AUTH_STATE_FILE=C:\auth_states\auth_state_preprod_chromium.json` |
| **prod** | `PROD_AUTH_STATE_FILE` | `PROD_AUTH_STATE_FILE=C:\auth_states\auth_state_prod_chromium.json` |

### Path Expansion

The framework supports path expansion features:

#### Home Directory Expansion
```bash
# Expands ~ to user's home directory
TEST_AUTH_STATE_FILE=~/auth_states/auth_state_test_chromium_latest.json
```

#### Environment Variable Substitution
```bash
# Uses environment variable substitution
TEST_AUTH_STATE_FILE=${AUTH_STATES_DIR}/auth_state_test_chromium_latest.json
TEST_AUTH_STATE_FILE=$AUTH_STATES_DIR/auth_state_test_chromium_latest.json
```

#### Absolute Paths
```bash
# Windows
TEST_AUTH_STATE_FILE=C:\_Dev\python\skipp_2FA_auth\auth_states\auth_state_test_chromium_latest.json

# Linux/Mac
TEST_AUTH_STATE_FILE=/opt/auth_states/auth_state_test_chromium_latest.json
```

---

## Docker Setup

### Using Environment Variables in Docker

For Docker deployments, use environment variable substitution:

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  test-runner:
    image: test-automation:latest
    environment:
      TEST_ENV: test
      AUTH_STATES_DIR: /app/auth_states
      TEST_AUTH_STATE_FILE: ${AUTH_STATES_DIR}/auth_state_test_chromium_latest.json
      PREPROD_AUTH_STATE_FILE: ${AUTH_STATES_DIR}/auth_state_preprod_chromium_latest.json
      PROD_AUTH_STATE_FILE: ${AUTH_STATES_DIR}/auth_state_prod_chromium_latest.json
    volumes:
      - ./auth_states:/app/auth_states:ro
      - ./tests:/app/tests
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy test code
COPY refua_tests/ refua_tests/
COPY pytest.ini .
COPY .env.test .

# Default environment
ENV TEST_ENV=test
ENV AUTH_STATES_DIR=/app/auth_states

# Run tests
CMD ["pytest", "refua_tests/tests/", "-v", "--tb=short"]
```

### Docker Path Examples

In Docker containers, use `/app/` or `/workspace/` paths:

**docker-compose.yml (alternative):**
```yaml
services:
  test-runner:
    image: test-automation:latest
    environment:
      TEST_ENV: test
      TEST_AUTH_STATE_FILE: /app/auth_states/auth_state_test_chromium_latest.json
      PREPROD_AUTH_STATE_FILE: /app/auth_states/auth_state_preprod_chromium_latest.json
      PROD_AUTH_STATE_FILE: /app/auth_states/auth_state_prod_chromium_latest.json
    volumes:
      - ./auth_states:/app/auth_states:ro
```

---

## Local Development Setup

### Windows Development

**Create `.env.local.test` for local overrides:**
```bash
# Local auth states (Windows path)
TEST_AUTH_STATE_FILE=C:\_Dev\python\skipp_2FA_auth\auth_states\auth_state_test_chromium_latest.json

# Or use home directory expansion
# TEST_AUTH_STATE_FILE=~/skipp_2FA_auth/auth_states/auth_state_test_chromium_latest.json
```

**Run tests:**
```bash
TEST_ENV=test pytest refua_tests/tests/ -v
```

### Linux/Mac Development

**Create `.env.local.test` for local overrides:**
```bash
# Local auth states (Linux/Mac path)
TEST_AUTH_STATE_FILE=/opt/auth_states/auth_state_test_chromium_latest.json

# Or use home directory expansion
TEST_AUTH_STATE_FILE=~/auth_states/auth_state_test_chromium_latest.json
```

**Run tests:**
```bash
TEST_ENV=test pytest refua_tests/tests/ -v
```

---

## Browser-Specific Auth States

### Using Different Browsers

If you have browser-specific auth state files, configure them separately:

**.env.test:**
```bash
# General auth state (used by default)
TEST_AUTH_STATE_FILE=C:\auth_states\auth_state_test_chromium_latest.json

# Browser-specific overrides
TEST_AUTH_STATE_CHROMIUM=C:\auth_states\auth_state_test_chromium_latest.json
TEST_AUTH_STATE_FIREFOX=C:\auth_states\auth_state_test_firefox_latest.json
TEST_AUTH_STATE_WEBKIT=C:\auth_states\auth_state_test_webkit_latest.json
```

### Running Tests with Different Browsers

```bash
# Run with Chromium (default)
TEST_ENV=test pytest refua_tests/tests/ -v

# Run with Firefox
TEST_ENV=test BROWSER=firefox pytest refua_tests/tests/ -v

# Run with WebKit
TEST_ENV=test BROWSER=webkit pytest refua_tests/tests/ -v
```

---

## Auth State File Format

The auth state JSON file contains Playwright storage state with cookies and localStorage:

```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123...",
      "domain": ".meditek.app",
      "path": "/",
      "expires": 1735689600,
      "httpOnly": true,
      "secure": true,
      "sameSite": "Strict"
    }
  ],
  "origins": [
    {
      "origin": "https://meditek.app",
      "localStorage": [
        {
          "name": "auth_token",
          "value": "eyJhbGciOiJIUzI1NiIs..."
        },
        {
          "name": "user_id",
          "value": "user123"
        }
      ]
    }
  ],
  "metadata": {
    "captured_at": "2025-01-15T10:30:00Z",
    "expires_at": "2025-01-22T10:30:00Z",
    "environment": "test",
    "browser": "chromium"
  }
}
```

### Capturing New Auth State Files

Use the session capture script:

```bash
# For test environment
python -m refua_core.scripts.capture_session --env test --user john.doe --browser chromium

# For preprod environment
python -m refua_core.scripts.capture_session --env preprod --user qa_user --browser chromium

# For production environment (read-only)
python -m refua_core.scripts.capture_session --env prod --user readonly_user --browser chromium
```

---

## CI/CD Integration

### GitHub Actions

**.github/workflows/test.yml:**
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install

      - name: Download auth states from secret
        env:
          AUTH_STATES: ${{ secrets.AUTH_STATES_JSON }}
        run: |
          mkdir -p auth_states
          echo "$AUTH_STATES" | base64 -d > auth_states/auth_state_test_chromium_latest.json

      - name: Run tests
        env:
          TEST_ENV: test
          TEST_AUTH_STATE_FILE: auth_states/auth_state_test_chromium_latest.json
        run: pytest refua_tests/tests/ -v --tb=short

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-artifacts
          path: test-artifacts/
```

### GitLab CI

**.gitlab-ci.yml:**
```yaml
test:
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - playwright install
    - mkdir -p auth_states
    - echo "$AUTH_STATE_TEST" | base64 -d > auth_states/auth_state_test_chromium_latest.json
    - TEST_ENV=test TEST_AUTH_STATE_FILE=auth_states/auth_state_test_chromium_latest.json pytest refua_tests/tests/ -v
  variables:
    AUTH_STATE_TEST: $AUTH_STATE_TEST_B64  # Base64-encoded auth state file
  artifacts:
    paths:
      - test-artifacts/
    when: always
```

---

## Troubleshooting

### Auth State File Not Found

**Error:** `SessionFileNotFoundError: Session file not found`

**Solution:**
1. Verify the file path is correct: `TEST_AUTH_STATE_FILE=<path>`
2. Check file exists: `ls -la /path/to/auth_state_test_chromium_latest.json`
3. Verify environment variable is set: `echo $TEST_AUTH_STATE_FILE`

### Auth State File Expired

**Error:** `SessionExpiredError: Session expired at...`

**Solution:**
1. Re-capture the auth state file:
   ```bash
   python -m refua_core.scripts.capture_session --env test --user your_name
   ```
2. Update the auth state file in the configured location

### Path Expansion Issues

**Error:** `FileNotFoundError: [Errno 2] No such file or directory`

**Solution:**
1. Use absolute paths instead of environment variables for debugging
2. Test path expansion: `echo $AUTH_STATES_DIR`
3. Verify directory permissions: `ls -ld /path/to/auth_states`

### Docker Mount Issues

**Error:** `Permission denied` or `No such file or directory`

**Solution:**
1. Check volume mounts in docker-compose.yml
2. Verify auth_states directory exists locally
3. Check file permissions: `chmod 644 auth_states/*.json`
4. Use absolute paths in Docker: `/app/auth_states/...`

---

## Best Practices

### Security

- ✅ Store auth state files outside the project
- ✅ Add auth_states directory to `.gitignore`
- ✅ Use environment variables for sensitive paths
- ✅ Restrict file permissions: `chmod 600 auth_state_*.json`
- ✅ Use read-only volume mounts in Docker: `:ro`
- ✅ Store auth states in CI/CD secrets, not in code

### Organization

- ✅ Separate auth state files per environment
- ✅ Use consistent naming: `auth_state_{env}_{browser}_latest.json`
- ✅ Document auth state locations in team wiki
- ✅ Keep auth states updated (check expiration dates)
- ✅ Use relative paths where possible
- ✅ Document Docker paths in README

### Maintenance

- ✅ Capture new auth states before they expire
- ✅ Monitor session TTL in logs
- ✅ Re-capture if authentication requirements change
- ✅ Version auth state files if needed
- ✅ Test auth states locally before deployment
- ✅ Alert team when auth states are refreshed

---

## Examples

### Example 1: Local Development (Windows)

**`.env.test`:**
```bash
TEST_BASE_URL=https://test.meditek.app
TEST_API_ENDPOINT=https://api-test.meditek.app
TEST_AUTH_STATE_FILE=C:\Users\YourName\auth_states\auth_state_test_chromium_latest.json
TEST_SKIP_2FA=true
```

**Run command:**
```bash
TEST_ENV=test pytest refua_tests/tests/ -v
```

### Example 2: Docker Deployment

**docker-compose.yml:**
```yaml
services:
  tests:
    build: .
    environment:
      TEST_ENV: test
      TEST_AUTH_STATE_FILE: /app/auth_states/auth_state_test_chromium_latest.json
    volumes:
      - /path/to/local/auth_states:/app/auth_states:ro
```

**Run:**
```bash
docker-compose up tests
```

### Example 3: CI/CD Pipeline

**GitHub Actions:**
```bash
- name: Run tests with auth state
  env:
    TEST_ENV: test
    TEST_AUTH_STATE_FILE: /tmp/auth_states/auth_state_test_chromium_latest.json
  run: |
    mkdir -p /tmp/auth_states
    # Load auth state from CI/CD secret
    echo "${{ secrets.AUTH_STATE_TEST }}" > /tmp/auth_states/auth_state_test_chromium_latest.json
    pytest refua_tests/tests/ -v
```

---

## See Also

- Framework Documentation: `refuaAutomationCore/ARCHITECTURE.md`
- Test Architecture: `ARCHITECTURE.md`
- Test Guide: `CLAUDE.md`
- Framework API: `refuaAutomationCore/CLAUDE.md`

---

**Questions?** Refer to the complete framework documentation in refuaAutomationCore repository.
