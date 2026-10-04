# Authentication Setup

The suite supports two authentication modes, chosen by `TEST_AUTH_METHOD`. Both are handled by the `auth_state_session` fixture in `refua_tests/tests/conftest.py`, and both feed a single shared browser tab (`app_session`) used by pytest and BDD tests alike.

|              | `automation`                                                         | `session_state` (default)                                           |
| ------------ | -------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Environments | TEST only                                                            | test / preprod / prod                                               |
| How          | Opens `/automation/login/:personalNumber` once per run               | Injects a captured Playwright storage state (cookies + MSAL tokens) |
| Needs        | `--personal-number` (or `TEST_PERSONAL_NUMBER`), `AUTOMATION_SECRET` | A valid session file, or a manual login + 2FA                       |
| 2FA          | Not involved                                                         | Once per capture                                                    |

## Automation login (recommended on TEST)

```powershell
$env:TEST_ENV = "test"
venv\Scripts\pytest.exe --personal-number <approved digits>
```

- `--personal-number` (root `conftest.py`) sets `TEST_PERSONAL_NUMBER` and defaults `TEST_AUTH_METHOD=automation`.
- The same personal number is the DB seed user (see [ARCHITECTURE.md](../architecture/ARCHITECTURE.md#meditik-db-seeding)).
- `AUTOMATION_SECRET` comes from `.env.test` (resolved by the framework's `EnvironmentManager`).
- Before any test: the environment health check runs, the number must be ASCII digits, and the secret must exist - otherwise the run exits immediately.
- The login must land on `/home` with `meditik-home-page` visible within 60s.
- The session lives only in the loaded app tab, so tests navigate in-app (history navigation) instead of opening new pages.

## Captured session

```dotenv
# .env.test
TEST_AUTH_METHOD=session_state
TEST_AUTH_STATE_FILE=~/.refua_sessions/auth_state_meditek_test_chromium_latest.json   # default; ~ and $VARS expand
AUTH_CHECK_HEADLESS=false   # true for CI/background validation
```

Before all tests the file is validated: exists, parses, not expired, captured on the app host, and a live check confirms it bypasses 2FA. If invalid, `..\refuaAutomationCore\scripts\capture_session.py` runs (manual login + Authenticator approval) and the file is re-validated. After all tests a warning is printed if the session expired mid-run.

Capture manually:

```powershell
cd ..\refuaAutomationCore
..\refuaAutomationTests\venv\Scripts\python.exe scripts\capture_session.py --env test --app meditek --browser chromium
```

Sessions expire after a few days; the default output is `~\.refua_sessions\auth_state_meditek_<env>_<browser>_latest.json`.

## Troubleshooting

| Message                                                            | Cause / fix                                                        |
| ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `TEST_AUTH_METHOD must be session_state or automation.`            | Typo in the variable                                               |
| `Automation login is enabled only for TEST in this repository.`    | Use `TEST_ENV=test` or switch to `session_state`                   |
| `Set TEST_PERSONAL_NUMBER to the approved numeric TEST account.`   | Pass `--personal-number <digits>`                                  |
| `AUTOMATION_SECRET is required for automation login.`              | Add it to `.env.test`                                              |
| `TEST automation login did not establish a visible home dashboard` | Wrong number / secret, or app down - open the login URL manually   |
| `Auth state was captured, but it still redirects to Microsoft/2FA` | Captured session is not honoured by the app - use automation login |
| `capture_session.py was not found`                                 | `refuaAutomationCore` must be a sibling folder of this repo        |
