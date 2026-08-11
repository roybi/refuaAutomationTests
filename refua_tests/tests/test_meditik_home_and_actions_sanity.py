"""
Meditik home + speed-dial + widget sanity (beyond side-menu suite).

Shared Chrome session: login once → home checks → widget navigations →
speed-dial on key screens → return home between steps.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/test_meditik_home_and_actions_sanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright

from refua_core.config.environment import get_env_manager

from refua_tests.pages.automation_ids import MeditikIds as Ids
from refua_tests.pages.common.pop_up_info import PopUpInfo
from refua_tests.pages.home_page_meditek import MeditekHomePage
from refua_tests.pages.meditek_base_page import MeditekBasePage
from refua_tests.pages.speed_dial import SPEED_DIAL_BY_PATH, SpeedDial


@pytest.fixture(scope="class")
def home_actions_page(auth_state_session, request):
    with auth_state_session.open("r", encoding="utf-8") as auth_state:
        session_data = json.load(auth_state)
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
    PopUpInfo.install_auto_dismiss(home_actions_page)
    PopUpInfo(home_actions_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(home_actions_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[home_actions] return_to_home failed: {error}")


@pytest.mark.smoke
@pytest.mark.ui
class TestMeditikHomeAndActionsSanity:
    """Home widgets, CTAs, and speed-dial actions (not side-menu)."""

    def test_home_widgets_present(self, home_actions_page):
        MeditekHomePage(home_actions_page).assert_widgets_present()

    def test_home_speed_dial_actions(self, home_actions_page):
        MeditekHomePage(home_actions_page).assert_speed_dial_actions()

    def test_home_cta_send_doctor_request(self, home_actions_page):
        MeditekHomePage(home_actions_page).assert_send_doctor_request_cta()

    def test_home_last_update_time(self, home_actions_page):
        """זמן עדכון אחרון: click → stamp 'עודכן ב-…' appears."""
        MeditekHomePage(home_actions_page).assert_last_update_time()

    def test_home_widget_user_requests(self, home_actions_page):
        MeditekHomePage(home_actions_page).assert_widget_navigates(
            Ids.HOME_BTN_USER_REQUESTS_WIDGET
        )

    def test_home_widget_appointments(self, home_actions_page):
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
            # Shell chrome (speed dial) often mounts after list content.
            page.wait_for_timeout(1000)
            return SpeedDial(page)

        dial = _load_and_check()
        if not dial.is_present(timeout=20000):
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
