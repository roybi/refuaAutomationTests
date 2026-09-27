"""
Meditik Vaccinations (חיסונים) — /vaccinations module page.

Implements the 4 "Ready" cases from the Vaccinations workbook
(VACC-001..020; see docs/setup/VACCINATIONS_CASES.json for every column). The
remaining 16 cases are registered as skipped/pending in
test_vaccinations_pending.py — each needs UX/Security/API/Product/
Business-Rule confirmation that is not yet available.

This workbook is a case-for-case twin of Sick_days, so the page object is a
configuration of the shared EmptyStateModulePage rather than a separate
implementation. Two carried-over rules:
  * The workbook fails on a MISSING, DUPLICATED or HIDDEN element, so the
    assertions check uniqueness (exactly one match), not merely visibility.
  * VACC-002 pins the exact Hebrew copy and requires failing when the text
    differs, so that string is asserted HARD.

All four Ready cases describe the EMPTY state, so each skips with a clear reason
if the account actually holds vaccination records; nothing is seeded or deleted.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikVaccinationsSanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright
from refua_core.config.environment import get_env_manager

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.vaccinationsModulePage import VaccinationsModulePage


@pytest.fixture(scope="class")
def vaccinations_page(auth_state_session, request):
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
def _return_home_after(vaccinations_page):
    PopUpInfo.install_auto_dismiss(vaccinations_page)
    PopUpInfo(vaccinations_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(vaccinations_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[vaccinations] return_to_home failed: {error}")


def _open_vaccinations(page) -> VaccinationsModulePage:
    vaccinations = VaccinationsModulePage(page).open_direct()
    vaccinations.wait_until_loaded()
    return vaccinations


def _skip_unless_empty(vaccinations, case_id: str):
    """Every Ready case describes the empty state; never seed or delete data."""
    if not vaccinations.inspect().empty_state_visible:
        pytest.skip(
            f"{case_id}: this account currently holds vaccination records, so "
            f"the empty-state assertions cannot run. The suite does not seed or "
            f"delete data — re-run with an account that has no vaccinations."
        )


@pytest.mark.meditik
@pytest.mark.vaccinations
class MeditikVaccinationsSanity:
    """The 4 Ready VACC cases against the /vaccinations page."""

    # VACC-001 — Open the Vaccinations page successfully
    def test_vaccinations_page_opens(self, vaccinations_page):
        vaccinations = _open_vaccinations(vaccinations_page)
        _skip_unless_empty(vaccinations, "VACC-001")
        vaccinations.assert_page_shell()

    # VACC-002 — Exact empty-state text (hard Hebrew assertion)
    def test_vaccinations_empty_state_text_is_exact(self, vaccinations_page):
        vaccinations = _open_vaccinations(vaccinations_page)
        _skip_unless_empty(vaccinations, "VACC-002")
        vaccinations.assert_empty_state_text()

    # VACC-003 — Exactly one visible empty-state icon, image loaded
    def test_vaccinations_empty_state_icon(self, vaccinations_page):
        vaccinations = _open_vaccinations(vaccinations_page)
        _skip_unless_empty(vaccinations, "VACC-003")
        vaccinations.assert_empty_state_icon()

    # VACC-014 — Refresh keeps one route and one empty state
    def test_vaccinations_survives_refresh(self, vaccinations_page):
        vaccinations = _open_vaccinations(vaccinations_page)
        _skip_unless_empty(vaccinations, "VACC-014")
        vaccinations.refresh()
        vaccinations.assert_single_page_instance()
        # The copy must still be correct after the reload.
        vaccinations.assert_empty_state_text()
