import pytest
from playwright.sync_api import expect
from refua_core.pages.home_Page import homePage

# Helpers already implemented in conftest.py:
#   _auth_state_path()      -> Path from TEST_AUTH_STATE_FILE (.env.test)
#   _auth_state_is_valid()  -> file exists, parses, not expired, app-host URL
#   _capture_auth_state()   -> runs capture_session.py (manual login + 2FA)
from refua_tests.tests.conftest import (
    _auth_state_is_valid,
    _auth_state_path,
    _capture_auth_state,
)


# This fixture acts as a beforeAll and afterAll hook
@pytest.fixture(scope="module", autouse=True)
def before_all_after_all():
    # --- BEFORE ALL CODE GOES HERE ---
    print("\n[Setup] This runs ONCE before all tests in the module")

    auth_state_path = _auth_state_path()
    print(f"[Setup] Validating capture_session JSON: {auth_state_path}")

    if _auth_state_is_valid(auth_state_path):
        print("[Setup] JSON is valid — tests will reuse the captured session")
    else:
        print("[Setup] JSON is missing/expired/invalid — running capture_session.py")
        _capture_auth_state()

        if not _auth_state_is_valid(auth_state_path):
            pytest.exit(
                f"capture_session.py ran but {auth_state_path} is still invalid — "
                "finish the login flow (credentials + 2FA) and run pytest again.",
                returncode=1,
            )
        print("[Setup] New session captured and validated")

    yield  # The tests run while this yield is active

    # --- AFTER ALL CODE GOES HERE ---
    print("\n[Teardown] This runs ONCE after all tests in the module")

    if not _auth_state_is_valid(auth_state_path):
        print(
            f"[Teardown] WARNING: {auth_state_path} is no longer valid "
            "(likely expired during the run) — next run will recapture it."
        )


# SpeedDial label rendered only on the logged-in MEDITEK dashboard
DASHBOARD_QUICK_ACTIONS = "פעולות מהירות"


def test_open_app_with_captured_session(browser_page):
    """Open /home with the captured session and reach the app without 2FA.

    Handles both known outcomes:
    1. MSAL picks up the stored tokens and signs in silently — dashboard.
    2. The login page appears — clicking התחברות must SSO into the app
       without a 2FA prompt.
    """
    browser_page.goto(homePage.PAGE_URL)
    home = homePage(browser_page)

    login_button = browser_page.locator("#login-button")
    dashboard = browser_page.get_by_text(DASHBOARD_QUICK_ACTIONS).first

    # Wait until the app settles on one of the two known states
    expect(login_button.or_(dashboard).first).to_be_visible(timeout=60000)

    if login_button.is_visible():
        home.close_pwa_dialog()
        expect(login_button).to_be_enabled()
        expect(login_button).to_contain_text("התחברות")
        home.click_login()

    # Either path must end authenticated in the app, never on a 2FA page
    expect(dashboard).to_be_visible(timeout=60000)
    assert "microsoftonline" not in browser_page.url, (
        f"Ended on a Microsoft login/2FA page instead of the app: {browser_page.url}"
    )
