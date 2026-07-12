# MEDITEK Test Automation — Runbook

Quick reference for day-to-day operations.

---

## Capture Sessions (2FA Bypass)

Sessions expire every **3 days**. Run from `refuaAutomationCore`.

```powershell
cd C:\_Dev\python\refuaAutomationCore

# Chromium
venv\Scripts\python.exe scripts/capture_session.py --env test --browser chromium

# Firefox
venv\Scripts\python.exe scripts/capture_session.py --env test --browser firefox
```

The browser window opens automatically — log in manually, approve 2FA in Authenticator.  
Sessions are saved to: `~\.refua_sessions\auth_state_meditek_test_{browser}_latest.json`

---

## Run Tests

Run from `refuaAutomationTests`.

```powershell
cd C:\_Dev\python\refuaAutomationTests

# Chromium
$env:TEST_APP="meditek"; $env:TEST_ENV="test"; $env:BROWSER="chromium"; venv\Scripts\python.exe -m pytest

# Firefox
$env:TEST_APP="meditek"; $env:TEST_ENV="test"; $env:BROWSER="firefox"; venv\Scripts\python.exe -m pytest
```

### Useful flags

```powershell
# Verbose output
... pytest -v

# Specific test file
... pytest refua_tests/tests/test_home_page.py -v

# Specific test by name
... pytest -k "test_login_page_title" -v

# Smoke tests only
... pytest -m smoke -v

# Stop on first failure
... pytest -x -v
```

---

## Session Files Location

```
~\.refua_sessions\
├── auth_state_meditek_test_chromium_latest.json   ← used by BROWSER=chromium
└── auth_state_meditek_test_firefox_latest.json    ← used by BROWSER=firefox
```

---

## Check Session Expiry

```powershell
$f = "$env:USERPROFILE\.refua_sessions\auth_state_meditek_test_chromium_latest.json"
(Get-Content $f | ConvertFrom-Json).metadata.expires_at
```
