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

One entry point runs any registered system. **`--system` and `--user` are explicit per-run parameters**: one invocation targets one system (`meditik`, later `cprgo`, or `all`) and exactly one user. The next run can use another user (4444405, 4444411, ...).

```powershell
# Meditik BDD, only @smoke scenarios, user 4444401, TEST
.\venv\Scripts\python.exe run_tests.py --system meditik --suite bdd --tags smoke --user 4444401 --env test

# Same selection, another user, results kept in their own Allure folder
.\venv\Scripts\python.exe run_tests.py --system meditik --suite bdd --tags smoke --user 4444405 --allure-dir auto

# Everything of every system; one module; collection only
.\venv\Scripts\python.exe run_tests.py --system all --user 4444411
.\venv\Scripts\python.exe run_tests.py --system meditik --tags medicines --user 4444401
.\venv\Scripts\python.exe run_tests.py --system meditik --user 4444401 -- --collect-only -q

.\venv\Scripts\python.exe run_tests.py --list-systems
```

| Option          | Meaning                                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------------------------- |
| `--system`      | Required: a registered system (`meditik`, alias `meditek`) or `all`                                         |
| `--user`        | Personal number of the test user, digits only; required for systems that need a login (Meditik)           |
| `--env`         | `test` (default), `preprod`, `prod`; exported as `TEST_ENV`                                                |
| `--suite`       | `bdd` (Gherkin), `pytest` (page-object tests) or `all` (default)                                           |
| `--tags`        | pytest marker expression: `smoke`, `"smoke and my_requests"`, `"not known_issue"`                          |
| `--allure-dir`  | Default `allure/results`; `auto` = `allure/results/<system>_<user>_<timestamp>`                            |
| `--clean`       | Empty the Allure directory first (only inside `allure/`)                                                   |
| `--dry-run`     | Print the pytest command without running it                                                                |
| `-- <args>`     | Anything else is passed to pytest (`-x`, `--lf`, `-k "<expr>"`, `--headless`, `--collect-only`)             |

The wrapper only builds a pytest command and prints it. The equivalent native command (`pytest.ini` already adds `-v`, `--alluredir=allure/results` and both test paths):

```powershell
$env:TEST_ENV = "test"
venv\Scripts\python.exe -m pytest refua_tests\bdd --system meditik -m smoke --personal-number 4444401
```

How `--system` works: a test belongs to the system whose marker it carries (`@pytest.mark.meditik` on pytest tests, `@meditik` feature tag on BDD scenarios). The run keeps only that system's tests, exports its `TEST_APP`, and starts only that system's session fixtures (login, DB seed), so a CPR GO run never logs into Meditik. When system-owned tests are collected and `--system` is missing, pytest exits with code 4; this also applies to `--collect-only` (use `--system all`). Tests outside the registry (for example `tools/tests`) run without `--system`.

Other direct commands (always add `--system`):

```powershell
$env:TEST_ENV = "test"
$pn = "<approved personal number>"

# One module (file or marker)
venv\Scripts\python.exe -m pytest refua_tests\tests\meditikMedicinesSanity.py --system meditik --personal-number $pn
venv\Scripts\python.exe -m pytest -m "visit_summaries" --system meditik --personal-number $pn

# Skip known product issues
venv\Scripts\python.exe -m pytest -m "not known_issue" --system all --personal-number $pn

# Collection check only (no browser, no login)
venv\Scripts\python.exe -m pytest --collect-only -q --system all
```

Module markers: `home`, `menu`, `request_forms`, `my_requests`, `my_appointments`, `scheduling`, `referrals`, `new_referral`, `medicines`, `sick_days`, `vaccinations`, `medical_profile`, `visit_summaries`.

Clean old results first, otherwise runs mix in the report (or use `--clean` / `--allure-dir auto`):

```powershell
Remove-Item -Recurse -Force allure\results\* -ErrorAction SilentlyContinue
```

### Adding a new system (for example CPR GO)

1. Register it in `refua_tests/systems.py` (`SystemSpec(name, marker, app_id, description, requires_user)`); `--system`, `run_tests.py --list-systems` and the usage messages pick it up automatically.
2. Register its marker in `pytest.ini` (`cprgo` is already reserved).
3. Add its page objects, pytest tests (`refua_tests/tests/cprgo<Module>Sanity.py`, each class/test `@pytest.mark.cprgo`) and its features (`refua_tests/bdd/features/cprgo_*.feature`, tagged `@bdd @cprgo`).
4. Add its BDD loader `refua_tests/bdd/test_cprgo_bdd.py` that imports only CPR GO step modules (shared step names would collide with Meditik's).
5. Put its login/session fixtures behind `is_system_active(request.config, "cprgo")` (see `auth_state_session` in `refua_tests/tests/conftest.py`) and add its URL/credentials to the `.env.<env>` files.
6. Add the tracker rows (`docs/setup/TEST_CASE_TRACKER.csv`, `CPRGO-001`...), then verify with `run_tests.py --system cprgo --user <PN> -- --collect-only -q` and `--system meditik` (counts for Meditik must not change).

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

| Symptom                                                            | Fix                                                                                                    |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `Auth state was captured, but it still redirects to Microsoft/2FA` | Use automation login (`--personal-number`), or delete the session file and recapture                   |
| `Set TEST_PERSONAL_NUMBER to the approved numeric TEST account`    | Pass `--personal-number <digits>`                                                                      |
| `AUTOMATION_SECRET is required`                                    | Add it to `.env.test`                                                                                  |
| `Meditik DB seed skipped (...)` warning                            | Check `MEDITIK_SEED_ENV`, `SEED_ALLOWED_PERSONAL_NUMBERS`, DB access; run `leftovers` for a stuck lock |
| Pending tests "skipped"                                            | Expected - reason is the workbook Clarification Status                                                 |
| Guard test fails                                                   | Workbook marked a case Ready: implement it (sanity + BDD) and update the tracker                       |
| `--strict-markers` error                                           | Register the marker in `pytest.ini`                                                                    |
| `--system is required` (exit code 4)                               | Add `--system meditik` (or `all`); also needed for `--collect-only`                                    |
| `Unknown system '<name>'`                                          | Register it in `refua_tests/systems.py` (see "Adding a new system")                                    |
| `--user is required` (wrapper)                                     | Pass exactly one personal number, digits only: `--user 4444401`                                        |
