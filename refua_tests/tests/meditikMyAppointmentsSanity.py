"""
Meditik My Appointments (התורים שלי) — tabbed /zimun-torim screen.

Implements the 13 "Ready" cases from the My Appointments workbook
(APPT-001..034; see docs/setup/MY_APPOINTMENTS_CASES.json for every column).
The remaining 21 cases are registered as skipped/pending in
test_my_appointments_pending.py — each needs Product/Security/API/
Accessibility/Non-Functional confirmation that is not yet available (see the
workbook's Clarification Status column).

Strategy (same standard as the My Requests suite):
  Login once via the pre-captured auth-state. Generic list/panel/card/widget
  checks never seed or delete appointments — they detect whichever single
  branch (populated or scoped-empty) is currently live and validate that
  branch, via MyAppointmentsTabbedPage.assert_panel_data_state().

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikMyAppointmentsSanity.py -v
"""

import pytest

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.myAppointmentsTabbedPage import (DEFAULT_TAB_KEY,
                                                        MyAppointmentsTabbedPage)


@pytest.fixture(scope="class")
def my_appointments_page(app_session):
    page = app_session.ensure_page()
    shell = MeditekBasePage(page)
    shell.open_home()
    shell.ensure_logged_in()
    shell.dismiss_blocking_dialogs()
    yield page


@pytest.fixture(autouse=True)
def _return_home_after(my_appointments_page):
    # Re-install per test; navigations can unmount the previous page's handler.
    PopUpInfo.install_auto_dismiss(my_appointments_page)
    PopUpInfo(my_appointments_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(my_appointments_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[my_appointments] return_to_home failed: {error}")


@pytest.mark.meditik
@pytest.mark.my_appointments
class MeditikMyAppointmentsSanity:
    """The 13 Ready APPT cases against the tabbed /zimun-torim screen."""

    # APPT-001 — Open My Appointments from Home
    def test_open_my_appointments_from_home(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page)
        appts.open_from_home_widget()
        appts.wait_until_loaded()

    # APPT-002 — Render My Appointments page shell
    def test_page_shell_renders(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page).open_direct()
        appts.wait_until_loaded()
        appts.assert_page_shell()

    # APPT-003/004/005 — Display Upcoming / Waiting Lists / Past tab
    @pytest.mark.parametrize(
        "tab_key",
        [
            pytest.param("upcoming", id="APPT-003"),
            pytest.param("waiting_lists", id="APPT-004"),
            pytest.param("past", id="APPT-005"),
        ],
    )
    def test_tab_displays_valid_data_state(self, my_appointments_page, tab_key):
        appts = MyAppointmentsTabbedPage(my_appointments_page).open_direct()
        appts.wait_until_loaded()
        appts.activate_tab(tab_key)
        appts.assert_only_panel_active(tab_key)
        appts.assert_tab_selected(tab_key)
        appts.assert_panel_data_state(tab_key)

    # APPT-006 — Show Upcoming Appointments as the default context
    def test_default_tab_is_upcoming(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page).open_direct()
        appts.wait_until_loaded()
        appts.assert_only_panel_active(DEFAULT_TAB_KEY)
        appts.assert_tab_selected(DEFAULT_TAB_KEY)
        appts.assert_panel_data_state(DEFAULT_TAB_KEY)

    # APPT-007 — Validate past appointment cards when present
    def test_past_appointment_cards_validated_when_present(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page).open_direct()
        appts.wait_until_loaded()
        appts.activate_tab("past")
        state = appts.assert_panel_data_state("past")
        if state.has_records:
            testids = appts.card_testids("past")
            assert len(testids) == len(set(testids)), (
                f"Past appointment cards must be uniquely located: {testids!r}"
            )

    # APPT-011 — Return to Home using the navbar logo
    def test_return_home_via_logo(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page).open_direct()
        appts.wait_until_loaded()
        appts.return_home_via_logo()

    # APPT-013 — Display the Home appointment widget in its current state
    def test_home_widget_data_state(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page)
        appts.assert_widget_data_state()

    # APPT-022 — Keep the final tab active during rapid switching
    def test_rapid_tab_switching_keeps_final_tab_active(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page).open_direct()
        appts.wait_until_loaded()
        appts.rapid_switch(["upcoming", "waiting_lists", "past", "upcoming"])

    # APPT-023 — Validate every appointment category in its current state
    def test_every_category_validated_in_current_data_state(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page).open_direct()
        appts.wait_until_loaded()
        appts.assert_all_categories_valid()

    # APPT-028 — Render Hebrew RTL in the current data state
    def test_hebrew_rtl_rendering(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page).open_direct()
        appts.wait_until_loaded()
        appts.assert_hebrew_rtl_rendering()

    # APPT-032 — Navigate from the Home widget to My Appointments in any state
    def test_home_widget_navigates_to_my_appointments(self, my_appointments_page):
        appts = MyAppointmentsTabbedPage(my_appointments_page)
        appts.open_from_home_widget()
        appts.wait_until_loaded()
        appts.assert_panel_data_state(DEFAULT_TAB_KEY)
