"""
Sanity: כל הפעולות tiles → request form pages load with key objects.

Does not submit forms — only open + verify URL / title / critical fields.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/test_meditik_request_forms_sanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright

from refua_core.config.environment import get_env_manager

from refua_tests.pages.automation_ids import MeditikIds as Ids
from refua_tests.pages.common.pop_up_info import PopUpInfo
from refua_tests.pages.meditek_base_page import MeditekBasePage
from refua_tests.pages.request_forms import REQUEST_FORMS, RequestFormPage, RequestFormSpec
from refua_tests.pages.speed_dial import SpeedDial


@pytest.fixture(scope="class")
def forms_page(auth_state_session, request):
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
def _back_to_all_actions_or_home(forms_page):
    PopUpInfo.install_auto_dismiss(forms_page)
    PopUpInfo(forms_page).dismiss_if_present()
    yield
    shell = MeditekBasePage(forms_page)
    try:
        shell.dismiss_blocking_dialogs()
        if "torim." in forms_page.url:
            shell.return_to_home()
            return
        shell.close_menu()
        shell.go_to_all_actions()
        forms_page.wait_for_url("**/all-actions**", timeout=30000)
        shell.close_menu()
        shell.dismiss_blocking_dialogs()
    except Exception:
        try:
            shell.return_to_home()
            shell.close_menu()
            shell.dismiss_blocking_dialogs()
        except Exception as error:
            print(f"[request_forms] teardown failed: {error}")


@pytest.mark.smoke
@pytest.mark.ui
class TestMeditikRequestFormsSanity:
    """Open each known request form from כל הפעולות and assert objects loaded."""

    @pytest.mark.parametrize("spec", REQUEST_FORMS, ids=lambda s: s.path.strip("/"))
    def test_request_form_opens_from_all_actions(self, forms_page, spec: RequestFormSpec):
        RequestFormPage(forms_page, spec).run_sanity_from_all_actions(session_ready=True)

    def test_urgent_care_from_all_actions(self, forms_page):
        page = forms_page
        shell = MeditekBasePage(page)
        shell.go_to_all_actions()
        shell.close_menu()
        tile = page.locator("button").filter(has_text="רפואה דחופה").first
        tile.scroll_into_view_if_needed()
        tile.click(force=True)
        page.wait_for_url("**/urgent-care**", timeout=60000)
        shell.close_menu()
        shell.wait_for_loading_done()
        shell.assert_no_app_error(context="רפואה דחופה")
        body = shell._body_text(timeout=10000)
        assert "דף זה לא נמצא" not in body
        assert "רפואה דחופה" in body or "פניה לרפואה דחופה" in body, (
            f"Urgent care content missing. Body snip: {body[:250]!r}"
        )

    def test_speed_dial_opens_prescription_form(self, forms_page):
        """Speed dial → בקשה למרשם lands on prescription form with key objects."""
        page = forms_page
        shell = MeditekBasePage(page)
        shell.return_to_home()
        shell.close_menu()
        dial = SpeedDial(page)
        dial.open()
        action = page.get_by_test_id(Ids.SPEED_DIAL_PRESCRIPTION)
        action.wait_for(state="attached", timeout=10000)
        # MUI speed-dial actions can sit outside the viewport; DOM click is reliable.
        action.evaluate("el => el.click()")
        page.wait_for_url(
            "**/prescription-request**",
            timeout=60000,
            wait_until="domcontentloaded",
        )
        shell.close_menu()
        dial.close()
        shell.wait_for_loading_done()
        spec = next(s for s in REQUEST_FORMS if s.path == "/prescription-request")
        form = RequestFormPage(page, spec)
        form._wait_for_form_shell()
        form.assert_form_loaded()
