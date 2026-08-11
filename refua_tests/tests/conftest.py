"""
Pytest configuration for refuaAutomationTests.

This conftest imports selected fixtures from the framework
to avoid conflicts with pytest-playwright.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_REPO_ROOT = REPO_ROOT.parent / "refuaAutomationCore"
AUTH_STATE_HOST = "meditik.test.medical.idf.il"
AUTH_STATE_URL = f"https://{AUTH_STATE_HOST}/home"


def _load_environment_file() -> None:
    test_env = os.getenv("TEST_ENV", "test")
    os.environ.setdefault("TEST_ENV", test_env)

    load_dotenv(REPO_ROOT / f".env.{test_env}", override=False)


def _auth_state_path() -> Path:
    auth_state_file = os.getenv(
        "TEST_AUTH_STATE_FILE",
        "~/.refua_sessions/auth_state_meditek_test_chromium_latest.json",
    )
    return Path(os.path.expandvars(auth_state_file)).expanduser()


def _auth_state_is_valid(auth_state_path: Path) -> bool:
    if not auth_state_path.exists():
        return False

    try:
        with auth_state_path.open("r", encoding="utf-8") as auth_state:
            data = json.load(auth_state)
    except (OSError, json.JSONDecodeError):
        return False

    metadata = data.get("metadata", {})
    expires_at = metadata.get("expires_at")
    captured_url = metadata.get("url", "")

    if not expires_at:
        return False

    try:
        expires_at = expires_at.replace("Z", "+00:00")
        expires = datetime.fromisoformat(expires_at)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
    except ValueError:
        return False

    if datetime.now(timezone.utc) >= expires:
        return False

    return urlparse(captured_url).netloc == AUTH_STATE_HOST


DASHBOARD_QUICK_ACTIONS = "פעולות מהירות"  # SpeedDial label, rendered only when logged in


def _auth_state_bypasses_2fa(auth_state_path: Path) -> bool:
    from playwright.sync_api import sync_playwright

    # Session files wrap Playwright's storage state under a "storage_state"
    # key (with capture metadata alongside). Passing the raw file path would
    # make Playwright load zero cookies.
    with auth_state_path.open("r", encoding="utf-8") as auth_state:
        session_data = json.load(auth_state)
    storage_state = session_data.get("storage_state", session_data)

    # Headed by default so the session validation is visible during local
    # runs; set AUTH_CHECK_HEADLESS=true for CI/background execution.
    check_headless = os.getenv("AUTH_CHECK_HEADLESS", "false").lower() == "true"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=check_headless)
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()

        try:
            page.goto(AUTH_STATE_URL, wait_until="domcontentloaded", timeout=60000)

            login_button = page.locator("#login-button")
            dashboard = page.get_by_text(DASHBOARD_QUICK_ACTIONS).first

            # The app settles in one of two states: silent MSAL sign-in
            # (dashboard) or the login page.
            try:
                login_button.or_(dashboard).first.wait_for(
                    state="visible", timeout=45000
                )
            except Exception:
                body_text = ""
                try:
                    body_text = page.locator("body").inner_text(timeout=2000)[:200]
                except Exception:
                    pass
                if "503" in body_text or "Unavailable" in body_text:
                    raise RuntimeError(
                        f"MEDITEK test environment is unavailable (503) at {AUTH_STATE_URL} — "
                        "cannot verify the session or run tests. Try again later."
                    )
                return False

            if dashboard.is_visible():
                # Tokens were picked up silently — no login click, no 2FA.
                return True

            try:
                login_button.click(timeout=10000)
            except Exception:
                # The login button can vanish between the visibility wait and
                # the click when MSAL signs in silently and swaps in the
                # dashboard — that is a success, not a failure.
                try:
                    dashboard.wait_for(state="visible", timeout=15000)
                    return True
                except Exception:
                    return False

            try:
                page.wait_for_url(
                    lambda url: urlparse(url).netloc != AUTH_STATE_HOST
                    or urlparse(url).path != "/home",
                    timeout=30000,
                )
            except Exception:
                pass

            parsed_url = urlparse(page.url)
            if parsed_url.netloc == AUTH_STATE_HOST and parsed_url.path != "/home":
                return True

            # Some flows land back on /home with the dashboard rendered there.
            try:
                dashboard.wait_for(state="visible", timeout=15000)
                return True
            except Exception:
                return False
        finally:
            context.close()
            browser.close()


def _capture_auth_state() -> None:
    script_path = CORE_REPO_ROOT / "scripts" / "capture_session.py"
    if not script_path.exists():
        raise RuntimeError(f"capture_session.py was not found: {script_path}")

    command = [
        sys.executable,
        str(script_path),
        "--env",
        os.getenv("TEST_ENV", "test"),
        "--app",
        os.getenv("TEST_APP", "meditek"),
        "--browser",
        os.getenv("BROWSER", "chromium"),
    ]
    try:
        subprocess.run(command, cwd=CORE_REPO_ROOT, check=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "capture_session.py did not complete successfully. "
            "Finish the login flow in the browser window, including credentials and 2FA, "
            "then run pytest again."
        ) from error


def _check_environment_is_up() -> None:
    """Fail fast with a clear message when the app itself is unreachable."""
    import urllib.request

    request = urllib.request.Request(AUTH_STATE_URL, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.status
    except urllib.error.HTTPError as error:
        status = error.code
    except Exception as error:
        raise RuntimeError(
            f"MEDITEK test environment is unreachable at {AUTH_STATE_URL}: {error}"
        ) from None

    if status != 200:
        raise RuntimeError(
            f"MEDITEK test environment returned HTTP {status} at {AUTH_STATE_URL} — "
            "the environment is down; tests cannot run. Try again later."
        )


def _ensure_auth_state() -> None:
    auth_state_path = _auth_state_path()
    if _auth_state_is_valid(auth_state_path) and _auth_state_bypasses_2fa(auth_state_path):
        return

    _capture_auth_state()

    if not _auth_state_is_valid(auth_state_path) or not _auth_state_bypasses_2fa(auth_state_path):
        raise RuntimeError(
            "Auth state was captured, but it still redirects to Microsoft/2FA. "
            f"Expected the saved session to open MEDITEK after login: {auth_state_path}"
        )


_load_environment_file()

# Framework fixtures still available to tests.
# browser_page is defined locally below — core no longer ships that fixture.
from refua_core.conftest import env_manager, playwright_instance  # noqa: F401
from refua_core.config.environment import get_env_manager
from refua_tests.pages.soft_notes import (
    clear_session_soft_notes,
    clear_soft_notes,
    drain_soft_notes,
    publish_soft_notes_to_allure,
    session_soft_notes,
    soft_notes_mode,
)


@pytest.fixture(autouse=True)
def _soft_notes_per_test():
    """Collect soft label notes and publish them to Allure at teardown."""
    clear_soft_notes()
    yield
    notes = drain_soft_notes()
    if not notes:
        return
    publish_soft_notes_to_allure(notes)
    mode = soft_notes_mode()
    summary = "\n".join(f"• {n}" for n in notes)
    if mode == "fail":
        pytest.fail(
            "[SOFT WARNING] UI copy/label mismatch (data-testid OK):\n" + summary,
            pytrace=False,
        )
    if mode == "broken":
        # Non-AssertionError → Allure usually shows as broken (orange).
        raise RuntimeError(
            "[SOFT WARNING] UI copy/label mismatch (data-testid OK):\n" + summary
        )


@pytest.fixture(scope="session", autouse=True)
def _soft_notes_session_log(auth_state_session):
    """Write a suite-level soft-warnings log into allure/results at the end."""
    clear_session_soft_notes()
    results_dir = REPO_ROOT / "allure" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    categories_src = REPO_ROOT / "allure" / "categories.json"
    if categories_src.exists():
        (results_dir / "categories.json").write_text(
            categories_src.read_text(encoding="utf-8"), encoding="utf-8"
        )
    yield
    notes = session_soft_notes()
    if not notes:
        return
    log_path = results_dir / "soft-warnings-log.txt"
    log_path.write_text(
        "Meditik soft warnings (label/copy mismatches; data-testid OK)\n"
        + "=" * 60
        + "\n"
        + "\n".join(f"• {n}" for n in notes)
        + "\n",
        encoding="utf-8",
    )
    print(f"\n[soft-warnings] {len(notes)} note(s) → {log_path}")


@pytest.fixture(scope="session", autouse=True)
def auth_state_session():
    """BEFORE ALL / AFTER ALL for the captured MEDITEK session.

    BEFORE ALL (setup, runs once before any test):
      1. Resolve the session JSON path from TEST_AUTH_STATE_FILE (.env.test).
      2. Validate it (exists, parses, not expired, captured on the app host,
         and actually bypasses 2FA in a live headless check).
      3. Valid   -> continue; the browser_page fixture inserts the stored
                    cookies + MSAL tokens into the Chrome context of every
                    test, so tests never see the Microsoft 2FA prompt.
         Invalid -> run capture_session.py (manual login + 2FA once) to
                    produce a valid file, then re-validate.

    AFTER ALL (teardown, runs once after the last test):
      Re-check the file and warn if it expired while the suite was running.
    """
    try:
        _check_environment_is_up()
        _ensure_auth_state()
    except RuntimeError as error:
        pytest.exit(str(error), returncode=1)

    auth_state_path = _auth_state_path()
    yield auth_state_path

    # AFTER ALL — surface expiry problems early for the next run
    if not _auth_state_is_valid(auth_state_path):
        print(
            f"\n[auth_state_session] WARNING: {auth_state_path} is no longer valid "
            "(likely expired) — the next run will trigger capture_session.py."
        )


@pytest.fixture(scope="function")
def browser_page(auth_state_session, request):
    """Authenticated Playwright page for UI tests (2FA bypass via storage_state).

    Session JSON from capture_session.py wraps Playwright's storage under
    ``storage_state``; we unwrap before creating the context so cookies +
    MSAL localStorage tokens are applied correctly.
    """
    from playwright.sync_api import sync_playwright

    auth_state_path = auth_state_session
    with auth_state_path.open("r", encoding="utf-8") as auth_state:
        session_data = json.load(auth_state)
    storage_state = session_data.get("storage_state", session_data)

    env_mgr = get_env_manager()
    browser_name = env_mgr.get_browser_type()
    headless = bool(request.config.getoption("--headless", default=False))

    with sync_playwright() as playwright:
        browser_launcher = getattr(playwright, browser_name)
        browser = browser_launcher.launch(headless=headless)
        context = browser.new_context(
            storage_state=storage_state,
            locale="he-IL",
            timezone_id="Asia/Jerusalem",
        )
        page = context.new_page()
        from refua_tests.pages.common.pop_up_info import PopUpInfo

        # Early install so PWA overlay is handled even before page objects exist.
        PopUpInfo.install_auto_dismiss(page)
        yield page
        context.close()
        browser.close()


def pytest_configure(config):
    """Set TEST_ENV from environment if not already set."""
    if not os.getenv("TEST_ENV"):
        # Default to 'test' environment if not specified
        os.environ["TEST_ENV"] = "test"
