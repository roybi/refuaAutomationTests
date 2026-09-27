"""
Meditik Referrals (הפניות) — tabbed /referrals screen.

Implements the 8 "Ready" cases from the MediTik Referrals BDD/E2E workbook
(REFERRALS-001..024; see docs/setup/REFERRALS_CASES.json for every column).
The remaining 16 cases are registered as skipped/pending in
test_referrals_pending.py — each needs Security/API/UX/Business-Rule
confirmation that is not yet available (Clarification Status column).

Standards carried over from the My Requests / My Appointments suites:
  * data-testid is the hard check; Hebrew/English copy differences are soft
    notes in Allure (the workbook's expected copy is English, the app Hebrew).
  * Nothing is seeded or deleted. The empty-state cases (REFERRALS-009/010/011)
    assert the scoped empty state when the account is genuinely empty and skip
    with a clear reason when records exist, rather than forcing data.
  * The shared empty-state testids are always scoped to the active panel
    (REFERRALS-024) and must resolve to exactly one match.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikReferralsSanity.py -v
"""

import json

import pytest
from playwright.sync_api import sync_playwright
from refua_core.config.environment import get_env_manager

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.referralsTabbedPage import (DEFAULT_TAB_KEY,
                                                   REFERRAL_TABS,
                                                   ReferralsTabbedPage)


@pytest.fixture(scope="class")
def referrals_page(auth_state_session, request):
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
def _return_home_after(referrals_page):
    PopUpInfo.install_auto_dismiss(referrals_page)
    PopUpInfo(referrals_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(referrals_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[referrals] return_to_home failed: {error}")


def _skip_unless_empty(referrals, tab_key: str, case_id: str):
    """Empty-state cases need a zero-record category; never seed one."""
    state = referrals.inspect_panel(tab_key)
    if not state.empty_state_visible:
        pytest.skip(
            f"{case_id}: the {tab_key} category currently holds records in this "
            f"environment, and the suite does not seed or delete referral data. "
            f"Re-run with an account that has no {tab_key} referrals."
        )
    return state


@pytest.mark.meditik
@pytest.mark.referrals
class MeditikReferralsSanity:
    """The 8 Ready REFERRALS cases against the tabbed /referrals screen."""

    # REFERRALS-001 — Successfully load the Referrals page
    def test_referrals_page_loads_with_all_tabs(self, referrals_page):
        referrals = ReferralsTabbedPage(referrals_page).open_direct()
        referrals.wait_until_loaded()
        referrals.assert_page_shell()

    # REFERRALS-002/003/004 — Display each referral category panel
    @pytest.mark.parametrize(
        "tab_key",
        [
            pytest.param("mine", id="REFERRALS-002"),
            pytest.param("waiting_approval", id="REFERRALS-003"),
            pytest.param("past", id="REFERRALS-004"),
        ],
    )
    def test_referral_tab_displays_its_panel(self, referrals_page, tab_key):
        referrals = ReferralsTabbedPage(referrals_page).open_direct()
        referrals.wait_until_loaded()
        referrals.activate_tab(tab_key)
        referrals.assert_panel_displayed(tab_key)

    # REFERRALS-009 — My Referrals empty state (icon + title, panel-scoped)
    def test_my_referrals_empty_state(self, referrals_page):
        referrals = ReferralsTabbedPage(referrals_page).open_direct()
        referrals.wait_until_loaded()
        referrals.activate_tab("mine")
        _skip_unless_empty(referrals, "mine", "REFERRALS-009")
        referrals.assert_scoped_empty_state("mine", require_icon=True)

    # REFERRALS-010/011 — Waiting-for-approval / Past empty-state titles
    @pytest.mark.parametrize(
        "tab_key",
        [
            pytest.param("waiting_approval", id="REFERRALS-010"),
            pytest.param("past", id="REFERRALS-011"),
        ],
    )
    def test_referral_category_empty_state_title(self, referrals_page, tab_key):
        referrals = ReferralsTabbedPage(referrals_page).open_direct()
        referrals.wait_until_loaded()
        referrals.activate_tab(tab_key)
        case_id = "REFERRALS-010" if tab_key == "waiting_approval" else "REFERRALS-011"
        _skip_unless_empty(referrals, tab_key, case_id)
        # The workbook specifies a title only (no icon) for these two cases.
        referrals.assert_scoped_empty_state(tab_key, require_icon=False)

    # REFERRALS-015 — E2E navigation through all referral states
    def test_navigate_through_all_referral_states(self, referrals_page):
        referrals = ReferralsTabbedPage(referrals_page).open_direct()
        referrals.wait_until_loaded()
        referrals.walk_all_categories()
        # Sanity: the walk covered every registered category.
        assert set(REFERRAL_TABS) == {"mine", "waiting_approval", "past"}
        referrals.assert_panel_displayed("past")
        # Return to the default category to leave a predictable state.
        referrals.activate_tab(DEFAULT_TAB_KEY)
        referrals.assert_panel_displayed(DEFAULT_TAB_KEY)
