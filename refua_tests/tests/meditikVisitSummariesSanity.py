"""
Meditik Visit Summaries (סיכומי ביקור) — /appointments module page.

Implements the 6 "Ready" cases from the Visit Summaries workbook
(VSUM-001..014; see docs/setup/VISIT_SUMMARIES_CASES.json for every column).
The remaining 8 cases are registered as skipped/pending in
test_visit_summaries_pending.py — each needs Security / API-Contract / UX /
Product / Business-Rule / Performance confirmation that is not yet available.

Shape
-----
This is the third instance of the non-tabbed empty-state module shape (after
Sick Days and Vaccinations), so the page object is a configuration of the
shared EmptyStateModulePage. Carried-over rules:
  * The validation columns reject a MISSING, DUPLICATED, HIDDEN or truncated
    element, so assertions check uniqueness, not merely visibility.
  * VSUM-003 pins the exact Hebrew copy and rejects a duplicate or truncated
    title, so that string is asserted HARD.

ROUTE WARNING: Visit Summaries is at /appointments, not /zimun-torim.

Five of the six Ready cases describe the EMPTY state, so each skips with a
clear reason if the account actually holds visit summaries; nothing is seeded or
deleted. VSUM-004 (quick actions) is data-independent and always runs.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikVisitSummariesSanity.py -v
"""

import allure
import pytest

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.visitSummariesModulePage import VisitSummariesModulePage


@pytest.fixture(scope="class")
def visit_summaries_page(app_session):
    page = app_session.ensure_page()
    shell = MeditekBasePage(page)
    shell.open_home()
    shell.ensure_logged_in()
    shell.dismiss_blocking_dialogs()
    yield page


@pytest.fixture(autouse=True)
def _return_home_after(visit_summaries_page):
    PopUpInfo.install_auto_dismiss(visit_summaries_page)
    PopUpInfo(visit_summaries_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(visit_summaries_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[visit-summaries] return_to_home failed: {error}")


def _open_visit_summaries(page) -> VisitSummariesModulePage:
    summaries = VisitSummariesModulePage(page).open_direct()
    summaries.wait_until_loaded()
    return summaries


def _skip_unless_empty(summaries, case_id: str):
    """The empty-state cases must not seed or delete data."""
    if not summaries.inspect().empty_state_visible:
        pytest.skip(
            f"{case_id}: this account currently holds visit summaries, so the "
            f"empty-state assertions cannot run. The suite does not seed or "
            f"delete data — re-run with an account that has no visit summaries."
        )


@allure.epic("Meditik")
@allure.feature("Visit Summaries")
@pytest.mark.meditik
@pytest.mark.visit_summaries
class MeditikVisitSummariesSanity:
    """The 6 Ready VSUM cases against the /appointments page."""

    # VSUM-001 — User can open the Visit Summaries page
    @allure.story("Open the Visit Summaries page")
    @allure.title("VSUM-001: the Visit Summaries page opens")
    def test_visit_summaries_page_opens(self, visit_summaries_page):
        summaries = _open_visit_summaries(visit_summaries_page)
        _skip_unless_empty(summaries, "VSUM-001")
        summaries.assert_page_shell()

    # VSUM-002 — Empty-state icon is displayed, no broken image
    @allure.story("Empty state")
    @allure.title("VSUM-002: the empty-state icon renders with a loaded image")
    def test_visit_summaries_empty_state_icon(self, visit_summaries_page):
        summaries = _open_visit_summaries(visit_summaries_page)
        _skip_unless_empty(summaries, "VSUM-002")
        summaries.assert_empty_state_icon()

    # VSUM-003 — Exact empty-state copy, no duplicate or truncated title
    @allure.story("Empty state")
    @allure.title("VSUM-003: the empty-state message matches the approved copy")
    def test_visit_summaries_empty_state_text_is_exact(self, visit_summaries_page):
        summaries = _open_visit_summaries(visit_summaries_page)
        _skip_unless_empty(summaries, "VSUM-003")
        summaries.assert_empty_state_text()

    # VSUM-004 — Quick-actions control is available (data-independent)
    @allure.story("Quick actions")
    @allure.title("VSUM-004: the quick-actions control is available and enabled")
    def test_visit_summaries_quick_action_control(self, visit_summaries_page):
        summaries = _open_visit_summaries(visit_summaries_page)
        summaries.assert_quick_action_control()

    # VSUM-008 — Zero-result dataset renders the COMPLETE empty state
    @allure.story("Zero-result dataset")
    @allure.title("VSUM-008: a zero-result dataset renders the complete empty state")
    def test_visit_summaries_zero_results_render_complete_empty_state(
        self, visit_summaries_page
    ):
        summaries = _open_visit_summaries(visit_summaries_page)
        _skip_unless_empty(summaries, "VSUM-008")
        with allure.step("Icon and exact title shown once, no phantom record"):
            summaries.assert_complete_empty_state()

    # VSUM-011 — Reached through application navigation
    @allure.story("Critical path")
    @allure.title("VSUM-011: application navigation reaches Visit Summaries")
    def test_visit_summaries_reached_via_application_navigation(
        self, visit_summaries_page
    ):
        shell = MeditekBasePage(visit_summaries_page)
        shell.open_home()
        shell.ensure_logged_in()
        shell.dismiss_blocking_dialogs()

        summaries = VisitSummariesModulePage(visit_summaries_page)
        with allure.step("Open navigation and select סיכומי ביקור"):
            summaries.open_via_application_menu()
            summaries.wait_until_loaded()
        _skip_unless_empty(summaries, "VSUM-011")
        with allure.step("The URL is /appointments and the empty state is displayed"):
            summaries.assert_page_shell()
            summaries.assert_empty_state_text()
