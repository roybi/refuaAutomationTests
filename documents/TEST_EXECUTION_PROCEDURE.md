# Test Execution Procedure — with Allure Reporting

Step-by-step procedure for executing the MEDITEK automation tests and producing an Allure report.
For day-to-day command snippets see [RUNBOOK.md](RUNBOOK.md); for report tooling internals see
`refua_tests/reports/QUICK_START.md` and `refua_tests/reports/TROUBLESHOOTING.md`.

All commands below are **Windows PowerShell**, run from the repo root `C:\_Dev\python\refuaAutomationTests`
unless stated otherwise.

---

## 0. Prerequisites (one-time)

| Requirement | Check | Install |
|---|---|---|
| Python 3.12 venv | `venv\Scripts\python.exe --version` | `python -m venv venv` then `pip install -r requirements.txt` |
| Playwright browsers | `venv\Scripts\playwright.exe --version` | `venv\Scripts\playwright.exe install` |
| allure-pytest plugin | `venv\Scripts\pip.exe show allure-pytest` | installed via `requirements.txt` |
| Allure CLI (for report generation) | `allure --version` | `npm install -g allure-commandline` — **or skip**: the Java generator below works without the CLI wrapper |
| Java (for report generation) | `java -version` | https://www.oracle.com/java/technologies/downloads/ |

---

## 1. Ensure a valid captured session (2FA bypass)

Tests reuse a captured MSAL session so they never see the Microsoft 2FA prompt.
Sessions **expire every 3 days**.

**Check the current session file:**

```powershell
Get-Content "$HOME\.refua_sessions\auth_state_meditek_test_chromium_latest.json" -Raw |
  ConvertFrom-Json | Select-Object -ExpandProperty metadata
```

If `expires_at` is in the past (or the file is missing), recapture:

```powershell
cd C:\_Dev\python\refuaAutomationCore
C:\_Dev\python\refuaAutomationTests\venv\Scripts\python.exe scripts\capture_session.py --env test --app meditik --browser chromium
```

A browser window opens — click **התחברות**, enter credentials, approve the number in
**Microsoft Authenticator**. The script saves the session to
`~\.refua_sessions\auth_state_meditek_test_chromium_latest.json` automatically.

> The test-suite setup (`conftest.py::auth_state_session`) validates this file before any test
> runs and launches `capture_session.py` itself if the file is invalid — but capturing up front
> avoids a surprise interactive prompt in the middle of a "hands-off" run.

---

## 2. Run the tests

`pytest.ini` already adds `--alluredir=allure/results` to every run, so **Allure results are
collected automatically** — no extra flag needed.

```powershell
cd C:\_Dev\python\refuaAutomationTests

# Full suite
$env:TEST_ENV="test"; venv\Scripts\pytest.exe refua_tests\tests\ -v

# Single file (example: the captured-session smoke test)
$env:TEST_ENV="test"; venv\Scripts\pytest.exe refua_tests\tests\new_tests.py -v

# Single test / keyword filter
$env:TEST_ENV="test"; venv\Scripts\pytest.exe -k "captured_session" -v

# By marker
$env:TEST_ENV="test"; venv\Scripts\pytest.exe -m smoke -v
```

Useful extras:

```powershell
# Show print() output live
... pytest ... -s

# Stop at first failure
... pytest ... -x

# Re-run only last failures
... pytest --lf
```

**Clean old results first** (recommended, otherwise old runs mix into the report):

```powershell
Remove-Item -Recurse -Force allure\results\* -ErrorAction SilentlyContinue
```

---

## 3. Generate the Allure report

Results land in `allure/results/` (raw JSON). Turn them into an HTML report:

```powershell
# Recommended — Java generator (bypasses the npm wrapper bug with spaces in the Windows username)
venv\Scripts\python.exe -m refua_tests.reports.generate_report_java

# Or simply double-click / run:
.\generate_report.bat
```

The report is written to `allure/report/` and opens in the browser automatically.

Alternative methods if the Java generator fails:

```powershell
# Node.js allure-commandline wrapper
venv\Scripts\python.exe -m refua_tests.reports.generate_report

# Dynamic Allure server (no static files, serves and opens directly)
venv\Scripts\python.exe -m refua_tests.reports.serve_allure
```

---

## 4. View the report

If the report did not open automatically, **do not open `index.html` via `file://`** — browsers
block its data loading (CORS). Serve it over HTTP instead:

```powershell
venv\Scripts\python.exe -m refua_tests.reports.serve_http        # http://localhost:8000
# or
.\view_report.bat
```

---

## 5. Quick one-liner (run + report)

```powershell
cd C:\_Dev\python\refuaAutomationTests; `
Remove-Item -Recurse -Force allure\results\* -ErrorAction SilentlyContinue; `
$env:TEST_ENV="test"; venv\Scripts\pytest.exe refua_tests\tests\ -v; `
venv\Scripts\python.exe -m refua_tests.reports.generate_report_java
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Setup error: `Page.goto: Timeout 60000ms exceeded` before any test runs | Test environment serving the ~3 MB app bundle very slowly (`no-store`, no caching) — `domcontentloaded` waits for it | Retry; if persistent, the environment is degraded — check with the dev team |
| Redirect loop `/login#code=...` → Microsoft → `/login#code=...`, dashboard never appears | App-side MSAL failure: token endpoint returns **400 AADSTS70008** (auth code expires before the slow-loading app redeems it) | Environment/app bug — report to MEDITEK dev team; tests cannot pass until fixed |
| Suite exits immediately: "capture_session.py ran but ... still invalid" | Session file expired / login not completed during capture | Re-run capture (step 1) and complete credentials + 2FA fully |
| `allure` not recognized | npm CLI not installed or not on PATH | Use the Java generator (step 3) — it needs only Java |
| Report opens but is empty / spins forever | Opened via `file://` | Serve over HTTP (step 4) |
| Old/stale tests appear in report | `allure/results` not cleaned between runs | Delete `allure\results\*` before running |

---

*Created 2026-07-15.*
