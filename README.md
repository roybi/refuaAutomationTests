# refuaAutomationTests

**Test Automation Implementation for MEDITEK (Meditik) Medical Application**

## Overview

Playwright + pytest + pytest-bdd automation for the Meditik application. It uses the **refuaAutomationCore** framework for infrastructure, so this repo focuses on page objects, tests, BDD features and test data.

Coverage is driven by the product **workbooks** (`docs/setup/*_CASES.json`):

- **Ready** cases are implemented as sanity tests and BDD scenarios.
- **Pending** cases are registered and skipped with their exact workbook _Clarification Status_ (never asserting unapproved behaviour).
- Each suite has a **guard test** that fails if a workbook case is marked Ready but is still unimplemented.

Current modules: Home & quick actions, Side menu, Request forms, My Requests, My Appointments, Scheduling, Referrals, New Referral, Medicines, Sick Days, Vaccinations, Medical Profile, Visit Summaries.

## What is This Repository?

This repository contains **only test implementation** - test cases, page objects, and test data. The reusable **framework infrastructure** is in a separate repository: `refuaAutomationCore` (expected as a sibling folder, `../refuaAutomationCore`).

### Key Principle

```
refuaAutomationCore (Framework) ← Reusable Infrastructure
         ↓
refuaAutomationTests (Tests) ← Application Test Implementation
```

The test repository **depends on** the framework, not the other way around.

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/DigitalIDF/refuaAutomationTests.git
cd refuaAutomationTests

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

The framework is expected as a sibling checkout (`../refuaAutomationCore`, installed with `pip install -e ../refuaAutomationCore`).

### 2. Authentication

Two modes, selected by `TEST_AUTH_METHOD`:

| Mode                      | How it works                                                                                                                                                                                                                                          |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `automation` (TEST only)  | Logs in once per run via `/automation/login/:personalNumber`. Requires `--personal-number` (or `TEST_PERSONAL_NUMBER`) and `AUTOMATION_SECRET` in `.env.test`. Passing `--personal-number` selects this mode automatically.                           |
| `session_state` (default) | Reuses a captured browser session (`TEST_AUTH_STATE_FILE`, default `~/.refua_sessions/auth_state_meditek_test_chromium_latest.json`). If missing/expired, `../refuaAutomationCore/scripts/capture_session.py` runs for a one-time manual login + 2FA. |

Either way, **one browser and one tab are shared by the whole run** (pytest and BDD); in-app navigation uses history navigation so the automation session is kept.

### 3. Run Tests

```powershell
$env:TEST_ENV = "test"

# Everything (sanity + pending + BDD)
pytest --personal-number <PN>

# One module
pytest refua_tests/tests/meditikVisitSummariesSanity.py --personal-number <PN>
pytest -m sick_days --personal-number <PN>

# BDD only
pytest refua_tests/bdd --personal-number <PN>

# Collect only (no browser) - quick import/marker check
pytest --collect-only -q
```

## Project Structure

```
refuaAutomationTests/
├── conftest.py                     # --personal-number option (automation login + DB seed)
├── pytest.ini                      # testpaths, file patterns, markers, logging, allure dir
├── requirements.txt
├── refua_tests/
│   ├── conftest.py                 # Session-wide Meditik DB seed (before all / after all)
│   ├── pages/                      # Page objects (data-testid ids in automationIds.py)
│   │   ├── meditikBasePage.py, meditikHomePage.py, menuPages.py, allActionsPage.py
│   │   ├── *TabbedPage.py          # My Requests, My Appointments, Referrals, Medicines
│   │   ├── emptyStateModulePage.py # Shared base: Sick Days, Vaccinations, Visit Summaries
│   │   ├── medicalProfilePage.py, requestForms.py, speedDial.py
│   │   └── softNotes.py            # Non-fatal label/copy notes reported to Allure
│   ├── tests/
│   │   ├── conftest.py             # Auth, shared app_session browser, artifacts
│   │   ├── meditik*Sanity.py       # Ready workbook cases per module
│   │   ├── test_*_pending.py       # Pending workbook cases + guard test
│   │   └── test_workbook_cases.py
│   ├── bdd/
│   │   ├── features/               # meditik_*.feature (+ *_pending.feature)
│   │   ├── step_defs/              # Step definitions per module
│   │   └── test_*_bdd.py           # scenarios() collectors
│   ├── utils/                      # meditik_seed.py, db_queries.py
│   └── reports/                    # Allure generate/serve helpers
├── tools/
│   ├── db_seed_meditik.py          # Seed CLI: plan / seed / verify / cleanup / leftovers
│   ├── db_discover_schema.py       # Read-only schema/FK discovery
│   ├── workbook_to_cases_json.py   # Workbook -> docs/setup/*_CASES.json
│   └── generate_pending_feature.py # Cases JSON -> pending .feature file
├── docs/                           # architecture/, bdd/, db/, guides/, reports/, setup/
└── .env.test / .env.preprod / .env.prod   # Credentials (never commit)
```

## Test Organization

### Page Objects (`refua_tests/pages/`)

- One page object per screen; locators are `@property` and use `data-testid` values from `automationIds.py`.
- Screens with the same shape share a base (`emptyStateModulePage.py`, the `*TabbedPage.py` family) - new modules are mostly configuration.

### Sanity tests (`refua_tests/tests/meditik*Sanity.py`)

- One file per module, one test per Ready workbook case (case id in the test name/docstring).
- Run on the shared authenticated tab (`app_session`).

### Pending tests (`refua_tests/tests/test_*_pending.py`)

- One skipped test per Pending case, skip reason = workbook Clarification Status.
- Guard test fails if the workbook marks a case Ready that has no implementation.

### BDD (`refua_tests/bdd/`)

- Each workbook case maps 1:1 to a scenario in `features/meditik_*.feature`.
- See [docs/bdd/QUICK_START_BDD.md](docs/bdd/QUICK_START_BDD.md) and [docs/bdd/WORKBOOK_V2.md](docs/bdd/WORKBOOK_V2.md).

### Tracking

- [docs/setup/TEST_CASE_TRACKER.csv](docs/setup/TEST_CASE_TRACKER.csv) - case -> test mapping and status.
- [docs/TESTS_HUMAN_DESCRIPTION.txt](docs/TESTS_HUMAN_DESCRIPTION.txt), [docs/REQUEST_FORMS_COVERAGE_SUMMARY.txt](docs/REQUEST_FORMS_COVERAGE_SUMMARY.txt).

## Meditik DB Test Data Seeding

When `MEDITIK_SEED_ENV` equals `TEST_ENV`, the session fixture seeds **3 requests of every Meditik request type** for the run's personal number before all tests, and cleans up after all tests. Seeded dates fall on Israeli working days.

| Variable (`.env.<env>`)         | Purpose                                         |
| ------------------------------- | ----------------------------------------------- |
| `MEDITIK_SEED_ENV`              | Must equal `TEST_ENV` to enable seeding         |
| `SEED_ALLOWED_PERSONAL_NUMBERS` | Allowed personal numbers/ranges (guard)         |
| `MEDITIK_SEED_DATASET`          | Dataset to seed (default `all`)                 |
| `MEDITIK_SEED_CLEANUP`          | `report` (keep rows, default) or `delete-owned` |
| `MEDITIK_SEED_MANIFEST_DIR`     | Run manifests (default `~/.refua_seeds`)        |

A blocked or failed seed is logged as a warning and never fails the suite; tests needing seed data use the `meditik_seeded_requests` fixture and skip without it.

Manual CLI:

```powershell
python tools\db_seed_meditik.py plan      --env test --user <PN> --dataset all   # read-only
python tools\db_seed_meditik.py seed      --env test --user <PN> --dataset all
python tools\db_seed_meditik.py verify    --env test --run-id <id>
python tools\db_seed_meditik.py cleanup   --env test --run-id <id> [--mode delete-owned]
python tools\db_seed_meditik.py leftovers --env test --user <PN>
```

## Running Tests

### Basic Commands

```bash
# All tests (testpaths = refua_tests/tests + refua_tests/bdd)
TEST_ENV=test pytest --personal-number <PN>

# Specific file
TEST_ENV=test pytest refua_tests/tests/meditikMenuSanity.py --personal-number <PN>

# Specific test
TEST_ENV=test pytest "refua_tests/tests/meditikMenuSanity.py::<Class>::<test>" --personal-number <PN>

# Tests matching pattern
TEST_ENV=test pytest -k "empty_state" --personal-number <PN>
```

Test discovery (`pytest.ini`): files `test_*.py` and `*Sanity.py`, classes `Test*` and `Meditik*`.

### Test Markers

```bash
# Area markers
TEST_ENV=test pytest -m sanity
TEST_ENV=test pytest -m bdd

# Module markers: home, menu, request_forms, my_requests, my_appointments, scheduling,
# referrals, new_referral, medicines, sick_days, vaccinations, medical_profile, visit_summaries
TEST_ENV=test pytest -m "medicines or referrals"
```

`--strict-markers` is on: add new markers to `pytest.ini` before using them.

### Parallel Execution

```bash
# Use all CPU cores
TEST_ENV=test pytest -n auto refua_tests/tests/ -v

# Use specific number of workers
TEST_ENV=test pytest -n 4 refua_tests/tests/ -v
```

### Device/Browser Testing

```bash
# Run on iPhone
TEST_ENV=test DEVICE=iphone_15 pytest refua_tests/tests/ -v

# Run on Android
TEST_ENV=test DEVICE=android_pixel pytest refua_tests/tests/ -v

# Run with Firefox
TEST_ENV=test BROWSER=firefox pytest refua_tests/tests/ -v
```

### Reporting

Results are always written to `allure/results` (`--alluredir` is in `pytest.ini`).

```bash
# Generate + open the HTML report (Windows helpers)
generateReport.bat
viewReport.bat

# Or with the Allure CLI
allure serve ./allure/results
```

## Environment Variables

### Required

```bash
TEST_ENV=test|preprod|prod    # Target environment
```

### Authentication

```bash
TEST_AUTH_METHOD=session_state|automation   # default session_state; --personal-number sets automation
TEST_PERSONAL_NUMBER=<PN>                   # or --personal-number (automation login + DB seed user)
AUTOMATION_SECRET=...                       # required for automation login (.env.test)
TEST_AUTH_STATE_FILE=~/.refua_sessions/...  # session_state file
AUTH_CHECK_HEADLESS=true|false              # headless session validation (CI)
```

### Optional

```bash
TEST_APP=meditek               # Application (default: meditek)
DEVICE=desktop|iphone|android  # Device profile (default: desktop)
BROWSER=chromium|firefox|webkit  # Browser (default: chromium)
RECORD_VIDEO=true|false        # Capture video (default: true)
```

DB seeding variables: see [Meditik DB Test Data Seeding](#meditik-db-test-data-seeding).

## Features

### Multi-Environment Support

- **test**: Local development (3-day session TTL)
- **preprod**: Integration testing (3-day session TTL)
- **prod**: Production validation (30-min session TTL, read-only)

### Authentication

- **Automation login (TEST)**: `pytest --personal-number <PN>` - no 2FA, one login per run.
- **Captured session**: validated before the run; if invalid, `capture_session.py` (core repo) opens for a one-time manual login + 2FA.

### Mobile Device Testing

```bash
# Built-in device profiles
TEST_ENV=test DEVICE=iphone_15 pytest refua_tests/tests/ -v
TEST_ENV=test DEVICE=android_pixel pytest refua_tests/tests/ -v
```

### Parallel Execution

```bash
# Run tests on multiple workers
TEST_ENV=test pytest -n auto refua_tests/tests/ -v
```

### Automatic Artifact Management

- **On Pass**: Videos and screenshots are deleted (saves storage)
- **On Fail**: Artifacts are retained for debugging

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/test-new-feature
```

### 2. Write Tests

1. Add/extend a page object: `refua_tests/pages/<module>Page.py` (ids in `automationIds.py`)
2. Ready cases: `refua_tests/tests/meditik<Module>Sanity.py` + scenario in `refua_tests/bdd/features/meditik_<module>.feature`
3. Pending cases: `refua_tests/tests/test_<module>_pending.py` (+ `tools/generate_pending_feature.py` for the pending feature)
4. Register the module marker in `pytest.ini` and update `docs/setup/TEST_CASE_TRACKER.csv`

### 3. Run Tests Locally

```bash
TEST_ENV=test pytest refua_tests/tests/meditik<Module>Sanity.py --personal-number <PN>
```

### 4. Commit and Push

```bash
git add refua_tests/ docs/
git commit -m "test: add <module> workbook suite"
git push origin feature/test-new-feature
```

### 5. Create Pull Request

PRs into `main` must pass the org security checks (Code Scanner / CodeQL, ScanLi, Secret Scanner). Do not commit real phone numbers, connection strings or credentials - they fail the scan.

## Dependencies

### Core

- `refua-automation-core` - framework (sibling repo, `pip install -e ../refuaAutomationCore`)
- `playwright>=1.40.0` - Browser automation
- `pytest>=7.0.0`, `pytest-bdd>=7.0.0` - Test framework + BDD
- `python-dotenv>=1.0.0` - Environment configuration

### Execution & Data

- `pytest-xdist>=3.0.0` - Parallel execution (DB seed runs on worker `gw0` only)
- `pytest-timeout>=2.1.0` - Test timeout handling
- `psycopg2-binary`, `boto3` - Meditik DB access / AWS secrets
- `holidays` - Israeli working-day rules for seeded dates
- `allure-pytest` - install separately when needed

See `requirements.txt` for complete list.

## Configuration

### `.env.*` Files (Environment-Specific)

- `.env.test` - Test environment credentials
- `.env.preprod` - Preprod environment credentials
- `.env.prod` - Production environment credentials

**⚠️ Never commit `.env` files with real credentials!**

### `pytest.ini` (Pytest Configuration)

- Test discovery settings
- Markers and categorization
- Logging configuration
- Timeout settings

### `requirements.txt` (Python Dependencies)

- Framework package
- Test dependencies
- Development tools

## Documentation

- [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) - Test architecture and patterns
- [docs/guides/RUNBOOK.md](docs/guides/RUNBOOK.md) - Running the suites (setup, auth, run, report, seed, troubleshooting)
- [docs/setup/AUTH_STATE_SETUP.md](docs/setup/AUTH_STATE_SETUP.md) - Session / auth setup
- [docs/bdd/QUICK_START_BDD.md](docs/bdd/QUICK_START_BDD.md) - BDD and workbook mapping
- [docs/reports/README.md](docs/reports/README.md) - Allure reporting
- [AGENT_HANDOFF.md](AGENT_HANDOFF.md), [CLAUDE.md](CLAUDE.md) - Guidance for AI agents
- **Framework Docs** - See the `refuaAutomationCore` repository

## Troubleshooting

### Session Expired / Still Redirects to Microsoft 2FA

- Prefer automation login on TEST: `pytest --personal-number <PN>` (needs `AUTOMATION_SECRET`).
- Otherwise delete the file at `TEST_AUTH_STATE_FILE`; the next run triggers `capture_session.py` for a fresh login.

### DB Seed Skipped

Check the warning text: `MEDITIK_SEED_ENV` must equal `TEST_ENV`, and the personal number must be in `SEED_ALLOWED_PERSONAL_NUMBERS`. Use `tools\db_seed_meditik.py leftovers` to find rows from earlier runs.

### Framework Import Error

```bash
# Verify framework installation
python -c "from refua_core.config.environment import EnvironmentManager; print('OK')"

# Reinstall if needed
pip install refua-automation-core
```

### Tests Timeout

- Check `pytest.ini` timeout setting
- Increase for slow operations: `timeout = 600`
- Add explicit waits in page objects

### Flaky Tests

Check for:

- Missing waits (use `page.wait_for_selector()`)
- Race conditions
- Unreliable locators
- Network issues

## Best Practices

### Page Objects

✅ One page object per page/screen
✅ Group locators using @property
✅ Keep locators at top of class
✅ Encapsulate complex interactions
❌ Avoid hard-coded waits
❌ Don't mix UI logic with assertions

### Test Cases

✅ Use Arrange-Act-Assert pattern
✅ Descriptive test names
✅ Test one feature per test
✅ Use fixtures for setup
❌ Avoid test interdependencies
❌ Don't use hard-coded wait times

### Test Data

✅ Use factories to generate test data
✅ Randomize data to avoid conflicts
✅ Isolate test data per test
❌ Hard-coded test data
❌ Sharing test data between tests

## CI/CD Integration

This repo has no test-execution workflow yet; suites are run locally or on the test runner.

Pushes and pull requests to DigitalIDF run the organization's required checks:

- Code Scanner / CodeQL, ScanLi (SAST, PII, secrets), Secret Scanner, Container Image Security Scan
- Repository custom properties (`Owner_Name`, `Owner_Phone`) must be set

`main` is protected: pushes are rejected while the **Code Scanner** required workflow is failing.

## Support

For issues or questions:

- Check [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) for detailed guidance
- Review [CLAUDE.md](CLAUDE.md) for development tips
- Check the `refuaAutomationCore` framework docs

## Contributing

1. Create feature branch: `git checkout -b feature/description`
2. Write tests following established patterns
3. Run tests locally: `TEST_ENV=test pytest --personal-number <PN>`
4. Commit with clear messages: `git commit -m "test: description"`
5. Push and create pull request

## License

[Specify your license here]

## See Also

- Framework Repository: `refuaAutomationCore`
- Framework Architecture: `refuaAutomationCore/ARCHITECTURE.md`
- Framework Documentation: `refuaAutomationCore/CLAUDE.md`
