"""
Meditik My Requests (הבקשות שלי) — tabbed /user-requests screen.

Implements the 15 "Ready" cases from ``My_Requset_Test_cases.xlsx``
(MYREQ-001..031; see docs/setup/MY_REQUESTS_CASES.json for every column).
The remaining 16 cases are registered as skipped/pending in
test_my_requests_pending.py — each needs Product/Security/API/Accessibility/
Non-Functional confirmation not yet available (see the workbook's
Clarification Status column).

Strategy (per Requirements_Instructions INST-002/003/005/006):
  Login once via pre-captured auth-state. Generic list/panel/card/widget
  checks never seed or delete data — they detect whichever single branch
  (populated or scoped-empty) is currently live and validate that branch,
  via MyRequestsTabbedPage.assert_panel_data_state().

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikMyRequestsSanity.py -v
"""

import pytest

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.myRequestsTabbedPage import (DEFAULT_TAB_KEY,
                                                     MyRequestsTabbedPage)


@pytest.fixture(scope="class")
def my_requests_page(app_session):
    page = app_session.ensure_page()
    shell = MeditekBasePage(page)
    shell.open_home()
    shell.ensure_logged_in()
    shell.dismiss_blocking_dialogs()
    yield page


@pytest.fixture(autouse=True)
def _return_home_after(my_requests_page):
    # Re-install before each test; navigations can unmount the handler registered on the previous page.
    PopUpInfo.install_auto_dismiss(my_requests_page)
    PopUpInfo(my_requests_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(my_requests_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[my_requests] return_to_home failed: {error}")


@pytest.mark.meditik
@pytest.mark.my_requests
class MeditikMyRequestsSanity:
    """The 15 Ready MYREQ cases against the tabbed /user-requests screen."""

    # MYREQ-001 — Open My Requests from Home
    def test_open_my_requests_from_home(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page)
        tabbed.open_from_home_widget()
        tabbed.wait_until_loaded()

    # MYREQ-002 — Render My Requests page shell
    def test_page_shell_renders(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.assert_page_shell()

    # MYREQ-003/004/005 — Display New/Approved/Declined Requests tab
    @pytest.mark.parametrize(
        "tab_key",
        [
            pytest.param("active", id="MYREQ-003"),
            pytest.param("approved", id="MYREQ-004"),
            pytest.param("declined", id="MYREQ-005"),
        ],
    )
    def test_tab_displays_valid_data_state(self, my_requests_page, tab_key):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.activate_tab(tab_key)
        tabbed.assert_only_panel_active(tab_key)
        tabbed.assert_tab_selected(tab_key)
        tabbed.assert_panel_data_state(tab_key)

    # MYREQ-006 — Show New Requests as the default context
    def test_default_tab_is_new_requests(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.assert_only_panel_active(DEFAULT_TAB_KEY)
        tabbed.assert_tab_selected(DEFAULT_TAB_KEY)
        tabbed.assert_panel_data_state(DEFAULT_TAB_KEY)

    # MYREQ-007 — Validate request cards when present without requiring data
    def test_request_cards_validated_when_present(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.assert_panel_data_state(DEFAULT_TAB_KEY)

    # MYREQ-008 — Return to Home using the navbar logo
    def test_return_home_via_logo(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.return_home_via_logo()

    # MYREQ-010/011 — Validate Approved/Declined Requests content state
    @pytest.mark.parametrize(
        "tab_key",
        [
            pytest.param("approved", id="MYREQ-010"),
            pytest.param("declined", id="MYREQ-011"),
        ],
    )
    def test_panel_content_state_without_assumed_data(self, my_requests_page, tab_key):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.activate_tab(tab_key)
        tabbed.assert_panel_data_state(tab_key)

    # MYREQ-018 — Keep final tab active during rapid switching
    def test_rapid_tab_switching_keeps_final_tab_active(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.rapid_switch(["active", "approved", "declined", "active"])

    # MYREQ-019 — Validate each category in its current data state
    def test_each_category_validated_in_current_data_state(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.assert_all_categories_valid()

    # MYREQ-023 — Render Hebrew RTL in the current data state
    def test_hebrew_rtl_rendering(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page).open_direct()
        tabbed.wait_until_loaded()
        tabbed.assert_hebrew_rtl_rendering()

    # MYREQ-026 — Navigate from the Home widget to My Requests
    def test_home_widget_navigates_to_my_requests(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page)
        tabbed.open_from_home_widget()
        tabbed.wait_until_loaded()
        tabbed.assert_panel_data_state(DEFAULT_TAB_KEY)

    # MYREQ-030 — Display the My Requests widget in its current data state
    def test_home_widget_data_state(self, my_requests_page):
        tabbed = MyRequestsTabbedPage(my_requests_page)
        tabbed.assert_widget_data_state()
