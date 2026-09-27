"""
Meditik Medicines & Prescriptions (תרופות ומרשמים) — tabbed /medicines screen.

Implements the 6 "Ready" cases from the MediTik Medicines & Prescriptions
BDD/E2E workbook (MEDICINES-001..024; see docs/setup/MEDICINES_CASES.json for
every column). The remaining 18 cases are registered as skipped/pending in
test_medicines_pending.py — each needs Security/API/UX/Business-Rule
confirmation that is not yet available (Clarification Status column).

Standards carried over from the My Requests / My Appointments / Referrals
suites:
  * data-testid is the hard check; undefined copy is never asserted.
  * Nothing is seeded or deleted. MEDICINES-009 asserts the scoped empty state
    when My Prescriptions is genuinely empty and skips with a clear reason when
    prescriptions exist.
  * Shared empty-state testids are scoped to the active panel and must resolve
    to exactly one match (MEDICINES-024).

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikMedicinesSanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright
from refua_core.config.environment import get_env_manager

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.medicinesTabbedPage import (DEFAULT_TAB_KEY,
                                                   MEDICINE_TABS,
                                                   MedicinesTabbedPage)
from refua_tests.pages.meditikBasePage import MeditekBasePage


@pytest.fixture(scope="class")
def medicines_page(auth_state_session, request):
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
def _return_home_after(medicines_page):
    PopUpInfo.install_auto_dismiss(medicines_page)
    PopUpInfo(medicines_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(medicines_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[medicines] return_to_home failed: {error}")


@pytest.mark.meditik
@pytest.mark.medicines
class MeditikMedicinesSanity:
    """The 6 Ready MEDICINES cases against the tabbed /medicines screen."""

    # MEDICINES-001 — Load the Medicines & Prescriptions page
    def test_medicines_page_loads_with_all_tabs(self, medicines_page):
        medicines = MedicinesTabbedPage(medicines_page).open_direct()
        medicines.wait_until_loaded()
        medicines.assert_page_shell()

    # MEDICINES-002/003/004 — Open each medicine category
    @pytest.mark.parametrize(
        "tab_key",
        [
            pytest.param("active", id="MEDICINES-002"),
            pytest.param("permanent", id="MEDICINES-003"),
            pytest.param("expired", id="MEDICINES-004"),
        ],
    )
    def test_medicine_tab_is_active_content(self, medicines_page, tab_key):
        medicines = MedicinesTabbedPage(medicines_page).open_direct()
        medicines.wait_until_loaded()
        medicines.activate_tab(tab_key)
        medicines.assert_panel_is_active_content(tab_key)

    # MEDICINES-009 — My Prescriptions empty state (icon + title, panel-scoped)
    def test_my_prescriptions_empty_state(self, medicines_page):
        medicines = MedicinesTabbedPage(medicines_page).open_direct()
        medicines.wait_until_loaded()
        medicines.activate_tab(DEFAULT_TAB_KEY)
        state = medicines.inspect_panel(DEFAULT_TAB_KEY)
        if not state.empty_state_visible:
            pytest.skip(
                "MEDICINES-009: My Prescriptions currently holds active "
                "prescriptions in this environment, and the suite does not seed "
                "or delete medicine data. Re-run with an account that has no "
                "active prescriptions."
            )
        medicines.assert_scoped_empty_state(DEFAULT_TAB_KEY)

    # MEDICINES-014 — E2E medicine category navigation
    def test_navigate_through_all_medicine_categories(self, medicines_page):
        medicines = MedicinesTabbedPage(medicines_page).open_direct()
        medicines.wait_until_loaded()
        medicines.walk_all_categories()
        assert set(MEDICINE_TABS) == {"active", "permanent", "expired"}
        # Leave a predictable state on the default category.
        medicines.activate_tab(DEFAULT_TAB_KEY)
        medicines.assert_panel_is_active_content(DEFAULT_TAB_KEY)
