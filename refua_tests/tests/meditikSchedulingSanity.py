"""
Meditik Appointment Scheduling — /zimun-torim tabbed screen.

Implements the 8 "Ready" cases from the MediTik Appointment Scheduling BDD/E2E
workbook (APPOINTMENTS-001..030; see docs/setup/SCHEDULING_CASES.json for every
column). The remaining 22 cases are registered as skipped/pending in
test_scheduling_pending.py.

IMPORTANT — this workbook specs the SAME screen as the earlier My Appointments
workbook (APPT-001..034): identical route (/zimun-torim), identical tabs
(active-requests-tab / waiting-lists-tab / past-appointments-tab) and panels.
The two workbooks are overlapping specifications of one screen, so this suite
deliberately REUSES MyAppointmentsTabbedPage instead of duplicating a page
object. Where this workbook goes further than the earlier one — explicit
empty-state coverage per panel, the Past-Appointments filter control, the
indexed past card plus its location/extra-info card — those helpers were added
to that same page object.

Standards carried over from the previous suites:
  * data-testid is the hard check; undefined copy is never asserted.
  * Nothing is seeded or deleted. Cases whose Given requires specific data
    (a past appointment exists; the user has no upcoming appointments) assert
    when that state is genuinely live and skip with a clear reason otherwise.
  * Shared empty-state testids are scoped to the active panel and must resolve
    to exactly one match (APPOINTMENTS-014).

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikSchedulingSanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright
from refua_core.config.environment import get_env_manager

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.myAppointmentsTabbedPage import (APPOINTMENT_TABS,
                                                        MyAppointmentsTabbedPage)


@pytest.fixture(scope="class")
def scheduling_page(auth_state_session, request):
    # One browser context shared across the class — avoids re-login per test.
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
        PopUpInfo.install_auto_dismiss(page)
        shell = MeditekBasePage(page)
        shell.open_home()
        shell.ensure_logged_in()
        shell.dismiss_blocking_dialogs()
        yield page
        context.close()
        browser.close()


@pytest.fixture(autouse=True)
def _return_home_after(scheduling_page):
    PopUpInfo.install_auto_dismiss(scheduling_page)
    PopUpInfo(scheduling_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(scheduling_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[scheduling] return_to_home failed: {error}")


def _open_scheduling(page) -> MyAppointmentsTabbedPage:
    scheduling = MyAppointmentsTabbedPage(page).open_direct()
    scheduling.wait_until_loaded()
    return scheduling


def _skip_unless_empty(scheduling, tab_key: str, case_id: str, what: str):
    """Empty-state cases need a zero-record category; never seed one."""
    title = scheduling.scoped_empty_title(tab_key)
    if title.count() == 0 or not title.first.is_visible():
        pytest.skip(
            f"{case_id}: the {tab_key} category currently holds {what} in this "
            f"environment, and the suite does not seed or delete appointment "
            f"data. Re-run with an account that has none."
        )


@pytest.mark.meditik
@pytest.mark.scheduling
class MeditikSchedulingSanity:
    """The 8 Ready APPOINTMENTS cases against the /zimun-torim screen."""

    # APPOINTMENTS-001 — Load Appointment Scheduling
    def test_scheduling_page_loads_with_all_tabs(self, scheduling_page):
        scheduling = _open_scheduling(scheduling_page)
        scheduling.assert_page_shell()
        # All three appointment tabs displayed (the workbook's core assertion).
        for tab in APPOINTMENT_TABS.values():
            tab_el = scheduling_page.get_by_test_id(tab.tab_test_id)
            assert tab_el.count() > 0 and tab_el.first.is_visible(), (
                f"Appointment tab {tab.tab_test_id} is not displayed"
            )

    # APPOINTMENTS-002/003 — Open Upcoming / Waiting Lists
    @pytest.mark.parametrize(
        "tab_key",
        [
            pytest.param("upcoming", id="APPOINTMENTS-002"),
            pytest.param("waiting_lists", id="APPOINTMENTS-003"),
        ],
    )
    def test_appointment_tab_is_active_panel(self, scheduling_page, tab_key):
        scheduling = _open_scheduling(scheduling_page)
        scheduling.activate_tab(tab_key)
        scheduling.assert_only_panel_active(tab_key)

    # APPOINTMENTS-004 — Open Past Appointments (filter, card, location, link)
    def test_past_appointments_panel_controls_and_card(self, scheduling_page):
        scheduling = _open_scheduling(scheduling_page)
        scheduling.activate_tab("past")
        scheduling.assert_only_panel_active("past")
        # Filter control and booking link are data-independent.
        scheduling.assert_past_panel_controls()
        # The card + location assertions require the workbook's Given
        # ("a past appointment exists"); never seed one.
        if scheduling.past_card(0).count() == 0:
            pytest.skip(
                "APPOINTMENTS-004: no past appointment exists for this account, "
                "so the card and location assertions cannot run. The filter "
                "control and booking link were verified. Re-run with an account "
                "that has appointment history."
            )
        scheduling.assert_past_card_with_location(0)

    # APPOINTMENTS-011 — Upcoming Appointments empty state (icon + title)
    def test_upcoming_empty_state(self, scheduling_page):
        scheduling = _open_scheduling(scheduling_page)
        scheduling.activate_tab("upcoming")
        _skip_unless_empty(
            scheduling, "upcoming", "APPOINTMENTS-011", "upcoming appointments"
        )
        scheduling.assert_scoped_empty_state("upcoming", require_icon=True)

    # APPOINTMENTS-012 — Waiting Lists empty state (title only per the workbook)
    def test_waiting_lists_empty_state(self, scheduling_page):
        scheduling = _open_scheduling(scheduling_page)
        scheduling.activate_tab("waiting_lists")
        _skip_unless_empty(
            scheduling, "waiting_lists", "APPOINTMENTS-012", "waiting-list entries"
        )
        scheduling.assert_scoped_empty_state("waiting_lists", require_icon=False)

    # APPOINTMENTS-014 — Panel-scoped shared empty-state title
    def test_shared_empty_state_title_is_panel_scoped(self, scheduling_page):
        scheduling = _open_scheduling(scheduling_page)
        scheduling.assert_shared_empty_state_scoping(["upcoming", "waiting_lists"])

    # APPOINTMENTS-017 — Complete appointment category navigation
    def test_complete_category_navigation(self, scheduling_page):
        scheduling = _open_scheduling(scheduling_page)
        for tab_key in APPOINTMENT_TABS:
            scheduling.activate_tab(tab_key)
            scheduling.assert_only_panel_active(tab_key)
            # Category-correct data: whichever branch is live must be coherent.
            scheduling.assert_panel_data_state(tab_key)
