"""
Meditik home + speed-dial + widget sanity (beyond side-menu suite).

Strategy:
  Login once via pre-captured auth-state. Tests verify the home dashboard
  in isolation: widgets are rendered, CTAs navigate correctly, the last-update
  timestamp updates on click, and the speed-dial FAB appears on every major
  content screen with the correct action buttons.

Coverage:
  - Dashboard widget presence and navigation
  - Send-doctor-request CTA
  - Last-update-time interaction
  - Speed-dial on: user-requests, zimun-torim, medicines, referrals, lab-results, sick-days

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikHomeAndActionsSanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright
from refua_core.config.environment import get_env_manager

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.meditikHomePage import MeditekHomePage
from refua_tests.pages.speedDial import SPEED_DIAL_BY_PATH, SpeedDial


@pytest.fixture(scope="class")
def home_actions_page(auth_state_session, request):
    # One browser context shared across the class — avoids re-login overhead for each test.
    with auth_state_session.open("r", encoding="utf-8") as auth_state:
        session_data = json.load(auth_state)
    # Unwrap the "storage_state" key so Playwright picks up the cookies and MSAL tokens.
    storage_state = session_data.get("storage_state", session_data)

    env_mgr = get_env_manager()
    browser_name = env_mgr.get_browser_type()
    headless = bool(request.config.getoption("--headless", default=False))

    with sync_playwright() as playwright:
        browser = getattr(playwright, browser_name).launch(headless=headless)
        context = browser.new_context(
            storage_state=storage_state,
            locale="he-IL",
            timezone_id="Asia/Jerusalem",
        )
        page = context.new_page()
        # Same as menu suite: install before any navigation.
        PopUpInfo.install_auto_dismiss(page)
        shell = MeditekBasePage(page)
        shell.open_home()
        shell.ensure_logged_in()
        shell.dismiss_blocking_dialogs()
        yield page
        context.close()
        browser.close()


@pytest.fixture(autouse=True)
def _return_home_after(home_actions_page):
    # Re-install before each test; navigations can unmount the handler registered on the previous page.
    PopUpInfo.install_auto_dismiss(home_actions_page)
    PopUpInfo(home_actions_page).dismiss_if_present()  # clear any leftover modal
    yield
    # Swallow errors so a teardown failure never obscures the actual test result.
    try:
        shell = MeditekBasePage(home_actions_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[home_actions] return_to_home failed: {error}")


@pytest.mark.smoke
@pytest.mark.ui
class MeditikHomeAndActionsSanity:
    """
    Home widgets, CTAs, and speed-dial actions (not side-menu).

    This class covers everything on the home screen that is NOT reached via
    the hamburger side-menu — that is covered by MeditikMenuSanity.
    All tests share one browser context; _return_home_after resets between them.
    """

    def test_home_widgets_present(self, home_actions_page):
        # Verifies that all expected dashboard widgets are rendered on the home page.
        MeditekHomePage(home_actions_page).assert_widgets_present()

    def test_home_speed_dial_actions(self, home_actions_page):
        # Verifies the speed-dial FAB is present and all expected action buttons are listed.
        MeditekHomePage(home_actions_page).assert_speed_dial_actions()
        

    def test_home_cta_send_doctor_request(self, home_actions_page):
        # Clicks the “send request to doctor” CTA and verifies the form page loads.
        MeditekHomePage(home_actions_page).assert_send_doctor_request_cta()

    def test_home_last_update_time(self, home_actions_page):
        """זמן עדכון אחרון: click → stamp 'עודכן ב-…' appears."""
        MeditekHomePage(home_actions_page).assert_last_update_time()

    def test_home_widget_user_requests(self, home_actions_page):
        # Taps the “my requests” widget and confirms the page URL changes to the requests screen.
        MeditekHomePage(home_actions_page).assert_widget_navigates(
            Ids.HOME_BTN_USER_REQUESTS_WIDGET
        )

    def test_home_widget_appointments(self, home_actions_page):
        # Taps the “future appointments” widget and confirms navigation.
        MeditekHomePage(home_actions_page).assert_widget_navigates(
            Ids.HOME_BTN_FUTURE_APPOINTMENTS_WIDGET
        )

    def test_home_widget_referrals(self, home_actions_page):
        MeditekHomePage(home_actions_page).assert_widget_navigates(
            Ids.HOME_BTN_REFERRALS_WIDGET
        )

    def test_home_widget_medicines(self, home_actions_page):
        MeditekHomePage(home_actions_page).assert_widget_navigates(
            Ids.HOME_BTN_MEDICINES_WIDGET
        )

    def test_home_widget_exemptions(self, home_actions_page):
        MeditekHomePage(home_actions_page).assert_widget_navigates(
            Ids.HOME_BTN_EXEMPTIONS_WIDGET
        )

    @pytest.mark.parametrize(
        "path",
        [
            "/user-requests",
            "/zimun-torim",
            "/medicines",
            "/referrals",
            "/lab-results",
            "/sick-days",
        ],
    )
    def test_speed_dial_on_screen(self, home_actions_page, path):
        # Navigates directly to each content screen and asserts the speed-dial FAB and its actions are present.
        page = home_actions_page
        shell = MeditekBasePage(page)
        base = shell.home_url.rstrip("/")
        if base.endswith("/home"):
            base = base[: -len("/home")]

        def _load_and_check() -> SpeedDial:
            page.goto(f"{base}{path}", wait_until="domcontentloaded", timeout=60000)
            shell.dismiss_blocking_dialogs()
            page.wait_for_url(f"**{path}**", timeout=60000)
            shell.wait_for_loading_done()
            shell.assert_no_app_error(context=path)
            # Speed dial mounts after list content; brief wait avoids a race condition.
            page.wait_for_timeout(1000)
            return SpeedDial(page)

        dial = _load_and_check()
        if not dial.is_present(timeout=20000):
            # Retry once with a full reload — some screens delay FAB mount on first visit.
            page.reload(wait_until="domcontentloaded", timeout=60000)
            shell.dismiss_blocking_dialogs()
            shell.wait_for_loading_done()
            shell.assert_no_app_error(context=path)
            page.wait_for_timeout(1000)
            dial = SpeedDial(page)

        assert dial.is_present(timeout=30000), (
            f"Speed dial missing on {path} "
            f"(root #speed-dial / meditik-speed-dial-btn-trigger not in DOM). "
            f"URL={page.url}"
        )
        dial.assert_actions_present(SPEED_DIAL_BY_PATH[path])
        dial.close()
