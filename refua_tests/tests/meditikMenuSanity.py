"""
Meditik menu navigation sanity suite — one shared Chrome session.

Strategy:
  Login once via the pre-captured auth-state file (bypasses Microsoft 2FA).
  For each side-menu screen:
    1. Open the hamburger menu.
    2. Click the target item.
    3. Assert the page title, URL and list/card content loaded.
    4. Return to /home for the next test.

Skips utility/admin items that open external flows or require special roles:
    מנהלן, חיילי דיבאג, install, share, logout.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikMenuSanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright
from refua_core.config.environment import get_env_manager

from refua_tests.pages.allActionsPage import AllActionsPage
from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.medicalProfilePage import MedicalProfilePage
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.menuPages import (BookAppointmentPage, ExemptionsPage,
                                         FeedbackPage, LabResultsPage,
                                         MedicinesPage, ReferralsPage,
                                         SickDaysPage, UrgentCarePage,
                                         VaccinationsPage, VisitSummariesPage)
from refua_tests.pages.myAppointmentsPage import MyAppointmentsPage
from refua_tests.pages.myRequestsPage import MyRequestsPage


@pytest.fixture(scope="class")
def menu_sanity_page(auth_state_session, request):
    """One Chromium context for the whole menu-sanity class."""
    # scope="class" means one browser/context is shared across all 14 tests — faster than opening a new browser per test.
    with auth_state_session.open("r", encoding="utf-8") as auth_state:
        session_data = json.load(auth_state)
    # The session file wraps Playwright's storage under "storage_state"; unwrap so cookies/MSAL tokens load correctly.
    storage_state = session_data.get("storage_state", session_data)

    env_mgr = get_env_manager()
    browser_name = env_mgr.get_browser_type()
    headless = bool(request.config.getoption("--headless", default=False))

    with sync_playwright() as playwright:
        browser = getattr(playwright, browser_name).launch(headless=headless)
        context = browser.new_context(
            storage_state=storage_state,
            locale="he-IL",       # ensures Hebrew RTL layout matches production
            timezone_id="Asia/Jerusalem",
        )
        page = context.new_page()
        # Install before any navigation so the PWA install banner is dismissed automatically.
        PopUpInfo.install_auto_dismiss(page)
        shell = MeditekBasePage(page)
        shell.open_home()
        shell.ensure_logged_in()  # verifies MSAL tokens worked; triggers re-login if the session expired
        shell.dismiss_blocking_dialogs()

        yield page

        context.close()
        browser.close()


@pytest.fixture(autouse=True)
def _return_home_after_each(menu_sanity_page):
    """Keep the shared session on home between checks."""
    # Re-install on each test because some navigations leave the page without the handler.
    PopUpInfo.install_auto_dismiss(menu_sanity_page)
    PopUpInfo(menu_sanity_page).dismiss_if_present()  # clear any leftover modal before the test begins
    yield
    # Teardown: always try to return home so the next test starts from a clean state.
    # Errors are swallowed intentionally — a teardown failure should not mask the test result.
    try:
        shell = MeditekBasePage(menu_sanity_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[menu_sanity] return_to_home failed: {error}")


@pytest.mark.smoke
@pytest.mark.ui
class MeditikMenuSanity:
    """
    Shared-session sanity for every side-menu content screen.

    All tests in this class share one browser context (scope="class").
    Each test navigates to its screen, asserts content loaded correctly,
    and relies on the _return_home_after_each fixture to reset state.
    Failures here indicate either a navigation regression or a backend data issue.
    """

    # session_ready=True tells each page object to skip its own browser setup — the shared page is already on home.

    def test_meditik_navigation_ZimunTor(self, menu_sanity_page):
        # זימון תור: opens the appointment booking flow (redirects to external booking host).
        BookAppointmentPage(menu_sanity_page).run_menu_sanity(session_ready=True)

    def test_meditik_navigationToShlihatBakashaLeRofe(self, menu_sanity_page):
        # כל הפעולות: the "all actions" hub — every request-type tile must be visible.
        AllActionsPage(menu_sanity_page).run_menu_sanity(session_ready=True)

    def test_meditik_navigation_RefuaDchufa(self, menu_sanity_page):
        # רפואה דחופה: urgent care page must load without an app error banner.
        UrgentCarePage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_URGENT_CARE, session_ready=True
        )

    def test_meditik_navigation_ATorimSheli(self, menu_sanity_page):
        # תורים שלי: list of the patient’s upcoming appointments must render (list or empty-state).
        MyAppointmentsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_MY_APPOINTMENTS, session_ready=True
        )

    def test_meditik_navigation_HaBakashotSheli(self, menu_sanity_page):
        # הבקשות שלי: list of submitted requests must render (list or empty-state).
        MyRequestsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_MY_REQUESTS, session_ready=True
        )

    def test_meditik_navigation_TotzaotBdikot(self, menu_sanity_page):
        # תוצאות בדיקות: lab results list (or empty-state) must load without error.
        LabResultsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_LAB_RESULTS, session_ready=True
        )

    def test_meditik_navigation_TrufotVeMirshamim(self, menu_sanity_page):
        # תרופות ומרשמים: medicines/prescriptions list must render.
        MedicinesPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_MEDICINES, session_ready=True
        )

    def test_meditik_navigation_SikumeiBikur(self, menu_sanity_page):
        # סיכומי ביקור: visit summaries list must render.
        VisitSummariesPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_VISIT_SUMMARIES, session_ready=True
        )

    def test_meditik_navigation_Pturim(self, menu_sanity_page):
        # פטורים: exemptions list must render.
        ExemptionsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_EXEMPTIONS, session_ready=True
        )

    def test_meditik_navigation_YemeiMachala(self, menu_sanity_page):
        # ימי מחלה: sick-days list must render.
        SickDaysPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_SICK_DAYS, session_ready=True
        )

    def test_meditik_navigation_Hapniyot(self, menu_sanity_page):
        # הפניות: referrals list must render.
        ReferralsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_REFERRALS, session_ready=True
        )

    def test_meditik_navigation_Hisunim(self, menu_sanity_page):
        # חיסונים: vaccinations list must render; an app error banner here indicates a backend failure.
        VaccinationsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_VACCINATIONS, session_ready=True
        )

    def test_meditik_navigationToProfilRefui(self, menu_sanity_page):
        # פרופיל רפואי: medical profile must load; the page uses a card layout, not a list.
        MedicalProfilePage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_MEDICAL_PROFILE, session_ready=True
        )

    def test_meditik_navigation_FeedbackButton(self, menu_sanity_page):
        # משוב: feedback modal must open from the side menu and display all required controls.
        FeedbackPage(menu_sanity_page).run_menu_sanity(session_ready=True)
