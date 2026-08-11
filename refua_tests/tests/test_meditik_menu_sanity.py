"""
Meditik menu navigation sanity suite — one shared Chrome session.

Login once → for each screen: menu navigate → assert → return home → next.
Skips utility/admin items: feedback, מנהלן, חיילי דיבאג, install, share, logout.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/test_meditik_menu_sanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright

from refua_core.config.environment import get_env_manager

from refua_tests.pages.all_actions_page import AllActionsPage
from refua_tests.pages.common.pop_up_info import PopUpInfo
from refua_tests.pages.medical_profile_page import MedicalProfilePage
from refua_tests.pages.meditek_base_page import MeditekBasePage
from refua_tests.pages.menu_pages import (
    BookAppointmentPage,
    ExemptionsPage,
    LabResultsPage,
    MedicinesPage,
    ReferralsPage,
    SickDaysPage,
    UrgentCarePage,
    VaccinationsPage,
    VisitSummariesPage,
)
from refua_tests.pages.my_appointments_page import MyAppointmentsPage
from refua_tests.pages.my_requests_page import MyRequestsPage


@pytest.fixture(scope="class")
def menu_sanity_page(auth_state_session, request):
    """One Chromium context for the whole menu-sanity class."""
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
def _return_home_after_each(menu_sanity_page):
    """Keep the shared session on home between checks."""
    PopUpInfo.install_auto_dismiss(menu_sanity_page)
    PopUpInfo(menu_sanity_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(menu_sanity_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[menu_sanity] return_to_home failed: {error}")


@pytest.mark.smoke
@pytest.mark.ui
class TestMeditikMenuSanity:
    """Shared-session sanity for every side-menu content screen."""

    def test_meditik_navigation_ZimunTor(self, menu_sanity_page):
        BookAppointmentPage(menu_sanity_page).run_menu_sanity(session_ready=True)

    def test_meditik_navigationToShlihatBakashaLeRofe(self, menu_sanity_page):
        AllActionsPage(menu_sanity_page).run_menu_sanity(session_ready=True)

    def test_meditik_navigation_RefuaDchufa(self, menu_sanity_page):
        UrgentCarePage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_URGENT_CARE, session_ready=True
        )

    def test_meditik_navigation_ATorimSheli(self, menu_sanity_page):
        MyAppointmentsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_MY_APPOINTMENTS, session_ready=True
        )

    def test_meditik_navigation_HaBakashotSheli(self, menu_sanity_page):
        MyRequestsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_MY_REQUESTS, session_ready=True
        )

    def test_meditik_navigation_TotzaotBdikot(self, menu_sanity_page):
        LabResultsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_LAB_RESULTS, session_ready=True
        )

    def test_meditik_navigation_TrufotVeMirshamim(self, menu_sanity_page):
        MedicinesPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_MEDICINES, session_ready=True
        )

    def test_meditik_navigation_SikumeiBikur(self, menu_sanity_page):
        VisitSummariesPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_VISIT_SUMMARIES, session_ready=True
        )

    def test_meditik_navigation_Pturim(self, menu_sanity_page):
        ExemptionsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_EXEMPTIONS, session_ready=True
        )

    def test_meditik_navigation_YemeiMachala(self, menu_sanity_page):
        SickDaysPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_SICK_DAYS, session_ready=True
        )

    def test_meditik_navigation_Hapniyot(self, menu_sanity_page):
        ReferralsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_REFERRALS, session_ready=True
        )

    def test_meditik_navigation_Hisunim(self, menu_sanity_page):
        VaccinationsPage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_VACCINATIONS, session_ready=True
        )

    def test_meditik_navigationToProfilRefui(self, menu_sanity_page):
        MedicalProfilePage(menu_sanity_page).run_menu_sanity(
            MeditekBasePage.MENU_MEDICAL_PROFILE, session_ready=True
        )
