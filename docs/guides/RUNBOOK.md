# Runbook - Running the Meditik Suites

All commands are Windows PowerShell from the repo root (`C:\_Dev\python\refuaAutomationTests`).

## 0. One-time setup

```powershell
python -m venv venv
venv\Scripts\pip.exe install -r requirements.txt
venv\Scripts\pip.exe install -e ..\refuaAutomationCore
venv\Scripts\pip.exe install allure-pytest        # needed for Allure results
venv\Scripts\playwright.exe install chromium
```

Report generation also needs Java and/or `npm install -g allure-commandline` (see [docs/reports/README.md](../reports/README.md)).

`.env.test` must contain the app/DB settings plus, for automation login, `AUTOMATION_SECRET`. Never commit `.env.*` files.

## 1. Authenticate

**Automation login (TEST, recommended)** - nothing to prepare; pass `--personal-number` on every run. The suite logs in once via `/automation/login/:personalNumber` and fails fast if the environment is down, the number is not numeric, or `AUTOMATION_SECRET` is missing.

**Captured session (`TEST_AUTH_METHOD=session_state`)** - the suite validates `TEST_AUTH_STATE_FILE` (default `~\.refua_sessions\auth_state_meditek_test_chromium_latest.json`) and, if invalid, launches `..\refuaAutomationCore\scripts\capture_session.py` for a manual login + 2FA. To capture up front:

```powershell
cd ..\refuaAutomationCore
..\refuaAutomationTests\venv\Scripts\python.exe scripts\capture_session.py --env test --app meditek --browser chromium
cd ..\refuaAutomationTests
```

Details: [docs/setup/AUTH_STATE_SETUP.md](../setup/AUTH_STATE_SETUP.md).

## 2. Run

`pytest.ini` already adds `-v`, `--alluredir=allure/results` and both test paths.

```powershell
$env:TEST_ENV = "test"
$pn = "<approved personal number>"

# Everything (sanity + pending + BDD)
venv\Scripts\pytest.exe --personal-number $pn

# One module (file or marker)
venv\Scripts\pytest.exe refua_tests\tests\meditikMedicinesSanity.py --personal-number $pn
venv\Scripts\pytest.exe -m "visit_summaries" --personal-number $pn

# BDD only / pytest only
venv\Scripts\pytest.exe refua_tests\bdd --personal-number $pn
venv\Scripts\pytest.exe refua_tests\tests --personal-number $pn

# Skip known product issues
venv\Scripts\pytest.exe -m "not known_issue" --personal-number $pn

# Collection check only (no browser, no login)
venv\Scripts\pytest.exe --collect-only -q
```

Module markers: `home`, `menu`, `request_forms`, `my_requests`, `my_appointments`, `scheduling`, `referrals`, `new_referral`, `medicines`, `sick_days`, `vaccinations`, `medical_profile`, `visit_summaries`.

Useful flags: `-x` (stop on first failure), `--lf` (last failed), `-k "<expr>"`, `--headless` (framework plugin option).

Clean old results first, otherwise runs mix in the report:

```powershell
Remove-Item -Recurse -Force allure\results\* -ErrorAction SilentlyContinue
```

## 3. Report

```powershell
.\generateReport.bat   # allure/results -> allure/report (Java generator)
.\viewReport.bat       # serve allure/report on http://localhost:8000
```

## 4. DB seed (optional / manual)

Automatic when `MEDITIK_SEED_ENV` equals `TEST_ENV` in `.env.test`. Manual control:

```powershell
venv\Scripts\python.exe tools\db_seed_meditik.py plan      --env test --user $pn --dataset all
venv\Scripts\python.exe tools\db_seed_meditik.py leftovers --env test --user $pn
venv\Scripts\python.exe tools\db_seed_meditik.py cleanup   --env test --run-id <id> --mode delete-owned
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Auth state was captured, but it still redirects to Microsoft/2FA` | Use automation login (`--personal-number`), or delete the session file and recapture |
| `Set TEST_PERSONAL_NUMBER to the approved numeric TEST account` | Pass `--personal-number <digits>` |
| `AUTOMATION_SECRET is required` | Add it to `.env.test` |
| `Meditik DB seed skipped (...)` warning | Check `MEDITIK_SEED_ENV`, `SEED_ALLOWED_PERSONAL_NUMBERS`, DB access; run `leftovers` for a stuck lock |
| Pending tests "skipped" | Expected - reason is the workbook Clarification Status |
| Guard test fails | Workbook marked a case Ready: implement it (sanity + BDD) and update the tracker |
| `--strict-markers` error | Register the marker in `pytest.ini` |
